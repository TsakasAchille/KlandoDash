import sys
import os
import streamlit as st
import importlib.util
import pandas as pd

from src.streamlit_apps.components import Table, Styles, setup_page, set_page_background

from src.streamlit_apps.pages.components.trips_backend import TripsApp
from src.streamlit_apps.pages.components.users import UserView
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker

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

# Créer les instances des applications
trips_app = TripsApp()
users_app = UserView()

# Charger les données d'utilisateurs
users_df = users_app.get_data()

if users_df is None:
    st.error("Aucun utilisateur trouvé")
else:
    st.session_state["user_df"] = users_df


# Charger les données de trajets
trips_df = trips_app.get_data()

if trips_df is None:
    st.error("Aucun trajet trouvé")
else:
    st.session_state["trip_df"] = trips_df

# Créer les onglets pour la navigation
tab1, tab2 = st.tabs(["Trajets", "Détails du trajet"])

# Premier onglet : liste des trajets
with tab1:
    st.write("Veuillez sélectionner un trajet dans le tableau.")
    
    # Afficher le tableau des trajets
    selected_df = trips_app.display_trips_table(trips_df)
    
    # Vérifier s'il y a une sélection valide
    has_selection = False
    if isinstance(selected_df, list):
        has_selection = len(selected_df) > 0
    elif isinstance(selected_df, pd.DataFrame):
        has_selection = not selected_df.empty
    else:
        has_selection = selected_df is not None
    
    # Stockage de la sélection
    if has_selection:
        # Stocker la sélection dans la session state
        st.session_state["selected_trip_id"] = selected_df[0]['trip_id'] if isinstance(selected_df, list) else selected_df.iloc[0]['trip_id']

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
                trips_app.display_route_info(selected_trip)
                
                # Financial information
                trips_app.display_financial_info(selected_trip)
                
                # Seat occupation information
                trips_app.display_seat_occupation_info(selected_trip)
                
            with col2:
                # Time and date metrics
                trips_app.display_time_metrics(selected_trip)
                
                # Map display
                trips_app.display_map(trips_df, selected_trip)
                
                # Distance and other metrics
                trips_app.display_all_metrics(selected_trip)
        
        # Afficher les informations sur les passagers
        with passengers_container:
            trips_app.display_people_info(selected_trip)
            
    else:
        st.write("Veuillez sélectionner un trajet dans l'onglet 'Trajets'")
