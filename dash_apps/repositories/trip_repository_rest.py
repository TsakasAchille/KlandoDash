"""
Repository pour les trajets utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from dash_apps.utils.settings import load_json_config

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
                                 status: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Récupère une page de trajets avec pagination et filtres complets
        
        Args:
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            status: Filtre optionnel par statut (rétrocompatibilité)
            filters: Dictionnaire complet des filtres (text, date_from, date_to, etc.)
            
        Returns:
            Un dictionnaire contenant la liste des trajets et les métadonnées de pagination
        """
        try:
            # Charger la configuration JSON pour les mappings
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('trips_table_config.json')
            filters_config = config.get('filters', {})
            
            # Calculer le décalage (offset)
            skip = (page - 1) * page_size
            
            # Construire la requête avec filtres basés sur la config JSON
            from dash_apps.utils.supabase_client import supabase
            query = supabase.table(self.table_name).select("*")
            
            # Appliquer les filtres avec une fonction réutilisable
            query = self._apply_filters_to_query(query, filters, status, filters_config)
            
            # Appliquer le tri selon la config
            default_sort = config.get('default_sort', {})
            sort_column = default_sort.get('column', 'departure_date')
            sort_desc = default_sort.get('direction', 'desc') == 'desc'
            
            # Override du tri si spécifié dans les filtres
            if filters and filters.get('date_sort'):
                sort_desc = filters['date_sort'] == 'desc'
            
            query = query.order(sort_column, desc=sort_desc)
            
            # Appliquer la pagination
            query = query.range(skip, skip + page_size - 1)
            
            # Exécuter la requête
            print(f"[DEBUG_QUERY] Exécution de la requête avec filtres appliqués")
            response = query.execute()
            trips = response.data or []
            print(f"[DEBUG_QUERY] Résultats: {len(trips)} trajets trouvés")
            
            # Debug: afficher quelques exemples de dates si on a des résultats
            if trips:
                for i, trip in enumerate(trips[:3]):  # 3 premiers trajets
                    print(f"[DEBUG_DATES] Trajet {i+1}: departure_date={trip.get('departure_date')}, departure_schedule={trip.get('departure_schedule')}")
            else:
                print("[DEBUG_DATES] Aucun trajet trouvé - vérifier les formats de dates")
            
            # Compter le nombre total avec les mêmes filtres (réutilisation de la logique)
            count_query = supabase.table(self.table_name).select('*', count='exact')
            count_query = self._apply_filters_to_query(count_query, filters, status, filters_config)
            
            count_response = count_query.execute()
            total_count = count_response.count if hasattr(count_response, 'count') else 0
            
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
            logger.error(f"Erreur get_trips_with_pagination: {str(e)}")
            return {
                "trips": [],
                "total_count": 0,
                "pagination": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
    
    def _apply_filters_to_query(self, query, filters: Optional[Dict[str, Any]], status: Optional[str], filters_config: Dict):
        """
        Applique les filtres à une requête Supabase de manière optimisée
        Ordre des filtres optimisé pour les performances des index
        """
        print(f"[DEBUG_FILTERS] Filters reçus: {filters}")
        print(f"[DEBUG_FILTERS] Status: {status}")
        print(f"[DEBUG_FILTERS] Config filtres: {filters_config}")
        
        # 1. Filtres d'égalité d'abord (meilleur pour les index)
        if filters:
            # Filtre de statut (config: filters.status.column)
            if filters.get('status') and filters_config.get('status', {}).get('enabled'):
                status_column = filters_config['status']['column']
                print(f"[DEBUG_FILTERS] Applique filtre statut: {status_column} = {filters['status']}")
                query = query.eq(status_column, filters['status'])
        
        # Rétrocompatibilité: ajouter le statut si fourni directement
        if status:
            status_column = filters_config.get('status', {}).get('column', 'status')
            print(f"[DEBUG_FILTERS] Applique statut rétrocompatible: {status_column} = {status}")
            query = query.eq(status_column, status)
        
        # 2. Filtres de plage (date) - après les filtres d'égalité
        if filters and filters_config.get('date_range', {}).get('enabled'):
            date_column = filters_config['date_range']['column']
            print(f"[DEBUG_FILTERS] Colonne date configurée: {date_column}")
            
            if filters.get('date_filter_type') == 'after' and filters.get('single_date'):
                print(f"[DEBUG_FILTERS] Applique filtre AFTER: {date_column} >= {filters['single_date']}")
                query = query.gte(date_column, filters['single_date'])
            elif filters.get('date_filter_type') == 'before' and filters.get('single_date'):
                print(f"[DEBUG_FILTERS] Applique filtre BEFORE: {date_column} <= {filters['single_date']}")
                query = query.lte(date_column, filters['single_date'])
            elif filters.get('date_filter_type') == 'range':
                if filters.get('date_from'):
                    print(f"[DEBUG_FILTERS] Applique filtre RANGE FROM: {date_column} >= {filters['date_from']}")
                    query = query.gte(date_column, filters['date_from'])
                if filters.get('date_to'):
                    print(f"[DEBUG_FILTERS] Applique filtre RANGE TO: {date_column} <= {filters['date_to']}")
                    query = query.lte(date_column, filters['date_to'])
        
        # 3. Filtres de recherche textuelle en dernier (plus coûteux)
        if filters and filters.get('text') and filters_config.get('location', {}).get('enabled'):
            location_columns = filters_config['location']['columns']
            search_text = filters['text']
            or_conditions = [f"{col}.ilike.%{search_text}%" for col in location_columns]
            query = query.or_(','.join(or_conditions))
        
        return query
    
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
    
  
