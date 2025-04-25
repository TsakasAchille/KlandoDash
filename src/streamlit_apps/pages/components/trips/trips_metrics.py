import streamlit as st
import pandas as pd
import locale
from datetime import datetime
from src.streamlit_apps.components import Cards
from src.streamlit_apps.components.modern_card import modern_card

class TripsMetrics:
    """Classe responsable de la gestion et l'affichage des métriques de trajets"""
    
    def __init__(self):
        """Initialisation de la classe de métriques"""
        # Tentative de définition de la locale française
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        except:
            pass  # Si la locale n'est pas disponible, continuer sans erreur
    
    def display_distance_info(self, selected_trip):
        """Affiche l'information de distance pour le trajet sélectionné
        
        Args:
            selected_trip: Dictionnaire contenant les informations du trajet sélectionné
        """
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:
                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
                st.metric("Kilomètres parcourus", f"{trip_distance:.1f} km")
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")
    
    def display_fuel_info(self, selected_trip):
        """Affiche les informations d'économie de carburant
        
        Args:
            selected_trip: Dictionnaire contenant les informations du trajet sélectionné
        """
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:
                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
                
                # Estimer l'économie de carburant (exemple: 10L par km)
                total_fuel = trip_distance * 0.10  # 10L/km
                
                st.metric("Économie de carburant", f"{total_fuel:.1f} L")
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")
    
    def display_CO2_info(self, selected_trip):
        """Affiche les informations d'économie de CO2
        
        Args:
            selected_trip: Dictionnaire contenant les informations du trajet sélectionné
        """
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:
                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
                
                # Estimer l'économie de CO2 (exemple: 150g par km)
                total_co2 = trip_distance * 0.15  # 150g/km converti en kg
                
                st.metric("Économie de CO2", f"{total_co2:.1f} kg")
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")
    
    def display_all_metrics(self, selected_trip):
        """Affiche toutes les métriques dans un composant unique
        
        Args:
            selected_trip: Dictionnaire contenant les informations du trajet sélectionné
        """
        if selected_trip is not None and 'trip_id' in selected_trip:
            trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
            total_fuel = trip_distance * 0.10
            total_co2 = trip_distance * 0.15
            
            # Création des métriques pour le composant Cards
            metrics_data = [
                ("Kilomètres parcourus", f"{trip_distance:.1f} km"),
                ("Économie de carburant", f"{total_fuel:.1f} L"),
                ("Économie de CO2", f"{total_co2:.1f} kg")
            ]
            
            # Utilisation du composant Cards pour afficher les métriques
            metrics_html = Cards.create_metric_cards(metrics_data)
            st.markdown(metrics_html, unsafe_allow_html=True)
    
    def display_time_metrics(self, selected_trip):
        """Affiche les métriques de temps pour le trajet sélectionné
        
        Args:
            selected_trip: DataFrame avec une ligne pour le trajet sélectionné
        """
        departure_field = 'departure_schedule'
        arrival_field = 'arrival_schedule'
        if arrival_field not in selected_trip and 'created_at' in selected_trip:
            arrival_field = 'created_at'
        if departure_field in selected_trip and arrival_field in selected_trip:
            if isinstance(selected_trip[departure_field], pd.Series):
                departure_time = selected_trip[departure_field].values[0]
                arrival_time = selected_trip[arrival_field].values[0]
            else:
                departure_time = selected_trip[departure_field]
                arrival_time = selected_trip[arrival_field]
            try:
                if not isinstance(departure_time, pd.Timestamp) and not isinstance(departure_time, datetime):
                    departure_time = pd.to_datetime(departure_time)
                if not isinstance(arrival_time, pd.Timestamp) and not isinstance(arrival_time, datetime):
                    arrival_time = pd.to_datetime(arrival_time)
                departure = departure_time.strftime("%d/%m/%Y à %H:%M") if departure_time else "Non disponible"
                arrival = arrival_time.strftime("%d/%m/%Y à %H:%M") if arrival_time else "Non disponible"
            except:
                departure = str(departure_time) if departure_time else "Non disponible"
                arrival = str(arrival_time) if arrival_time else "Non disponible"
            modern_card(
                title="Horaires du trajet",
                icon="⏰",
                items=[
                    ("Départ", departure),
                    ("Arrivée", arrival)
                ],
                accent_color="#2B8CB6"
            )
        else:
            modern_card(
                title="Horaires du trajet",
                icon="⏰",
                items=[("Départ", "Non disponible"), ("Arrivée", "Non disponible")],
                accent_color="#2B8CB6"
            )