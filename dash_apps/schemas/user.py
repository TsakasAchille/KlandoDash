from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class UserSchema(BaseModel):
    uid: str
    display_name: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    name: Optional[str]
    phone_number: Optional[str]
    birth: Optional[date]
    photo_url: Optional[str]
    bio: Optional[str]
    driver_documents_transmitted: Optional[bool]
    driver_licence_url: Optional[str]
    gender: Optional[str]
    id_card_url: Optional[str]
    rating: Optional[float]
    rating_count: Optional[int]
    role_preference: Optional[str]
    updated_at: Optional[datetime]
    created_at: Optional[datetime]
    is_driver_doc_validated: Optional[bool]

    class Config:
        from_attributes = True
