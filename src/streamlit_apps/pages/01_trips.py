import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 



# Common components

#Trip components
from src.data_processing.processors.trip_processor import TripProcessor
from src.streamlit_apps.pages.components import TripUsers
from src.streamlit_apps.pages.components import TripMap

#Common components
from src.streamlit_apps.components import Table, Styles, setup_page
from streamlit_folium import st_folium
try:
    import streamlit_aggrid as st_aggrid
    from streamlit_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, JsCode
    AGGRID_AVAILABLE = True
except ImportError:
    AGGRID_AVAILABLE = False

import sys
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

# Configurer la page et afficher le logo (doit être appelé en premier)
setup_page()


class TripsApp:


    """Application principale pour l'affichage des trajets"""


    def __init__(self):
        """Initialisation de l'application"""
        self.trip_processor = TripProcessor()
        self.trip_map = TripMap()
        self.trip_users = TripUsers()
        self.table = Table()
        self.styles = Styles()
        
                
    def load_style(self):
        """Charge les styles CSS personnalisés"""
        try:
            # Chemin vers le fichier CSS
            css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "style.css")
            
            # Vérifier si le fichier existe
            if os.path.exists(css_path):
                with open(css_path, "r") as f:
                    css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            else:
                st.warning(f"Le fichier CSS n'a pas été trouvé : {css_path}")
        except Exception as e:
            st.error(f"Erreur lors du chargement du CSS : {str(e)}")
            # Fallback au CSS intégré en cas d'erreur
            st.markdown("""
            <style>
                /* CSS de secours en cas d'erreur */
                .main .block-container {
                    max-width: 100% !important;
                    width: 100% !important;
                }
            </style>
            """, unsafe_allow_html=True)

    def run(self):
        """Point d'entrée principal de l'application"""
        
        # Charger les styles
        self.load_style()
        
        st.title("Tableau de bord des trajets")

        #Loading
        trips_df = self.trip_processor.handler()

        # Charger les données
        if trips_df is None:
            st.error("Aucun trajet trouvé")
            return

        print("=== Debug TripsApp.run ===")
        print(f"Types dans trips_df: {trips_df.dtypes}")

            
        # Disposition à deux onglets au lieu de trois

        with st.container():

            tab1, tab2 = st.tabs(["Tableau des trajets","Details du trajet"])

            with tab1:
                st.subheader("Tableau des trajets")
                    
                # Colonnes à afficher
                display_cols = [
                    'trip_id',
                    'trip_distance',
                    'all_passengers_display',  # Utiliser la colonne prétraitée
                    'departure_schedule',
                    'departure_name',
                    'destination_name',
                    'price_per_seat',
                    'available_seats',
                    'number_of_seats'
                ]

                    
                # Filtrer les colonnes existantes
                valid_cols = [col for col in display_cols if col in trips_df.columns]
                    
                # Configuration de la grille avec case à cocher
                gb = GridOptionsBuilder.from_dataframe(trips_df[valid_cols])
                gb.configure_selection('single', use_checkbox=True)
                gb.configure_grid_options(suppressRowClickSelection=True)
                    
                # Afficher la grille
                grid_response = AgGrid(
                    trips_df[valid_cols],
                    gridOptions=gb.build(),
                    fit_columns_on_grid_load=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    height=700,

                    )
            
            # Affichage de la carte et profil dans le même onglet avec deux colonnes
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
               
            
        
                # Utiliser deux colonnes pour afficher la carte et le profil côte à côte

                    st.subheader("Carte du trajet")
                        
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
                                row = selected_df[0]  # Liste de dictionnaires
                            else:
                                row = selected_df.iloc[0]  # DataFrame
                                
                            # Vérifier si trip_id est présent
                            if 'trip_id' in row:
                                trip_id = row['trip_id']
                                    
                                # Récupérer les données complètes du trajet
                                trip_data = trips_df[trips_df['trip_id'] == trip_id]
                                    
                                if not trip_data.empty:
                                    # Afficher la carte
                                    self.trip_map.display_trip_map(trip_data.iloc[0])
                                else:
                                    st.info("Données complètes du trajet non trouvées")
                            else:
                                st.info("ID de trajet manquant dans la sélection")
                        else:
                            # Message d'instruction
                            st.info("Sélectionnez un trajet dans le tableau pour voir sa carte")
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
                
                with col2:
                    st.subheader("Profil des utilisateurs")
                        
                    try:
                        # Vérifier s'il y a une sélection dans la grille
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
                                row = selected_df[0]  # Liste de dictionnaires
                            else:
                                row = selected_df.iloc[0]  # DataFrame
                                
                            # Obtenir l'ID du trajet et récupérer les données complètes
                            if 'trip_id' in row:
                                trip_id = row['trip_id']
                                trip_data = trips_df[trips_df['trip_id'] == trip_id]
                                    
                                if not trip_data.empty:
                                    trip = trip_data.iloc[0]
                                    
                                    # Afficher les informations sur les sièges
                                    self.trip_users.display_seat_info(trip)
                                else:
                                    st.info("Données complètes du trajet non trouvées")
                        else:
                            # Message d'instruction
                            st.info("Sélectionnez un trajet dans le tableau pour voir les informations sur les utilisateurs et les sièges")
                    except Exception as e:
                        st.error(f"Erreur lors de l'affichage des informations sur les utilisateurs: {str(e)}")
                        import traceback
                        st.write(traceback.format_exc())
  
    def get_image_as_base64(self, file_path):
        """Convertit une image en base64 pour l'affichage en HTML"""
        import base64
        with open(file_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return encoded

if __name__ == "__main__":
    app = TripsApp()

    
    app.run()