import pandas as pd
from dash_apps.utils.data_schema import get_trips, get_trip_by_id, get_trips_for_user

# Fonction pour initialiser/récupérer les données de trajets
def get_trip_data():
    """
    Récupère les données de trajets depuis la base de données en utilisant
    les définitions de tables JSON dans /dash_apps/utils/data_definition/
    """
    # Charge tous les trajets via notre nouveau module data_schema
    return get_trips()

def get_single_trip(trip_id):
    """
    Récupère un trajet spécifique par son ID
    """
    return get_trip_by_id(trip_id)

def get_user_trips(user_id, as_driver=False, as_passenger=False):
    """
    Récupère les trajets d'un utilisateur spécifique
    """
    return get_trips_for_user(user_id, as_driver, as_passenger)
