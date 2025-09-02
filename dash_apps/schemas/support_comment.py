from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import uuid

class SupportCommentSchema(BaseModel):
    comment_id: Optional[str] = None
    ticket_id: str
    user_id: str
    user_name: Optional[str] = None  # Nom d'utilisateur pour l'affichage
    comment_text: str
    comment_sent: Optional[str] = None  # Message envoyé au client
    comment_received: Optional[str] = None  # Message reçu du client
    comment_source: Optional[str] = None  # Source: mail, phone
    comment_type: str = "internal"  # internal, external_sent, external_received
    created_at: datetime

    @field_validator('comment_id', 'ticket_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convertit automatiquement les UUIDs en strings"""
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    model_config = ConfigDict(from_attributes=True)
