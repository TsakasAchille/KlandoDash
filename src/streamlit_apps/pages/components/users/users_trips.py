import streamlit as st
import pandas as pd
from datetime import datetime
from src.streamlit_apps.components.modern_card import modern_card
from src.data_processing.processors.trip_processor import TripProcessor
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

class UsersTripsManager:
    """Gère l'affichage des trajets associés aux utilisateurs"""
    
    def __init__(self):
        """Initialise le gestionnaire de trajets utilisateur"""
        self.trip_processor = TripProcessor()
    
    def display_trips_info(self, user_data):
        """Affiche les trajets associés à l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        try:
            # Extraire l'ID de l'utilisateur
            user_id = user_data.get('uid', None)
            if not user_id:
                return
            
            # Récupérer les trajets de l'utilisateur
            user_trips = self._get_user_trips(user_id)
            
            if user_trips.empty:
                st.info("Aucun trajet associé à cet utilisateur")
                return
            
            # Afficher un titre pour la section
            st.subheader(f"Trajets de l'utilisateur ({len(user_trips)} trajets)")
            
            # Afficher un tableau des trajets avec AgGrid
            self._display_trips_table(user_trips)
            
            # Afficher une carte récapitulative des trajets récents
            self._display_recent_trips_summary(user_trips)
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des trajets: {str(e)}")
    
    def _get_user_trips(self, user_id):
        """Récupère tous les trajets associés à un utilisateur via une seule requête optimisée (conducteur OU passager)"""
        try:
            trips_df = self.trip_processor.get_all_user_trips(str(user_id))
            return trips_df
        except Exception as e:
            st.error(f"Erreur lors de la récupération des trajets (lecture optimisée): {str(e)}")
            return pd.DataFrame()
    
    def _display_trips_table(self, trips_df):
        """Affiche un tableau des trajets de l'utilisateur
        
        Args:
            trips_df: DataFrame contenant les trajets de l'utilisateur
        """
        # Sélectionner les colonnes à afficher
        display_cols = [
            'trip_id', 'departure_name', 'destination_name', 
            'departure_schedule', 'trip_distance', 'price_per_seat'
        ]
        
        # Filtrer les colonnes existantes
        display_cols = [col for col in display_cols if col in trips_df.columns]
        
        if not display_cols:
            st.warning("Aucune colonne disponible pour afficher les trajets")
            return
        
        # Renommer les colonnes pour l'affichage
        column_names = {
            'trip_id': 'ID',
            'departure_name': 'Départ',
            'destination_name': 'Destination',
            'departure_schedule': 'Date',
            'trip_distance': 'Distance (km)',
            'price_per_seat': 'Prix/place'
        }
        
        # Créer une copie du DataFrame avec les colonnes sélectionnées et renommées
        display_df = trips_df[display_cols].copy()
        display_df.rename(columns={col: column_names.get(col, col) for col in display_cols}, inplace=True)
        
        # Configuration de la grille
        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=5)
        gb.configure_selection('single', use_checkbox=False)
        
        # Afficher la grille
        grid_response = AgGrid(
            display_df,
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            height=300,
            update_mode=GridUpdateMode.SELECTION_CHANGED
        )
        
        # Traiter la sélection si nécessaire
        selected_rows = grid_response["selected_rows"]
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_trip = selected_rows[0]
            trip_id = selected_trip.get('ID', None)
            if trip_id:
                st.info(f"Trajet sélectionné: {trip_id}")
                # Ici, vous pourriez ajouter une logique pour naviguer vers la page du trajet
    
    def _display_recent_trips_summary(self, trips_df):
        """Affiche un résumé des trajets récents de l'utilisateur
        
        Args:
            trips_df: DataFrame contenant les trajets de l'utilisateur
        """
        if trips_df.empty:
            return
        
        # Trier les trajets par date (du plus récent au plus ancien)
        if 'departure_schedule' in trips_df.columns:
            trips_df = trips_df.sort_values('departure_schedule', ascending=False)
        
        # Prendre les 3 trajets les plus récents
        recent_trips = trips_df.head(3)
        
        # Préparer les données pour l'affichage
        for _, trip in recent_trips.iterrows():
            # Extraire les informations du trajet
            departure = trip.get('departure_name', 'Non disponible')
            destination = trip.get('destination_name', 'Non disponible')
            date = trip.get('departure_schedule', 'Non disponible')
            distance = trip.get('trip_distance', 0)
            price = trip.get('price_per_seat', 0)
            
            # Formater la date si nécessaire
            if isinstance(date, (datetime, pd.Timestamp)):
                date = date.strftime("%d/%m/%Y à %H:%M")
            
            # Afficher le trajet avec modern_card
            modern_card(
                title=f"Trajet: {departure} à {destination}",
                icon="🚗",  # ud83dude97 = "ud83dude97" (emoji voiture)
                items=[
                    ("Date", date),
                    ("Distance", f"{distance:.1f} km"),
                    ("Prix", f"{price} XOF")
                ],
                accent_color="#e74c3c"  # Rouge pour les trajets
            )
