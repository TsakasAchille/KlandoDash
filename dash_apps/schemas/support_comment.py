from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SupportCommentSchema(BaseModel):
    comment_id: Optional[str] = None
    ticket_id: str
    user_id: str
    user_name: Optional[str] = None  # Nom d'utilisateur pour l'affichage
    comment_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
