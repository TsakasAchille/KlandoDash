import folium
from folium.plugins import FloatImage, MeasureControl
from streamlit_folium import st_folium
import io
from PIL import Image
import base64
import math
import pandas as pd
import streamlit as st

class TripMap:
    def __init__(self):
        """Initialise l'objet de carte de trajet"""
        pass
        
    def display_trip_map(self, selected_row):
        """Affiche une carte avec les points de départ et d'arrivée du trajet sélectionné"""
        if isinstance(selected_row, pd.DataFrame):
            if not selected_row.empty:
                selected_row = selected_row.iloc[0].to_dict()  # Premier élément du DataFrame 
            else:
                st.warning("Aucune ligne sélectionnée")
                return
        elif not selected_row:
            st.warning("Aucune ligne sélectionnée")
            return
        
        # Vérifier si les coordonnées nécessaires sont disponibles
        required_coords = [
            "departure_latitude", "departure_longitude", 
            "destination_latitude", "destination_longitude"
        ]
        
        if all(coord in selected_row for coord in required_coords):
            # Récupérer les coordonnées
            dep_lat = float(selected_row["departure_latitude"])
            dep_lon = float(selected_row["departure_longitude"])
            dest_lat = float(selected_row["destination_latitude"])
            dest_lon = float(selected_row["destination_longitude"])
            
            # Calculer le centre de la carte
            center_lat = (dep_lat + dest_lat) / 2
            center_lon = (dep_lon + dest_lon) / 2
            
            # Créer la carte avec une tuile plus attrayante
            m = folium.Map(
                location=[center_lat, center_lon], 
                zoom_start=10,
                tiles='CartoDB positron',  # Style plus moderne
                control_scale=True  # Ajouter une échelle
            )
            
            # Ajouter un outil de mesure
            m.add_child(MeasureControl())
            
            # Informations pour les popups
            dep_info = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="color: #4CAF50; margin-bottom: 5px;">Point de départ</h4>
                <p><b>Adresse:</b> {selected_row.get('departure_address', 'Non spécifiée')}</p>
                <p><b>Date:</b> {selected_row.get('departure_date', 'Non spécifiée')}</p>
                <p><b>Heure:</b> {selected_row.get('departure_time', 'Non spécifiée')}</p>
            </div>
            """
            
            dest_info = f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="color: #F44336; margin-bottom: 5px;">Destination</h4>
                <p><b>Adresse:</b> {selected_row.get('destination_address', 'Non spécifiée')}</p>
                <p><b>Distance:</b> {selected_row.get('distance', '0')} km</p>
                <p><b>Durée estimée:</b> {selected_row.get('duration', '0')} min</p>
            </div>
            """
            
            # Ajouter un marqueur pour le point de départ avec popup amélioré
            folium.Marker(
                location=[dep_lat, dep_lon],
                popup=folium.Popup(dep_info, max_width=300),
                tooltip="Départ",
                icon=folium.Icon(color="green", icon="play", prefix='fa')
            ).add_to(m)
            
            # Ajouter un marqueur pour le point d'arrivée avec popup amélioré
            folium.Marker(
                location=[dest_lat, dest_lon],
                popup=folium.Popup(dest_info, max_width=300),
                tooltip="Destination",
                icon=folium.Icon(color="red", icon="stop", prefix='fa')
            ).add_to(m)
            
            # Calculer l'angle de la ligne (pour l'orientation de la flèche)
            longitude_difference = dest_lon - dep_lon
            latitude_difference = dest_lat - dep_lat
            avg_latitude = (dep_lat + dest_lat) / 2 
            
            # Calculer la rotation pour un marqueur de flèche
            rotation = math.atan(latitude_difference / (longitude_difference * math.cos(avg_latitude * math.pi/180))) * 180/math.pi
            rotation = rotation if longitude_difference > 0 else rotation + 180
            
            # Calculer un point intermédiaire pour placer une flèche
            mid_lat = dep_lat + (dest_lat - dep_lat) * 0.5
            mid_lon = dep_lon + (dest_lon - dep_lon) * 0.5
            
            # Ajouter une flèche au milieu de la ligne pour indiquer la direction
            folium.RegularPolygonMarker(
                location=[mid_lat, mid_lon],
                fill_color='blue',
                number_of_sides=3,
                radius=7,
                rotation=rotation,
                fill_opacity=0.8,
                color='blue'
            ).add_to(m)
            
            # Ajouter une ligne reliant les deux points avec un style amélioré
            line = folium.PolyLine(
                locations=[[dep_lat, dep_lon], [dest_lat, dest_lon]],
                color="#3186cc",
                weight=4,
                opacity=0.8,
                dash_array='10, 10'  # Ligne en pointillé pour un style plus attrayant
            ).add_to(m)
            
            # Ajouter un rayon d'environ 500m autour des points de départ et d'arrivée
            folium.Circle(
                radius=500,
                location=[dep_lat, dep_lon],
                color='green',
                fill=True,
                fill_opacity=0.2,
                tooltip='Zone de départ'
            ).add_to(m)
            
            folium.Circle(
                radius=500,
                location=[dest_lat, dest_lon],
                color='red',
                fill=True,
                fill_opacity=0.2,
                tooltip='Zone de destination'
            ).add_to(m)
            
            # Afficher la carte
            st.write("### Carte du trajet")
            st.markdown("""
            <style>
            .folium-map {
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            </style>
            """, unsafe_allow_html=True)
            
            st_folium(m, width=700, height=500)
            
            # Afficher des informations additionnelles sur le trajet
            if 'trip_id' in selected_row:
                st.subheader(f"Détails du trajet: {selected_row['trip_id']}")
                
                # Créer un tableau de données
                if 'driver_name' in selected_row or 'departure_date' in selected_row:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"🚗 Conducteur: {selected_row.get('driver_name', 'Non spécifié')}")
                        
                    with col2:
                        st.info(f"📅 Date: {selected_row.get('departure_date', 'Non spécifiée')}")
        else:
            missing = [coord for coord in required_coords if coord not in selected_row]
            st.warning(f"Impossible d'afficher la carte. Coordonnées manquantes : {', '.join(missing)}")