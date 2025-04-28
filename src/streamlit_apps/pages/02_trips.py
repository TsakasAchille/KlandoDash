import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
from src.streamlit_apps.components.password_protect import protect
protect()

import importlib.util
import pandas as pd
from src.streamlit_apps.components import Table, Styles, setup_page, set_page_background

# Nouvelle importation directe des fonctions
from src.streamlit_apps.pages.components.trips import (
    get_trip_data, 
    display_trips_table,
    display_map,
    display_route_info,
    display_financial_info, 
    display_seat_occupation_info,
    display_time_metrics,
    display_distance_info,
    display_fuel_info,
    display_CO2_info,
    display_people_info
)
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker
# Importer directement UserProcessor pour charger les données utilisateurs
from src.data_processing.processors.user_processor import UserProcessor

setup_page()
set_page_background()

# Titre principal
st.markdown("""
    <h2 style='font-size:24px; margin-bottom:10px;'>
        Dashboard utilisateurs et trajets
    </h2>
""", unsafe_allow_html=True)


# Créer une instance de UsersTripsLinker pour gérer les liens entre utilisateurs et trajets
users_trips_linker = UsersTripsLinker()

# Charger les données d'utilisateurs avec UserProcessor directement
if "user_df" not in st.session_state:
    # Ancien : users_df = user_processor.handler()
    # Nouveau : lecture directe via la méthode statique
    users_df = UserProcessor.get_all_users()
    if users_df is not None:
        st.session_state["user_df"] = users_df
else:
    users_df = st.session_state["user_df"]

if users_df is None:
    st.error("Aucun utilisateur trouvé")

# Charger les données de trajets (en utilisant la nouvelle fonction avec cache)
if "trips_df" not in st.session_state:
    trips_df = get_trip_data()  # Fonction avec @st.cache_data
    if trips_df is not None:
        st.session_state["trips_df"] = trips_df
else:
    trips_df = st.session_state["trips_df"]

if trips_df is None:
    st.error("Aucun trajet trouvé")
else:
    st.session_state["trip_df"] = trips_df

# Créer les onglets pour la navigation
tab1, tab2 = st.tabs(["Trajets", "Détails du trajet"])

# Premier onglet : liste des trajets tableau 
with tab1:
    st.write("Veuillez sélectionner un trajet dans le tableau.")
    
    # Afficher le tableau des trajets avec la nouvelle fonction qui met à jour session_state
    display_trips_table(trips_df)
    
# Deuxième onglet : détails du trajet sélectionné
with tab2:
    if "selected_trip_id" in st.session_state:
        selected_trip_id = st.session_state["selected_trip_id"]
        
        # Récupérer le trajet correspondant
        selected_trip = trips_df[trips_df['trip_id'] == selected_trip_id].iloc[0]
        
        # Créer des expanders pour organiser l'information
        trip_container = st.expander("Informations sur le trajet", expanded=True)
        passengers_container = st.expander("Passagers", expanded=True)
        
        # Afficher les informations du trajet
        with trip_container:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Route information
                display_route_info(selected_trip)
                
                # Financial information
                display_financial_info(selected_trip)
                
                # Seat occupation information
                display_seat_occupation_info(selected_trip)
                
            with col2:
                # Time and date metrics
                display_time_metrics(selected_trip)
                
                # Map display
                display_map(trips_df, selected_trip)
                
                # Métriques alignées horizontalement
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                with metrics_col1:
                    display_distance_info(selected_trip)
                with metrics_col2:
                    display_fuel_info(selected_trip)
                with metrics_col3:
                    display_CO2_info(selected_trip)
        
        # Afficher les informations sur les passagers
        with passengers_container:
            # Si besoin d'obtenir les passagers d'un trip_id :
            # (remplacer par une logique adaptée si nécessaire)
            passenger_ids = []
            display_people_info(selected_trip)
            
    else:
        st.write("Veuillez sélectionner un trajet dans l'onglet 'Trajets'")
