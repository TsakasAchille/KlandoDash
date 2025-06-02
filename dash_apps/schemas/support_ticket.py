from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SupportTicketSchema(BaseModel):
    ticket_id: Optional[str] = None
    user_id: str
    subject: str
    message: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    contact_preference: Optional[str] = None
    phone: Optional[str] = None
    mail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
