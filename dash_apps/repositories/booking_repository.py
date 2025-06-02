from typing import List, Optional
from dash_apps.core.database import SessionLocal
from dash_apps.models.bookings import Booking
from dash_apps.schemas.booking import BookingSchema

class BookingRepository:
    @staticmethod
    def get_all_bookings() -> List[BookingSchema]:
        with SessionLocal() as db:
            bookings = db.query(Booking).all()
            return [BookingSchema.from_orm(b) for b in bookings]

    @staticmethod
    def get_booking(trip_id: str, user_id: str) -> Optional[BookingSchema]:
        with SessionLocal() as db:
            booking = db.query(Booking).filter(Booking.trip_id == trip_id, Booking.user_id == user_id).first()
            return BookingSchema.from_orm(booking) if booking else None

    @staticmethod
    def get_trip_bookings(trip_id: str) -> list:
        """
        Récupère la liste complète des réservations pour un trip_id depuis la table bookings (ORM).
        Retourne une liste de dicts (booking.to_dict()) pour chaque réservation.
        """
        with SessionLocal() as db:
            bookings = db.query(Booking).filter(Booking.trip_id == trip_id).all()
            return [b.to_dict() for b in bookings] if bookings else []

