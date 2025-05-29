import streamlit as st
import pandas as pd

class TripsMapManager:
    """Gu00e8re l'affichage des cartes pour les trajets"""
    
    def __init__(self, trip_map):
        """Initialisation avec une reference a la carte des trajets"""
        self.trip_map = trip_map
        
    def display_map(self, trips_df, selected_trip):
        """Affiche la carte du trajet selectionne
        
        Args:
            trips_df: DataFrame avec tous les trajets
            selected_trip: Dictionnaire contenant les informations du trajet selectionne
        """
        if selected_trip is not None and 'trip_id' in selected_trip:
            # Recuperer l'ID du trajet selectionne
            trip_id = selected_trip['trip_id']
            
            # Recuperer les donnes completes du trajet
            trip_data = trips_df[trips_df['trip_id'] == trip_id]
            
            if not trip_data.empty:
                # Afficher la carte
                self.trip_map.display_trip_map(trip_data.iloc[0])
            else:
                st.info("Donnees completes du trajet non trouves")
        else:
            st.info("Veuillez selectionner un trajet pour voir la carte")
            
    def display_multiple_map(self, trips_df):
        """Affiche la carte de plusieurs trajets
        
        Args:
            trips_df: DataFrame contenant les donnes des trajets a afficher
        """
        if not trips_df.empty:
            self.trip_map.display_multiple_trips_map(trips_df)
        else:
            st.info("Aucun trajet a afficher sur la carte")
