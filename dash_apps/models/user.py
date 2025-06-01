from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric, DateTime
from dash_apps.core.database import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True)
    display_name = Column(String)
    email = Column(String)
    first_name = Column(String)
    name = Column(String)
    phone_number = Column(String)
    birth = Column(Date)
    photo_url = Column(String)
    bio = Column(String)
    driver_documents_transmitted = Column(Boolean)
    driver_licence_url = Column(String)
    gender = Column(String)
    id_card_url = Column(String)
    rating = Column(Numeric)
    rating_count = Column(Integer)
    role_preference = Column(String)
    updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    is_driver_doc_validated = Column(Boolean)

    def to_dict(self):
        """Retourne un dictionnaire des champs du modèle User."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
