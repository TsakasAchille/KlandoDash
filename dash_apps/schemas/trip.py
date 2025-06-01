from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TripSchema(BaseModel):
    trip_id: str
    created_at: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    departure_name: Optional[str] = None
    departure_schedule: Optional[datetime] = None
    destination_name: Optional[str] = None
    destination_schedule: Optional[datetime] = None
    number_of_seats: Optional[int] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[float] = None
    trip_distance: Optional[float] = None
    trip_precision: Optional[float] = None
    trip_polyline: Optional[str] = None
    auto_confirmation: Optional[bool] = None
    passenger_count: Optional[int] = None
    driver_id: Optional[str] = None
    passenger_reservations: Optional[int] = None
    departure_latitude: Optional[float] = None
    departure_longitude: Optional[float] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
