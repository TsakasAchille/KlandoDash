import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union

# Importation des gestionnaires spécifiques (lazy loading)
def _get_profile_manager():
    from .users_profile import UsersProfileManager
    return UsersProfileManager()

def _get_stats_manager():
    from .users_stats import UsersStatsManager
    return UsersStatsManager()

def _get_trips_manager():
    from .users_trips import UsersTripsManager
    return UsersTripsManager()

class UsersDisplay:
    """
    Classe pour afficher les détails d'un utilisateur dans la page 03_users.py.
    Sert de façade pour les différents composants d'affichage des utilisateurs.
    """
    
    def __init__(self):
        """Initialise l'affichage des utilisateurs"""
        pass
    
    def user_display_handler(self, user_data):
        """Gère l'affichage complet des informations d'un utilisateur
        
        Args:
            user_data: DataFrame contenant les données de l'utilisateur sélectionné
        """
        if user_data is None or user_data.empty:
            st.warning("Aucune donnée utilisateur à afficher")
            return
            
        # Extraire la première ligne si c'est un DataFrame
        user = user_data.iloc[0] if isinstance(user_data, pd.DataFrame) else user_data
        
        # Afficher les différentes sections d'information
        self.display_user_profile(user)
        
        # Afficher les statistiques de l'utilisateur
        self.display_user_stats(user)
        
        # Afficher les trajets de l'utilisateur
        self.display_user_trips(user)
    
    def display_user_profile(self, user_data):
        """Affiche les informations de profil de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        return _get_profile_manager().display_profile_info(user_data)
    
    def display_user_stats(self, user_data):
        """Affiche les statistiques de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        return _get_stats_manager().display_stats_info(user_data)
    
    def display_user_trips(self, user_data):
        """Affiche les trajets associés à l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        return _get_trips_manager().display_trips_info(user_data)
