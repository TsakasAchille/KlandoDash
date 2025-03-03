import folium
from folium.plugins import MeasureControl
from streamlit_folium import st_folium
import pandas as pd
import streamlit as st

class TripMap:
    def __init__(self):
        """Initialise l'objet de carte de trajet"""
        if 'map_object' not in st.session_state:
            st.session_state.map_object = None
            st.session_state.current_trip_id = None

    def display_trip_map(self, selected_row):
        """Affiche une carte avec les points de départ et d'arrivée du trajet sélectionné"""
        if isinstance(selected_row, pd.DataFrame):
            if not selected_row.empty:
                selected_row = selected_row.iloc[0].to_dict()
            else:
                return
        elif not selected_row:
            return

        # Vérifier les coordonnées
        required_coords = ["departure_latitude", "departure_longitude", "destination_latitude", "destination_longitude"]
        if not all(coord in selected_row for coord in required_coords):
            return

        # Obtenir l'ID du trajet actuel pour le comparer
        current_trip_id = selected_row.get('trip_id', str(selected_row))

        # Récupérer les coordonnées
        dep_lat = float(selected_row["departure_latitude"])
        dep_lon = float(selected_row["departure_longitude"])
        dest_lat = float(selected_row["destination_latitude"])
        dest_lon = float(selected_row["destination_longitude"])

        # Calculer le centre
        center_lat = (dep_lat + dest_lat) / 2
        center_lon = (dep_lon + dest_lon) / 2

        # Ne créer une nouvelle carte que si nécessaire
        if st.session_state.map_object is None or st.session_state.current_trip_id != current_trip_id:
            # Créer la carte
            m = folium.Map(
                location=[center_lat, center_lon], 
                zoom_start=10,
                tiles='CartoDB positron'
            )
            
            # Marqueurs simples
            folium.Marker(
                [dep_lat, dep_lon],
                tooltip="Départ",
                icon=folium.Icon(color="green")
            ).add_to(m)
            
            folium.Marker(
                [dest_lat, dest_lon],
                tooltip="Arrivée",
                icon=folium.Icon(color="red")
            ).add_to(m)
            
            # Ligne simple
            folium.PolyLine(
                [[dep_lat, dep_lon], [dest_lat, dest_lon]],
                color="blue"
            ).add_to(m)
            
            # Sauvegarder l'objet carte et l'ID du trajet
            st.session_state.map_object = m
            st.session_state.current_trip_id = current_trip_id

        # Style minimal
        st.markdown("""
        <style>.folium-map {width: 100%;}</style>
        """, unsafe_allow_html=True)

        # Afficher la carte (toujours le même objet pour le même trajet)
        st.write("### Carte du trajet")
        st_folium(st.session_state.map_object, width="100%", height=500, returned_objects=[])