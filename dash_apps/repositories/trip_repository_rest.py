"""
Repository pour les trajets utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict
import datetime
import logging

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
    
    def get_trip(self, trip_id: str) -> Optional[Dict]:
        """
        Récupère un trajet par son ID
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Dictionnaire contenant les informations du trajet ou None si non trouvé
        """
        return self.get_by_id("trip_id", trip_id)
    
    def list_trips(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Liste les trajets avec pagination
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste de trajets
        """
        return self.get_all(offset=skip, limit=limit)
    
    def get_trip_by_id(self, trip_id: str) -> Optional[Dict]:
        """
        Récupère un trajet par son ID
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Dictionnaire contenant les informations du trajet ou None si non trouvé
        """
        return self.get_by_id("trip_id", trip_id)
    
    def get_trip_position(self, trip_id: str) -> Optional[int]:
        """
        Trouve la position d'un trajet dans la liste triée par date de création (desc par défaut)
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            Position du trajet (0-based index) ou None si non trouvé
        """
        try:
            # Récupérer le trajet cible
            target_trip = self.get_by_id("trip_id", trip_id)
            if not target_trip or not target_trip.get("created_at"):
                return None
            
            # Récupérer la date de création du trajet cible
            target_created_at = target_trip.get("created_at")
            
            # Récupérer tous les trajets triés par date de création (desc)
            trips = self.get_all(order_by="created_at", order_direction="desc")
            
            # Trouver la position du trajet
            for i, trip in enumerate(trips):
                if trip.get("trip_id") == trip_id:
                    return i
            
            return None
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la position du trajet: {str(e)}")
            return None
    
    def get_trips_paginated_minimal(self, page: int = 0, page_size: int = 10, filters: dict = None) -> Dict:
        """
        Version optimisée qui ne charge que les champs essentiels pour le tableau
        
        Args:
            page: Numéro de page (commence à 0)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres à appliquer
            
        Returns:
            Un dictionnaire contenant:
            - trips: Liste des trajets avec champs minimaux
            - total_count: Nombre total de trajets après filtrage
        """
        try:
            # Initialiser les paramètres de filtre pour Supabase
            supabase_filters = {}
            order_by = "created_at"
            order_direction = "desc"
            
            # Appliquer les filtres de base qui correspondent directement à des colonnes
            if filters:
                # Filtre statut
                if filters.get("status") and filters["status"] != "all":
                    supabase_filters["status"] = filters["status"].upper()
                
                # Tri par date
                date_sort = filters.get("date_sort", "desc")
                if date_sort in ["asc", "desc"]:
                    order_direction = date_sort
            
            # Récupérer tous les trajets avec les filtres de base
            all_trips = self.get_all(order_by=order_by, order_direction=order_direction, filters=supabase_filters)
            
            # Appliquer les filtres plus complexes en post-traitement
            filtered_trips = all_trips
            
            if filters:
                # Filtre texte (origine, destination, trip_id)
                if filters.get("text"):
                    search_term = filters["text"].lower()
                    filtered_trips = [
                        t for t in filtered_trips if (
                            search_term in (t.get("departure_name", "") or "").lower() or
                            search_term in (t.get("destination_name", "") or "").lower() or
                            search_term in (t.get("trip_id", "") or "").lower()
                        )
                    ]
                
                # Filtrage par date de création
                date_filter_type = filters.get("date_filter_type", "range")
                
                if date_filter_type == "after" and filters.get("single_date"):
                    try:
                        date_obj = datetime.datetime.strptime(filters["single_date"], "%Y-%m-%d").date()
                        filtered_trips = [
                            t for t in filtered_trips if (
                                t.get("created_at") and 
                                datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() >= date_obj
                            )
                        ]
                    except (ValueError, TypeError):
                        pass
                
                elif date_filter_type == "before" and filters.get("single_date"):
                    try:
                        date_obj = datetime.datetime.strptime(filters["single_date"], "%Y-%m-%d").date()
                        filtered_trips = [
                            t for t in filtered_trips if (
                                t.get("created_at") and 
                                datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() <= date_obj
                            )
                        ]
                    except (ValueError, TypeError):
                        pass
                
                else:  # range
                    if filters.get("date_from"):
                        try:
                            date_from = datetime.datetime.strptime(filters["date_from"], "%Y-%m-%d").date()
                            filtered_trips = [
                                t for t in filtered_trips if (
                                    t.get("created_at") and 
                                    datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() >= date_from
                                )
                            ]
                        except (ValueError, TypeError):
                            pass
                    
                    if filters.get("date_to"):
                        try:
                            date_to = datetime.datetime.strptime(filters["date_to"], "%Y-%m-%d").date()
                            filtered_trips = [
                                t for t in filtered_trips if (
                                    t.get("created_at") and 
                                    datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() <= date_to
                                )
                            ]
                        except (ValueError, TypeError):
                            pass
            
            # Calculer le nombre total après filtrage
            total_count = len(filtered_trips)
            
            # Appliquer la pagination
            start_idx = page * page_size
            end_idx = start_idx + page_size
            paginated_trips = filtered_trips[start_idx:end_idx]
            
            # Extraire seulement les champs nécessaires pour optimiser
            trips_data = []
            for trip in paginated_trips:
                trips_data.append({
                    "trip_id": trip.get("trip_id"),
                    "departure_name": trip.get("departure_name"),
                    "destination_name": trip.get("destination_name"),
                    "departure_date": trip.get("departure_date"),
                    "departure_schedule": trip.get("departure_schedule"),
                    "seats_available": trip.get("seats_available"),
                    "passenger_price": trip.get("passenger_price"),
                    "status": trip.get("status"),
                    "created_at": trip.get("created_at")
                })
            
            return {
                "trips": trips_data,
                "total_count": total_count
            }
            
        except Exception as e:
            logger.error(f"[TRIP_REPO] Erreur get_trips_paginated_minimal: {str(e)}")
            return {
                "trips": [],
                "total_count": 0
            }
    
    def get_trips_paginated(self, page: int = 0, page_size: int = 10, filters: dict = None) -> Dict:
        """
        Récupère les trajets de façon paginée avec filtrage optionnel
        
        Args:
            page: Numéro de page (commence à 0)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres à appliquer avec les clés suivantes:
                - text: Recherche par origine, destination ou trip_id
                - date_from: Date de création minimale
                - date_to: Date de création maximale
                - status: Filtrer par statut (active, completed, cancelled)
            
        Returns:
            Un dictionnaire contenant:
            - trips: Liste des trajets de la page
            - total_count: Nombre total de trajets après filtrage
        """
        # Cette implémentation est presque identique à get_trips_paginated_minimal
        # mais renvoie tous les champs des trajets au lieu des champs minimaux
        try:
            # Initialiser les paramètres de filtre pour Supabase
            supabase_filters = {}
            order_by = "created_at"
            order_direction = "desc"
            
            # Appliquer les filtres de base qui correspondent directement à des colonnes
            if filters:
                # Filtre statut
                if filters.get("status") and filters["status"] != "all":
                    supabase_filters["status"] = filters["status"].upper()
                
                # Tri par date
                date_sort = filters.get("date_sort", "desc")
                if date_sort in ["asc", "desc"]:
                    order_direction = date_sort
            
            # Récupérer tous les trajets avec les filtres de base
            all_trips = self.get_all(order_by=order_by, order_direction=order_direction, filters=supabase_filters)
            
            # Appliquer les filtres plus complexes en post-traitement
            filtered_trips = all_trips
            
            if filters:
                # Filtre texte (origine, destination, trip_id)
                if filters.get("text"):
                    search_term = filters["text"].lower()
                    filtered_trips = [
                        t for t in filtered_trips if (
                            search_term in (t.get("departure_name", "") or "").lower() or
                            search_term in (t.get("destination_name", "") or "").lower() or
                            search_term in (t.get("trip_id", "") or "").lower()
                        )
                    ]
                
                # Filtrage par date de création
                date_filter_type = filters.get("date_filter_type", "range")
                
                if date_filter_type == "after" and filters.get("single_date"):
                    try:
                        date_obj = datetime.datetime.strptime(filters["single_date"], "%Y-%m-%d").date()
                        filtered_trips = [
                            t for t in filtered_trips if (
                                t.get("created_at") and 
                                datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() >= date_obj
                            )
                        ]
                    except (ValueError, TypeError):
                        pass
                
                elif date_filter_type == "before" and filters.get("single_date"):
                    try:
                        date_obj = datetime.datetime.strptime(filters["single_date"], "%Y-%m-%d").date()
                        filtered_trips = [
                            t for t in filtered_trips if (
                                t.get("created_at") and 
                                datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() <= date_obj
                            )
                        ]
                    except (ValueError, TypeError):
                        pass
                
                else:  # range
                    if filters.get("date_from"):
                        try:
                            date_from = datetime.datetime.strptime(filters["date_from"], "%Y-%m-%d").date()
                            filtered_trips = [
                                t for t in filtered_trips if (
                                    t.get("created_at") and 
                                    datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() >= date_from
                                )
                            ]
                        except (ValueError, TypeError):
                            pass
                    
                    if filters.get("date_to"):
                        try:
                            date_to = datetime.datetime.strptime(filters["date_to"], "%Y-%m-%d").date()
                            filtered_trips = [
                                t for t in filtered_trips if (
                                    t.get("created_at") and 
                                    datetime.datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')).date() <= date_to
                                )
                            ]
                        except (ValueError, TypeError):
                            pass
            
            # Calculer le nombre total après filtrage
            total_count = len(filtered_trips)
            
            # Appliquer la pagination
            start_idx = page * page_size
            end_idx = start_idx + page_size
            paginated_trips = filtered_trips[start_idx:end_idx]
            
            # Optimisation du count pour éviter de compter tous les résultats
            # comme dans l'implémentation d'origine
            if len(paginated_trips) < page_size:
                # Page incomplète = on a atteint la fin
                total_count = page * page_size + len(paginated_trips)
            else:
                # Page complète : estimation optimiste
                # On suppose qu'il y a au moins une page de plus
                total_count = (page + 1) * page_size + 1
            
            return {
                "trips": paginated_trips,
                "total_count": total_count
            }
            
        except Exception as e:
            logger.error(f"[TRIP_REPO] Erreur get_trips_paginated: {str(e)}")
            return {
                "trips": [],
                "total_count": 0
            }
    
    def create_trip(self, trip_data: dict) -> Optional[Dict]:
        """
        Crée un nouveau trajet
        
        Args:
            trip_data: Données du trajet à créer
            
        Returns:
            Trajet créé ou None en cas d'erreur
        """
        return self.create(trip_data)
    
    def update_trip(self, trip_id: str, updates: dict) -> bool:
        """
        Met à jour un trajet existant
        
        Args:
            trip_id: Identifiant du trajet
            updates: Données à mettre à jour
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        return self.update("trip_id", trip_id, updates)
    
    def delete_trip(self, trip_id: str) -> bool:
        """
        Supprime un trajet
        
        Args:
            trip_id: Identifiant du trajet
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        return self.delete("trip_id", trip_id)
