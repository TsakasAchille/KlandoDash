import streamlit as st
import pandas as pd

# Importer les classes déplacées dans des fichiers séparés
from .trips_table import TripsTableManager
from .trips_map import TripsMapManager
from .trips_route import TripsRouteManager
from .trips_finance import TripsFinanceManager

class TripsDisplay:
    """Classe responsable de l'affichage des données des trajets"""
    
    def __init__(self, trip_map):
        """Initialisation avec une référence à la carte des trajets"""
        self.trip_map = trip_map
        self.table_manager = TripsTableManager()
        self.route_manager = TripsRouteManager()
        self.finance_manager = TripsFinanceManager()
        self.map_manager = TripsMapManager(trip_map)
        
    def display_trips_table(self, trips_df):
        """Affiche le tableau des trajets et gère la sélection
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            
        Returns:
            bool: True si un trajet est sélectionné, False sinon
        """
        return self.table_manager.display_table(trips_df)
        
    def display_map(self, trips_df, selected_trip):
        """Affiche la carte du trajet sélectionné
        
        Args:
            trips_df: DataFrame avec tous les trajets
            selected_trip: Dictionnaire contenant les informations du trajet sélectionné
        """
        self.map_manager.display_map(trips_df, selected_trip)
            
    def display_multiple_map(self, trips_df):
        """Affiche la carte de plusieurs trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets à afficher
        """
        self.map_manager.display_multiple_map(trips_df)
        
    def display_route_info(self, trip_data):
        """Affiche la carte d'itinéraire incluant départ, destination et distance
        
        Args:
            trip_data: Données du trajet sélectionné
        """
        self.route_manager.display_route_info(trip_data)
    
    def display_financial_info(self, trip_data):
        """Affiche les informations financières du trajet
        
        Args:
            trip_data: Données du trajet sélectionné
        """
        self.finance_manager.display_financial_info(trip_data)
