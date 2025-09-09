"""
Factory pour créer les repositories REST Supabase
"""
import logging

# Repositories REST uniquement
from dash_apps.repositories.user_repository_rest import UserRepositoryRest
from dash_apps.repositories.trip_repository_rest import TripRepositoryRest
from dash_apps.repositories.support_ticket_repository_rest import SupportTicketRepositoryRest
from dash_apps.repositories.support_comment_repository_rest import SupportCommentRepositoryRest
from dash_apps.repositories.booking_repository_rest import BookingRepositoryRest

# Logger
logger = logging.getLogger(__name__)

class RepositoryFactory:
    """
    Factory pour créer les repositories REST Supabase
    
    Usage:
        user_repo = RepositoryFactory.get_user_repository()
        trips = user_repo.get_all_users()
    """
    
    @classmethod
    def get_user_repository(cls):
        """
        Retourne le repository utilisateur REST
        
        Returns:
            UserRepositoryRest
        """
        return UserRepositoryRest()
    
    @classmethod
    def get_trip_repository(cls):
        """
        Retourne le repository trajet REST
        
        Returns:
            TripRepositoryRest
        """
        return TripRepositoryRest()
    
    @classmethod
    def get_support_ticket_repository(cls):
        """
        Retourne le repository ticket de support REST
        
        Returns:
            SupportTicketRepositoryRest
        """
        return SupportTicketRepositoryRest()
    
    @classmethod
    def get_support_comment_repository(cls):
        """
        Retourne le repository commentaire de support REST
        
        Returns:
            SupportCommentRepositoryRest
        """
        return SupportCommentRepositoryRest()
    
    @classmethod
    def get_booking_repository(cls):
        """
        Retourne le repository réservation REST
        
        Returns:
            BookingRepositoryRest
        """
        return BookingRepositoryRest()
