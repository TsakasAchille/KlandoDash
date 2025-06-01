import pandas as pd
from dash_apps.repositories.trip_repository import TripRepository
from dash_apps.schemas.trip import TripSchema
from dash_apps.core.database import get_session
import pandas as pd

# Fonction pour initialiser/récupérer les données de trajets
def get_trip_data():
    """
    Récupère les données de trajets depuis la base de données via TripRepository (SQLAlchemy)
    """
    with get_session() as session:
        trips = TripRepository.list_trips(session)
        return pd.DataFrame([trip.model_dump() for trip in trips])

def get_single_trip(trip_id):
    """
    Récupère un trajet spécifique par son ID via TripRepository
    """
    with get_session() as session:
        trip = TripRepository.get_trip(session, trip_id)
        return trip.model_dump() if trip else None

def get_user_trips(user_id, as_driver=False, as_passenger=False):
    """
    Récupère les trajets d'un utilisateur spécifique (conducteur/passager)
    """
    # À adapter si tu veux des requêtes personnalisées (par défaut, retourne tous les trajets où driver_id = user_id si as_driver)
    with get_session() as session:
        if as_driver:
            trips = session.query(TripRepository.Trip).filter_by(driver_id=user_id).all()
        elif as_passenger:
            # Nécessite une jointure avec Booking si tu veux les trajets où l'utilisateur est passager
            # À implémenter selon besoin
            trips = []
        else:
            trips = session.query(TripRepository.Trip).all()
        return pd.DataFrame([TripSchema.model_validate(trip).model_dump() for trip in trips])
