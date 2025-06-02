from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TripSchema(BaseModel):
    trip_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    departure_name: Optional[str] = None
    departure_schedule: Optional[datetime] = None
    destination_name: Optional[str] = None
    destination_schedule: Optional[datetime] = None
    seats_available: Optional[int] = None
    seats_booked: Optional[int] = None
    seats_published: Optional[int] = None
    passenger_price: Optional[float] = None
    driver_price: Optional[float] = None
    distance: Optional[float] = None
    precision: Optional[str] = None
    polyline: Optional[str] = None
    driver_id: Optional[str] = None
    departure_latitude: Optional[float] = None
    departure_longitude: Optional[float] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None
    status: Optional[str] = None
    departure_description: Optional[str] = None
    destination_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
