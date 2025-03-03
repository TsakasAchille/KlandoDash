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

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode, JsCode

class TripsApp:
    def __init__(self):
        self.backend = Backend()
        self.loader = Loader()
        self.setup_page()
        self.load_style()
        self.trip_processor = TripProcessor()
        self.table = Table()
        self.styles = Styles()
        self.trip_map = TripMap()
        
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



        st.write("### Tableau des trajets")

        trips_df = self.trip_processor.handler()
        if trips_df is None:
            st.error("Erreur : Aucun fichier de trajets trouvé")
            return

        # Définir l'ordre des colonnes à afficher
        column_order = [
            'trip_id',
            'departure_schedule',
            'trip_distance',
            'departure_name',
            'destination_name',
            'price_per_seat',
            'available_seats',
            'number_of_seats',
            'updated_at',
            'departure_date',
            'auto_confirmation',
            'driver_reference',
            'destination_schedule',
            'departure_latitude',
            'departure_longitude',
            'destination_latitude',
            'destination_longitude',
            'region',
            'trip_polyline',
            'all_passengers',
            'passenger_reservations'


        ]

        # Réorganiser les colonnes du DataFrame
        # Les colonnes définies seront d'abord affichées dans l'ordre spécifié
        # Les autres colonnes seront ajoutées à la fin
        all_columns = column_order + [col for col in trips_df.columns if col not in column_order]
        trips_df = trips_df[all_columns]
        print("Colonnes disponibles:", trips_df.columns.tolist())         



        gd = GridOptionsBuilder.from_dataframe(trips_df)

        gd.configure_default_column(
            groupable=True, 
            editable=True,
            resizable=True,
            autoHeight=False,
            autoWidth=True,
            wrapText=True
        )  

        # Masquer les colonnes de coordonnées sans les supprimer du dataframe
        hidden_columns = [
            'departure_latitude', 
            'departure_longitude', 
            'destination_latitude', 
            'destination_longitude',
            'destination_schedule',
            'trip_polyline',
            'passenger_reservations',
            'all_passengers',
            'updated_at',
            'departure_date'
        ]
        for col in hidden_columns:
            if col in trips_df.columns:
                gd.configure_column(col, hide=True)
                
        # Définir l'ordre des colonnes (les colonnes non spécifiées seront affichées après celles-ci)
        column_order = [
            'trip_id',
            'departure_schedule',
            'trip_distance',
            'departure_name',
            'destination_name',
            'price_per_seat',
            'available_seats',
            'number_of_seats'
        ]
        
        # Configurer l'ordre des colonnes
        for i, col in enumerate(column_order):
            if col in trips_df.columns:
                print(f"Configuring column {col} at index {i}")
                gd.configure_column(col, order=i)

        # Ajout de la colonne des cases à cocher
        sel_mode = st.radio("Mode de sélection", ["single", "multiple"])
        gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
        
        # Forcer l'affichage de la colonne des cases à cocher
        gd.configure_grid_options(
            rowSelection=sel_mode,
            suppressRowClickSelection=True,
            autoSizeColumns=True
        )
        
        # Forcer l'affichage de la colonne des cases à cocher (résout parfois le problème)

        gridoptions = gd.build()

        # Gère les callbacks de sélection
        sel_row = self.render_grid_with_callback(trips_df, gridoptions)

        # Convertir la sélection en un DataFrame
        valid_sel_row = pd.DataFrame(sel_row)

        # Afficher la carte du trajet sélectionné
        self.trip_map.display_trip_map(valid_sel_row)
    



if __name__ == "__main__":
    app = TripsApp()
    app.run()