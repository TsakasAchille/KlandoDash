import streamlit as st
import pandas as pd
from src.streamlit_apps.components.modern_card import modern_card

class TripsRouteManager:
    """Gère l'affichage des informations d'itinéraire des trajets"""
    
    def display_route_info(self, trip_data):
        """Affiche la carte d'itinéraire incluant départ, destination et distance
        
        Args:
            trip_data: Données du trajet sélectionné
        """
        if 'departure_name' in trip_data and 'destination_name' in trip_data:
            try:
                departure = trip_data['departure_name'] if trip_data['departure_name'] else "Non disponible"
                destination = trip_data['destination_name'] if trip_data['destination_name'] else "Non disponible"
                modern_card(
                    title="Itinéraire",
                    icon="🧭",
                    items=[
                        ("Départ", departure),
                        ("Destination", destination)
                    ],
                    accent_color="#2B8CB6"
                )
            except Exception as e:
                st.error(f"Erreur lors de l'affichage de l'itinéraire: {str(e)}")
