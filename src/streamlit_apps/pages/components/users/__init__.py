# Exporter les composants principaux pour les utilisateurs
from .users_display import UsersDisplay
from .users_profile import UsersProfileManager
from .users_stats import UsersStatsManager
from .users_trips import UsersTripsManager

# Fonctions d'aide pour faciliter l'importation
def get_users_display():
    """Retourne une instance de UsersDisplay"""
    return UsersDisplay()

def display_user_profile(user_data):
    """Affiche le profil de l'utilisateur"""
    return get_users_display().display_user_profile(user_data)

def display_user_stats(user_data):
    """Affiche les statistiques de l'utilisateur"""
    return get_users_display().display_user_stats(user_data)

def display_user_trips(user_data):
    """Affiche les trajets de l'utilisateur"""
    return get_users_display().display_user_trips(user_data)
