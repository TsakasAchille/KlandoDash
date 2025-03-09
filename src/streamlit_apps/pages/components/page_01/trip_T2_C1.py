import folium
from streamlit_folium import folium_static
import pandas as pd
import streamlit as st
from src.streamlit_apps.components import Cards  # Importez la nouvelle classe Cards

class TripMap:
    def __init__(self):
        """Initialise l'objet de carte de trajet"""
        # Charger les styles pour les cartes
        Cards.load_card_styles()
        
    def display_trip_map0(self, trip_data):
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
            
            # Afficher la carte directement sans conteneur stylisé
            folium_static(m, height=660, width=800)
            
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte: {str(e)}")
    
    def display_trip_map(self, trip_data):
        """
        Affiche une carte avec les points de départ et d'arrivée du trajet sélectionné.
        Si disponible, utilise le polyline pour afficher le tracé exact du trajet.
        
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
            
        try:
            # Vérifier si un polyline est disponible
            has_polyline = 'trip_polyline' in trip_data and trip_data['trip_polyline']
            
            if has_polyline:
                # Si polyline disponible, utiliser celui-ci pour la carte
                import polyline  # Vous aurez besoin d'installer: pip install polyline
                
                # Décodage du polyline
                coordinates = polyline.decode(trip_data['trip_polyline'])
                
                if coordinates:
                    # Créer la carte centrée sur le premier point du polyline
                    m = folium.Map(
                        location=coordinates[0],
                        tiles='CartoDB positron',
                        zoom_start=12
                    )
                    
                    # Ajouter le tracé exact à la carte
                    folium.PolyLine(
                        coordinates,
                        color="blue",
                        weight=4,
                        opacity=0.7
                    ).add_to(m)
                    
                    # Ajouter les marqueurs de départ et d'arrivée
                    folium.Marker(
                        coordinates[0],
                        popup=trip_data.get('departure_name', 'Départ'),
                        icon=folium.Icon(color='green', icon='play', prefix='fa')
                    ).add_to(m)
                    
                    folium.Marker(
                        coordinates[-1],
                        popup=trip_data.get('destination_name', 'Arrivée'),
                        icon=folium.Icon(color='red', icon='stop', prefix='fa')
                    ).add_to(m)
                    
                    # Afficher la carte
                    folium_static(m, height=655, width=925)
                    return
            
            # Si pas de polyline ou si une erreur s'est produite, utiliser la méthode standard
            # Vérifier les coordonnées nécessaires
            required_fields = ['departure_latitude', 'departure_longitude', 
                              'destination_latitude', 'destination_longitude']
            
            for field in required_fields:
                if field not in trip_data or pd.isna(trip_data[field]):
                    st.warning(f"Coordonnée manquante: {field}")
                    return
            
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
                zoom_start=10
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
            
            # Afficher la carte directement sans conteneur stylisé
            folium_static(m, height=655, width=925)
            

         
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte: {str(e)}")