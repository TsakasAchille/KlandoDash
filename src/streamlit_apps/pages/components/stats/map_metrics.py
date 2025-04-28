import streamlit as st
from src.streamlit_apps.components.modern_card import modern_card

class MapMetrics:
    """Classe responsable de l'affichage des métriques de la carte"""
    
    def __init__(self):
        """Initialise le gestionnaire de métriques"""
        pass
    
    def display_map_metrics(self, trips_df):
        """Affiche les métriques de la carte
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        # Calculer les métriques de la carte
        total_trips = len(trips_df)
        
        # Calculer la distance totale parcourue
        total_distance = trips_df['trip_distance'].sum() if 'trip_distance' in trips_df.columns else 0
        
        # Calculer les économies de CO2 si disponible
        co2_savings = trips_df['co2_savings'].sum() if 'co2_savings' in trips_df.columns else 0
        
        # Calculer les économies de carburant si disponible
        fuel_savings = trips_df['fuel_savings'].sum() if 'fuel_savings' in trips_df.columns else 0
        
        # Afficher les métriques avec modern_card
        modern_card(
            title="Impact environnemental des trajets",
            icon="🗺️",  # Carte
            items=[
                ("Nombre de trajets", total_trips),
                ("Distance totale", f"{total_distance:.1f} km"),
                ("Economies de CO2", f"{co2_savings:.1f} kg"),
                ("Economies de carburant", f"{fuel_savings:.1f} L")
            ],
            accent_color="#27ae60"  # Vert pour l'impact environnemental
        )
