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
            folium_static(m, height=400, width=750)
            
            # Afficher les informations du trajet
            self.display_trip_info(trip_data)
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte: {str(e)}")
    
    def display_trip_info(self, trip_data):
        """
        Affiche les informations du trajet de manière élégante avec des cartes stylisées
        
        Args:
            trip_data: Données du trajet à afficher
        """
        try:
            # Créer un conteneur pour les cartes
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            
            # Créer deux colonnes pour les cartes
            col1, col2 = st.columns(2)
            
            # Carte d'itinéraire dans la première colonne
            with col1:
                if 'departure_name' in trip_data and 'destination_name' in trip_data:
                    departure = trip_data['departure_name']
                    destination = trip_data['destination_name']
                    
                    route_card = Cards.create_route_card(departure, destination)
                    st.markdown(route_card, unsafe_allow_html=True)
            
            # Carte de détails dans la seconde colonne
            with col2:
                # Rassembler les données disponibles
                details = []
                
                if 'trip_distance' in trip_data:
                    distance = trip_data['trip_distance']
                    details.append(Cards.format_detail("Distance", f"{distance} km"))
                
                if 'duration' in trip_data:
                    duration = trip_data['duration']
                    if isinstance(duration, (int, float)):
                        hours = int(duration // 60)
                        minutes = int(duration % 60)
                        if hours > 0:
                            duration_str = f"{hours}h {minutes}min"
                        else:
                            duration_str = f"{minutes}min"
                    else:
                        duration_str = duration
                    details.append(Cards.format_detail("Durée estimée", duration_str))
                
                if 'price' in trip_data:
                    price = trip_data['price']
                    if isinstance(price, (int, float)):
                        price_str = f"{price:.2f} €"
                    else:
                        price_str = price
                    details.append(Cards.format_detail("Prix", price_str))
                
                # Créer la carte de détails si des données sont disponibles
                if details:
                    details_card = Cards.create_details_card(details)
                    st.markdown(details_card, unsafe_allow_html=True)
                    
            # Ajouter d'autres informations si nécessaire
            if 'additional_info' in trip_data and trip_data['additional_info']:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    info_card = Cards.create_info_card(
                        "Informations complémentaires", 
                        f"<p>{trip_data['additional_info']}</p>"
                    )
                    st.markdown(info_card, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")