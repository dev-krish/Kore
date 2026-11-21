from bson import ObjectId
from fastapi import APIRouter, HTTPException
from app.core.database import get_database

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("/{contact_id}")
async def get_contact(contact_id: str):
    db = get_database()
    doc = await db.contacts.find_one({"_id": ObjectId(contact_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Contact not found")
    doc["_id"] = str(doc["_id"])
    return doc
