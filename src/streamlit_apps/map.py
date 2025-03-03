import folium
from streamlit_folium import folium_static
import pandas as pd
import streamlit as st

class TripMap:
    def __init__(self):
        """Initialise l'objet de carte de trajet"""
        pass
        
    def display_trip_map(self, trip_data):
        """
        Affiche une carte avec les points de départ et d'arrivée du trajet sélectionné.
        
        Args:
            trip_data: DataFrame row ou dict contenant les coordonnées du trajet
        """
        # Vérifier le type d'entrée
        if trip_data is None:
            st.warning("Aucune donnée de trajet fournie")
            return
            
        # Convertir en dictionnaire si nécessaire
        if hasattr(trip_data, 'to_dict'):
            trip_data = trip_data.to_dict()
            
        # Vérifier les coordonnées nécessaires
        required_fields = ['departure_latitude', 'departure_longitude', 
                           'destination_latitude', 'destination_longitude']
        
        for field in required_fields:
            if field not in trip_data or pd.isna(trip_data[field]):
                st.warning(f"Coordonnée manquante: {field}")
                return
        
        try:
            # Convertir les coordonnées en float
            dep_lat = float(trip_data['departure_latitude'])
            dep_lon = float(trip_data['departure_longitude'])
            dest_lat = float(trip_data['destination_latitude'])
            dest_lon = float(trip_data['destination_longitude'])

            # Calculer le centre de la carte (milieu entre départ et arrivée)
            center_lat = (dep_lat + dest_lat) / 2
            center_lon = (dep_lon + dest_lon) / 2
                        
            # Créer la carte
            m = folium.Map(
                location=[center_lat, center_lon],
                tiles='CartoDB positron',
                zoom_start=10  # Essayer une valeur entre 5 et 8
            )
            
            # Ajouter les marqueurs
            folium.Marker(
                [dep_lat, dep_lon],
                popup=trip_data.get('departure_name', 'Départ'),
                icon=folium.Icon(color='green', icon='play', prefix='fa')
            ).add_to(m)
            
            folium.Marker(
                [dest_lat, dest_lon],
                popup=trip_data.get('destination_name', 'Arrivée'),
                icon=folium.Icon(color='red', icon='stop', prefix='fa')
            ).add_to(m)
            
            # Ajouter une ligne entre les deux points
            folium.PolyLine(
                [[dep_lat, dep_lon], [dest_lat, dest_lon]],
                color='blue',
                weight=3,
                opacity=0.7
            ).add_to(m)
            
            # Ajuster la vue pour montrer tous les marqueurs

            
            # Afficher la carte
            folium_static(m)
            
            # Afficher quelques informations supplémentaires
            if 'departure_name' in trip_data and 'destination_name' in trip_data:
                st.markdown(f"**Trajet** : {trip_data['departure_name']} → {trip_data['destination_name']}")
            
            if 'trip_distance' in trip_data:
                st.markdown(f"**Distance** : {trip_data['trip_distance']} km")
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte: {str(e)}")