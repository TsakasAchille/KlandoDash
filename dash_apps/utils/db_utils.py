import pandas as pd
from sqlalchemy import create_engine, text
import os

# Récupère la DATABASE_URL depuis les variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

from dash_apps.models.bookings import Booking
from dash_apps.core.database import get_session

def get_trip_bookings(trip_id):
    """
    Récupère la liste complète des réservations pour un trip_id depuis la table bookings (ORM).
    Retourne une liste de dicts (booking.to_dict()) pour chaque réservation.
    """
    try:
        with get_session() as session:
            bookings = session.query(Booking).filter(Booking.trip_id == trip_id).all()
            return [b.to_dict() for b in bookings] if bookings else []
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return []
