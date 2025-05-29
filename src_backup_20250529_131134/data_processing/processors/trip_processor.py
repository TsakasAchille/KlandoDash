from src.core.database import get_session, Trip, TripPassenger
import pandas as pd

class TripProcessor:
    """Gestionnaire optimisé des trajets (lecture seule)"""

    @staticmethod
    def get_all_trips():
        """Retourne tous les trajets de la base (DataFrame)"""
        with get_session() as session:
            trips = session.query(Trip).all()
            return pd.DataFrame([t.to_dict() for t in trips]) if trips else pd.DataFrame()

    @staticmethod
    def get_all_user_trips(user_id):
        """Retourne tous les trajets où l'utilisateur est conducteur OU passager (requête optimisée) + debug"""
        with get_session() as session:
            print(f"[DEBUG get_all_user_trips] user_id utilisé = {user_id}")
            driver_trips = session.query(Trip).filter(Trip.driver_id == user_id)
            passenger_trips = session.query(Trip).join(
                TripPassenger, Trip.trip_id == TripPassenger.trip_id
            ).filter(TripPassenger.passenger_id == user_id)
            print(f"[DEBUG] nb driver_trips = {driver_trips.count()} | nb passenger_trips = {passenger_trips.count()}")
            all_trips = driver_trips.union(passenger_trips).all()
            print(f"[DEBUG] total trips retournés = {len(all_trips)}")
            return pd.DataFrame([t.to_dict() for t in all_trips]) if all_trips else pd.DataFrame()

    @staticmethod
    def get_trips_for_passenger(user_id):
        """Retourne tous les trips où l'utilisateur est passager uniquement (debug)"""
        with get_session() as session:
            print(f"[DEBUG get_trips_for_passenger] user_id utilisé = {user_id}")
            trips = session.query(Trip).join(
                TripPassenger, Trip.trip_id == TripPassenger.trip_id
            ).filter(TripPassenger.passenger_id == user_id).all()
            print(f"[DEBUG] nb trips trouvés comme passager = {len(trips)}")
            return pd.DataFrame([t.to_dict() for t in trips]) if trips else pd.DataFrame()

    @staticmethod
    def get_trip_by_id(trip_id):
        """Retourne un trajet par son ID (dict)"""
        with get_session() as session:
            trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()
            return trip.to_dict() if trip else None

    @staticmethod
    def get_trips_by_driver_id(driver_id):
        """Retourne tous les trajets où driver_id == driver_id"""
        with get_session() as session:
            trips = session.query(Trip).filter(Trip.driver_id == driver_id).all()
            return pd.DataFrame([t.to_dict() for t in trips]) if trips else pd.DataFrame()

    @staticmethod
    def get_trips_by_trip_ids(trip_ids):
        """Retourne tous les trajets dont trip_id est dans trip_ids"""
        if not trip_ids:
            return pd.DataFrame()
        with get_session() as session:
            trips = session.query(Trip).filter(Trip.trip_id.in_(trip_ids)).all()
            return pd.DataFrame([t.to_dict() for t in trips]) if trips else pd.DataFrame()