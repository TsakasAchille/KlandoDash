import sys
import os
import streamlit as st
import importlib.util
import pandas as pd

from src.streamlit_apps.components import Table, Styles, setup_page, set_page_background

from src.streamlit_apps.pages.components.trips import (
    get_trip_data,
    display_trips_table,
    display_map,
    display_route_info,
    display_financial_info,
    display_seat_occupation_info,
    display_time_metrics,
    display_all_metrics,
    display_people_info
)
from src.streamlit_apps.pages.components.users import (
    get_user_data,
    display_users_table,
    display_user_info,
    display_trips_info,
    display_stats_info
)
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

# Créer les onglets pour la navigation


users_df = get_user_data()

if users_df is None:
    st.error("Aucun utilisateur trouvé")
else:
    st.session_state["user_df"] = users_df


trips_df = get_trip_data()

if trips_df is None:
    st.error("Aucun trajet trouvé")
else:
    st.session_state["trip_df"] = trips_df


col1, col2 = st.columns([1,2])

with col1:
    st.write("Veuillez sélectionner un trajet dans le tableau.")

with col2:
    st.write("")

trip_container = st.expander("Informations sur le trajet", expanded=True)
passengers_container = st.expander("Passagers", expanded=True)
user_container = st.expander("Utilisateurs", expanded=True)



#-------------------TRIPS-------------------
with trip_container:
    col1, col2 = st.columns([1,2])

    with col1:

        #------------TABLE----------------

        selected_df = display_trips_table(trips_df)

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
                        display_route_info(selected_trip)

                        #------------Financial----------------
                        display_financial_info(selected_trip)

                        #------------Seat Occupation----------------
                        display_seat_occupation_info(selected_trip)

                    with col2:
                    
                        #------------Time Date----------------
                        display_time_metrics(selected_trip)

                        #------------MAP----------------
                        display_map(trips_df, selected_trip)
                
                        #------------Distance----------------                
                        display_all_metrics(selected_trip)


                
                with BottomContainer:
                        pass
                        #------------People----------------     
                        # TODO:Better linking, using dataframe not get data for user info           
                        #display_people_info(selected_trip)
                       
        else:
            st.write("Veuillez sélectionner un trajet")         
                    

if "selected_trip_id" in st.session_state:
            #selected_trip = st.session_state["selected_trip"]
            selected_trip_id = st.session_state["selected_trip_id"]

            # Récupérer le trajet correspondant
            selected_trip = trips_df[trips_df['trip_id'] == selected_trip_id].iloc[0]

#-------------------PEOPLE-------------------

            with passengers_container:
            # TODO:Better linking, using dataframe not get data for user info  
            #          
                display_people_info(selected_trip)

#-------------------USERS-------------------

with user_container:


    col1, col2 = st.columns([1,2])

    with col1:

        #------------TABLE----------------



        grid_response = display_users_table(users_df)


    if "selected_user_id" in st.session_state:
        selected_user_id = st.session_state["selected_user_id"]
        
        # Rechercher l'utilisateur par id (PostgreSQL) ou user_id (ancien format)
        if 'uid' in users_df.columns:  
            selected_user_df = users_df[users_df['uid'] == selected_user_id]
        elif 'id' in users_df.columns:
            selected_user_df = users_df[users_df['id'] == selected_user_id]
        elif 'user_id' in users_df.columns:
            selected_user_df = users_df[users_df['user_id'] == selected_user_id]
        else:
            st.error("Colonnes d'identifiant d'utilisateur non trouvées dans les données")
            selected_user_df = pd.DataFrame()
        
        # Débogage pour comprendre le problème
        st.write(f"ID utilisateur recherché: {selected_user_id}")
        st.write(f"Colonnes disponibles: {users_df.columns.tolist()}")
        st.write(f"Utilisateur trouvé: {not selected_user_df.empty}")
        
        if not selected_user_df.empty:
            try:
                # Convertir le DataFrame en dictionnaire avec gestion d'erreur
                user_dict = selected_user_df.iloc[0].to_dict()
                
                # Afficher les informations de l'utilisateur dans la colonne de droite
                with col2:
                    st.subheader(f"Profil de {user_dict.get('display_name', user_dict.get('name', 'Utilisateur'))}")
                    display_user_info(user_dict)
                    display_stats_info(user_dict)

            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations utilisateur: {str(e)}")
                st.write("Données utilisateur:")
                st.write(selected_user_df)
    else:
        st.write("Veuillez sélectionner un utilisateur")
