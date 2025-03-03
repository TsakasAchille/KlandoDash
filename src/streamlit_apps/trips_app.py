import sys
import os

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.backend import Backend
from data_processing.loaders.loader import Loader
from data_processing.processors.trip_processor import TripProcessor
from streamlit_apps.components import Table, Styles
from streamlit_folium import st_folium
try:
    import streamlit_aggrid as st_aggrid
    from streamlit_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, JsCode
    AGGRID_AVAILABLE = True
except ImportError:
    AGGRID_AVAILABLE = False

import sys
import streamlit as st
from map import TripMap
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from car_view import CarView

class TripsApp:
    """Application principale pour l'affichage des trajets"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self.trip_processor = TripProcessor()
        self.trip_map = TripMap()
        self.car_view = CarView()
        self.table = Table()
        self.styles = Styles()
        
    def setup_page(self):
        """Configure la page Streamlit"""
        st.set_page_config(
            page_title="Trajets",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def load_style(self):
        """Charge les styles CSS personnalisés"""
        st.markdown("""
        <style>
            .stApp {
                background-color: #f8f9fa;
            }
            .dataframe {
                font-size: 14px !important;
            }
            .dataframe thead th {
                background-color: #e9ecef;
                color: #495057;
                font-weight: 600;
                text-align: center !important;
            }
            .filter-container {
                background-color: white;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
            }
            /* Correction du problème de texte blanc sur fond blanc */
            h1, h2, h3, h4, h5, h6, p, span, div, .stMarkdown, code {
                color: #333333 !important;
            }
            /* Exception pour les textes spécifiques */
            .stException, .stError {
                color: #ff0000 !important;
            }
            /* Styles pour les éléments de sidebar */
            .css-1d391kg, .css-1wrcr25 {
                color: #333333 !important;
            }
        </style>
        """, unsafe_allow_html=True)

    def show_filters(self):
        """Affiche et gère les filtres"""
        with st.container():
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            cols = st.columns(5)
            
            filters = {}
            with cols[0]:
                filters['date'] = st.date_input("Date", key="date_filter")
            with cols[1]:
                filters['destination'] = st.text_input("Destination", key="destination_filter")
            with cols[2]:
                filters['min_distance'] = st.number_input("Distance min (km)", min_value=0)
            with cols[3]:
                filters['max_distance'] = st.number_input("Distance max (km)", min_value=0)
            with cols[4]:
                filters['min_seats'] = st.number_input("Places min", min_value=0)
            st.markdown('</div>', unsafe_allow_html=True)
            
            return filters

    def apply_filters(self, df, filters):
        """Applique les filtres au DataFrame"""
        mask = pd.Series(True, index=df.index)
        
        if filters['date']:
            mask &= pd.to_datetime(df['departure_date']).dt.date == filters['date']
        if filters['destination']:
            mask &= df['destination'].str.contains(filters['destination'], case=False)
        if filters['min_distance'] > 0:
            mask &= df['distance'] >= filters['min_distance']
        if filters['max_distance'] > 0:
            mask &= df['distance'] <= filters['max_distance']
        if filters['min_seats'] > 0:
            mask &= df['available_seats'] >= filters['min_seats']
        
        return df[mask]

    def show_stats(self, df):
        """Affiche les statistiques"""
        st.markdown("### Statistiques")
        stats_cols = st.columns(4)
        
        with stats_cols[0]:
            st.metric("Nombre de trajets", len(df))
        
        with stats_cols[1]:
            st.metric("Distance moyenne", f"{df['distance'].mean():.1f} km")
        
        with stats_cols[2]:
            st.metric("Prix moyen", f"{df['price'].mean():,.0f} XOF")
        
        with stats_cols[3]:
            st.metric("Places disponibles", df['available_seats'].sum())

    def show_trip_details_test(self, trip_data):
        """Affiche les détails d'un trajet dans un onglet"""
        st.subheader(f"Trajet {trip_data['departure_name']} → {trip_data['destination_name']}")
        
        # Informations principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Prix par siège", f"{trip_data['price_per_seat']} XOF")
        with col2:
            st.metric("Places disponibles", f"{trip_data['available_seats']}/{trip_data['number_of_seats']}")
        with col3:
            st.metric("Distance", f"{trip_data['trip_distance']} km")
    
        # Dates et horaires
        st.subheader("Dates et horaires")
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            st.write("Départ:", trip_data['departure_schedule'].strftime("%d/%m/%Y %H:%M"))
        with dcol2:
            st.write("Arrivée:", trip_data['destination_schedule'].strftime("%d/%m/%Y %H:%M"))
    
        # Carte du trajet si on a les coordonnées
        if all(pd.notna([trip_data['departure_latitude'], trip_data['departure_longitude'], 
                         trip_data['destination_latitude'], trip_data['destination_longitude']])):
            st.subheader("Itinéraire")
            m = folium.Map(location=[trip_data['departure_latitude'], trip_data['departure_longitude']], zoom_start=6)
            
            # Marqueur de départ
            folium.Marker(
                [trip_data['departure_latitude'], trip_data['departure_longitude']],
                popup=trip_data['departure_name'],
                icon=folium.Icon(color='green')
            ).add_to(m)
            
            # Marqueur d'arrivée
            folium.Marker(
                [trip_data['destination_latitude'], trip_data['destination_longitude']],
                popup=trip_data['destination_name'],
                icon=folium.Icon(color='red')
            ).add_to(m)
            
            # Ligne entre les deux points
            folium.PolyLine(
                locations=[[trip_data['departure_latitude'], trip_data['departure_longitude']], 
                          [trip_data['destination_latitude'], trip_data['destination_longitude']]],
                weight=2,
                color='blue'
            ).add_to(m)
            
            folium(m)
  
    def show_table(self, df):
        """Affiche le tableau des trajets"""
        selection_container = st.container()
        
        # Colonnes à exclure
        exclude_columns = ['trip_polyline', 'passenger_reservations', 'all_passengers']
        
        # Définir une fonction pour gérer les clics sur les cellules
     
        # Afficher le tableau avec la détection de clics sur les colonnes
        self.table.display_aggrid(
            df=df,
            exclude_columns=exclude_columns,
            height=400,
            on_select=lambda selection: self.styles.display_info( 
                selection_container,
                f"🔍 Trajet sélectionné: {selection['trip_id'].iloc[0]}",
                "selection-info",
                color="#1e3d59"  # Couleur personnalisée
            ),
            on_cell_click=self.handle_cell_click  # Nouvelle fonction de callback pour les clics sur cellules
        )

    # commentaire, on entre pas ici
    def handle_cell_click(self,row_data, column_id):
            # Afficher des informations en fonction de la colonne cliquée
            if column_id == "destination" or column_id == "departure":
                st.toast(f"Vous avez cliqué sur {column_id}: {row_data[column_id]}")
            elif column_id == "price_per_seat":
                st.toast(f"Prix par siège: {row_data[column_id]} XOF")
            elif column_id == "trip_distance":
                st.toast(f"Distance: {row_data[column_id]} km")

            print("=== Debug Table.handle_selection ===")
            
            # On peut également mettre à jour session_state pour se souvenir de la colonne cliquée
            st.session_state.last_clicked_column = column_id
            st.session_state.last_clicked_row_id = row_data.get("trip_id")
     
    

    def handle_trip_details(self, trip_id: str, df: pd.DataFrame):
        """Affiche les détails d'un trajet"""
        if trip_id:
            trip_data = df[df['trip_id'] == trip_id].iloc[0]
            
            # Afficher les détails du trajet
            st.header(f"Détails du trajet {trip_id}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("📅 Date:", trip_data['departure_schedule'])
                st.write("💶 Prix:", f"{trip_data['price_per_seat']} XOF")
                st.write("👥 Places:", f"{trip_data['available_seats']}/{trip_data['number_of_seats']}")
                
            with col2:
                st.write("🚗 Véhicule:", trip_data['vehicle_brand'])
                st.write("📏 Distance:", f"{trip_data['trip_distance']:.1f} km")
                st.write("⏱️ Durée:", f"{trip_data['trip_duration']:.1f}h")
            
            # Afficher la carte si les coordonnées sont disponibles
            if all(pd.notna([trip_data['departure_latitude'], trip_data['departure_longitude'], 
                            trip_data['destination_latitude'], trip_data['destination_longitude']])):
                st.subheader("📍 Itinéraire")
                m = folium.Map(location=[trip_data['departure_latitude'], trip_data['departure_longitude']], 
                            zoom_start=6)
                
                # Marqueur départ
                folium.Marker(
                    [trip_data['departure_latitude'], trip_data['departure_longitude']],
                    popup=trip_data['departure_name'],
                    icon=folium.Icon(color='green')
                ).add_to(m)
                
                # Marqueur arrivée
                folium.Marker(
                    [trip_data['destination_latitude'], trip_data['destination_longitude']],
                    popup=trip_data['destination_name'],
                    icon=folium.Icon(color='red')
                ).add_to(m)
                
                # Ligne entre les points
                folium.PolyLine(
                    locations=[
                        [trip_data['departure_latitude'], trip_data['departure_longitude']],
                        [trip_data['destination_latitude'], trip_data['destination_longitude']]
                    ],
                    color='blue'
                ).add_to(m)
                
                st_folium(m)
  
   


    def handle_row_selection(self, selected_rows):
        """Gère les lignes sélectionnées dans le tableau AgGrid"""
        
        # Aucune sélection
        if not selected_rows or len(selected_rows) == 0:
            st.write("Aucune ligne sélectionnée")
            return
            
        # Traiter la première ligne sélectionnée
        selected_row = selected_rows[0]  # Premier élément de la liste
        
        # Afficher les détails
        st.write("### Détails du trajet sélectionné")
        
        # Extraire les informations importantes
        trip_id = selected_row.get("trip_id", "N/A")
        departure = selected_row.get("departure", "N/A")
        destination = selected_row.get("destination", "N/A")
        
        # Affichage formaté
        st.markdown(f"""
        **ID du trajet**: {trip_id}  
        **Départ**: {departure}  
        **Destination**: {destination}
        """)
        
        # Vous pouvez ajouter des détails supplémentaires ici
        with st.expander("Voir tous les détails"):
            st.json(selected_row)



    def render_grid_with_callback(self, dataframe, gridoptions):


        """Rend la grille et gère les callbacks de sélection"""
        grid_table = AgGrid(
            dataframe,
            gridOptions=gridoptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True
        )

        sel_row = grid_table["selected_rows"]

        return sel_row
                
       

    def configure_grid(self, gridoptions):
        """Configure la grille en fonction des paramètres fournis"""
        grid_table = AgGrid(
            self.trips_df,
            gridOptions=gridoptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True
        )

         

    



    def run(self):
        """Point d'entrée principal de l'application"""
        st.title("Tableau de bord des trajets")
        
        # Charger les données
        trips_df = self.trip_processor.handler()
        if trips_df is None:
            st.error("Aucun trajet trouvé")
            return


        print("=== Debug TripsApp.run ===")
        print(f"Types dans trips_df: {trips_df.dtypes}")

        # Prétraiter la colonne all_passengers pour la rendre affichable
        if 'all_passengers' in trips_df.columns:
            print("=== La colonne all_passengers existe ===")
            # Print les 2 premières valeurs
            print(f"Premier élément: {trips_df['all_passengers'].iloc[0]}, Type: {type(trips_df['all_passengers'].iloc[0])}")
            if len(trips_df) > 1:
                print(f"Deuxième élément: {trips_df['all_passengers'].iloc[1]}, Type: {type(trips_df['all_passengers'].iloc[1])}")
            
            # Formatage de la colonne all_passengers en fonction de son contenu
            def format_passengers(x):
                if isinstance(x, list):
                    # Si c'est une liste (comme initialement prévu)
                    return f"{len(x)} passager(s)"
                elif isinstance(x, str) and x.strip():
                    # Si c'est une chaîne non vide (ID utilisateur)
                    return "1 passager"
                else:
                    # Si c'est vide ou autre
                    return "0 passager"
            
            trips_df['all_passengers_display'] = trips_df['all_passengers'].apply(format_passengers)
        
        # Disposition à deux colonnes
        tab1, tab2, tab3 = st.tabs(["Tableau des trajets", "Carte du trajet","Profil des utilisateurs"])
        
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
                height=400
                )
        
        # Affichage de la carte
        with tab2:
            st.subheader("Carte du trajet")
            
            try:
                # Récupérer les lignes sélectionnées comme DataFrame
                selected_df = grid_response["selected_rows"]
                
                # Vérifier s'il y a une sélection valide
                has_selection = isinstance(selected_df, pd.DataFrame) and not selected_df.empty
                
                if has_selection:
                    # Récupérer la première ligne sélectionnée
                    row = selected_df.iloc[0]
                    
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
  

        
    

        with tab3:
            st.subheader("Profil des utilisateurs et visualisation des sièges")
            
            try:
                # Vérifier s'il y a une sélection dans la grille
                selected_df = grid_response["selected_rows"]
                has_selection = isinstance(selected_df, pd.DataFrame) and not selected_df.empty
                
                if has_selection:
                    # Récupérer la première ligne sélectionnée
                    row = selected_df.iloc[0]
                    
                    # Obtenir l'ID du trajet et récupérer les données complètes
                    if 'trip_id' in row:
                        trip_id = row['trip_id']
                        trip_data = trips_df[trips_df['trip_id'] == trip_id]
                        
                        if not trip_data.empty:
                            # Afficher les informations sur les sièges et les passagers
                            self.car_view.display_seat_info(trip_data.iloc[0])
                        else:
                            st.info("Données complètes du trajet non trouvées")
                    else:
                        st.info("ID de trajet manquant dans la sélection")
                else:
                    # Message d'instruction
                    st.info("Sélectionnez un trajet dans le tableau pour voir les informations sur les sièges")
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations sur les sièges: {str(e)}")
                import traceback
                st.write(traceback.format_exc())
  
if __name__ == "__main__":
    app = TripsApp()
    app.run()