import streamlit as st
import pandas as pd
from .trips_table import TripsTableManager
from .trips_map import TripsMapManager
from .trips_route import TripsRouteManager
from .trips_finance import TripsFinanceManager
from .trips_metrics import TripsMetrics
from .trips_people import TripsPeople
from .trips_chat import TripsChat
from .trips_occupation import TripsOccupationManager
from src.data_processing.processors.trip_processor import TripProcessor
from src.streamlit_apps.pages.components.trip_map import TripMap

# Lazy loading des managers pour éviter les dépendances circulaires
_trip_map = None
_table_manager = None
_map_manager = None
_route_manager = None
_finance_manager = None
_metrics = None
_people = None
_chat = None
_occupation_manager = None

def _get_trip_map():
    global _trip_map
    if _trip_map is None:
        _trip_map = TripMap()
    return _trip_map

def _get_table_manager():
    global _table_manager
    if _table_manager is None:
        _table_manager = TripsTableManager()
    return _table_manager

def _get_map_manager():
    global _map_manager
    if _map_manager is None:
        # On passe TripMap à TripsMapManager comme exigé
        _map_manager = TripsMapManager(_get_trip_map())
    return _map_manager

def _get_route_manager():
    global _route_manager
    if _route_manager is None:
        _route_manager = TripsRouteManager()
    return _route_manager

def _get_finance_manager():
    global _finance_manager
    if _finance_manager is None:
        _finance_manager = TripsFinanceManager()
    return _finance_manager

def _get_metrics():
    global _metrics
    if _metrics is None:
        _metrics = TripsMetrics()
    return _metrics

def _get_people():
    global _people
    if _people is None:
        _people = TripsPeople()
    return _people

def _get_chat():
    global _chat
    if _chat is None:
        _chat = TripsChat()
    return _chat

def _get_occupation_manager():
    global _occupation_manager
    if _occupation_manager is None:
        _occupation_manager = TripsOccupationManager()
    return _occupation_manager

# Fonction pour initialiser/récupérer les données
@st.cache_data
def get_trip_data():
    """Récupère les données de trajets depuis la base de données"""
    # Ancien : return TripProcessor.get_trips_by_trip_ids(None)
    # Nouveau : charge tous les trajets via la nouvelle méthode
    return TripProcessor.get_all_trips()

# === Fonctions de tableau ===
def display_trips_table(trips_df):
    """Affiche le tableau des trajets et gère la sélection"""
    # Vérifier si trips_df est None ou vide
    if trips_df is None or len(trips_df) == 0:
        st.warning("Aucun trajet disponible. La base de données est vide ou inaccessible.")
        return None
        
    selected_rows = _get_table_manager().display_table(trips_df)
    
    # Mettre à jour la session state avec la sélection
    if selected_rows is not None and not hasattr(selected_rows, 'empty') and len(selected_rows) > 0:
        # C'est une liste
        st.session_state["selected_trip_id"] = selected_rows[0]['trip_id'] 
        st.session_state["selected_trip"] = trips_df[trips_df['trip_id'] == selected_rows[0]['trip_id']].iloc[0]
    elif selected_rows is not None and hasattr(selected_rows, 'empty') and not selected_rows.empty:
        # C'est un DataFrame
        st.session_state["selected_trip_id"] = selected_rows.iloc[0]['trip_id'] 
        st.session_state["selected_trip"] = trips_df[trips_df['trip_id'] == selected_rows.iloc[0]['trip_id']].iloc[0]
    
    return selected_rows

# === Fonctions de carte ===
def display_map(trips_df, selected_trip):
    """Affiche la carte du trajet sélectionné"""
    return _get_map_manager().display_map(trips_df, selected_trip)

def display_multiple_map(trips_df):
    """Affiche la carte de plusieurs trajets"""
    return _get_map_manager().display_multiple_map(trips_df)

# === Fonctions d'informations d'itinéraire ===
def display_route_info(trip_data):
    """Affiche la carte d'itinéraire incluant départ, destination et distance"""
    return _get_route_manager().display_route_info(trip_data)

# === Fonctions d'informations financières ===
def display_financial_info(trip_data):
    """Affiche les informations financières du trajet"""
    return _get_finance_manager().display_financial_info(trip_data)

# === Fonctions de métriques ===
def display_distance_info(selected_trip):
    """Affiche l'information de distance pour le trajet sélectionné"""
    return _get_metrics().display_distance_info(selected_trip)

def display_fuel_info(selected_trip):
    """Affiche les informations d'économie de carburant"""
    return _get_metrics().display_fuel_info(selected_trip)

def display_CO2_info(selected_trip):
    """Affiche les informations d'économie de CO2"""
    return _get_metrics().display_CO2_info(selected_trip)

def display_all_metrics(selected_trip):
    """Affiche toutes les métriques dans un composant unique"""
    return _get_metrics().display_all_metrics(selected_trip)

def display_time_metrics(selected_trip):
    """Affiche les métriques de temps pour le trajet sélectionné"""
    return _get_metrics().display_time_metrics(selected_trip)

# === Fonctions d'occupation des sièges ===
def display_seat_occupation_info(trip_data, info_cols=None):
    """Affiche les informations sur l'occupation des sièges"""
    return _get_occupation_manager().display_seat_occupation_info(trip_data, info_cols)

# === Fonctions sur les personnes ===
def display_people_info(trip_data, info_cols=None):
    """Affiche les informations sur le conducteur et les passagers
    
    Args:
        trip_data: Données du trajet sélectionné
        info_cols: Colonnes Streamlit pour l'affichage (optionnel)
    """
    return _get_people().display_people_info(trip_data, info_cols)

# === Fonctions de chat ===
def display_chat_popup():
    """Affiche la popup de chat"""
    return _get_chat().display_chat_popup()
