from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from dash_apps.core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    departure_date = Column(DateTime(timezone=True), nullable=True)
    departure_name = Column(String, nullable=True)
    departure_schedule = Column(DateTime(timezone=True), nullable=True)
    destination_name = Column(String, nullable=True)
    seats_available = Column(Integer, nullable=True)
    seats_booked = Column(Integer, nullable=True)
    seats_published = Column(Integer, nullable=True)
    passenger_price = Column(Integer, nullable=True)
    driver_price = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)
    precision = Column(String, nullable=True)
    polyline = Column(String, nullable=True)
    driver_id = Column(String, ForeignKey("users.uid"), nullable=True)
    departure_latitude = Column(Float, nullable=True)
    departure_longitude = Column(Float, nullable=True)
    destination_latitude = Column(Float, nullable=True)
    destination_longitude = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    departure_description = Column(String, nullable=True)
    destination_description = Column(String, nullable=True)

    def to_dict(self):
        return {
            "trip_id": self.trip_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "departure_date": self.departure_date,
            "departure_name": self.departure_name,
            "departure_schedule": self.departure_schedule,
            "destination_name": self.destination_name,
            "seats_available": self.seats_available,
            "seats_booked": self.seats_booked,
            "seats_published": self.seats_published,
            "passenger_price": self.passenger_price,
            "driver_price": self.driver_price,
            "distance": self.distance,
            "precision": self.precision,
            "polyline": self.polyline,
            "driver_id": self.driver_id,
            "departure_latitude": self.departure_latitude,
            "departure_longitude": self.departure_longitude,
            "destination_latitude": self.destination_latitude,
            "destination_longitude": self.destination_longitude,
            "status": self.status,
            "departure_description": self.departure_description,
            "destination_description": self.destination_description,
        }
