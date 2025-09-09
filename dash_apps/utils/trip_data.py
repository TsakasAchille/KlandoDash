import pandas as pd
from dash_apps.repositories.repository_factory import RepositoryFactory

# Fonction pour initialiser/récupérer les données de trajets
def get_trip_data():
    """
    Récupère les données de trajets depuis l'API REST via RepositoryFactory
    """
    try:
        trip_repository = RepositoryFactory.get_trip_repository()
        trips = trip_repository.list_trips(limit=1000)  # Récupérer plus de trajets pour les stats
        return pd.DataFrame(trips)
    except Exception as e:
        print(f"Erreur lors de la récupération des trajets: {e}")
        return pd.DataFrame()

def get_single_trip(trip_id):
    """
    Récupère un trajet spécifique par son ID via REST API
    """
    try:
        trip_repository = RepositoryFactory.get_trip_repository()
        trip = trip_repository.get_trip(trip_id)
        return trip
    except Exception as e:
        print(f"Erreur lors de la récupération du trajet {trip_id}: {e}")
        return None

def get_user_trips(user_id, as_driver=False, as_passenger=False):
    """
    Récupère les trajets d'un utilisateur spécifique via REST API
    """
    try:
        trip_repository = RepositoryFactory.get_trip_repository()
        
        if as_driver:
            # Filtrer les trajets où l'utilisateur est conducteur
            trips = trip_repository.search_trips(filters={'driver_id': user_id})
        elif as_passenger:
            # Pour les passagers, il faudrait une méthode spécifique ou une jointure
            # Pour l'instant, retourner une liste vide
            trips = []
        else:
            # Retourner tous les trajets
            trips = trip_repository.list_trips(limit=1000)
            
        return pd.DataFrame(trips)
    except Exception as e:
        print(f"Erreur lors de la récupération des trajets utilisateur {user_id}: {e}")
        return pd.DataFrame()
