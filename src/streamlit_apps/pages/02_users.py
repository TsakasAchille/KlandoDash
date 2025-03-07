import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 

from src.data_processing.processors.user_processor import UserProcessor
from src.streamlit_apps.components import Table, Styles, setup_page
from src.streamlit_apps.pages.components import UsersDisplay
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker


setup_page()

class UserView:
    """
    Classe pour l'affichage des données utilisateurs dans un tableau interactif
    """
    
    def __init__(self):
        """Initialisation de la vue utilisateur"""
        self.user_processor = UserProcessor()
        self.table = Table()
        self.styles = Styles()
        self.users_display = UsersDisplay()  # Initialisation de la nouvelle classe d'affichage
        self.users_trips_linker = UsersTripsLinker()


    def run(self):
        """
        Exécute l'application d'affichage des utilisateurs
        """
     
        st.sidebar.title("Utilisateurs")
        
        # Charger les données des utilisateurs
        users_df = self.user_processor.handler()

        if users_df is None:
            st.sidebar.error("Aucun utilisateur trouvé")
            return
        
        print("=== Debug UsersApp.run ===")
        print(f"Types dans users_df: {users_df.dtypes}")    
        
        # Vérifier si des données ont été chargées
        if users_df.empty:
            st.error("Aucun utilisateur n'a pu être chargé")
            return
            
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


                # Colonnes à afficher dans la table
                display_cols = [
                    'user_id',
                    'display_name',
                    'email',
                    'phone_number',
                    'age',
                    'created_time'
                ]
                
                # Filtrer les colonnes existantes
                valid_cols = [col for col in display_cols if col in users_df.columns]
                    
                # Configuration de la grille avec case à cocher
                gb = GridOptionsBuilder.from_dataframe(users_df[valid_cols])
                gb.configure_selection('single', use_checkbox=True)
                gb.configure_grid_options(suppressRowClickSelection=True)
                
                # Sélectionner automatiquement l'utilisateur si demandé
                if pre_selected_user_id and 'user_id' in users_df.columns:
                    # Code pour pré-sélectionner une ligne dans AgGrid
                    # Cela utilise rowIndex pour identifier quelle ligne sélectionner
                    user_row_index = users_df[users_df['user_id'] == pre_selected_user_id].index.tolist()
                    if user_row_index:
                        gb.configure_selection('single', use_checkbox=True, pre_selected_rows=[user_row_index[0]])
                        # Automatiquement afficher les détails dans l'onglet 2
                        st.experimental_set_query_params(tab='details')
                    
                # Afficher la grille
                grid_response = AgGrid(
                    users_df[valid_cols],
                    gridOptions=gb.build(),
                    fit_columns_on_grid_load=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    height=700,
                )
                
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
                        
                    # Vérifier s'il y a une sélection valide (liste non vide ou DataFrame non vide)
                    has_selection = False
                    if isinstance(selected_df, list):
                        has_selection = len(selected_df) > 0
                    elif isinstance(selected_df, pd.DataFrame):
                        has_selection = not selected_df.empty
                    else:
                        has_selection = selected_df is not None
                        
                    if has_selection:
                        # Récupérer la première ligne sélectionnée (adapter selon le type)
                        if isinstance(selected_df, list):
                            user = selected_df[0]  # Liste de dictionnaires
                        else:
                            user = selected_df.iloc[0]  # DataFrame
                            
                        # Vérifier si user_id est présent
                        if 'user_id' in user:
                            user_id = user['user_id']
                            print(f"Traitement des trajets pour l'utilisateur: {user_id}")
                                
                            # Récupérer les données complètes de l'utilisateur si nécessaire
                            # (Optionnel: si vous avez besoin de données supplémentaires non présentes dans la ligne sélectionnée)
                            user_data = users_df[users_df['user_id'] == user_id]
                            print(f"Traitement des données pour l'utilisateur: {user_data}")
                                
                            if not user_data.empty:
                                # Afficher les détails de l'utilisateur avec la nouvelle classe
                                self.users_display.user_display_handler(user_data)
                                
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
if __name__ == "__main__":
    app = UserView()

    
    app.run()