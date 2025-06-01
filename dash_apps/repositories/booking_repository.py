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
    def create_booking(booking_data: BookingSchema) -> BookingSchema:
        with SessionLocal() as db:
            db_booking = Booking(**booking_data.model_dump(exclude_unset=True))
            db.add(db_booking)
            db.commit()
            db.refresh(db_booking)
            return BookingSchema.from_orm(db_booking)

    @staticmethod
    def update_booking(trip_id: str, user_id: str, booking_data: BookingSchema) -> Optional[BookingSchema]:
        with SessionLocal() as db:
            booking = db.query(Booking).filter(Booking.trip_id == trip_id, Booking.user_id == user_id).first()
            if not booking:
                return None
            for field, value in booking_data.model_dump(exclude_unset=True).items():
                setattr(booking, field, value)
            db.commit()
            db.refresh(booking)
            return BookingSchema.from_orm(booking)

    @staticmethod
    def delete_booking(trip_id: str, user_id: str) -> bool:
        with SessionLocal() as db:
            booking = db.query(Booking).filter(Booking.trip_id == trip_id, Booking.user_id == user_id).first()
            if not booking:
                return False
            db.delete(booking)
            db.commit()
            return True
