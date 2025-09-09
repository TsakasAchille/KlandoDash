"""
Service de cache pour les données utilisateurs avec logique de génération centralisée
"""
import time
import threading
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.repositories.repository_factory import RepositoryFactory
# Redis cache removed - using local cache + REST API only

# Initialiser le repository utilisateur via la factory
user_repository = RepositoryFactory.get_user_repository()

class UsersCacheService:
    """Service centralisé pour la gestion du cache des données utilisateurs"""
    
    # Cache en mémoire pour les panneaux HTML générés
    _html_cache = {}
    
    # Mode debug pour les logs (désactivé en production)
    _debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
    
    # Cache local rapide pour éviter Redis sur les accès fréquents
    _local_cache = {}
    _cache_timestamps = {}
    _local_cache_ttl = int(os.getenv('LOCAL_CACHE_TTL', '45'))  # TTL local configurable (par défaut 45s)
    _local_max_entries = int(os.getenv('LOCAL_CACHE_MAX_ENTRIES', '200'))  # Limite max d'entrées en L1
    _profile_ttl_seconds = 600  # 10 minutes pour le profil utilisateur en cache local
    
    @staticmethod
    def _get_cache_key(page_index: int, page_size: int, filter_params: Dict) -> str:
        """Génère une clé de cache optimisée sans hash MD5"""
        # Simplifier la génération de clé pour plus de rapidité
        filter_str = ""
        if filter_params:
            # Créer une chaîne simple des filtres les plus importants
            key_filters = ['text', 'role', 'date_from', 'date_to', 'gender']
            filter_parts = []
            for key in key_filters:
                if key in filter_params and filter_params[key]:
                    filter_parts.append(f"{key}:{filter_params[key]}")
            filter_str = "|".join(filter_parts)
        
        return f"users:{page_index}:{page_size}:{filter_str}"
    
    @staticmethod
    def _get_from_local_cache(cache_key: str) -> Optional[Dict]:
        """Récupère les données du cache local si valides"""
        if (cache_key in UsersCacheService._local_cache and 
            UsersCacheService._is_local_cache_valid(cache_key)):
            return UsersCacheService._local_cache[cache_key]
        return None
    
    @staticmethod
    def _get_from_redis_cache(cache_key: str, page_index: int, page_size: int, filters: Dict) -> Optional[Dict]:
        """Redis cache removed - always return None to force local cache or API calls"""
        return None
    
    @staticmethod
    def _store_in_local_cache(cache_key: str, result: Dict):
        """Stocke les données dans le cache local"""
        UsersCacheService._local_cache[cache_key] = result
        UsersCacheService._cache_timestamps[cache_key] = time.time()
        UsersCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def _store_in_redis_cache(cache_key: str, result: Dict, page_index: int, page_size: int, filters: Dict):
        """Redis cache removed - no-op method for compatibility"""
        pass
    
    @staticmethod
    def _is_local_cache_valid(cache_key: str) -> bool:
        """Vérifie si le cache local est encore valide"""
        import time
        if cache_key not in UsersCacheService._cache_timestamps:
            return False
        
        elapsed = time.time() - UsersCacheService._cache_timestamps[cache_key]
        return elapsed < UsersCacheService._local_cache_ttl
    
    @staticmethod
    def get_users_page_result(page_index: int, page_size: int, filter_params: Dict,
                             force_reload: bool = False, selected_uid: Optional[str] = None) -> Dict:
        """
        Récupère le résultat brut d'une page d'utilisateurs avec cache multi-niveaux optimisé
        
        Returns:
            Dict: Résultat complet du repository (users, total_count, basic_by_uid, table_rows_data)
        """
        import time
        
        # Utiliser la même méthode de génération de clé que get_users_page_data pour la cohérence
        cache_key = UsersCacheService._get_cache_key(page_index, page_size, filter_params)
        
        if not force_reload:
            # Niveau 1: Cache local ultra-rapide (en mémoire)
            if (cache_key in UsersCacheService._local_cache and 
                UsersCacheService._is_local_cache_valid(cache_key)):
                
                if UsersCacheService._debug_mode:
                    try:
                        users_count = len(UsersCacheService._local_cache[cache_key].get("users", []))
                        total_count = UsersCacheService._local_cache[cache_key].get("total_count", 0)
                        print(f"[USERS][LOCAL CACHE HIT] page_index={page_index} users={users_count} total={total_count}")
                    except Exception:
                        pass

                cached = UsersCacheService._local_cache[cache_key]
                return cached
            
            # Niveau 2: Redis cache removed - skip to API REST calls
        
        # Niveau 2: API REST calls (Redis removed)
        result = user_repository.get_users_paginated(page_index, page_size, filters=filter_params)
        
        # Mettre à jour tous les niveaux de cache
        UsersCacheService._store_in_local_cache(cache_key, result)
        UsersCacheService._store_in_redis_cache(cache_key, result, page_index, page_size, filter_params)
        
        if UsersCacheService._debug_mode:
            try:
                users_count = len(result.get("users", []))
                total_count = result.get("total_count", 0)
                print(f"[USERS][FETCH] page_index={page_index} users={users_count} total={total_count} refresh={force_reload}")
            except Exception:
                pass
        
        return result

    @staticmethod
    def _evict_local_cache_if_needed():
        """
        Évite la dérive mémoire du cache local par une éviction LRU approximative
        basée sur les timestamps. Supprime les plus anciens jusqu'à rentrer
        sous la limite _local_max_entries.
        """
        try:
            size = len(UsersCacheService._local_cache)
            if size <= UsersCacheService._local_max_entries:
                return
            # Trier les clés par ancienneté (timestamp croissant)
            items = sorted(
                UsersCacheService._cache_timestamps.items(), key=lambda kv: kv[1]
            )
            to_remove = size - UsersCacheService._local_max_entries
            removed = 0
            for key, _ in items:
                if key in UsersCacheService._local_cache:
                    del UsersCacheService._local_cache[key]
                if key in UsersCacheService._cache_timestamps:
                    del UsersCacheService._cache_timestamps[key]
                removed += 1
                if removed >= to_remove:
                    break
            if UsersCacheService._debug_mode:
                print(f"[USERS][LOCAL CACHE EVICT] removed={removed} size={len(UsersCacheService._local_cache)}")
        except Exception:
            # Éviter tout crash dû à l'éviction
            pass

    @staticmethod
    def invalidate_local_users_pages(predicate=None):
        """
        Invalide (supprime) des entrées du cache local L1.
        predicate: callable optionnel de signature (key: str, value: Dict) -> bool
                   si None, invalide toutes les entrées.
        """
        try:
            keys = list(UsersCacheService._local_cache.keys())
            for key in keys:
                value = UsersCacheService._local_cache.get(key)
                if predicate is None or (callable(predicate) and predicate(key, value)):
                    del UsersCacheService._local_cache[key]
                    if key in UsersCacheService._cache_timestamps:
                        del UsersCacheService._cache_timestamps[key]
            if UsersCacheService._debug_mode:
                print(f"[USERS][LOCAL CACHE INVALIDATE] size={len(UsersCacheService._local_cache)}")
        except Exception:
            pass

    
    @staticmethod
    def extract_table_data(result: Dict) -> Tuple[List, int, List]:
        """
        Extrait les données nécessaires pour le rendu du tableau
        
        Returns:
            Tuple[users, total_users, table_rows_data]
        """
        users = result.get("users", [])
        total_users = int(result.get("total_count", 0))
        table_rows_data = result.get("table_rows_data", [])
        
        return users, total_users, table_rows_data

    def get_users_page_data(self, page_index: int = 0, page_size: int = 10, filters: dict = None, force_reload: bool = False, selected_uid: str = None) -> dict:
        """
        Récupère les données complètes pour une page d'utilisateurs avec cache intelligent
        
        Args:
            page_index: Index de la page (0-based)
            page_size: Nombre d'utilisateurs par page
            filters: Filtres à appliquer
            force_reload: Force le rechargement depuis la DB
            selected_uid: UID de l'utilisateur sélectionné
            
        Returns:
            Dict contenant users, total_count, table_rows_data
        """
        print(f"[DEBUG] get_users_page_data called with page_index={page_index}, page_size={page_size}, filters={filters}, force_reload={force_reload}")
        
        # Générer une clé de cache basée sur les paramètres
        cache_key = UsersCacheService._get_cache_key(page_index, page_size, filters)
        
        # Vérifier le cache local d'abord (si pas de force reload)
        if not force_reload:
            cached_result = UsersCacheService._get_from_local_cache(cache_key)
            if cached_result:
                print(f"[LOCAL CACHE HIT] Page {page_index} récupérée du cache local")
                return cached_result
            else:
                print(f"[LOCAL CACHE MISS] Pas de cache local pour page {page_index}")
        
        # Redis cache removed - skip to API REST calls
        
        # Charger depuis l'API REST
        print(f"[DEBUG] Chargement depuis l'API REST...")
        try:
            result = user_repository.get_users_paginated(page_index, page_size, filters=filters)
            print(f"[DEBUG] Résultat DB: {len(result.get('users', []))} utilisateurs, total={result.get('total_count', 0)}")
            
            # Stocker le résultat dans les caches
            UsersCacheService._store_in_local_cache(cache_key, result)
            UsersCacheService._store_in_redis_cache(cache_key, result, page_index, page_size, filters)
            
            return result
            
        except Exception as e:
            print(f"[DB ERROR] Erreur chargement page {page_index}: {e}")
            return {
                "users": [],
                "total_count": 0,
                "table_rows_data": []
            }
    
    @staticmethod
    def _load_panel_config():
        """Charge la configuration des panneaux utilisateur depuis le fichier JSON"""
        import json
        import os
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'user_panels_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[CONFIG] Erreur chargement user_panels_config.json: {e}")
            return {}
    
    @staticmethod
    def _get_cached_panel_generic(selected_uid: str, panel_config: dict):
        """Fonction générique optimisée pour récupérer un panneau utilisateur"""
        if not selected_uid:
            from dash import html
            return html.Div()
        
        panel_type = panel_config.get('panel_name', 'unknown')
        methods = panel_config.get('methods', {})
        
        # 1. Vérifier cache HTML
        html_panel = UsersCacheService._check_html_cache(selected_uid, panel_type, methods.get('cache', {}))
        if html_panel:
            return html_panel
        
        # 2. Récupérer données (Cache local ou API REST)
        data = UsersCacheService._get_panel_data(selected_uid, panel_type, methods)
        if isinstance(data, str) and data.startswith('ERROR:'):
            return UsersCacheService._create_error_panel(data)
        
        # 3. Rendre le panneau
        return UsersCacheService._render_panel(selected_uid, panel_type, data, methods)
    
    @staticmethod
    def _check_html_cache(selected_uid: str, panel_type: str, cache_config: dict):
        """Vérifie le cache HTML"""
        if not cache_config.get('html_cache_enabled', False):
            return None
        
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, panel_type)
        if cached_panel and UsersCacheService._debug_mode:
            print(f"[{panel_type.upper()}][HTML CACHE HIT] Panneau récupéré pour {selected_uid[:8]}...")
        return cached_panel
    
    @staticmethod
    def _get_panel_data(selected_uid: str, panel_type: str, methods: dict):
        """Récupère les données depuis le cache local ou via l'API REST"""
        cache_config = methods.get('cache', {})
        data_fetcher_config = methods.get('data_fetcher', {})
        
        # Essayer le cache local d'abord
        if cache_config.get('cache_enabled', True):  # Activé par défaut
            try:
                cached_data = UsersCacheService._get_cache_data_generic(selected_uid, panel_type)
                if cached_data:
                    if UsersCacheService._debug_mode:
                        print(f"[{panel_type.upper()}] Données récupérées du cache pour {selected_uid[:8]}...")
                    return cached_data
            except Exception as e:
                print(f"[{panel_type.upper()}] Erreur cache: {e}")
        
        # Exécuter le fetcher
        return UsersCacheService._execute_data_fetcher(selected_uid, panel_type, data_fetcher_config, cache_config)
    
    @staticmethod
    def _execute_data_fetcher(selected_uid: str, panel_type: str, data_fetcher_config: dict, cache_config: dict):
        """Exécute le data fetcher et met en cache"""
        try:
            if UsersCacheService._debug_mode:
                print(f"[{panel_type.upper()}][DATA FETCH] Chargement {selected_uid[:8]}...")
            
            # Validation inputs
            inputs = {'user_id': selected_uid}
            error = UsersCacheService._validate_inputs(data_fetcher_config.get('inputs', {}), inputs, panel_type)
            if error:
                return error
            
            # Utiliser uniquement REST API
            data = UsersCacheService._execute_rest_data_fetcher(data_fetcher_config, inputs)
            
            if data is None:
                return f"ERROR:Données non trouvées pour {selected_uid}"
            
            # Cache des données localement
            if cache_config.get('cache_enabled', True):
                try:
                    cache_ttl = cache_config.get('cache_ttl', 600)
                    UsersCacheService._set_cache_data_generic(selected_uid, panel_type, data, cache_ttl)
                except Exception as e:
                    print(f"[CACHE] Erreur stockage cache: {e}")
            
            return data
            
        except Exception as e:
            return f"ERROR:Erreur lors de la récupération: {e}"
    
    @staticmethod
    def _execute_rest_data_fetcher(data_fetcher_config: dict, inputs: dict):
        """Exécute un data fetcher REST - récupère les données via l'API REST"""
        try:
            rest_config = data_fetcher_config.get('rest_config', {})
            function_name = rest_config.get('function')
            module_name = rest_config.get('module')
            params = rest_config.get('params', {})
            
            print(f"[DATA_FETCHER_DEBUG] === DÉBUT _execute_rest_data_fetcher ===")
            print(f"[DATA_FETCHER_DEBUG] Function: {function_name}")
            print(f"[DATA_FETCHER_DEBUG] Module: {module_name}")
            print(f"[DATA_FETCHER_DEBUG] Params config: {params}")
            print(f"[DATA_FETCHER_DEBUG] Inputs: {inputs}")
            
            if not function_name or not module_name:
                print(f"[DATA_FETCHER_DEBUG] Configuration incomplète")
                return None
            
            # Import dynamique du module
            import importlib
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            # Préparer les paramètres
            call_params = {}
            for param_key, input_key in params.items():
                if input_key in inputs:
                    call_params[param_key] = inputs[input_key]
                elif isinstance(input_key, (str, int, float)):
                    call_params[param_key] = input_key
            
            print(f"[DATA_FETCHER_DEBUG] Paramètres d'appel: {call_params}")
            
            # Appeler la fonction
            result = function(**call_params)
            print(f"[DATA_FETCHER_DEBUG] Résultat: {type(result)}")
            if hasattr(result, 'shape'):
                print(f"[DATA_FETCHER_DEBUG] DataFrame shape: {result.shape}")
            print(f"[DATA_FETCHER_DEBUG] === FIN _execute_rest_data_fetcher ===")
            
            return result
            
        except Exception as e:
            print(f"[DATA_FETCHER_DEBUG] ERREUR: {e}")
            print(f"[REST FETCHER] Erreur: {e}")
            return None
    
    @staticmethod
    def _render_panel(selected_uid: str, panel_type: str, data: dict, methods: dict):
        """Rend le panneau final"""
        try:
            print(f"[RENDER_PANEL_DEBUG] === DÉBUT _render_panel ===")
            print(f"[RENDER_PANEL_DEBUG] Panel type: {panel_type}")
            print(f"[RENDER_PANEL_DEBUG] Data type: {type(data)}")
            print(f"[RENDER_PANEL_DEBUG] User ID: {selected_uid}")
            
            cache_config = methods.get('cache', {})
            renderer_config = methods.get('renderer', {})
            
            print(f"[RENDER_PANEL_DEBUG] Renderer config: {renderer_config}")
            
            # Validation inputs renderer
            render_inputs = {'user_id': selected_uid, 'data': data}
            error = UsersCacheService._validate_inputs(renderer_config.get('inputs', {}), render_inputs, panel_type)
            if error:
                print(f"[RENDER_PANEL_DEBUG] Erreur validation: {error}")
                return UsersCacheService._create_error_panel(error)
            
            print(f"[RENDER_PANEL_DEBUG] Validation OK, appel renderer...")
            
            # Exécution renderer
            panel = UsersCacheService._execute_renderer(renderer_config, render_inputs)
            
            print(f"[RENDER_PANEL_DEBUG] Renderer terminé, résultat: {type(panel)}")
            
            # Cache HTML
            if cache_config.get('html_cache_enabled', False):
                UsersCacheService.set_cached_panel(selected_uid, panel_type, panel)
                print(f"[RENDER_PANEL_DEBUG] Panneau mis en cache")
            
            print(f"[RENDER_PANEL_DEBUG] === FIN _render_panel ===")
            return panel
            
        except Exception as e:
            print(f"[RENDER_PANEL_DEBUG] ERREUR: {e}")
            return UsersCacheService._create_error_panel(f"Erreur génération panneau: {e}")
    
    @staticmethod
    def _execute_renderer(renderer_config: dict, inputs: dict):
        """Exécute le renderer pour générer le panneau HTML"""
        try:
            module_name = renderer_config.get('module')
            function_name = renderer_config.get('function')
            
            print(f"[RENDERER_DEBUG] === DÉBUT _execute_renderer ===")
            print(f"[RENDERER_DEBUG] Module: {module_name}")
            print(f"[RENDERER_DEBUG] Function: {function_name}")
            print(f"[RENDERER_DEBUG] Inputs: {list(inputs.keys())}")
            print(f"[RENDERER_DEBUG] Data type: {type(inputs.get('data'))}")
            
            if not module_name or not function_name:
                raise Exception("Configuration renderer incomplète")
            
            # Import dynamique
            import importlib
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            # Appeler la fonction de rendu avec les bons paramètres selon la signature
            import inspect
            sig = inspect.signature(function)
            
            print(f"[RENDERER_DEBUG] Signature détectée: {sig}")
            
            if 'user_id' in sig.parameters and 'data' in sig.parameters:
                # Nouvelle signature (render_user_trips)
                print(f"[RENDERER_DEBUG] Appel avec user_id et data")
                print(f"[RENDERER_DEBUG] user_id: {inputs['user_id']}")
                print(f"[RENDERER_DEBUG] data: {type(inputs['data'])}")
                result = function(user_id=inputs['user_id'], data=inputs['data'])
                print(f"[RENDERER_DEBUG] Résultat: {type(result)}")
                return result
            elif 'user' in sig.parameters:
                # Ancienne signature (render_user_profile, render_user_stats)
                print(f"[RENDERER_DEBUG] Appel avec user seulement")
                result = function(inputs['data'])
                print(f"[RENDERER_DEBUG] Résultat: {type(result)}")
                return result
            else:
                # Fallback: essayer avec data seulement
                print(f"[RENDERER_DEBUG] Appel fallback avec data")
                result = function(inputs['data'])
                print(f"[RENDERER_DEBUG] Résultat: {type(result)}")
                return result
            
        except Exception as e:
            print(f"[RENDERER_DEBUG] ERREUR: {e}")
            raise Exception(f"Erreur exécution renderer: {e}")
    
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
    def _get_cache_data_generic(user_id: str, panel_type: str):
        """Fonction cache générique basée sur la configuration JSON"""
        config = UsersCacheService._load_panel_config()
        panel_config = config.get(panel_type, {})
        
        cache_key_prefix = panel_config.get('cache_key_prefix', panel_type)
        cache_key = f"{cache_key_prefix}:{user_id}"
        
        # Vérifier cache local seulement (Redis removed)
        if (cache_key in UsersCacheService._local_cache and 
            UsersCacheService._is_local_cache_valid(cache_key)):
            return UsersCacheService._local_cache[cache_key]
        
        return None
    
    @staticmethod
    def _set_cache_data_generic(user_id: str, panel_type: str, data: dict, ttl_seconds: int):
        """Stocke les données dans le cache local"""
        config = UsersCacheService._load_panel_config()
        panel_config = config.get(panel_type, {})
        
        cache_key_prefix = panel_config.get('cache_key_prefix', panel_type)
        cache_key = f"{cache_key_prefix}:{user_id}"
        
        # Stocker en cache local seulement (Redis removed)
        UsersCacheService._local_cache[cache_key] = data
        UsersCacheService._cache_timestamps[cache_key] = time.time()
        UsersCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def get_user_profile_panel(selected_uid: str):
        """Cache HTML → Cache local → API REST pour panneau profil - utilise la nouvelle config JSON"""
        config = UsersCacheService._load_panel_config()
        panel_config = config.get('profile', {})
        return UsersCacheService._get_cached_panel_generic(selected_uid, panel_config)
    
    @staticmethod
    def get_user_profile_panel_legacy(selected_uid: str):
        """Version legacy - Cache HTML → API REST pour panneau profil"""
        if not selected_uid:
            print("[PROFILE] UID vide, retour panneau vide")
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'profile')
        if cached_panel:
            print(f"[PROFILE][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis cache removed - skip to API REST calls
        data = None
        
        # API REST
        if not data:
            try:
                print(f"[PROFILE][API FETCH] Chargement {selected_uid[:8]}... via API REST")
                # Import direct depuis data_schema_rest
                from dash_apps.utils.data_schema_rest import get_user_profile
                print(f"[PROFILE] Utilisation de l'API REST pour {selected_uid[:8]}")
                data = get_user_profile(selected_uid)
                
                if not data:
                    print(f"[PROFILE][ERROR] Aucune donnée trouvée pour {selected_uid}")
                    return html.Div(dbc.Alert(f"Utilisateur {selected_uid[:8]}... introuvable", color="warning"))
                
                print(f"[PROFILE][API SUCCESS] Données récupérées pour {selected_uid[:8]}, type: {type(data)}")
                
                # Redis cache removed - data only stored in local cache via HTML panel caching
            except Exception as e:
                print(f"[PROFILE][API ERROR] Erreur récupération: {e}")
                return html.Div(dbc.Alert(f"Erreur lors du chargement des données: {e}", color="danger"))
        
        # Render
        try:
            print(f"[PROFILE][RENDER] Rendu panneau pour {selected_uid[:8]}, data type: {type(data)}")
            from dash_apps.components.user_profile import render_user_profile
            panel = render_user_profile(data)
            print(f"[PROFILE][RENDER SUCCESS] Panneau généré pour {selected_uid[:8]}")
            
            # Mise en cache du panneau HTML
            UsersCacheService.set_cached_panel(selected_uid, 'profile', panel)
            print(f"[HTML CACHE] Panneau profile mis en cache pour {selected_uid[:8]}...")
            return panel
        except Exception as e:
            print(f"[PROFILE][RENDER ERROR] Erreur génération panneau: {e}")
            return html.Div(dbc.Alert(f"Erreur d'affichage du profil: {e}", color="danger"))
    
    @staticmethod
    def get_user_stats_panel(selected_uid: str):
        """Cache HTML → Cache local → API REST pour panneau stats - utilise la nouvelle config JSON"""
        config = UsersCacheService._load_panel_config()
        panel_config = config.get('stats', {})
        return UsersCacheService._get_cached_panel_generic(selected_uid, panel_config)
    
    @staticmethod
    def get_user_stats_panel_legacy(selected_uid: str):
        """Version legacy - Cache HTML → API REST pour panneau stats"""
        if not selected_uid:
            print("[STATS] UID vide, retour panneau vide")
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'stats')
        if cached_panel:
            print(f"[STATS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis cache removed - skip to API REST calls
        data = None
        
        # API
        if not data:
            try:
                print(f"[USER_DETAILS][API FETCH] Chargement {selected_uid[:8]}... via API REST")
                # Import direct depuis data_schema_rest
                from dash_apps.utils.data_schema_rest import get_user_stats_optimized
                print(f"[STATS] Utilisation de l'API REST pour {selected_uid[:8]}")
                stats = get_user_stats_optimized(selected_uid)
                
                if stats is None:
                    print(f"[STATS][ERROR] Aucune statistique trouvée pour {selected_uid}")
                    return html.Div(html.P("Aucune statistique disponible pour cet utilisateur"))
                
                data = {'uid': selected_uid, 'stats': stats}
                print(f"[STATS][DB SUCCESS] Stats récupérées pour {selected_uid[:8]}")
                
                # Redis cache removed - data only stored in local cache via HTML panel caching
            except Exception as e:
                print(f"[STATS][API ERROR] Erreur récupération stats: {e}")
                return html.Div(dbc.Alert(f"Erreur lors du chargement des statistiques: {e}", color="warning"))
        
        # Render
        try:
            print(f"[STATS][RENDER] Rendu panneau stats pour {selected_uid[:8]}")
            from dash_apps.components.user_stats import render_user_stats
            panel = render_user_stats(data)
            UsersCacheService.set_cached_panel(selected_uid, 'stats', panel)
            print(f"[HTML CACHE] Panneau stats mis en cache pour {selected_uid[:8]}...")
            return panel
        except Exception as e:
            print(f"[STATS][RENDER ERROR] Erreur génération panneau stats: {e}")
            return html.Div(dbc.Alert(f"Erreur d'affichage des statistiques: {e}", color="warning"))
    
    @staticmethod
    def get_user_trips_panel(selected_uid: str):
        """Cache HTML → Cache local → API REST pour panneau trips - utilise la nouvelle config JSON"""
        print(f"[TRIPS_SERVICE_DEBUG] === DÉBUT get_user_trips_panel ===")
        print(f"[TRIPS_SERVICE_DEBUG] selected_uid: {selected_uid}")
        
        config = UsersCacheService._load_panel_config()
        panel_config = config.get('trips', {})
        
        print(f"[TRIPS_SERVICE_DEBUG] Config chargée: {len(config)} panneaux")
        print(f"[TRIPS_SERVICE_DEBUG] Panel config trips: {panel_config}")
        
        result = UsersCacheService._get_cached_panel_generic(selected_uid, panel_config)
        
        print(f"[TRIPS_SERVICE_DEBUG] Résultat _get_cached_panel_generic: {type(result)}")
        print(f"[TRIPS_SERVICE_DEBUG] === FIN get_user_trips_panel ===")
        
        return result
    
    @staticmethod
    def get_user_trips_panel_legacy(selected_uid: str):
        """Version legacy - Cache HTML → API REST pour panneau trips"""
        if not selected_uid:
            print("[TRIPS] UID vide, retour panneau vide")
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'trips')
        if cached_panel:
            print(f"[TRIPS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis cache removed - skip to API REST calls
        data = None
        
        # API REST
        if not data:
            try:
                print(f"[TRIPS][API FETCH] Chargement {selected_uid[:8]}... via API REST")
                # Import direct depuis data_schema_rest
                from dash_apps.utils.data_schema_rest import get_user_trips_with_role
                print(f"[TRIPS] Utilisation de l'API REST pour {selected_uid[:8]}")
                trips_df = get_user_trips_with_role(str(selected_uid), limit=50)
                
                if trips_df is None or (isinstance(trips_df, pd.DataFrame) and trips_df.empty):
                    print(f"[TRIPS][EMPTY] Aucun trajet trouvé pour {selected_uid}")
                    return html.Div(html.P("Aucun trajet disponible pour cet utilisateur"))
                
                data = {'uid': selected_uid, 'trips': trips_df}
                print(f"[TRIPS][DB SUCCESS] {len(trips_df) if isinstance(trips_df, pd.DataFrame) else 'N/A'} trajets récupérés pour {selected_uid[:8]}")
                
                # Redis cache removed - data only stored in local cache via HTML panel caching
            except Exception as e:
                print(f"[TRIPS][API ERROR] Erreur récupération trajets: {e}")
                return html.Div(dbc.Alert(f"Erreur lors du chargement des trajets: {e}", color="warning"))
        
        # Render
        try:
            print(f"[TRIPS][RENDER] Rendu panneau trajets pour {selected_uid[:8]}")
            from dash_apps.components.user_trips import render_user_trips
            panel = render_user_trips(data)
            UsersCacheService.set_cached_panel(selected_uid, 'trips', panel)
            print(f"[HTML CACHE] Panneau trips mis en cache pour {selected_uid[:8]}...")
            return panel
        except Exception as e:
            print(f"[TRIPS][RENDER ERROR] Erreur génération panneau trajets: {e}")
            return html.Div(dbc.Alert(f"Erreur d'affichage des trajets: {e}", color="warning"))
    
    @staticmethod
    def get_cached_panel(user_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Récupère un panneau HTML en cache avec gestion intelligente
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            
        Returns:
            html.Div: Panneau en cache ou None si non trouvé
        """
        cache_key = f"{user_id}_{panel_type}"
        
        # Vérifier d'abord le cache HTML local
        if cache_key in UsersCacheService._html_cache:
            return UsersCacheService._html_cache[cache_key]
        
        # Redis cache removed - only use local HTML cache
        
        return None
    
    @staticmethod
    def set_cached_panel(user_id: str, panel_type: str, panel_html: html.Div):
        """
        Met en cache un panneau HTML généré avec TTL
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            panel_html: Panneau HTML à mettre en cache
        """
        cache_key = f"{user_id}_{panel_type}"
        
        # Cache local immédiat
        UsersCacheService._html_cache[cache_key] = panel_html
        
        # Limiter la taille du cache HTML local (LRU simple)
        if len(UsersCacheService._html_cache) > 100:  # Max 100 panneaux en mémoire
            # Supprimer les plus anciens (approximation simple)
            oldest_keys = list(UsersCacheService._html_cache.keys())[:20]
            for old_key in oldest_keys:
                del UsersCacheService._html_cache[old_key]
        
        if UsersCacheService._debug_mode:
            print(f"[HTML CACHE] Panneau {panel_type} mis en cache pour {user_id[:8]}...")
    
    @staticmethod
    def get_panel(panel_type: str, user_id: str) -> Optional[html.Div]:
        """
        Méthode générique pour récupérer un panneau utilisateur
        
        Args:
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            user_id: ID de l'utilisateur
            
        Returns:
            html.Div: Le panneau demandé
        """
        return UsersCacheService.get_user_panel(user_id, panel_type)
    
    @staticmethod
    def get_user_panel(user_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Méthode centralisée pour récupérer un panneau utilisateur (profile, stats, trips)
        Cette méthode redirige vers la méthode spécifique correspondant au type demandé
        
        Args:
            user_id: ID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            
        Returns:
            html.Div: Le panneau demandé
        """
        if not user_id or not panel_type:
            return html.Div()
            
        if panel_type == 'profile':
            return UsersCacheService.get_user_profile_panel(user_id)
        elif panel_type == 'stats':
            return UsersCacheService.get_user_stats_panel(user_id)
        elif panel_type == 'trips':
            return UsersCacheService.get_user_trips_panel(user_id)
        else:
            # Type de panneau inconnu
            return html.Div()
    
    @staticmethod
    def _preload_single_user(user_id: str, panel_types: List[str]):
        """
        Précharge les panneaux pour un utilisateur spécifique (fonction interne pour threading)
        
        Args:
            user_id: UID de l'utilisateur
            panel_types: Types de panneaux à précharger
        """
        try:
            # Récupérer les données utilisateur une seule fois
            # Précharger chaque panneau via get_user_panel (Read-Through cohérent)
            for panel_type in panel_types:
                cache_key = f"{user_id}_{panel_type}"
                if cache_key not in UsersCacheService._html_cache:
                    # Utiliser la méthode Read-Through pour cohérence
                    UsersCacheService.get_user_panel(user_id, panel_type)
            
            if UsersCacheService._debug_mode:
                print(f"[PRELOAD] Panneaux préchargés pour {user_id[:8]}")
        except Exception as e:
            if UsersCacheService._debug_mode:
                print(f"[PRELOAD] Erreur préchargement {user_id[:8]}: {e}")
                
    @staticmethod
    def preload_user_panels(user_ids: List[str], panel_types: List[str] = None, async_mode: bool = True):
        """
        Précharge les panneaux pour plusieurs utilisateurs en arrière-plan
        
        Args:
            user_ids: Liste des UIDs utilisateurs
            panel_types: Types de panneaux à précharger (défaut: tous)
            async_mode: Si True, utilise threading pour préchargement asynchrone
        """
        if not panel_types:
            panel_types = ['profile', 'stats', 'trips']
        
        # Filtrer les utilisateurs qui ont déjà tous leurs panneaux en cache
        users_to_preload = []
        for user_id in user_ids[:8]:  # Limiter à 8 utilisateurs pour éviter la surcharge
            needs_preload = False
            for panel_type in panel_types:
                cache_key = f"{user_id}_{panel_type}"
                if cache_key not in UsersCacheService._html_cache:
                    needs_preload = True
                    break
            if needs_preload:
                users_to_preload.append(user_id)
        
        if not users_to_preload:
            if UsersCacheService._debug_mode:
                print("[PRELOAD] Tous les panneaux sont déjà en cache")
            return
        
        if UsersCacheService._debug_mode:
            print(f"[PRELOAD] Préchargement de {len(users_to_preload)} utilisateurs x {len(panel_types)} panneaux...")
        
        if async_mode and len(users_to_preload) > 1:
            # Préchargement asynchrone avec threading
            threads = []
            for user_id in users_to_preload:
                thread = threading.Thread(
                    target=UsersCacheService._preload_single_user,
                    args=(user_id, panel_types),
                    daemon=True  # Thread daemon pour ne pas bloquer l'arrêt de l'app
                )
                threads.append(thread)
                thread.start()
            
            # Optionnel : attendre un court délai pour les premiers threads
            for thread in threads[:3]:  # Attendre seulement les 3 premiers
                thread.join(timeout=0.1)  # Timeout très court pour ne pas bloquer
                
        else:
            # Préchargement synchrone pour un seul utilisateur ou si async désactivé
            for user_id in users_to_preload:
                UsersCacheService._preload_single_user(user_id, panel_types)
    
    @staticmethod
    def clear_user_cache(user_id: str):
        """
        Efface le cache HTML pour un utilisateur spécifique
        
        Args:
            user_id: UID de l'utilisateur
        """
        keys_to_remove = [key for key in UsersCacheService._html_cache.keys() 
                         if key.startswith(f"{user_id}_")]
        for key in keys_to_remove:
            del UsersCacheService._html_cache[key]
        if UsersCacheService._debug_mode:
            print(f"[HTML CACHE] Cache effacé pour utilisateur {user_id[:8]}...")
    
    @staticmethod
    def clear_all_html_cache():
        """Efface tout le cache HTML"""
        UsersCacheService._html_cache.clear()
        if UsersCacheService._debug_mode:
            print("[HTML CACHE] Tout le cache HTML effacé")
    
    @staticmethod
    def get_cache_stats() -> Dict:
        """Retourne des statistiques détaillées sur le cache"""
        return {
            "local_cache_size": len(UsersCacheService._local_cache),
            "html_cache_size": len(UsersCacheService._html_cache),
            "cache_timestamps_size": len(UsersCacheService._cache_timestamps),
            "local_cache_ttl": UsersCacheService._local_cache_ttl,
            "redis_removed": "Redis cache removed - using local cache + REST API only"
        }
