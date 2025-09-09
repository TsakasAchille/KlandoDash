"""
Repository pour les trajets utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Logger
logger = logging.getLogger(__name__)

class TripRepositoryRest(SupabaseRepository):
    """
    Repository pour les trajets utilisant l'API REST Supabase
    """
    
    def __init__(self):
        """
        Initialise le repository avec la table 'trips'
        """
        super().__init__("trips")
    
    def get_trip_by_id(self, trip_id: str) -> Optional[Dict]:
        """
        Récupère un trajet par son ID
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Dictionnaire contenant les informations du trajet ou None si non trouvé
        """
        return self.get_by_id("trip_id", trip_id)
    
    def get_trip(self, trip_id: str) -> Optional[Dict]:
        """
        Alias pour get_trip_by_id pour compatibilité
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Dictionnaire contenant les informations du trajet ou None si non trouvé
        """
        return self.get_trip_by_id(trip_id)
    
    def list_trips(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Liste les trajets avec pagination
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste de trajets
        """
        return self.get_all(offset=skip, limit=limit, order_by="created_at", order_direction="desc")
    
    def create_trip(self, trip_data: dict) -> Optional[Dict]:
        """
        Crée un nouveau trajet
        
        Args:
            trip_data: Données du trajet
            
        Returns:
            Le trajet créé ou None
        """
        return self.create(trip_data)
    
    def update_trip(self, trip_id: str, updates: dict) -> Optional[Dict]:
        """
        Met à jour un trajet existant
        
        Args:
            trip_id: Identifiant du trajet
            updates: Dictionnaire avec les modifications
            
        Returns:
            Le trajet mis à jour ou None en cas d'erreur
        """
        if self.update("trip_id", trip_id, updates):
            return self.get_by_id("trip_id", trip_id)
        return None
    
    def delete_trip(self, trip_id: str) -> bool:
        """
        Supprime un trajet
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            True si supprimé, False sinon
        """
        return self.delete("trip_id", trip_id)
    
    def count_trips(self, status: Optional[str] = None) -> int:
        """
        Compte le nombre total de trajets, filtré par statut si spécifié
        
        Args:
            status: Filtre optionnel par statut
            
        Returns:
            Nombre de trajets correspondant aux critères
        """
        filters = {}
        if status:
            filters["status"] = status
        return self.count(filters=filters)
    
    def get_trips_by_driver(self, driver_id: str, limit: int = 100) -> List[Dict]:
        """
        Récupère les trajets d'un conducteur
        
        Args:
            driver_id: Identifiant du conducteur
            limit: Nombre maximum de trajets à retourner
            
        Returns:
            Liste des trajets du conducteur
        """
        return self.get_all(
            filters={"driver_id": driver_id},
            limit=limit,
            order_by="departure_date",
            order_direction="desc"
        )
    
    def get_trips_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """
        Récupère les trajets par statut
        
        Args:
            status: Statut des trajets à récupérer
            limit: Nombre maximum de trajets à retourner
            
        Returns:
            Liste des trajets avec le statut spécifié
        """
        return self.get_all(
            filters={"status": status},
            limit=limit,
            order_by="departure_date",
            order_direction="desc"
        )
    
    def get_trips_with_pagination(self, page: int = 1, page_size: int = 10, 
                                 status: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère une page de trajets avec pagination et métadonnées
        
        Args:
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            status: Filtre optionnel par statut
            
        Returns:
            Un dictionnaire contenant la liste des trajets et les métadonnées de pagination
        """
        try:
            # Calculer le décalage (offset)
            skip = (page - 1) * page_size
            
            # Préparer les filtres
            filters = {}
            if status:
                filters["status"] = status
            
            # Récupérer les trajets pour cette page
            trips = self.get_all(
                offset=skip,
                limit=page_size,
                order_by="departure_date",
                order_direction="desc",
                filters=filters
            )
            
            # Compter le nombre total de trajets
            total_count = self.count(filters=filters)
            
            # Calculer le nombre total de pages
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            
            return {
                "trips": trips,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur get_trips_with_pagination: {str(e)}")
            return {
                "trips": [],
                "pagination": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
    
    def search_trips(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Recherche des trajets par lieu de départ ou d'arrivée
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Liste de trajets correspondant à la recherche
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Recherche par lieu de départ ou d'arrivée
            response = supabase.table(self.table_name)\
                .select("*")\
                .or_(f"departure_location.ilike.%{query}%,arrival_location.ilike.%{query}%")\
                .limit(limit)\
                .order("departure_date", desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de trajets avec '{query}': {str(e)}")
            return []
    
    def get_upcoming_trips(self, limit: int = 50) -> List[Dict]:
        """
        Récupère les trajets à venir
        
        Args:
            limit: Nombre maximum de trajets à retourner
            
        Returns:
            Liste des trajets à venir
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Récupérer les trajets avec une heure de départ future
            now = datetime.now().isoformat()
            response = supabase.table(self.table_name)\
                .select("*")\
                .gte("departure_date", now)\
                .eq("status", "active")\
                .order("departure_date", desc=False)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des trajets à venir: {str(e)}")
            return []
    
    def get_trip_bookings(self, trip_id: str) -> List[Dict]:
        """
        Récupère les réservations d'un trajet
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Liste des réservations du trajet
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            response = supabase.table("bookings")\
                .select("*")\
                .eq("trip_id", trip_id)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des réservations pour le trajet {trip_id}: {str(e)}")
            return []
    
    def get_trip_passengers(self, trip_id: str) -> List[Dict]:
        """
        Récupère les passagers d'un trajet avec leurs informations
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Liste des passagers avec leurs informations
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Récupérer les réservations avec les informations des utilisateurs
            response = supabase.table("bookings")\
                .select("*, users(uid, display_name, email, phone_number)")\
                .eq("trip_id", trip_id)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des passagers pour le trajet {trip_id}: {str(e)}")
            return []
    
    def get_trip_stats(self, trip_id: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un trajet
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Dictionnaire contenant les statistiques du trajet
        """
        try:
            # Récupérer les informations du trajet
            trip = self.get_by_id("trip_id", trip_id)
            if not trip:
                return {}
            
            # Récupérer les réservations
            bookings = self.get_trip_bookings(trip_id)
            
            # Calculer les statistiques
            total_bookings = len(bookings)
            total_seats_booked = sum(booking.get("seats_count", 1) for booking in bookings)
            available_seats = trip.get("available_seats", 0)
            total_seats = trip.get("total_seats", 0)
            
            return {
                "trip_id": trip_id,
                "total_bookings": total_bookings,
                "total_seats_booked": total_seats_booked,
                "available_seats": available_seats,
                "total_seats": total_seats,
                "occupancy_rate": (total_seats_booked / total_seats * 100) if total_seats > 0 else 0,
                "status": trip.get("status", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques pour le trajet {trip_id}: {str(e)}")
            return {}
    
    def get_trips_paginated_minimal(self, page_index: int, page_size: int, 
                                   filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Version optimisée pour récupérer les trajets avec pagination minimale
        Compatible avec TripsCacheService - Utilise le même système de filtres que users
        
        Args:
            page_index: Index de la page (0-based)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres (text, status, etc.)
            
        Returns:
            Dict contenant trips, total_count et pagination
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Convertir page_index (0-based) en page (1-based)
            page = page_index + 1
            skip = page_index * page_size
            
            # Construire la requête de base
            query = supabase.table(self.table_name).select("*")
            
            # Appliquer les filtres si fournis
            if filters:
                # Filtre par texte (trip_id, lieux de départ/arrivée)
                if filters.get('text'):
                    text_filter = filters['text']
                    query = query.or_(f"trip_id.ilike.%{text_filter}%,departure_name.ilike.%{text_filter}%,destination_name.ilike.%{text_filter}%")
                
                # Filtre par statut
                if filters.get('status'):
                    query = query.eq("status", filters['status'])
            
            # Appliquer la pagination et l'ordre
            query = query.order("departure_date", desc=True).range(skip, skip + page_size - 1)
            
            # Exécuter la requête
            response = query.execute()
            trips = response.data if response.data else []
            
            # Compter le total avec les mêmes filtres
            count_query = supabase.table(self.table_name).select("*", count="exact")
            if filters:
                if filters.get('text'):
                    text_filter = filters['text']
                    count_query = count_query.or_(f"trip_id.ilike.%{text_filter}%,departure_name.ilike.%{text_filter}%,destination_name.ilike.%{text_filter}%")
                if filters.get('status'):
                    count_query = count_query.eq("status", filters['status'])
            
            count_response = count_query.execute()
            total_count = count_response.count if count_response.count is not None else 0
            
            # Calculer le nombre total de pages
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            
            return {
                "trips": trips,
                "total_count": total_count,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
                
        except Exception as e:
            logger.error(f"Erreur get_trips_paginated_minimal: {str(e)}")
            return {
                "trips": [],
                "total_count": 0,
                "pagination": {
                    "total_count": 0,
                    "page": page_index + 1,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
