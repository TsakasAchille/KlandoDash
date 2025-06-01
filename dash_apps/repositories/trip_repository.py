from dash_apps.models.trip import Trip
from dash_apps.schemas.trip import TripSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional

class TripRepository:
    @staticmethod
    def get_trip(session: Session, trip_id: str) -> Optional[TripSchema]:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        return TripSchema.model_validate(trip) if trip else None

    @staticmethod
    def list_trips(session: Session, skip: int = 0, limit: int = 100) -> List[TripSchema]:
        trips = session.query(Trip).offset(skip).limit(limit).all()
        return [TripSchema.model_validate(trip) for trip in trips]

    @staticmethod
    def create_trip(session: Session, trip_data: dict) -> TripSchema:
        trip = Trip(**trip_data)
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return TripSchema.model_validate(trip)

    @staticmethod
    def update_trip(session: Session, trip_id: str, updates: dict) -> Optional[TripSchema]:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            return None
        for key, value in updates.items():
            setattr(trip, key, value)
        session.commit()
        session.refresh(trip)
        return TripSchema.model_validate(trip)

    @staticmethod
    def delete_trip(session: Session, trip_id: str) -> bool:
        trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            return False
        session.delete(trip)
        session.commit()
        return True
