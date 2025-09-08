"""
Factory pour créer les repositories appropriés (SQL ou REST) selon la configuration
"""
import os
import logging
from dash_apps.config import Config
from dash_apps.utils.supabase_client import supabase

# Repositories SQL traditionnels
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.repositories.trip_repository import TripRepository
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.repositories.booking_repository import BookingRepository

# Repositories REST Supabase
from dash_apps.repositories.user_repository_rest import UserRepositoryRest
from dash_apps.repositories.trip_repository_rest import TripRepositoryRest
from dash_apps.repositories.support_ticket_repository_rest import SupportTicketRepositoryRest
from dash_apps.repositories.support_comment_repository_rest import SupportCommentRepositoryRest
from dash_apps.repositories.booking_repository_rest import BookingRepositoryRest

# Logger
logger = logging.getLogger(__name__)

class RepositoryFactory:
    """
    Factory pour créer les repositories appropriés (SQL ou REST)
    selon la configuration de l'environnement.
    
    Usage:
        user_repo = RepositoryFactory.get_user_repository()
        trips = user_repo.get_all_users()
    """
    
    # Mode debug pour les logs
    _debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def _use_rest_api(cls):
        """
        Détermine si l'application doit utiliser l'API REST Supabase
        au lieu de la connexion directe à PostgreSQL.
        
        Returns:
            bool: True si l'API REST doit être utilisée, False sinon
        """
        # Utiliser la méthode de la classe Config
        use_rest = Config.use_rest_api()
        
        if use_rest and cls._debug_mode:
            logger.info("Utilisation de l'API REST Supabase")
        
        return use_rest
    
    @classmethod
    def get_user_repository(cls):
        """
        Retourne le repository utilisateur approprié
        
        Returns:
            UserRepository ou UserRepositoryRest
        """
        if cls._use_rest_api():
            return UserRepositoryRest()
        else:
            return UserRepository
    
    @classmethod
    def get_trip_repository(cls):
        """
        Retourne le repository trajet approprié
        
        Returns:
            TripRepository ou TripRepositoryRest
        """
        if cls._use_rest_api():
            return TripRepositoryRest()
        else:
            return TripRepository
    
    @classmethod
    def get_support_ticket_repository(cls):
        """
        Retourne le repository ticket de support approprié
        
        Returns:
            SupportTicketRepository ou SupportTicketRepositoryRest
        """
        if cls._use_rest_api():
            return SupportTicketRepositoryRest()
        else:
            return SupportTicketRepository
    
    @classmethod
    def get_support_comment_repository(cls):
        """
        Retourne le repository commentaire de support approprié
        
        Returns:
            SupportCommentRepository ou SupportCommentRepositoryRest
        """
        if cls._use_rest_api():
            return SupportCommentRepositoryRest()
        else:
            return SupportCommentRepository
    
    @classmethod
    def get_booking_repository(cls):
        """
        Retourne le repository réservation approprié
        
        Returns:
            BookingRepository ou BookingRepositoryRest
        """
        if cls._use_rest_api():
            return BookingRepositoryRest()
        else:
            return BookingRepository
