"""
Service de cache centralisé pour les données des trajets
Gère le cache HTML, Redis et les requêtes DB avec pattern Read-Through
"""
import pandas as pd
from typing import Optional, Dict, Any, List
from dash import html
from dash_apps.services.redis_cache import redis_cache


class TripsCacheService:
    """Service centralisé pour la gestion du cache des trajets"""
    
    # Cache HTML en mémoire pour les panneaux générés
    _html_cache: Dict[str, html.Div] = {}
    
    # Cache local en mémoire pour les pages de trajets
    _local_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}
    _max_local_cache_size = 50  # Limite du cache local
    _local_cache_ttl_seconds = 180  # 3 minutes
    
    # Configuration du cache
    _profile_ttl_seconds = 300  # 5 minutes
    _debug_mode = True  # Mode debug pour les logs
    
    @staticmethod
    def _get_cache_key(page_index: int, page_size: int, filter_params: Dict[str, Any]) -> str:
        """Génère une clé de cache cohérente pour les pages de trajets"""
        import hashlib
        import json
        
        # Normaliser les filtres pour une clé déterministe
        normalized_filters = filter_params or {}
        filter_str = json.dumps(normalized_filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        
        return f"trips_page:{page_index}:{page_size}:{filter_hash}"
    
    @staticmethod
    def _get_from_redis_cache(cache_key: str) -> Optional[Dict]:
        """Récupère les données depuis Redis avec la clé donnée"""
        return redis_cache.get_json_by_key(cache_key)
    
    @staticmethod
    def _store_in_local_cache(cache_key: str, data: Dict):
        """Stocke les données dans le cache local avec timestamp"""
        import time
        TripsCacheService._local_cache[cache_key] = data
        TripsCacheService._cache_timestamps[cache_key] = time.time()
        TripsCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def _store_in_redis_cache(cache_key: str, data: Dict, ttl_seconds: int = 300):
        """Stocke les données dans Redis avec TTL"""
        import json
        try:
            redis_cache.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(data, default=str)
            )
            if TripsCacheService._debug_mode:
                print(f"[REDIS] Cache trajets mis à jour: {cache_key} (TTL: {ttl_seconds}s)")
        except Exception as e:
            print(f"[REDIS] Erreur stockage cache: {e}")
    
    @staticmethod
    def _is_local_cache_valid(cache_key: str) -> bool:
        """Vérifie si l'entrée du cache local est encore valide"""
        import time
        if cache_key not in TripsCacheService._cache_timestamps:
            return False
        age = time.time() - TripsCacheService._cache_timestamps[cache_key]
        return age < TripsCacheService._local_cache_ttl_seconds
    
    @staticmethod
    def _evict_local_cache_if_needed():
        """Éviction LRU simple du cache local si nécessaire"""
        if len(TripsCacheService._local_cache) <= TripsCacheService._max_local_cache_size:
            return
        
        # Trier par timestamp (plus ancien en premier)
        sorted_keys = sorted(TripsCacheService._cache_timestamps.items(), key=lambda x: x[1])
        keys_to_remove = [key for key, _ in sorted_keys[:10]]  # Supprimer les 10 plus anciens
        
        for key in keys_to_remove:
            TripsCacheService._local_cache.pop(key, None)
            TripsCacheService._cache_timestamps.pop(key, None)
    
    @staticmethod
    def get_trips_page_result(page_index: int, page_size: int, filter_params: Dict[str, Any], force_reload: bool = False) -> Dict[str, Any]:
        """
        Récupère les données d'une page de trajets avec cache multi-niveaux optimisé
        
        Args:
            page_index: Index de la page (0-based)
            page_size: Nombre d'éléments par page
            filter_params: Paramètres de filtrage
            force_reload: Force le rechargement depuis la DB
            
        Returns:
            Dict contenant trips, total_count, et données pré-calculées
        """
        import time
        from dash_apps.repositories.repository_factory import RepositoryFactory
        
        # Obtenir le repository approprié via la factory
        trip_repository = RepositoryFactory.get_trip_repository()
        
        # Unifier la clé L1/L2 en utilisant la méthode interne cohérente
        cache_key = TripsCacheService._get_cache_key(page_index, page_size, filter_params)
        
        if not force_reload:
            # Niveau 1: Cache local ultra-rapide (en mémoire)
            if (cache_key in TripsCacheService._local_cache and 
                TripsCacheService._is_local_cache_valid(cache_key)):
                
                if TripsCacheService._debug_mode:
                    try:
                        trips_count = len(TripsCacheService._local_cache[cache_key].get("trips", []))
                        total_count = TripsCacheService._local_cache[cache_key].get("total_count", 0)
                        print(f"[TRIPS][LOCAL CACHE HIT] page_index={page_index} trips={trips_count} total={total_count}")
                    except Exception:
                        pass

                cached = TripsCacheService._local_cache[cache_key]
                return cached
            
            # Niveau 2: Cache Redis
            cached_data = TripsCacheService._get_from_redis_cache(cache_key)
            if cached_data:
                # Stocker dans le cache local pour les prochains accès
                TripsCacheService._store_in_local_cache(cache_key, cached_data)
                
                if TripsCacheService._debug_mode:
                    try:
                        trips_count = len(cached_data.get("trips", []))
                        total_count = cached_data.get("total_count", 0)
                        print(f"[TRIPS][REDIS HIT] page_index={page_index} trips={trips_count} total={total_count}")
                    except Exception:
                        pass
                
                return cached_data
        
        # Niveau 3: Base de données (version optimisée)
        result = trip_repository.get_trips_paginated_minimal(page_index, page_size, filters=filter_params)
        
        # Mettre à jour tous les niveaux de cache
        TripsCacheService._store_in_local_cache(cache_key, result)
        TripsCacheService._store_in_redis_cache(cache_key, result, ttl_seconds=300)
        
        if TripsCacheService._debug_mode:
            try:
                trips_count = len(result.get("trips", []))
                total_count = result.get("total_count", 0)
                print(f"[TRIPS][FETCH] page_index={page_index} trips={trips_count} total={total_count} refresh={force_reload}")
            except Exception:
                pass
        
        return result
    
    @staticmethod
    def extract_table_data(result: Dict[str, Any]) -> tuple:
        """
        Extrait les données nécessaires pour le tableau depuis le résultat
        
        Args:
            result: Résultat de get_trips_page_result
            
        Returns:
            tuple: (trips, total_count, table_rows_data)
        """
        trips = result.get("trips", [])
        total_count = result.get("total_count", 0)
        
        # Convertir les objets TripSchema en dictionnaires pour le tableau
        table_rows_data = []
        if trips:
            for trip in trips:
                if hasattr(trip, 'model_dump'):
                    # Pydantic model - convertir en dict
                    table_rows_data.append(trip.model_dump())
                elif hasattr(trip, 'to_dict'):
                    # DataFrame ou autre objet avec to_dict
                    table_rows_data.append(trip.to_dict())
                elif isinstance(trip, dict):
                    # Déjà un dictionnaire
                    table_rows_data.append(trip)
                else:
                    # Fallback: essayer de convertir en dict via __dict__
                    try:
                        table_rows_data.append(trip.__dict__)
                    except:
                        # Si tout échoue, ignorer cet élément
                        continue
        
        return trips, total_count, table_rows_data
    
    @staticmethod
    def get_trip_details_panel(selected_trip_id: str):
        """Cache HTML → Redis → DB pour panneau détails trajet"""
        if not selected_trip_id:
            return html.Div()
        
        # Cache HTML
        cached_panel = TripsCacheService.get_cached_panel(selected_trip_id, 'details')
        if cached_panel:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_DETAILS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_trip_id[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_trip = redis_cache.get_trip_details(selected_trip_id)
            if cached_trip:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_DETAILS][REDIS HIT] Détails récupérés pour {selected_trip_id[:8]}...")
                data = cached_trip
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_DETAILS][DB FETCH] Chargement {selected_trip_id[:8]}... depuis la DB")
                from dash_apps.utils.data_schema_rest import get_trip_by_id
                print(f"[TRIP_DETAILS] Utilisation de l'API REST pour {selected_trip_id[:8]}")
                data = get_trip_by_id(selected_trip_id)
                if not data:
                    print(f"[TRIP_DETAILS][ERROR] Trajet avec ID {selected_trip_id} non trouvé")
                    import dash_bootstrap_components as dbc
                    return html.Div(dbc.Alert(f"Trajet avec l'ID {selected_trip_id} non trouvé.", color="warning", className="mb-3"))
                # Cache trip details
                try:
                    redis_cache.set_trip_details(selected_trip_id, data, ttl_seconds=TripsCacheService._profile_ttl_seconds)
                except Exception as e:
                    print(f"[REDIS] Erreur stockage cache: {e}")
            except Exception as e:
                print(f"[TRIP_DETAILS][ERROR] Erreur lors de la récupération du trajet {selected_trip_id}: {e}")
                import dash_bootstrap_components as dbc
                return html.Div(dbc.Alert(f"Erreur lors de la récupération du trajet {selected_trip_id}: {e}", color="danger", className="mb-3"))
        
        # Render
        try:
            # Utiliser le composant original de layout pour le rendu des détails du trajet
            from dash_apps.components.trip_details_layout import create_trip_details_layout
            panel = create_trip_details_layout(selected_trip_id, data)
            
            TripsCacheService.set_cached_panel(selected_trip_id, 'details', panel)
            return panel
        except Exception as e:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_DETAILS] Erreur génération panneau: {e}")
            import dash_bootstrap_components as dbc
            return html.Div(dbc.Alert(f"Erreur lors de la génération du panneau de détails: {e}", color="danger", className="mb-3"))
    
    @staticmethod
    def get_trip_stats_panel(selected_trip_id: str):
        """Cache HTML → Redis → DB pour panneau stats trajet"""
        if not selected_trip_id:
            return html.Div()
        
        # Cache HTML
        cached_panel = TripsCacheService.get_cached_panel(selected_trip_id, 'stats')
        if cached_panel:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_STATS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_trip_id[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_stats = redis_cache.get_trip_stats(selected_trip_id)
            if cached_stats:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_STATS][REDIS HIT] Stats récupérées pour {selected_trip_id[:8]}...")
                data = {'trip_id': selected_trip_id, 'stats': cached_stats}
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_STATS][DB FETCH] Chargement {selected_trip_id[:8]}... depuis la DB")
                from dash_apps.utils.data_schema_rest import get_trip_stats_optimized
                print(f"[TRIP_STATS] Utilisation de l'API REST pour {selected_trip_id[:8]}")
                stats = get_trip_stats_optimized(selected_trip_id)
                if not stats:
                    print(f"[TRIP_STATS][ERROR] Aucune statistique trouvée pour le trajet {selected_trip_id}")
                    import dash_bootstrap_components as dbc
                    return html.Div(dbc.Alert(f"Aucune statistique disponible pour ce trajet.", color="warning", className="mb-3"))
                data = {'trip_id': selected_trip_id, 'stats': stats}
                # Cache stats
                try:
                    redis_cache.set_trip_stats(selected_trip_id, stats, ttl_seconds=TripsCacheService._profile_ttl_seconds)
                except Exception as e:
                    print(f"[REDIS] Erreur stockage cache stats: {e}")
            except Exception as e:
                print(f"[TRIP_STATS][ERROR] Erreur lors de la récupération des stats du trajet {selected_trip_id}: {e}")
                import dash_bootstrap_components as dbc
                return html.Div(dbc.Alert(f"Erreur lors du chargement des statistiques: {e}", color="danger", className="mb-3"))
        
        # Render
        try:
            from dash_apps.components.trip_stats_panel import render_trip_stats_panel
            panel = render_trip_stats_panel(data)
            TripsCacheService.set_cached_panel(selected_trip_id, 'stats', panel)
            return panel
        except Exception as e:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_STATS] Erreur génération panneau: {e}")
            import dash_bootstrap_components as dbc
            return html.Div(dbc.Alert(f"Erreur lors de la génération des statistiques: {e}", color="danger", className="mb-3"))
    
    @staticmethod
    def get_trip_passengers_panel(selected_trip_id: str):
        """Cache HTML → Redis → DB pour panneau passagers trajet"""
        if not selected_trip_id:
            return html.Div()
        
        # Cache HTML
        cached_panel = TripsCacheService.get_cached_panel(selected_trip_id, 'passengers')
        if cached_panel:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_PASSENGERS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_trip_id[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_passengers = redis_cache.get_trip_passengers(selected_trip_id)
            if cached_passengers:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_PASSENGERS][REDIS HIT] Passagers récupérés pour {selected_trip_id[:8]}...")
                # Utiliser le pandas importé en haut du fichier
                data = {'trip_id': selected_trip_id, 'passengers': pd.DataFrame(cached_passengers)}
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_PASSENGERS][DB FETCH] Chargement {selected_trip_id[:8]}... depuis la DB")
                from dash_apps.utils.data_schema_rest import get_passengers_for_trip
                print(f"[TRIP_PASSENGERS] Utilisation de l'API REST pour {selected_trip_id[:8]}")
                # Import pandas ici pour s'assurer qu'il est disponible dans ce scope
                import pandas as pd
                passengers_df = get_passengers_for_trip(selected_trip_id)
                if passengers_df is None or (isinstance(passengers_df, pd.DataFrame) and passengers_df.empty):
                    print(f"[TRIP_PASSENGERS][EMPTY] Aucun passager trouvé pour le trajet {selected_trip_id}")
                    import dash_bootstrap_components as dbc
                    return html.Div(dbc.Alert(f"Aucun passager pour ce trajet.", color="warning", className="mb-3"))
                data = {'trip_id': selected_trip_id, 'passengers': passengers_df}
                # Cache passengers
                try:
                    redis_cache.set_trip_passengers(selected_trip_id, passengers_df, ttl_seconds=TripsCacheService._profile_ttl_seconds)
                except Exception as e:
                    print(f"[REDIS] Erreur stockage cache passagers: {e}")
            except Exception as e:
                print(f"[TRIP_PASSENGERS][ERROR] Erreur lors de la récupération des passagers du trajet {selected_trip_id}: {e}")
                import dash_bootstrap_components as dbc
                return html.Div(dbc.Alert(f"Erreur lors du chargement des passagers: {e}", color="danger", className="mb-3"))
        
        # Render
        try:
            from dash_apps.components.trip_passengers_panel import render_trip_passengers_panel
            panel = render_trip_passengers_panel(data)
            TripsCacheService.set_cached_panel(selected_trip_id, 'passengers', panel)
            return panel
        except Exception as e:
            if TripsCacheService._debug_mode:
                print(f"[TRIP_PASSENGERS] Erreur génération panneau: {e}")
            import dash_bootstrap_components as dbc
            return html.Div(dbc.Alert(f"Erreur lors de la génération du panneau des passagers: {e}", color="danger", className="mb-3"))
    
    @staticmethod
    def get_cached_panel(trip_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Récupère un panneau HTML en cache avec gestion intelligente
        
        Args:
            trip_id: ID du trajet
            panel_type: Type de panneau ('details', 'stats', 'passengers')
            
        Returns:
            html.Div: Panneau en cache ou None si non trouvé
        """
        cache_key = f"{trip_id}_{panel_type}"
        
        # Vérifier d'abord le cache HTML local
        if cache_key in TripsCacheService._html_cache:
            if TripsCacheService._debug_mode:
                print(f"[HTML_CACHE] Cache hit pour {cache_key}")
            return TripsCacheService._html_cache[cache_key]
        
        return None
    
    @staticmethod
    def set_cached_panel(trip_id: str, panel_type: str, panel: html.Div):
        """
        Met en cache un panneau HTML généré
        
        Args:
            trip_id: ID du trajet
            panel_type: Type de panneau ('details', 'stats', 'passengers')
            panel: Panneau HTML à mettre en cache
        """
        cache_key = f"{trip_id}_{panel_type}"
        TripsCacheService._html_cache[cache_key] = panel
        
        if TripsCacheService._debug_mode:
            print(f"[HTML_CACHE] Panneau {panel_type} mis en cache pour trajet {trip_id[:8]}...")
    
    @staticmethod
    def clear_trip_cache(trip_id: str):
        """
        Efface le cache pour un trajet spécifique
        
        Args:
            trip_id: ID du trajet
        """
        keys_to_remove = [key for key in TripsCacheService._html_cache.keys() if key.startswith(f"{trip_id}_")]
        for key in keys_to_remove:
            del TripsCacheService._html_cache[key]
        
        if TripsCacheService._debug_mode:
            print(f"[HTML_CACHE] Cache effacé pour trajet {trip_id[:8]}...")
    
    @staticmethod
    def clear_all_html_cache():
        """Efface tout le cache HTML"""
        TripsCacheService._html_cache.clear()
        if TripsCacheService._debug_mode:
            print("[HTML_CACHE] Tout le cache HTML effacé")
    
    @staticmethod
    def preload_trip_panels(trip_ids: List[str], panel_types: List[str]):
        """
        Précharge les panneaux pour plusieurs trajets
        
        Args:
            trip_ids: Liste des IDs de trajets
            panel_types: Types de panneaux à précharger ('details', 'stats', 'passengers')
        """
        if not trip_ids or not panel_types:
            return
        
        if TripsCacheService._debug_mode:
            print(f"[PRELOAD] Préchargement de {len(trip_ids)} trajets, panneaux: {panel_types}")
        
        for trip_id in trip_ids[:5]:  # Limiter à 5 trajets pour éviter la surcharge
            for panel_type in panel_types:
                try:
                    if panel_type == 'details':
                        TripsCacheService.get_trip_details_panel(trip_id)
                    elif panel_type == 'stats':
                        TripsCacheService.get_trip_stats_panel(trip_id)
                    elif panel_type == 'passengers':
                        TripsCacheService.get_trip_passengers_panel(trip_id)
                except Exception as e:
                    if TripsCacheService._debug_mode:
                        print(f"[PRELOAD] Erreur préchargement {panel_type} pour {trip_id[:8]}: {e}")
