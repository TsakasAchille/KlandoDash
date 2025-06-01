from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookingSchema(BaseModel):
    trip_id: str
    user_id: str
    seats: Optional[int]
    created_at: Optional[datetime]
    status: Optional[str]

    class Config:
        from_attributes = True
