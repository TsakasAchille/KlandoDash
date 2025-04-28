import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List, Union

# Importation des gestionnaires spu00e9cifiques (lazy loading)
def _get_general_manager():
    from .stats_general import StatsGeneralManager
    return StatsGeneralManager()

def _get_temporal_manager():
    from .stats_temporal import StatsTemporalManager
    return StatsTemporalManager()

def _get_geographic_manager():
    from .stats_geographic import StatsGeographicManager
    return StatsGeographicManager()

def _get_financial_manager():
    from .stats_financial import StatsFinancialManager
    return StatsFinancialManager()

def _get_map_manager():
    from .stats_map import StatsMapManager
    return StatsMapManager()

class StatsDisplay:
    """
    Classe pour afficher les statistiques des trajets dans la page 04_stat.py.
    Sert de fau00e7ade pour les diffu00e9rents composants d'affichage des statistiques.
    """
    
    def __init__(self):
        """Initialise l'affichage des statistiques"""
        pass
    
    def display_all_stats(self, trips_df):
        """Affiche toutes les statistiques des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        if trips_df is None or trips_df.empty:
            st.warning("Aucune donnu00e9e de trajet u00e0 afficher")
            return
            
        # Affichage du nombre total de trajets
        st.write(f"**Nombre total de trajets**: {len(trips_df)}")
        
        # Cru00e9ation des onglets pour diffu00e9rentes statistiques
        tabs = st.tabs(["Vue générale", "Analyse temporelle", "Analyse géographique", "Analyse financière", "Carte des trajets"])
        
        with tabs[0]:
            self.display_general_stats(trips_df)
        
        with tabs[1]:
            self.display_temporal_stats(trips_df)
        
        with tabs[2]:
            self.display_geographic_stats(trips_df)
        
        with tabs[3]:
            self.display_financial_stats(trips_df)
        
        with tabs[4]:
            self.display_map_stats(trips_df)
    
    def display_general_stats(self, trips_df):
        """Affiche les statistiques gu00e9nu00e9rales des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        return _get_general_manager().display_general_stats(trips_df)
    
    def display_temporal_stats(self, trips_df):
        """Affiche les statistiques temporelles des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        return _get_temporal_manager().display_temporal_stats(trips_df)
    
    def display_geographic_stats(self, trips_df):
        """Affiche les statistiques gu00e9ographiques des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        return _get_geographic_manager().display_geographic_stats(trips_df)
    
    def display_financial_stats(self, trips_df):
        """Affiche les statistiques financiu00e8res des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        return _get_financial_manager().display_financial_stats(trips_df)
    
    def display_map_stats(self, trips_df):
        """Affiche la carte des trajets
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        return _get_map_manager().display_map_stats(trips_df)
