from sqlalchemy import Column, String, Integer, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from dash_apps.core.database import Base
from dash_apps.models.user import User

class Booking(Base):
    __tablename__ = "bookings"

    trip_id = Column(String, ForeignKey("trips.trip_id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.uid"), primary_key=True)
    seats = Column(Integer, nullable=True, default=1)
    created_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)

    trip = relationship("Trip")
    user = relationship("User")

    def to_dict(self):
        return {
            "trip_id": self.trip_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "status": self.status,
            "seats": self.seats
        }
