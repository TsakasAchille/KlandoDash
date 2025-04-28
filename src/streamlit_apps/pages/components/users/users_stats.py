import streamlit as st
import pandas as pd
from src.streamlit_apps.components.modern_card import modern_card
from src.data_processing.processors.trip_processor import TripProcessor

class UsersStatsManager:
    """Gère l'affichage des statistiques des utilisateurs"""
    
    def __init__(self):
        """Initialise le gestionnaire de statistiques utilisateur"""
        self.trip_processor = TripProcessor()
    
    def display_stats_info(self, user_data):
        """Affiche les statistiques de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        try:
            # Extraire l'ID de l'utilisateur (priorité à uid pour la nouvelle architecture)
            user_id = None
            if 'uid' in user_data:
                user_id = user_data.get('uid')
            elif 'id' in user_data:
                user_id = user_data.get('id')
            
            if not user_id:
                st.warning("Impossible de trouver l'identifiant de l'utilisateur")
                return
            
                    
            # Récupérer les statistiques de l'utilisateur
            total_trips_count, driver_trips_count, passenger_trips_count, total_distance, total_seats = self._calculate_user_stats(user_id)
            
            # Afficher les statistiques avec modern_card
            modern_card(
                title="Statistiques Utilisateur",
                icon="📊",  
                items=[
                    ("Trajets effectués (total)", total_trips_count),
                    ("Trajets en tant que conducteur", driver_trips_count),
                    ("Trajets en tant que passager", passenger_trips_count),
                    ("Distance totale", f"{total_distance:.1f} km"),
                    ("Places réservées", total_seats)
                ],
                accent_color="#2ecc71"  # Vert pour les statistiques
            )
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des statistiques: {str(e)}")
    
    def _calculate_user_stats(self, user_id):
        """Calcule les statistiques pour un utilisateur donné via la méthode optimisée unique"""
        try:
            # Récupérer tous les trajets de l'utilisateur (conducteur + passager)
            all_trips_df = self.trip_processor.get_all_user_trips(str(user_id))
            
            # Récupérer les trajets où l'utilisateur est passager uniquement
            passenger_trips_df = self.trip_processor.get_trips_for_passenger(str(user_id))
            
            # Calculer les statistiques
            total_trips_count = len(all_trips_df)
            passenger_trips_count = len(passenger_trips_df)
            driver_trips_count = total_trips_count - passenger_trips_count
            
            # Calculer la distance totale
            total_distance = all_trips_df['trip_distance'].sum() if 'trip_distance' in all_trips_df.columns and not all_trips_df.empty else 0
            
            # Nombre de places réservées (simplement le nombre de trajets en tant que passager pour l'instant)
            total_seats = passenger_trips_count
            
            return total_trips_count, driver_trips_count, passenger_trips_count, total_distance, total_seats
        except Exception as e:
            st.error(f"Erreur lors du calcul des statistiques: {str(e)}")
            return 0, 0, 0, 0, 0
