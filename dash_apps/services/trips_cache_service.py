"""
Service de cache centralisé pour les données des trajets
Gère le cache HTML local et les requêtes API REST avec pattern Read-Through
"""
import pandas as pd
from typing import Optional, Dict, Any, List
from dash import html
from dash_apps.services.local_cache import local_cache as cache


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
    def _get_from_cache(cache_key: str) -> Optional[Dict]:
        """Récupère les données depuis le cache avec la clé donnée"""
        return cache.get('trips_list', key=cache_key)
    
    @staticmethod
    def _store_in_local_cache(cache_key: str, data: Dict):
        """Stocke les données dans le cache local avec timestamp"""
        import time
        TripsCacheService._local_cache[cache_key] = data
        TripsCacheService._cache_timestamps[cache_key] = time.time()
        TripsCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def _store_in_cache(cache_key: str, data: Dict, ttl_seconds: int = 300):
        """Stocke les données dans le cache avec TTL"""
        try:
            cache.set('trips_list', data, ttl=ttl_seconds, key=cache_key)
        except Exception as e:
            if TripsCacheService._debug_mode:
                print(f"[CACHE] Erreur stockage: {e}")
    
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
            
            # Niveau 2: Cache principal
            cached_data = TripsCacheService._get_from_cache(cache_key)
            if cached_data:
                # Stocker dans le cache local pour les prochains accès
                TripsCacheService._store_in_local_cache(cache_key, cached_data)
                
                if TripsCacheService._debug_mode:
                    try:
                        trips_count = len(cached_data.get("trips", []))
                        total_count = cached_data.get("total_count", 0)
                        print(f"[TRIPS][CACHE HIT] page_index={page_index} trips={trips_count} total={total_count}")
                    except Exception:
                        pass
                
                return cached_data
        
        # Niveau 3: Base de données (version optimisée)
        result = trip_repository.get_trips_paginated_minimal(page_index, page_size, filters=filter_params)
        
        # Mettre à jour tous les niveaux de cache
        TripsCacheService._store_in_local_cache(cache_key, result)
        TripsCacheService._store_in_cache(cache_key, result, ttl_seconds=300)
        
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
    def _load_panel_config():
        """Charge la configuration des panneaux depuis le fichier JSON"""
        import json
        import os
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'panels_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[CONFIG] Erreur chargement panels_config.json: {e}")
            return {}
    
    @staticmethod
    def _get_api_fetcher_generic(panel_type: str):
        """Fonction générique qui choisit entre SQL et REST selon la config JSON"""
        config = TripsCacheService._load_panel_config()
        panel_config = config.get(panel_type, {})
        data_source = panel_config.get('data_source', 'rest')  # REST par défaut
        
        if data_source == 'sql':
            # Mode SQL direct
            def sql_fetcher(trip_id):
                print(f"[{panel_type.upper()}] Utilisation du SQL Query Builder pour {trip_id[:8]}")
                try:
                    from dash_apps.services.sql_query_builder import SQLQueryBuilder
                    return SQLQueryBuilder.get_panel_data_via_sql(panel_type, trip_id)
                except Exception as e:
                    print(f"[{panel_type.upper()}] Erreur SQL Query Builder: {e}")
                    return None
            return sql_fetcher
        
        else:
            # Mode REST (fallback)
            rest_config = panel_config.get('rest_config', {})
            api_module = rest_config.get('api_module')
            api_function = rest_config.get('api_function')
            
            if not api_module or not api_function:
                print(f"[{panel_type.upper()}] Configuration REST manquante")
                return None
            
            def rest_fetcher(trip_id):
                print(f"[{panel_type.upper()}] Utilisation de l'API REST pour {trip_id[:8]}")
                try:
                    module = __import__(api_module, fromlist=[api_function])
                    api_func = getattr(module, api_function)
                    return api_func(trip_id)
                except Exception as e:
                    print(f"[{panel_type.upper()}] Erreur API REST: {e}")
                    return None
            return rest_fetcher
    
    @staticmethod
    def _get_cache_data_generic(trip_id: str, panel_type: str):
        """Fonction cache générique basée sur la configuration JSON"""
        config = TripsCacheService._load_panel_config()
        panel_config = config.get(panel_type, {})
        
        cache_key_prefix = panel_config.get('cache_key_prefix', panel_type)
        method_name = f"get_trip_{cache_key_prefix.replace('trip_', '')}"
        
        if hasattr(cache, method_name):
            return getattr(cache, method_name)(trip_id)
        return None
    
    @staticmethod
    def _set_cache_data_generic(trip_id: str, data_type: str, data, ttl_seconds: int):
        """Fonction cache générique pour stocker basée sur le type de données"""
        method_name = f"set_trip_{data_type}"
        if hasattr(cache, method_name):
            return getattr(cache, method_name)(trip_id, data, ttl_seconds)
        return None

    @staticmethod
    def _get_cached_panel_generic(selected_trip_id: str, panel_config: dict):
        """Fonction générique optimisée pour récupérer un panneau"""
        if not selected_trip_id:
            from dash import html
            return html.Div()
        
        panel_type = panel_config.get('panel_name', 'unknown')
        methods = panel_config.get('methods', {})
        
        # 1. Vérifier cache HTML
        html_panel = TripsCacheService._check_html_cache(selected_trip_id, panel_type, methods.get('cache', {}))
        if html_panel:
            return html_panel
        
        # 2. Récupérer données (Cache local ou API REST)
        data = TripsCacheService._get_panel_data(selected_trip_id, panel_type, methods)
        if isinstance(data, str) and data.startswith('ERROR:'):
            return TripsCacheService._create_error_panel(data)
        
        # 3. Rendre le panneau
        return TripsCacheService._render_panel(selected_trip_id, panel_type, data, methods)
    
    @staticmethod
    def _check_html_cache(selected_trip_id: str, panel_type: str, cache_config: dict):
        """Vérifie le cache HTML"""
        if not cache_config.get('html_cache_enabled', False):
            return None
        
        cached_panel = TripsCacheService.get_cached_panel(selected_trip_id, panel_type)
        if cached_panel and TripsCacheService._debug_mode:
            print(f"[{panel_type.upper()}][HTML CACHE HIT] Panneau récupéré pour {selected_trip_id[:8]}...")
        return cached_panel
    
    @staticmethod
    def _get_panel_data(selected_trip_id: str, panel_type: str, methods: dict):
        """Récupère les données depuis le cache local ou via l'API REST"""
        cache_config = methods.get('cache', {})
        data_fetcher_config = methods.get('data_fetcher', {})
        
        # Essayer le cache local d'abord
        if cache_config.get('cache_enabled', True):  # Activé par défaut maintenant
            try:
                cached_data = TripsCacheService._get_cache_data_generic(selected_trip_id, panel_type)
                if cached_data:
                    if TripsCacheService._debug_mode:
                        print(f"[{panel_type.upper()}] Données récupérées pour {selected_trip_id[:8]}...")
                    return cached_data
            except Exception as e:
                print(f"[{panel_type.upper()}] Erreur cache: {e}")
        
        # Exécuter le fetcher
        return TripsCacheService._execute_data_fetcher(selected_trip_id, panel_type, data_fetcher_config, cache_config)
    
    @staticmethod
    def _execute_data_fetcher(selected_trip_id: str, panel_type: str, data_fetcher_config: dict, cache_config: dict):
        """Exécute le data fetcher et met en cache"""
        try:
            if TripsCacheService._debug_mode:
                print(f"[{panel_type.upper()}][DATA FETCH] Chargement {selected_trip_id[:8]}...")
            
            # Validation inputs
            inputs = {'trip_id': selected_trip_id}
            error = TripsCacheService._validate_inputs(data_fetcher_config.get('inputs', {}), inputs, panel_type)
            if error:
                return error
            
            # Utiliser uniquement REST API - plus de SQL
            data = TripsCacheService._execute_rest_data_fetcher(data_fetcher_config, inputs)
            
            if not data:
                return f"ERROR:Données non trouvées pour {selected_trip_id}"
            
            # Cache des données localement
            if cache_config.get('cache_enabled', True):
                try:
                    cache_ttl = cache_config.get('cache_ttl', 300)
                    TripsCacheService._set_cache_data_generic(selected_trip_id, panel_type, data, cache_ttl)
                except Exception as e:
                    print(f"[CACHE] Erreur stockage cache: {e}")
            
            return data
            
        except Exception as e:
            return f"ERROR:Erreur lors de la récupération: {e}"
    
    @staticmethod
    def _render_panel(selected_trip_id: str, panel_type: str, data: dict, methods: dict):
        """Rend le panneau final"""
        try:
            cache_config = methods.get('cache', {})
            renderer_config = methods.get('renderer', {})
            
            # Validation inputs renderer
            render_inputs = {'trip_id': selected_trip_id, 'data': data}
            error = TripsCacheService._validate_inputs(renderer_config.get('inputs', {}), render_inputs, panel_type)
            if error:
                return TripsCacheService._create_error_panel(error)
            
            # Exécution renderer
            panel = TripsCacheService._execute_renderer(renderer_config, render_inputs)
            
            # Cache HTML
            if cache_config.get('html_cache_enabled', False):
                TripsCacheService.set_cached_panel(selected_trip_id, panel_type, panel)
            
            return panel
            
        except Exception as e:
            return TripsCacheService._create_error_panel(f"Erreur génération panneau: {e}")
    
    @staticmethod
    def _validate_inputs(required_inputs: dict, provided_inputs: dict, panel_type: str) -> str:
        """Valide les inputs requis, retourne une erreur ou None"""
        for input_name, requirement in required_inputs.items():
            if requirement == "required" and input_name not in provided_inputs:
                return f"ERROR:Input manquant: {input_name}"
        return None
    
    @staticmethod
    def _create_error_panel(error_message: str):
        """Crée un panneau d'erreur standardisé"""
        import dash_bootstrap_components as dbc
        from dash import html
        
        # Extraire le message après ERROR:
        message = error_message.replace('ERROR:', '') if error_message.startswith('ERROR:') else error_message
        color = "warning" if "non trouvées" in message else "danger"
        
        return html.Div(dbc.Alert(message, color=color, className="mb-3"))

    @staticmethod
    def _execute_rest_data_fetcher(data_fetcher_config: dict, inputs: dict):
        """Exécute un data fetcher REST - récupère les données via l'API REST"""
        try:
            from dash_apps.repositories.repository_factory import RepositoryFactory
            trip_id = inputs.get('trip_id')
            
            if not trip_id:
                return None
            
            # Utiliser l'API REST pour récupérer les données du trajet
            trip_repository = RepositoryFactory.get_trip_repository()
            trip_data = trip_repository.get_trip(trip_id)
            
            if not trip_data:
                return None
            
            # Récupérer les données du conducteur si nécessaire
            driver_id = trip_data.get('driver_id')
            if driver_id:
                try:
                    user_repository = RepositoryFactory.get_user_repository()
                    driver_info = user_repository.get_user(driver_id)
                    if driver_info:
                        trip_data['driver_name'] = driver_info.get('display_name', '')
                        trip_data['driver_email'] = driver_info.get('email', '')
                        trip_data['driver_phone'] = driver_info.get('phone_number', '')
                except Exception as e:
                    print(f"[REST] Erreur récupération conducteur: {e}")
            
            print(f"[REST] Données récupérées pour trajet {trip_id}")
            return trip_data
            
        except Exception as e:
            print(f"[REST_FETCHER] Erreur: {e}")
            return None
    
    
    @staticmethod
    def _execute_renderer(renderer_config: dict, inputs: dict):
        """Exécute un renderer basé sur la config"""
        try:
            module_name = renderer_config.get('module')
            function_name = renderer_config.get('function')
            trip_id = inputs.get('trip_id')
            data = inputs.get('data')
            
            if not module_name or not function_name:
                print("[RENDERER] Configuration renderer manquante")
                return None
            
            module = __import__(module_name, fromlist=[function_name])
            render_func = getattr(module, function_name)
            return render_func(trip_id, data)
            
        except Exception as e:
            print(f"[RENDERER] Erreur: {e}")
            return None

    @staticmethod
    def get_trip_details_panel(selected_trip_id: str):
        """Cache HTML → Cache local → API REST pour panneau détails trajet - utilise la nouvelle config JSON"""
        config = TripsCacheService._load_panel_config()
        panel_config = config.get('details', {})
        return TripsCacheService._get_cached_panel_generic(selected_trip_id, panel_config)
    
    @staticmethod
    def get_trip_stats_panel(selected_trip_id: str):
        """Cache HTML → Cache local → API REST pour panneau stats trajet - utilise la nouvelle config JSON"""
        config = TripsCacheService._load_panel_config()
        panel_config = config.get('stats', {})
        return TripsCacheService._get_cached_panel_generic(selected_trip_id, panel_config)
    
    @staticmethod
    def get_trip_passengers_panel(selected_trip_id: str):
        """Cache HTML → Cache local → API REST pour panneau passagers trajet"""
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
            cached_passengers = cache.get_trip_passengers(selected_trip_id)
            if cached_passengers:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_PASSENGERS][CACHE HIT] Passagers récupérés pour {selected_trip_id[:8]}...")
                # Utiliser le pandas importé en haut du fichier
                data = {'trip_id': selected_trip_id, 'passengers': pd.DataFrame(cached_passengers)}
        except Exception:
            pass
        
        # API REST
        if not data:
            try:
                if TripsCacheService._debug_mode:
                    print(f"[TRIP_PASSENGERS][API FETCH] Chargement {selected_trip_id[:8]}... via API REST")
                
                # Utiliser directement les repositories REST
                from dash_apps.repositories.repository_factory import RepositoryFactory
                import pandas as pd
                
                # Pour l'instant, retourner un DataFrame vide car nous n'avons pas encore de système de réservations
                # Dans le futur, il faudra implémenter get_bookings_for_trip dans le repository
                passengers_df = pd.DataFrame()
                
                print(f"[TRIP_PASSENGERS] Utilisation de l'API REST pour {selected_trip_id[:8]}")
                
                if passengers_df.empty:
                    print(f"[TRIP_PASSENGERS][EMPTY] Aucun passager trouvé pour le trajet {selected_trip_id}")
                    import dash_bootstrap_components as dbc
                    return html.Div(dbc.Alert(f"Aucun passager pour ce trajet.", color="warning", className="mb-3"))
                
                data = {'trip_id': selected_trip_id, 'passengers': passengers_df}
                
                # Cache passengers
                try:
                    cache.set_trip_passengers(selected_trip_id, passengers_df, ttl_seconds=TripsCacheService._profile_ttl_seconds)
                except Exception as e:
                    print(f"[CACHE] Erreur stockage cache passagers: {e}")
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
