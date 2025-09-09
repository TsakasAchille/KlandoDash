"""
Service pour la récupération et l'agrégation des données de trajet.
Sépare la logique métier de la présentation.
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TripDataService:
    """Service pour récupérer et agréger toutes les données nécessaires à l'affichage des détails d'un trajet."""
    
    @staticmethod
    def get_trip_complete_data(selected_trip_id: str, trips_data: Dict) -> Tuple[Dict, List, List, int]:
        """
        Récupère toutes les données nécessaires pour afficher les détails d'un trajet.
        
        Args:
            selected_trip_id: ID du trajet sélectionné
            trips_data: Données du trajet principal (déjà récupérées par l'API REST)
            
        Returns:
            Tuple contenant:
            - trip_dict: Données du trajet
            - passengers_list: Liste des passagers
            - signalements_list: Liste des signalements
            - signalements_count: Nombre de signalements
        """
        if not trips_data:
            raise ValueError(f"Trajet avec l'ID {selected_trip_id} non trouvé dans les données.")
        
        trip_dict = trips_data
        trip_id = trip_dict.get("trip_id")
        
        # Récupération des passagers
        passengers_list = TripDataService._get_passengers_data(trip_id)
        
        # Récupération des signalements
        signalements_list, signalements_count = TripDataService._get_signalements_data(trip_id)
        
        return trip_dict, passengers_list, signalements_list, signalements_count
    
    @staticmethod
    def _get_passengers_data(trip_id: str) -> List:
        """Récupère les données des passagers pour un trajet."""
        try:
            from dash_apps.utils.data_schema_rest import get_passengers_for_trip
            passengers_df = get_passengers_for_trip(trip_id)
            
            if passengers_df is None or (hasattr(passengers_df, 'empty') and passengers_df.empty):
                print("Aucun passager trouvé pour ce trajet")
                return []
            else:
                print("Passagers trouvés pour ce trajet")
                return passengers_df.to_dict('records') if hasattr(passengers_df, 'to_dict') else passengers_df
                
        except Exception as e:
            print(f"[WARNING] Erreur lors de la récupération des passagers: {str(e)}")
            return []
    
    @staticmethod
    def _get_signalements_data(trip_id: str) -> Tuple[List, int]:
        """Récupère les données des signalements pour un trajet."""
        try:
            from dash_apps.utils.data_schema_rest import get_signalements_for_trip
            signalements_data = get_signalements_for_trip(trip_id)
            
            if signalements_data and isinstance(signalements_data, list):
                return signalements_data, len(signalements_data)
            else:
                return [], 0
                
        except Exception as e:
            print(f"[WARNING] Erreur lors de la récupération des signalements: {str(e)}")
            return [], 0
