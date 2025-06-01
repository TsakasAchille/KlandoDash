from sqlalchemy import Column, String, Boolean, DateTime
from dash_apps.core.database import Base

class DashAuthorizedUser(Base):
    __tablename__ = "dash_authorized_users"

    email = Column(String, primary_key=True)
    active = Column(Boolean, default=True)
    role = Column(String, nullable=True)
    added_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    added_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "email": self.email,
            "active": self.active,
            "role": self.role,
            "added_at": self.added_at,
            "updated_at": self.updated_at,
            "added_by": self.added_by,
            "notes": self.notes
        }
