from datetime import datetime, timezone
import hashlib
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.config import settings
from app.core.database import get_database
from app.core.encryption import encrypt_token, decrypt_token
from app.api.deps import get_current_user_id
from app.models.draft import ApprovalStatus, EmailDraftModel, EmailDraftUpdate
from app.models.delivery import DeliveryStatus, EmailDeliveryModel
from app.services.email.approval_gate import approval_gate
from app.services.email.gmail_service import gmail_service

router = APIRouter(prefix="/drafts", tags=["Email Drafts & Approval"])

@router.get("")
async def list_drafts(
    campaignId: Optional[str] = None,
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    db = get_database()
    query = {"userId": user_id}
    if campaignId:
        query["campaignId"] = campaignId
    if status:
        query["approvalStatus"] = status

    cursor = db.emailDrafts.find(query).sort("createdAt", -1)
    drafts = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        drafts.append(d)
    return drafts

@router.get("/{draft_id}")
async def get_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    try:
        obj_id = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID format.")

    doc = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Email draft not found.")
    doc["_id"] = str(doc["_id"])
    return doc

@router.put("/{draft_id}")
async def update_draft(
    draft_id: str,
    update_data: EmailDraftUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Edits a draft's subject or body.
    CRITICAL: Any edit invalidates previous approvals to prevent unauthorized modification.
    Editing is strictly prohibited once sending has begun or completed.
    """
    db = get_database()
    try:
        obj_id = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID format.")

    existing = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Email draft not found.")

    current_status = existing.get("approvalStatus")
    if current_status in (ApprovalStatus.SENT.value, ApprovalStatus.SENDING.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit draft in '{current_status}' state."
        )

    update_fields = {}
    if update_data.subject is not None:
        update_fields["subject"] = update_data.subject
    if update_data.body is not None:
        update_fields["body"] = update_data.body

    # Invalidate approval because content changed!
    update_fields["approvalStatus"] = ApprovalStatus.PENDING_REVIEW.value
    update_fields["approvedContentHash"] = None
    update_fields["approvedAt"] = None
    update_fields["updatedAt"] = datetime.now(timezone.utc)

    updated = await db.emailDrafts.find_one_and_update(
        {"_id": obj_id, "userId": user_id},
        {"$set": update_fields},
        return_document=True
    )
    updated["_id"] = str(updated["_id"])
    return updated

@router.post("/{draft_id}/approve")
async def approve_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Explicit user approval of an exact email draft.
    Generates and stores the cryptographic SHA-256 integrity hash of recipient + subject + body.
    """
    db = get_database()
    try:
        obj_id = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID format.")

    draft = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found.")

    current_status = draft.get("approvalStatus")
    if current_status in (ApprovalStatus.SENT.value, ApprovalStatus.SENDING.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot re-approve an email that is already '{current_status}'."
        )

    content_hash = approval_gate.compute_content_hash(
        recipient=draft["recipientEmail"],
        subject=draft["subject"],
        body=draft["body"]
    )

    now = datetime.now(timezone.utc)
    updated = await db.emailDrafts.find_one_and_update(
        {"_id": obj_id, "userId": user_id},
        {
            "$set": {
                "approvalStatus": ApprovalStatus.APPROVED.value,
                "approvedContentHash": content_hash,
                "approvedAt": now,
                "updatedAt": now
            }
        },
        return_document=True
    )
    return {
        "status": "approved",
        "draftId": draft_id,
        "approvedContentHash": content_hash,
        "message": "Draft explicitly approved and cryptographically hashed for sending."
    }

@router.post("/{draft_id}/reject")
async def reject_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    """Rejects an email draft, archiving it from the active send queue."""
    db = get_database()
    try:
        obj_id = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID format.")

    draft = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found.")

    current_status = draft.get("approvalStatus")
    if current_status in (ApprovalStatus.SENT.value, ApprovalStatus.SENDING.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject an email that is already '{current_status}'."
        )

    now = datetime.now(timezone.utc)
    await db.emailDrafts.update_one(
        {"_id": obj_id, "userId": user_id},
        {
            "$set": {
                "approvalStatus": ApprovalStatus.REJECTED.value,
                "approvedContentHash": None,
                "updatedAt": now
            }
        }
    )
    return {"status": "rejected", "draftId": draft_id}

@router.post("/{draft_id}/send")
async def send_approved_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Sends an email draft ONLY after passing the strict Human Approval Gate.
    Guarantees:
    1. Atomic conditional state transition (Compare-And-Swap) preventing concurrent duplicate sends.
    2. Cryptographic content hash matching recipient + subject + body.
    3. User-specific Gmail OAuth token validation.
    4. Safe handling of uncertain or failed delivery outcomes.
    """
    db = get_database()
    try:
        obj_id = ObjectId(draft_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid draft ID format.")

    # Step 1: Read draft to verify approval preconditions
    draft_doc = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
    if not draft_doc:
        raise HTTPException(status_code=404, detail="Email draft not found.")

    draft_doc["_id"] = str(draft_doc["_id"])
    draft_model = EmailDraftModel(**draft_doc)

    is_valid, reason = approval_gate.verify_ready_for_sending(draft_model)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Human Approval Gate check failed: {reason}"
        )

    # Server-side guard 1: Validate recipient email is present and valid
    if not draft_model.recipientEmail or draft_model.recipientEmail == "contact@example.com":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send draft without a valid, verified recipient email address."
        )

    # Server-side guard 2: Strictly block live Gmail delivery to demo contacts
    is_demo = bool(draft_doc.get("isDemoRecord") or draft_doc.get("provenance") == "curated_demo" or draft_model.recipientEmail.endswith("@example.com"))
    if is_demo and settings.GMAIL_MODE == "live" and gmail_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Live Gmail delivery to demo contacts is strictly blocked. Switch GMAIL_MODE to 'demo' or use live discovered contacts."
        )

    now = datetime.now(timezone.utc)

    # Step 2: ATOMIC CONDITIONAL STATE TRANSITION (Prevents concurrent race conditions)
    # Only transitions to SENDING if current status is exactly APPROVED and hash matches!
    locked_draft = await db.emailDrafts.find_one_and_update(
        {
            "_id": obj_id,
            "userId": user_id,
            "approvalStatus": ApprovalStatus.APPROVED.value,
            "approvedContentHash": draft_model.approvedContentHash
        },
        {
            "$set": {
                "approvalStatus": ApprovalStatus.SENDING.value,
                "sendingStartedAt": now,
                "updatedAt": now
            }
        },
        return_document=True
    )

    if not locked_draft:
        # A concurrent request or status transition intervened!
        current = await db.emailDrafts.find_one({"_id": obj_id, "userId": user_id})
        status_val = current.get("approvalStatus") if current else "unknown"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Concurrent send or invalid state detected. Draft status is currently '{status_val}'. Duplicate send blocked."
        )

    # Step 3: Retrieve authenticated user's stored OAuth tokens (decrypted for dispatch)
    user_cred = await db.integrationCredentials.find_one({"userId": user_id, "provider": "gmail"})
    user_tokens = user_cred.get("tokens") if user_cred else None
    if user_tokens:
        user_tokens = dict(user_tokens)
        if "access_token" in user_tokens:
            user_tokens["access_token"] = decrypt_token(user_tokens["access_token"])
        if "refresh_token" in user_tokens:
            user_tokens["refresh_token"] = decrypt_token(user_tokens["refresh_token"])

    # Step 4: Dispatch via Gmail Service
    try:
        delivery_result = await gmail_service.send_email(
            recipient=draft_model.recipientEmail,
            subject=draft_model.subject,
            body=draft_model.body,
            user_tokens=user_tokens,
            is_demo_record=is_demo
        )
    except Exception as dispatch_err:
        delivery_result = {
            "success": False,
            "mode": "unknown",
            "error": f"Unexpected dispatch exception: {str(dispatch_err)}"
        }

    now_completed = datetime.now(timezone.utc)

    # Persist refreshed OAuth token if Google OAuth renewed the session
    if delivery_result.get("refreshedToken"):
        await db.integrationCredentials.update_one(
            {"userId": user_id, "provider": "gmail"},
            {
                "$set": {
                    "tokens.access_token": encrypt_token(delivery_result["refreshedToken"]),
                    "tokens.expiry": delivery_result.get("refreshedExpiry"),
                    "updatedAt": now_completed
                }
            }
        )

    # Handle Uncertain Delivery State (Ambiguous network failure mid-dispatch)
    if delivery_result.get("status") == "uncertain":
        err_msg = delivery_result.get("error", "Unconfirmed delivery outcome due to network timeout.")
        await db.emailDrafts.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "approvalStatus": ApprovalStatus.FAILED.value,
                    "deliveryError": f"UNCERTAIN: {err_msg} Automated retry is blocked to prevent double-send.",
                    "updatedAt": now_completed
                }
            }
        )
        await db.emailDeliveries.insert_one({
            "draftId": draft_id,
            "campaignId": draft_model.campaignId,
            "userId": user_id,
            "recipient": draft_model.recipientEmail,
            "subject": draft_model.subject,
            "contentHash": draft_model.approvedContentHash,
            "status": DeliveryStatus.UNCERTAIN.value,
            "mode": delivery_result.get("mode", "live_gmail"),
            "error": err_msg,
            "sentAt": now_completed
        })
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Email dispatch uncertain: {err_msg} Automated retry is blocked to prevent double-sending."
        )

    if delivery_result.get("success"):
        mode = delivery_result.get("mode", "live_gmail")
        delivery_status = DeliveryStatus.SUCCESS.value if mode == "live_gmail" else DeliveryStatus.DEMO_DELIVERED.value

        # Step 5: Record Delivery Audit Log
        delivery_doc = {
            "draftId": draft_id,
            "campaignId": draft_model.campaignId,
            "userId": user_id,
            "recipient": draft_model.recipientEmail,
            "subject": draft_model.subject,
            "contentHash": draft_model.approvedContentHash,
            "providerMessageId": delivery_result.get("providerMessageId"),
            "status": delivery_status,
            "mode": mode,
            "sentAt": now_completed
        }
        await db.emailDeliveries.insert_one(delivery_doc)

        # Step 6: Mark draft as SENT
        await db.emailDrafts.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "approvalStatus": ApprovalStatus.SENT.value,
                    "updatedAt": now_completed
                }
            }
        )

        # Step 7: Increment Campaign Sent Count
        try:
            await db.campaigns.update_one(
                {"_id": ObjectId(draft_model.campaignId)},
                {"$inc": {"emailsSentCount": 1}, "$set": {"updatedAt": now_completed}}
            )
        except Exception:
            pass

        return {
            "status": "sent",
            "draftId": draft_id,
            "deliveryResult": delivery_result
        }
    else:
        # Step 8: Safe Failure Handling: Transition status to FAILED, record audit log
        err_msg = delivery_result.get("error", "Unknown provider dispatch error.")
        await db.emailDrafts.update_one(
            {"_id": obj_id},
            {
                "$set": {
                    "approvalStatus": ApprovalStatus.FAILED.value,
                    "deliveryError": err_msg,
                    "updatedAt": now_completed
                }
            }
        )
        await db.emailDeliveries.insert_one({
            "draftId": draft_id,
            "campaignId": draft_model.campaignId,
            "userId": user_id,
            "recipient": draft_model.recipientEmail,
            "subject": draft_model.subject,
            "contentHash": draft_model.approvedContentHash,
            "status": DeliveryStatus.FAILED.value,
            "error": err_msg,
            "sentAt": now_completed
        })

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if "not connected" in err_msg.lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email dispatch failed: {err_msg}"
        )
