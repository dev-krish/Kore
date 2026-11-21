from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.deps import get_current_user_id

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/{company_id}")
async def get_company(company_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieves a discovered company record.
    Strictly verifies ownership: User must own the campaign that discovered this company.
    """
    db = get_database()
    try:
        obj_id = ObjectId(company_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid company ID format.")

    doc = await db.companies.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Company not found.")

    # Enforce user ownership via campaign verification
    campaign_id = doc.get("campaignId")
    if campaign_id:
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to view this company."
            )

    doc["_id"] = str(doc["_id"])
    return doc
