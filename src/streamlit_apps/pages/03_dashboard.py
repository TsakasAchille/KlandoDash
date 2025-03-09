import sys
import os
import streamlit as st
import importlib.util
import pandas as pd

from src.streamlit_apps.components import Table, Styles, setup_page, set_page_background

from src.streamlit_apps.pages.components.trips import TripsApp
from src.streamlit_apps.pages.components.users import UserView
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker

setup_page()
set_page_background()

# Titre principal
st.title("Dashboard utilisateurs et trajets")

# Créer une instance de UsersTripsLinker pour gérer les liens entre utilisateurs et trajets
users_trips_linker = UsersTripsLinker()

# Créer les instances des applications
trips_app = TripsApp()
users_app = UserView()

# Créer les onglets pour la navigation


users_df = users_app.get_data()

if users_df is None:
    st.error("Aucun utilisateur trouvé")
else:
    st.session_state["user_df"] = users_df


trips_df = trips_app.get_data()

if trips_df is None:
    st.error("Aucun trajet trouvé")
else:
    st.session_state["trip_df"] = trips_df


#-------------------TRIPS-------------------

col1, col2 = st.columns([1,2])

with col1:

    #------------TABLE----------------


    selected_df = trips_app.display_trips_table(trips_df)

    # Vérifier s'il y a une sélection valide
    has_selection = False
    if isinstance(selected_df, list):
        has_selection = len(selected_df) > 0
    elif isinstance(selected_df, pd.DataFrame):
        has_selection = not selected_df.empty
    else:
        has_selection = selected_df is not None

    #Stockage de la sélection
    if has_selection:
        # Stocker la sélection dans la session state
        #st.session_state["selected_trip"] = selected_df[0] if isinstance(selected_df, list) else selected_df.iloc[0]
        st.session_state["selected_trip_id"] = selected_df[0]['trip_id'] if isinstance(selected_df, list) else selected_df.iloc[0]['trip_id']

if "selected_trip_id" in st.session_state:
    #selected_trip = st.session_state["selected_trip"]
    selected_trip_id = st.session_state["selected_trip_id"]

    # Récupérer le trajet correspondant
    selected_trip = trips_df[trips_df['trip_id'] == selected_trip_id].iloc[0]


    with col2:
        TopContainer = st.container()
        BottomContainer = st.container()

        with TopContainer:
            col1, col2 = st.columns([1,2])

            with col1:

                #------------Route----------------
                trips_app.display_route_info(selected_trip)

                #------------Financial----------------
                trips_app.display_financial_info(selected_trip)

                #------------Seat Occupation----------------
                trips_app.display_seat_occupation_info(selected_trip)

            with col2:
            
                #------------Time Date----------------
                trips_app.display_time_metrics(selected_trip)

                #------------MAP----------------
                trips_app.display_map(trips_df, selected_trip)
        
                #------------Distance----------------                
                trips_app.display_all_metrics(selected_trip)


        
        with BottomContainer:

                #------------People----------------     
                # TODO:Better linking, using dataframe not get data for user info           
                trips_app.display_people_info(selected_trip)
        
                


    #-------------------USERS-------------------

    col1, col2 = st.columns([1,2])

    with col1:

        #------------TABLE----------------

  

        users_app.display_users_table(users_df)


    if "selected_user_id" in st.session_state:
        selected_user_id = st.session_state["selected_user_id"]
        selected_user_df = users_df[users_df['user_id'] == selected_user_id].iloc[0]

        with col2:

            TopContainer = st.container()
            BottomContainer = st.container()

            with TopContainer:
                col1, col2 = st.columns([1,2])
                with col1:
                    users_app.display_user_info(selected_user_df)
                with col2:
                    users_app.display_user_trip_infos(selected_user_df, trips_df)

       

    else:
        st.write("Veuillez sélectionner un utilisateur")

else:
    st.write("Veuillez sélectionner un trajet")
    