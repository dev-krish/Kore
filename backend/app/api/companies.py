from bson import ObjectId
from fastapi import APIRouter, HTTPException
from app.core.database import get_database

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/{company_id}")
async def get_company(company_id: str):
    db = get_database()
    doc = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Company not found")
    doc["_id"] = str(doc["_id"])
    return doc
