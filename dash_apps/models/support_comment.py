from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from dash_apps.core.database import Base
import uuid

class SupportComment(Base):
    __tablename__ = "support_comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(String, nullable=False)
    comment_text = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    comment_sent = Column(String, nullable=True)  # Message envoyé
    comment_received = Column(String, nullable=True)  # Message reçu
    comment_type = Column(String, nullable=True)  # Type de commentaire

    def to_dict(self):
        return {
            "comment_id": str(self.comment_id),
            "ticket_id": str(self.ticket_id),
            "user_id": self.user_id,
            "comment_text": self.comment_text,
            "comment_type": self.comment_type,
            "comment_sent": self.comment_sent,
            "comment_received": self.comment_received,
            "created_at": self.created_at,
        }
