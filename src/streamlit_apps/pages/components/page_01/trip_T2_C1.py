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
                    folium_static(m, height=450, width=650)
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
            folium_static(m, height=450, width=650)
            

         
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte: {str(e)}")

    def display_multiple_trips_map(self, trips_data, max_trips=None, height=500, width=700):
        """
        Affiche plusieurs trajets sur une même carte.
        
        Args:
            trips_data: DataFrame ou liste de dictionnaires contenant les données des trajets
            max_trips: Nombre maximum de trajets à afficher (None pour tous)
            height: Hauteur de la carte en pixels
            width: Largeur de la carte en pixels
        """
        if trips_data is None or (hasattr(trips_data, 'empty') and trips_data.empty):
            st.warning("Aucune donnée de trajet fournie")
            return
            
        # Convertir en liste si c'est un DataFrame
        if isinstance(trips_data, pd.DataFrame):
            trips_list = trips_data.to_dict('records')
        elif isinstance(trips_data, dict):  # Si un seul trajet est fourni
            trips_list = [trips_data]
        else:
            trips_list = trips_data
            
        # Limiter le nombre de trajets si nécessaire
        if max_trips and len(trips_list) > max_trips:
            trips_list = trips_list[:max_trips]
            st.info(f"Affichage limité à {max_trips} trajets sur {len(trips_list)}")
        
        # Liste pour stocker toutes les coordonnées pour centrer la carte
        all_coords = []
        
        # Créer la carte (le centre sera ajusté plus tard)
        m = folium.Map(location=[0, 0], tiles='CartoDB positron', zoom_start=10)
        
        # Palette de couleurs pour différencier les trajets
        colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'darkred', 
                  'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightred', 
                  'lightgreen', 'gray', 'black', 'lightgray']
        
        # Ajouter chaque trajet à la carte
        for i, trip in enumerate(trips_list):
            try:
                color = colors[i % len(colors)]
                
                # Vérifier si un polyline est disponible
                has_polyline = 'trip_polyline' in trip and trip['trip_polyline']
                
                if has_polyline:
                    # Utiliser le polyline pour le tracé
                    import polyline
                    coordinates = polyline.decode(trip['trip_polyline'])
                    
                    if coordinates:
                        all_coords.extend(coordinates)
                        
                        # Ajouter le tracé exact à la carte avec popup du trip_id
                        folium.PolyLine(
                            coordinates,
                            color=color,
                            weight=3,
                            opacity=0.7,
                            popup=f"Trajet: {trip.get('trip_id', i)}"
                        ).add_to(m)
                        
                        # Ajouter les marqueurs de départ et d'arrivée
                        folium.Marker(
                            coordinates[0],
                            popup=f"Départ: {trip.get('departure_name', 'Point de départ')}",
                            icon=folium.Icon(color='green', icon='play', prefix='fa')
                        ).add_to(m)
                        
                        folium.Marker(
                            coordinates[-1],
                            popup=f"Arrivée: {trip.get('destination_name', 'Point arrivée')}",
                            icon=folium.Icon(color='red', icon='stop', prefix='fa')
                        ).add_to(m)
                else:
                    # Méthode standard avec coordonnées de départ/arrivée
                    required_fields = ['departure_latitude', 'departure_longitude', 
                                      'destination_latitude', 'destination_longitude']
                    
                    if all(field in trip and not pd.isna(trip[field]) for field in required_fields):
                        # Convertir les coordonnées en float
                        dep_lat = float(trip['departure_latitude'])
                        dep_lon = float(trip['departure_longitude'])
                        dest_lat = float(trip['destination_latitude'])
                        dest_lon = float(trip['destination_longitude'])
                        
                        # Stocker les coordonnées pour le centrage de la carte
                        all_coords.append([dep_lat, dep_lon])
                        all_coords.append([dest_lat, dest_lon])
                        
                        # Ajouter les marqueurs
                        folium.Marker(
                            [dep_lat, dep_lon],
                            popup=f"Départ: {trip.get('departure_name', 'Point de départ')}",
                            icon=folium.Icon(color='green', icon='play', prefix='fa')
                        ).add_to(m)
                        
                        folium.Marker(
                            [dest_lat, dest_lon],
                            popup=f"Arrivée: {trip.get('destination_name', 'Point arrivée')}",
                            icon=folium.Icon(color='red', icon='stop', prefix='fa')
                        ).add_to(m)
                        
                        # Ajouter une ligne entre les deux points
                        folium.PolyLine(
                            [[dep_lat, dep_lon], [dest_lat, dest_lon]],
                            color=color,
                            weight=3,
                            opacity=0.7,
                            popup=f"Trajet: {trip.get('trip_id', i)}"
                        ).add_to(m)
            except Exception as e:
                st.warning(f"Erreur avec le trajet {i}: {str(e)}")
        
        # Centrer la carte sur l'ensemble des points si des coordonnées sont disponibles
        if all_coords:
            # Calculer le centre
            avg_lat = sum(coord[0] for coord in all_coords) / len(all_coords)
            avg_lon = sum(coord[1] for coord in all_coords) / len(all_coords)
            
            # Définir le centre de la carte
            m.location = [avg_lat, avg_lon]
            
            # Ajuster le zoom pour englober tous les points
            m.fit_bounds([[coord[0], coord[1]] for coord in all_coords])
        
        # Afficher la carte
        folium_static(m, height=height, width=width)