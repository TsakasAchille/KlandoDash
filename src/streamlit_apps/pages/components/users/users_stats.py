import streamlit as st
import pandas as pd
from datetime import datetime
from src.streamlit_apps.components.modern_card import modern_card
from src.data_processing.processors.trip_processor import TripProcessor

class UsersStatsManager:
    """Gu00e8re l'affichage des statistiques des utilisateurs"""
    
    def __init__(self):
        """Initialise le gestionnaire de statistiques utilisateur"""
        self.trip_processor = TripProcessor()
    
    def display_stats_info(self, user_data):
        """Affiche les statistiques de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        try:
            # Extraire l'ID de l'utilisateur
            user_id = user_data.get('id', None)
            if not user_id:
                return
            
            # Ru00e9cupu00e9rer les statistiques de l'utilisateur
            trips_count, total_distance, total_seats = self._calculate_user_stats(user_id)
            
            # Afficher les statistiques avec modern_card
            modern_card(
                title="Statistiques Utilisateur",
                icon="📊",  # ud83dudcca = "ud83dudcca" (emoji graphique)
                items=[
                    ("Trajets effectués", trips_count),
                    ("Distance totale", f"{total_distance:.1f} km"),
                    ("Places réservées", total_seats)
                ],
                accent_color="#2ecc71"  # Vert pour les statistiques
            )
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des statistiques: {str(e)}")
    
    def _calculate_user_stats(self, user_id):
        """Calcule les statistiques pour un utilisateur donnu00e9
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            tuple: (nombre de trajets, distance totale, nombre total de places)
        """
        # Ru00e9cupu00e9rer tous les trajets de la base de donnu00e9es
        try:
            trips_df = self.trip_processor.handler()
            
            # Filtrer les trajets de l'utilisateur en su00e9curisant le filtrage
            user_trips = pd.DataFrame()
            if 'all_passengers' in trips_df.columns:
                # Convertir user_id en string pour u00e9viter les probu00e8mes de type
                user_id_str = str(user_id)
                # Filtrer les trajets qui contiennent l'ID de l'utilisateur
                user_trips = trips_df[trips_df['all_passengers'].fillna('').apply(
                    lambda x: user_id_str in str(x).split(',') if x else False
                )]
            
            # Calculer les statistiques
            trips_count = len(user_trips)
            total_distance = user_trips['trip_distance'].sum() if 'trip_distance' in user_trips.columns else 0
            
            # Calculer le nombre total de places ru00e9servu00e9es (1 par trajet par du00e9faut)
            total_seats = trips_count
            
            return trips_count, total_distance, total_seats
            
        except Exception as e:
            st.error(f"Erreur lors du calcul des statistiques: {str(e)}")
            return 0, 0, 0
