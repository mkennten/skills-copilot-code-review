"""
Announcements endpoints for the High School Management System API

Provides CRUD operations for managing school announcements.
Only authenticated teachers can create, update, or delete announcements.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementCreate(BaseModel):
    """Schema for creating a new announcement"""
    message: str
    start_date: Optional[str] = None
    expiration_date: str


class AnnouncementUpdate(BaseModel):
    """Schema for updating an existing announcement"""
    message: Optional[str] = None
    start_date: Optional[str] = None
    expiration_date: Optional[str] = None
    is_active: Optional[bool] = None


def serialize_announcement(announcement: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    return {
        "id": str(announcement["_id"]),
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"],
        "created_by": announcement.get("created_by"),
        "created_at": announcement.get("created_at"),
        "is_active": announcement.get("is_active", True)
    }


@router.get("/")
def get_announcements(include_inactive: bool = False) -> List[Dict[str, Any]]:
    """
    Get all announcements.
    By default, returns only active and non-expired announcements.
    Set include_inactive=True to get all announcements (for management).
    """
    now = datetime.now().isoformat()
    
    if include_inactive:
        # Return all announcements for management purposes
        announcements = list(announcements_collection.find())
    else:
        # Return only active, non-expired announcements that have started
        announcements = list(announcements_collection.find({
            "is_active": True,
            "expiration_date": {"$gt": now},
            "$or": [
                {"start_date": None},
                {"start_date": {"$lte": now}}
            ]
        }))
    
    return [serialize_announcement(a) for a in announcements]


@router.get("/{announcement_id}")
def get_announcement(announcement_id: str) -> Dict[str, Any]:
    """Get a specific announcement by ID"""
    try:
        announcement = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID format")
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return serialize_announcement(announcement)


@router.post("/")
def create_announcement(
    announcement: AnnouncementCreate,
    teacher_username: str
) -> Dict[str, Any]:
    """
    Create a new announcement.
    Requires teacher authentication.
    """
    # Verify teacher exists
    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid teacher username")
    
    # Validate expiration date
    try:
        exp_date = datetime.fromisoformat(announcement.expiration_date.replace('Z', '+00:00'))
        if exp_date < datetime.now(exp_date.tzinfo) if exp_date.tzinfo else datetime.now():
            raise HTTPException(status_code=400, detail="Expiration date must be in the future")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expiration date format")
    
    # Validate start date if provided
    if announcement.start_date:
        try:
            datetime.fromisoformat(announcement.start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format")
    
    new_announcement = {
        "_id": ObjectId(),
        "message": announcement.message,
        "start_date": announcement.start_date,
        "expiration_date": announcement.expiration_date,
        "created_by": teacher_username,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    announcements_collection.insert_one(new_announcement)
    
    return serialize_announcement(new_announcement)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementUpdate,
    teacher_username: str
) -> Dict[str, Any]:
    """
    Update an existing announcement.
    Requires teacher authentication.
    """
    # Verify teacher exists
    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid teacher username")
    
    try:
        existing = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID format")
    
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Build update dict with only provided fields
    update_data = {}
    if announcement.message is not None:
        update_data["message"] = announcement.message
    if announcement.start_date is not None:
        update_data["start_date"] = announcement.start_date if announcement.start_date else None
    if announcement.expiration_date is not None:
        # Validate expiration date
        try:
            datetime.fromisoformat(announcement.expiration_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiration date format")
        update_data["expiration_date"] = announcement.expiration_date
    if announcement.is_active is not None:
        update_data["is_active"] = announcement.is_active
    
    if update_data:
        update_data["updated_at"] = datetime.now().isoformat()
        update_data["updated_by"] = teacher_username
        announcements_collection.update_one(
            {"_id": ObjectId(announcement_id)},
            {"$set": update_data}
        )
    
    # Return updated announcement
    updated = announcements_collection.find_one({"_id": ObjectId(announcement_id)})
    return serialize_announcement(updated)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: str
) -> Dict[str, str]:
    """
    Delete an announcement.
    Requires teacher authentication.
    """
    # Verify teacher exists
    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid teacher username")
    
    try:
        result = announcements_collection.delete_one({"_id": ObjectId(announcement_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID format")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"message": "Announcement deleted successfully"}
