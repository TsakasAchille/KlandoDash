import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
from src.streamlit_apps.components.password_protect import protect
protect()

import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 

from src.data_processing.processors.user_processor import UserProcessor
from src.streamlit_apps.components import Table, Styles, setup_page, set_page_background

# Nouvelle importation directe des fonctions depuis le module users refacturisé
from src.streamlit_apps.pages.components.users import (
    get_user_data,
    display_users_table,
    display_profile_info,
    display_stats_info,
    display_trips_info,
    display_user_info
)
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker


setup_page()
set_page_background()

# Titre principal
# st.sidebar.title("Utilisateurs")

# Charger les données des utilisateurs
users_df = get_user_data()

if users_df is None:
    st.sidebar.error("Aucun utilisateur trouvé")
    st.stop()

# Vérifier si des données ont été chargées
if users_df.empty:
    st.error("Aucun utilisateur n'a pu être chargé")
    st.stop()
    
# Vérifier si un utilisateur doit être sélectionné automatiquement
pre_selected_user_id = None
if UsersTripsLinker.should_select_user():
    pre_selected_user_id = UsersTripsLinker.get_selected_user_id()
    if pre_selected_user_id:
        st.info(f"Affichage automatique de l'utilisateur: {pre_selected_user_id}")
    # Effacer la sélection pour ne pas la refaire à chaque rechargement
    UsersTripsLinker.clear_selection()

with st.container():
    tab1, tab2 = st.tabs(["Tableau des Users","Détails du User"])

    with tab1:
        st.subheader("Tableau des Users")

        # Afficher toutes les colonnes disponibles dans le DataFrame
        display_cols = users_df.columns.tolist()
        
        # Afficher la grille et récupérer la réponse
        grid_response = display_users_table(users_df, pre_selected_user_id)
        
        # Traiter la sélection pour afficher les détails
        selected_rows = grid_response["selected_rows"]
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_user = selected_rows[0]
            # Stocker l'utilisateur sélectionné pour l'afficher dans l'onglet des détails
            st.session_state['selected_user'] = selected_user
            
    with tab2:
        st.subheader("Détails de l'utilisateur")

        try:
            # Récupérer les lignes sélectionnées
            selected_df = grid_response["selected_rows"]
                
            # Vérifier s'il y a une sélection valide
            has_selection = False
            if isinstance(selected_df, list):
                has_selection = len(selected_df) > 0
            elif isinstance(selected_df, pd.DataFrame):
                has_selection = not selected_df.empty
            else:
                has_selection = selected_df is not None
                
            if has_selection:
                # Récupérer la première ligne sélectionnée
                if isinstance(selected_df, list):
                    user = selected_df[0]  # Liste de dictionnaires
                else:
                    user = selected_df.iloc[0]  # DataFrame
                    
                # Vérifier si user_id est présent
                if 'uid' in user:
                    user_uid = user['uid']
                        
                    # Récupérer les données complètes de l'utilisateur si nécessaire
                    user_data = users_df[users_df['uid'] == user_uid]
                
                    if not user_data.empty:
                        # Convertir le DataFrame en dictionnaire (prendre la première ligne)
                        user_dict = user_data.iloc[0].to_dict()
                        
                        # Afficher les détails de l'utilisateur avec la fonction complète
                        display_user_info(user_dict)
                        
                    else:
                        st.info("Données complètes de l'utilisateur non trouvées")
                else:
                    st.info("ID utilisateur manquant dans la sélection")
            else:
                # Message d'instruction
                st.info("Sélectionnez un utilisateur dans le tableau pour voir ses détails")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            import traceback
            st.write(traceback.format_exc())

# Option de débogage - Aller directement à la page des trajets
if 'debug_mode' in st.session_state and st.session_state['debug_mode']:
    with st.expander("Options de débogage"):
        st.subheader("Navigation rapide vers un trajet")
        direct_trip_id = st.text_input("ID du trajet à afficher", "trip_1")
        if st.button("Aller au trajet"):
            # Enregistrer dans la session
            st.session_state["selected_trip_id"] = direct_trip_id
            st.session_state["select_trip_on_load"] = True
            
            # Afficher un message explicatif pour l'utilisation du menu
            st.info(f'''
            L'ID du trajet {direct_trip_id} a été stocker en mémoire. 
            
            Veuillez maintenant cliquer sur 'Trajets' dans le menu de navigation pour voir les détails du trajet.
            ''')
            
            # Expliquer la structure des pages Streamlit
            with st.expander("Pour comprendre la navigation Streamlit"):
                st.markdown('''
                **Navigation entre pages dans Streamlit**
                
                Streamlit utilise un menu de navigation latéral pour passer d'une page à l'autre.
                Il n'est pas possible de naviguer directement par une URL personnalisée avec des paramètres comme `/01_trips`.
                
                Au lieu de cela, il faut:
                1. Stocker les données nécessaires en session comme nous venons de le faire
                2. Cliquer sur le menu 'Trajets' dans la barre latérale pour aller à cette page 
                3. La page 'Trajets' détectera alors les données en session et affichera le bon trajet
                ''')