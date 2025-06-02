from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from dash_apps.core.database import Base
import uuid

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    ticket_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    contact_preference = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    mail = Column(String, nullable=True)

    def to_dict(self):
        return {
            "ticket_id": str(self.ticket_id),
            "user_id": self.user_id,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "contact_preference": self.contact_preference,
            "phone": self.phone,
            "mail": self.mail
        }
