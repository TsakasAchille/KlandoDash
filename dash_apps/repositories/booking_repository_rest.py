"""
Repository pour les réservations utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict
import logging

# Logger
logger = logging.getLogger(__name__)

class BookingRepositoryRest(SupabaseRepository):
    """
    Repository pour les réservations utilisant l'API REST Supabase
    """
    
    def __init__(self):
        """
        Initialise le repository avec la table 'bookings'
        """
        super().__init__("bookings")
    
    def get_all_bookings(self) -> List[Dict]:
        """
        Récupère toutes les réservations
        
        Returns:
            Liste des réservations
        """
        return self.get_all()
    
    def get_booking(self, trip_id: str, user_id: str) -> Optional[Dict]:
        """
        Récupère une réservation spécifique
        
        Args:
            trip_id: Identifiant du trajet
            user_id: Identifiant de l'utilisateur
            
        Returns:
            La réservation ou None si non trouvée
        """
        try:
            # Utiliser un filtrage multiple
            bookings = self.get_all(filters={
                "trip_id": trip_id,
                "user_id": user_id
            })
            
            # Retourner la première réservation qui correspond
            return bookings[0] if bookings else None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la réservation: {str(e)}")
            return None
    
    def get_trip_bookings(self, trip_id: str) -> List[Dict]:
        """
        Récupère la liste complète des réservations pour un trip_id
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Liste des réservations pour ce trajet
        """
        try:
            return self.get_all(filters={"trip_id": trip_id})
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des réservations du trajet: {str(e)}")
            return []
