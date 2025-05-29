# Exporter les composants principaux pour les utilisateurs
from .users_profile import UsersProfileManager
from .users_stats import UsersStatsManager
from .users_trips import UsersTripsManager

# Importer toutes les fonctions du nouveau module
from .user_components import (
    get_user_data,
    display_users_table,
    display_profile_info,
    display_stats_info,
    display_trips_info,
    display_user_info
)

# Fonctions d'aide pour la compatibilité avec le code existant
def get_profile_manager():
    """Retourne une instance de UsersProfileManager"""
    return UsersProfileManager()

def display_user_profile(user_data):
    """Affiche le profil de l'utilisateur"""
    return display_profile_info(user_data)

def get_stats_manager():
    """Retourne une instance de UsersStatsManager"""
    return UsersStatsManager()

def display_user_stats(user_data):
    """Affiche les statistiques de l'utilisateur"""
    return display_stats_info(user_data)

def get_trips_manager():
    """Retourne une instance de UsersTripsManager"""
    return UsersTripsManager()

def display_user_trips(user_data):
    """Affiche les trajets de l'utilisateur"""
    return display_trips_info(user_data)
