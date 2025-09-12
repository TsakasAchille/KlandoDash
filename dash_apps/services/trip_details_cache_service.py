"""
Service de cache spécialisé pour les détails de trajet avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
"""
import json
import os
from typing import Dict, Any, Optional
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.config import Config
from dash_apps.services.local_cache import local_cache as cache


class TripDetailsCache:
    """Service de cache pour les détails de trajet avec configuration JSON"""
    
    _config_cache = None
    _debug_mode = True
    _pending_requests = {}  # Track ongoing API requests to prevent duplicates
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration JSON pour les détails de trajet (validation différée)"""
        if TripDetailsCache._config_cache is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'trip_details_config.json'
            )
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    TripDetailsCache._config_cache = json.load(f)
                
                # Vérifier si le debug des trajets est activé
                import os
                debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
                
                from dash_apps.utils.callback_logger import CallbackLogger
                if debug_trips:
                    CallbackLogger.log_callback(
                        "load_trip_config",
                        {"config_path": os.path.basename(config_path)},
                        status="SUCCESS",
                        extra_info="Trip details configuration loaded"
                    )
                    
            except Exception as e:
                # Vérifier si le debug des trajets est activé
                import os
                debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
                
                from dash_apps.utils.callback_logger import CallbackLogger
                if debug_trips:
                    CallbackLogger.log_callback(
                        "load_trip_config",
                        {"config_path": os.path.basename(config_path), "error": str(e)},
                        status="ERROR",
                        extra_info="Configuration loading failed"
                    )
                TripDetailsCache._config_cache = {}
        
        return TripDetailsCache._config_cache.get('trip_details', {})
    
    @staticmethod
    def _validate_inputs(trip_id: str) -> Optional[str]:
        """Valide les inputs selon la configuration JSON"""
        config = TripDetailsCache._load_config()
        validation = config.get('validation', {})
        
        if not trip_id:
            return "ERROR: trip_id requis"
        
        # Validation du trip_id
        trip_id_rules = validation.get('trip_id', {})
        if 'min_length' in trip_id_rules and len(trip_id) < trip_id_rules['min_length']:
            return f"ERROR: trip_id trop court (min {trip_id_rules['min_length']})"
        
        if 'pattern' in trip_id_rules:
            import re
            if not re.match(trip_id_rules['pattern'], trip_id):
                return f"ERROR: trip_id ne respecte pas le pattern {trip_id_rules['pattern']}"
        
        return None  # Validation OK
    
    @staticmethod
    def _get_cache_key(trip_id: str) -> str:
        """Génère la clé de cache selon la configuration"""
        config = TripDetailsCache._load_config()
        cache_config = config.get('cache', {})
        prefix = cache_config.get('key_prefix', 'trip_details')
        return f"{prefix}:{trip_id}"
    
    @staticmethod
    def _get_cached_data(trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = TripDetailsCache._get_cache_key(trip_id)
            cached_data = cache.get('trip_details', key=cache_key)
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            
            if cached_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_details",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": True,
                            "cache_key": cache_key
                        },
                        status="SUCCESS",
                        extra_info="Cache HIT - data retrieved from cache"
                    )
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_details",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": False,
                            "cache_key": cache_key
                        },
                        status="INFO",
                        extra_info="Cache MISS - no data in cache"
                    )
            
            return cached_data
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_get_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "error": str(e)
                    },
                    status="ERROR",
                    extra_info="Cache get operation failed"
                )
            return None
    
    @staticmethod
    def _set_cache_data(trip_id: str, data: Dict[str, Any]) -> None:
        """Met en cache les données selon la configuration"""
        try:
            config = TripDetailsCache._load_config()
            cache_config = config.get('cache', {})
            
            if not cache_config.get('enabled', True):
                return
            
            cache_key = TripDetailsCache._get_cache_key(trip_id)
            ttl = cache_config.get('ttl_seconds', 300)
            
            cache.set('trip_details', data, ttl=ttl, key=cache_key)
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "ttl_seconds": ttl,
                        "cache_key": cache_key
                    },
                    status="SUCCESS",
                    extra_info="Trip details cached successfully"
                )
        
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "error": str(e)
                    },
                    status="ERROR",
                    extra_info="Cache set operation failed"
                )
    
    @staticmethod
    def get_trip_details_data(trip_id: str) -> Dict[str, Any]:
        """
        Récupère les données de trajet avec cache et validation
        Implémente la déduplication pour éviter les appels API simultanés
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            Dict contenant les données validées du trajet
        """
        from dash_apps.utils.callback_logger import CallbackLogger
        import time
        import threading
        
        # 1. Valider les entrées
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if not trip_id:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_details_data",
                    {"error": "trip_id is empty or None"},
                    status="ERROR",
                    extra_info="Invalid trip_id provided"
                )
            return {}
        
        # 2. Vérifier le cache
        cached_data = TripDetailsCache._get_cached_data(trip_id)
        if cached_data:
            # Le log de cache hit est déjà fait dans _get_cached_data
            return cached_data
        
        # 3. Vérifier si une requête est déjà en cours pour ce trip_id
        if trip_id in TripDetailsCache._pending_requests:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_details_data",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "source": "pending",
                        "cache_hit": False
                    },
                    status="INFO",
                    extra_info="Request already pending - waiting for completion"
                )
            
            # Attendre que la requête en cours se termine (max 5 secondes)
            start_time = time.time()
            while trip_id in TripDetailsCache._pending_requests and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            # Vérifier le cache après l'attente
            cached_data = TripDetailsCache._get_cached_data(trip_id)
            if cached_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "get_trip_details_data",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "source": "cache_after_wait",
                            "cache_hit": True
                        },
                        status="SUCCESS",
                        extra_info="Data retrieved from cache after waiting for pending request"
                    )
                return cached_data
        
        # 4. Marquer la requête comme en cours
        TripDetailsCache._pending_requests[trip_id] = time.time()
        
        try:
            # 5. Cache miss - récupérer depuis l'API REST
            # Le log de cache miss est déjà fait dans _get_cached_data
            
            from dash_apps.utils.data_schema_rest import get_trip_details_configured
            data = get_trip_details_configured(trip_id)
            
            # 6. Les données sont déjà validées dans get_trip_details_configured()
            # Pas besoin de validation supplémentaire ici
            
            # 7. Mettre en cache les données validées
            TripDetailsCache._set_cache_data(trip_id, data)
            
            # 8. Retourner les données validées
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_details_data",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "source": "api",
                        "data_retrieved": data is not None
                    },
                    status="SUCCESS" if data else "WARNING",
                    extra_info="API data retrieved and cached" if data else "No data returned from API"
                )
            
            return data
            
        finally:
            # 9. Nettoyer la requête en cours
            if trip_id in TripDetailsCache._pending_requests:
                del TripDetailsCache._pending_requests[trip_id]
