from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union
from datetime import datetime
import uuid

class SupportTicketSchema(BaseModel):
    ticket_id: Optional[str] = None
    
    @field_validator('ticket_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convertit automatiquement les UUIDs en strings"""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
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
