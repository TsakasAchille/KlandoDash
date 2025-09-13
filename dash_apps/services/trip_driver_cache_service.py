"""
Service de cache spécialisé pour les informations conducteur avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
"""
import json
import os
from typing import Dict, Any, Optional
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.config import Config
from dash_apps.services.local_cache import local_cache as cache


class TripDriverCache:
    """Service de cache pour les informations conducteur avec configuration JSON"""
    
    _config_cache = None
    _debug_mode = True
    _pending_requests = {}  # Track ongoing API requests to prevent duplicates
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration JSON pour les informations conducteur (validation différée)"""
        if TripDriverCache._config_cache is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'trip_driver_config.json'
            )
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    TripDriverCache._config_cache = json.load(f)
                
                # Vérifier si le debug des trajets est activé
                debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
                
                from dash_apps.utils.callback_logger import CallbackLogger
                if debug_trips:
                    CallbackLogger.log_callback(
                        "load_driver_config",
                        {"config_path": os.path.basename(config_path)},
                        status="SUCCESS",
                        extra_info="Trip driver configuration loaded"
                    )
                    
            except Exception as e:
                # Vérifier si le debug des trajets est activé
                debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
                
                from dash_apps.utils.callback_logger import CallbackLogger
                if debug_trips:
                    CallbackLogger.log_callback(
                        "load_driver_config",
                        {"error": str(e)},
                        status="ERROR",
                        extra_info="Failed to load trip driver configuration"
                    )
                
                # Configuration par défaut
                TripDriverCache._config_cache = {
                    "cache": {
                        "key_prefix": "trip_driver",
                        "ttl": 300
                    },
                    "validation": {
                        "trip_id": {
                            "required": True,
                            "min_length": 5
                        }
                    }
                }
        
        return TripDriverCache._config_cache
    
    @staticmethod
    def _validate_trip_id(trip_id: str) -> Optional[str]:
        """Valide le trip_id selon la configuration"""
        if not trip_id:
            return "ERROR: trip_id requis"
        
        config = TripDriverCache._load_config()
        validation_config = config.get('validation', {})
        trip_id_rules = validation_config.get('trip_id', {})
        
        if trip_id_rules.get('required', True) and not trip_id:
            return "ERROR: trip_id requis"
        
        min_length = trip_id_rules.get('min_length', 0)
        if len(trip_id) < min_length:
            return f"ERROR: trip_id doit faire au moins {min_length} caractères"
        
        return None  # Validation OK
    
    @staticmethod
    def _get_cache_key(trip_id: str) -> str:
        """Génère la clé de cache selon la configuration"""
        config = TripDriverCache._load_config()
        cache_config = config.get('cache', {})
        prefix = cache_config.get('key_prefix', 'trip_driver')
        return f"{prefix}:{trip_id}"
    
    @staticmethod
    def _get_cached_data(trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = TripDriverCache._get_cache_key(trip_id)
            cached_data = cache.get('trip_driver', key=cache_key)
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            
            if cached_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_driver",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": True,
                            "cache_key": cache_key
                        },
                        status="SUCCESS",
                        extra_info="Cache HIT - driver data retrieved from cache"
                    )
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_driver",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": False,
                            "cache_key": cache_key
                        },
                        status="INFO",
                        extra_info="Cache MISS - driver data not in cache"
                    )
            
            return cached_data
            
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error retrieving driver data from cache"
                )
            return None
    
    @staticmethod
    def _fetch_driver_data_from_api(trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données conducteur depuis l'API REST avec validation Pydantic"""
        try:
            from dash_apps.utils.driver_data_rest import get_trip_driver_configured
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Fetching driver data from API with Pydantic validation"
                )
            
            # Récupérer les données conducteur configurées et validées
            driver_data = get_trip_driver_configured(trip_id)
            
            if driver_data and isinstance(driver_data, dict):
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_driver",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "driver_found": bool(driver_data.get('name') or driver_data.get('uid')),
                            "fields_count": len(driver_data)
                        },
                        status="SUCCESS",
                        extra_info="Driver data retrieved and validated from API"
                    )
                
                return driver_data
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="WARNING",
                    extra_info="No driver data found or validation failed"
                )
            return None
            
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error fetching driver data from API"
                )
            return None
    
    @staticmethod
    def _cache_data(trip_id: str, data: Dict[str, Any]) -> None:
        """Met en cache les données conducteur"""
        try:
            cache_key = TripDriverCache._get_cache_key(trip_id)
            config = TripDriverCache._load_config()
            cache_config = config.get('cache', {})
            ttl = cache_config.get('ttl', 300)  # 5 minutes par défaut
            
            cache.set('trip_driver', key=cache_key, value=data, ttl=ttl)
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_driver",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "cache_key": cache_key,
                        "ttl": ttl
                    },
                    status="SUCCESS",
                    extra_info="Driver data cached successfully"
                )
                
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error caching driver data"
                )
    
    @staticmethod
    def get_trip_driver_data(trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Point d'entrée principal pour récupérer les données conducteur d'un trajet.
        Implémente le pattern: Cache → API → Cache
        """
        # 1. Validation
        validation_error = TripDriverCache._validate_trip_id(trip_id)
        if validation_error:
            return None
        
        # 2. Vérifier le cache d'abord
        cached_data = TripDriverCache._get_cached_data(trip_id)
        if cached_data:
            return cached_data
        
        # 3. Si pas en cache, récupérer depuis l'API
        api_data = TripDriverCache._fetch_driver_data_from_api(trip_id)
        if api_data:
            # 4. Mettre en cache pour les prochaines fois
            TripDriverCache._cache_data(trip_id, api_data)
            return api_data
        
        return None
