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

        # Logique de détection du trajet sélectionné
        pre_selected_trip_id = None
        
        # Méthode 1: Essayer st.query_params (Streamlit 1.30.0+)
        try:
            if hasattr(st, 'query_params'):
                query_params = st.query_params
                if "trip_id" in query_params:
                    pre_selected_trip_id = query_params["trip_id"]
                    print(f"DEBUG: ID de trajet trouvé via st.query_params: {pre_selected_trip_id}")
            else:
                print("DEBUG: st.query_params n'est pas disponible dans cette version de Streamlit")
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'accès à st.query_params: {str(e)}")
        
        # Méthode 2: Utiliser st.experimental_get_query_params (méthode ancienne)
        if pre_selected_trip_id is None:
            try:
                query_params = st.experimental_get_query_params()
                print(f"DEBUG: Paramètres d'URL (experimental): {query_params}")
                if "trip_id" in query_params and query_params["trip_id"]:
                    pre_selected_trip_id = query_params["trip_id"][0]  # Renvoie une liste
                    print(f"DEBUG: ID de trajet trouvé dans l'URL: {pre_selected_trip_id}")
            except Exception as e:
                print(f"DEBUG: Erreur lors de l'accès aux paramètres d'URL: {str(e)}")
        
        # Méthode 3: Vérifier dans la session Streamlit
        if pre_selected_trip_id is None and "selected_trip_id" in st.session_state:
            pre_selected_trip_id = st.session_state["selected_trip_id"]
            print(f"DEBUG: ID de trajet trouvé dans la session: {pre_selected_trip_id}")
        
        # Méthode 4: Vérifier via UsersTripsLinker
        if pre_selected_trip_id is None:
            from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker
            if UsersTripsLinker.should_select_trip():
                pre_selected_trip_id = UsersTripsLinker.get_selected_trip_id()
                print(f"DEBUG: ID de trajet trouvé via UsersTripsLinker: {pre_selected_trip_id}")
                # Effacer la sélection pour ne pas la refaire à chaque rechargement
                UsersTripsLinker.clear_trip_selection()
        
        # Affichage du résultat de la détection
        if pre_selected_trip_id:
            print(f"DEBUG: ID de trajet sélectionné final: {pre_selected_trip_id}")
            st.success(f"Affichage du trajet: {pre_selected_trip_id}")
            
            # Vérifier que le trajet existe
            if pre_selected_trip_id not in trips_df['trip_id'].values:
                st.warning(f"Attention: Le trajet {pre_selected_trip_id} n'existe pas dans les données!")
                pre_selected_trip_id = None

        with st.container():
            # Créer deux onglets: tableau et détails
            tab1, tab2 = st.tabs(["Tableau des trajets","Détails du trajet"])
            
            # Si un trajet est sélectionné, préparer les variables pour l'affichage
            selected_trip = None
            
            if pre_selected_trip_id and pre_selected_trip_id in trips_df['trip_id'].values:
                # Sélectionner le trajet
                selected_trip = trips_df[trips_df['trip_id'] == pre_selected_trip_id].iloc[0].to_dict()
                print(f"DEBUG: Trajet sélectionné: {selected_trip['trip_id']}")
                
                # Basculer vers l'onglet détails
                js = """
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Sélectionner le second onglet (index 1)
                    setTimeout(function() {
                        const tabs = window.parent.document.querySelectorAll('.stTabs [data-baseweb="tab-list"] [role="tab"]');
                        if (tabs && tabs.length > 1) {
                            tabs[1].click();
                            console.log('Tab switched to details');
                        } else {
                            console.log('Tabs not found or not enough tabs');
                        }
                    }, 200);
                });
                </script>
                """
                st.markdown(js, unsafe_allow_html=True)
                
            with tab1:  # Tableau des trajets
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
                
                # Stocker les données sélectionnées dans la session state pour les utiliser dans l'autre onglet
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
                    # Stocker la sélection dans la session state
                    st.session_state["selected_trip"] = selected_df[0] if isinstance(selected_df, list) else selected_df.iloc[0]
                    
            with tab2:  # Détails du trajet
                col1, col2 = st.columns(2)
                
                # Au lieu d'utiliser la variable grid_response qui n'est disponible que dans l'onglet 1,
                # vérifions s'il y a une sélection dans la session state ou si nous avons un trajet préselectionné
                
                selected_trip = None
                
                # Si nous avons un trajet préselectionné, l'utiliser directement
                if pre_selected_trip_id and pre_selected_trip_id in trips_df['trip_id'].values:
                    selected_trip = trips_df[trips_df['trip_id'] == pre_selected_trip_id].iloc[0]
                # Sinon, vérifier s'il y a une sélection dans la session state
                elif "selected_trip" in st.session_state:
                    selected_trip = st.session_state["selected_trip"]
                
                with col1:
                    st.subheader("Carte du trajet")
                    
                    if selected_trip is not None and 'trip_id' in selected_trip:
                        # Récupérer l'ID du trajet sélectionné
                        trip_id = selected_trip['trip_id']
                        
                        # Récupérer les données complètes du trajet
                        trip_data = trips_df[trips_df['trip_id'] == trip_id]
                        
                        if not trip_data.empty:
                            # Afficher la carte
                            self.trip_map.display_trip_map(trip_data.iloc[0])
                        else:
                            st.info("Données complètes du trajet non trouvées")
                    else:
                        # Message d'instruction
                        st.info("Sélectionnez un trajet dans le tableau pour voir sa carte")
                
                with col2:
                    st.subheader("Profil des utilisateurs")
                    
                    if selected_trip is not None and 'trip_id' in selected_trip:
                        # Récupérer l'ID du trajet sélectionné
                        trip_id = selected_trip['trip_id']
                        
                        # Récupérer les données complètes du trajet
                        trip_data = trips_df[trips_df['trip_id'] == trip_id]
                        
                        if not trip_data.empty:
                            # Afficher la visualisation des utilisateurs
                            self.trip_users.display_seat_info(trip_data.iloc[0])
                        else:
                            st.info("Données complètes du trajet non trouvées")
                    else:
                        # Message d'instruction
                        st.info("Sélectionnez un trajet dans le tableau pour voir les utilisateurs")
            
            # Si nous avons un trajet préselectionné, basculer vers l'onglet des détails
            if pre_selected_trip_id and selected_tab_index == 1:
                js = f"""
                <script>
                    // Set timeout to ensure the tabs are fully rendered
                    setTimeout(function() {{
                        const tabs = window.parent.document.querySelectorAll('.streamlit-tabs [role="tab"]');
                        if (tabs.length >= 2) {{
                            tabs[1].click();
                        }}
                    }}, 100);
                </script>
                """
                st.markdown(js, unsafe_allow_html=True)
  
    def get_image_as_base64(self, file_path):
        """Convertit une image en base64 pour l'affichage en HTML"""
        import base64
        with open(file_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return encoded

if __name__ == "__main__":
    app = TripsApp()

    
    app.run()