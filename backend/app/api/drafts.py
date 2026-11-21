from datetime import datetime, timezone
import hashlib
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.database import get_database
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
    doc = await db.emailDrafts.find_one({"_id": ObjectId(draft_id), "userId": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Email draft not found")
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
    """
    db = get_database()
    existing = await db.emailDrafts.find_one({"_id": ObjectId(draft_id), "userId": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Email draft not found")

    if existing.get("approvalStatus") == ApprovalStatus.SENT.value:
        raise HTTPException(status_code=400, detail="Cannot edit an email that has already been sent.")

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
        {"_id": ObjectId(draft_id), "userId": user_id},
        {"$set": update_fields},
        return_document=True
    )
    updated["_id"] = str(updated["_id"])
    return updated

@router.post("/{draft_id}/approve")
async def approve_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Explicit user approval of an exact email draft.
    Generates and stores the SHA-256 integrity hash of recipient + subject + body.
    """
    db = get_database()
    draft = await db.emailDrafts.find_one({"_id": ObjectId(draft_id), "userId": user_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found")

    if draft.get("approvalStatus") == ApprovalStatus.SENT.value:
        raise HTTPException(status_code=400, detail="Cannot re-approve an email that has already been sent.")

    content_hash = approval_gate.compute_content_hash(
        recipient=draft["recipientEmail"],
        subject=draft["subject"],
        body=draft["body"]
    )

    now = datetime.now(timezone.utc)
    updated = await db.emailDrafts.find_one_and_update(
        {"_id": ObjectId(draft_id), "userId": user_id},
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
    updated["_id"] = str(updated["_id"])
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
    draft = await db.emailDrafts.find_one({"_id": ObjectId(draft_id), "userId": user_id})
    if not draft:
        raise HTTPException(status_code=404, detail="Email draft not found")

    if draft.get("approvalStatus") == ApprovalStatus.SENT.value:
        raise HTTPException(status_code=400, detail="Cannot reject an email that has already been sent.")

    now = datetime.now(timezone.utc)
    updated = await db.emailDrafts.find_one_and_update(
        {"_id": ObjectId(draft_id), "userId": user_id},
        {
            "$set": {
                "approvalStatus": ApprovalStatus.REJECTED.value,
                "approvedContentHash": None,
                "updatedAt": now
            }
        },
        return_document=True
    )
    return {"status": "rejected", "draftId": draft_id}

@router.post("/{draft_id}/send")
async def send_approved_draft(draft_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Sends an email draft ONLY after passing the strict Human Approval Gate.
    Verifies content integrity hash, prevents duplicate sends, and logs delivery.
    """
    db = get_database()
    draft_doc = await db.emailDrafts.find_one({"_id": ObjectId(draft_id), "userId": user_id})
    if not draft_doc:
        raise HTTPException(status_code=404, detail="Email draft not found")

    draft_doc["_id"] = str(draft_doc["_id"])
    draft_model = EmailDraftModel(**draft_doc)

    # 1. Enforce Approval Gate
    is_valid, reason = approval_gate.verify_ready_for_sending(draft_model)
    if not is_valid:
        raise HTTPException(status_code=403, detail=f"Human Approval Gate check failed: {reason}")

    # Mark sending in progress
    await db.emailDrafts.update_one(
        {"_id": ObjectId(draft_id)},
        {"$set": {"approvalStatus": ApprovalStatus.SENDING.value}}
    )

    # 2. Dispatch via Gmail Service
    delivery_result = await gmail_service.send_email(
        recipient=draft_model.recipientEmail,
        subject=draft_model.subject,
        body=draft_model.body
    )

    now = datetime.now(timezone.utc)

    if delivery_result.get("success"):
        # 3. Record Delivery
        delivery_doc = {
            "draftId": draft_id,
            "campaignId": draft_model.campaignId,
            "userId": user_id,
            "recipient": draft_model.recipientEmail,
            "subject": draft_model.subject,
            "contentHash": draft_model.approvedContentHash,
            "providerMessageId": delivery_result.get("providerMessageId"),
            "status": DeliveryStatus.SUCCESS.value if delivery_result.get("mode") == "live_gmail" else DeliveryStatus.DEMO_DELIVERED.value,
            "sentAt": now
        }
        await db.emailDeliveries.insert_one(delivery_doc)

        # 4. Mark draft as SENT
        await db.emailDrafts.update_one(
            {"_id": ObjectId(draft_id)},
            {"$set": {"approvalStatus": ApprovalStatus.SENT.value, "updatedAt": now}}
        )

        # 5. Increment Campaign Sent Count
        await db.campaigns.update_one(
            {"_id": ObjectId(draft_model.campaignId)},
            {"$inc": {"emailsSentCount": 1}, "$set": {"updatedAt": now}}
        )

        return {
            "status": "sent",
            "draftId": draft_id,
            "deliveryResult": delivery_result
        }
    else:
        # Mark draft as FAILED
        await db.emailDrafts.update_one(
            {"_id": ObjectId(draft_id)},
            {"$set": {"approvalStatus": ApprovalStatus.FAILED.value, "updatedAt": now}}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Email dispatch failed: {delivery_result.get('error', 'Unknown provider error')}"
        )
