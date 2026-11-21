from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.deps import get_current_user_id

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("/{contact_id}")
async def get_contact(contact_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieves a discovered contact record.
    Strictly verifies ownership: User must own the campaign that sourced this contact.
    """
    db = get_database()
    try:
        obj_id = ObjectId(contact_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid contact ID format.")

    doc = await db.contacts.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Contact not found.")

    # Enforce user ownership via campaign verification
    campaign_id = doc.get("campaignId")
    if campaign_id:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to view this contact."
            )

    doc["_id"] = str(doc["_id"])
    return doc
