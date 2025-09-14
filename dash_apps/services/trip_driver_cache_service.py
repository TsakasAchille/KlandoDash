"""
Service de cache spécialisé pour les informations conducteur avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
"""
import json
import os
from typing import Dict, Any, Optional
from dash_apps.utils.driver_display_formatter import DriverDisplayFormatter
from dash_apps.infrastructure.repositories.supabase_driver_repository import SupabaseDriverRepository
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.validation_utils import validate_data
from dash_apps.models.config_models import TripDriverDataModel

class TripDriverCache:
    """Service de cache pour les informations conducteur avec configuration JSON"""
    
    _config_cache = None
    
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
    def _get_cache_key(trip_id: str) -> str:
        """Génère la clé de cache - utilise directement l'ID avec préfixe fixe"""
        return f"trip_driver:{trip_id}"
    
    @staticmethod
    def _set_cache_data_generic(trip_id: str, data_type: str, data, ttl_seconds: int):
        """Fonction cache générique pour stocker les données conducteur"""
        from dash_apps.services.local_cache import local_cache as cache
        method_name = f"set_trip_{data_type}"
        if hasattr(cache, method_name):
            return getattr(cache, method_name)(trip_id, data, ttl_seconds)
        return None
    
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
            from dash_apps.utils.callback_logger import CallbackLogger
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Fetching driver data from API with Pydantic validation"
                )
            
            # 1. Récupérer les données conducteur via le repository
            repository = SupabaseDriverRepository()
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Calling repository.get_by_trip_id"
                )
            
            # Gérer l'appel asynchrone selon le contexte
            import asyncio
            try:
                # Si on est déjà dans une boucle asyncio, utiliser await
                loop = asyncio.get_running_loop()
                # On est dans une boucle, créer une tâche
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, repository.get_by_trip_id(trip_id))
                    driver_data = future.result()
            except RuntimeError:
                # Pas de boucle en cours, utiliser asyncio.run normalement
                driver_data = asyncio.run(repository.get_by_trip_id(trip_id))
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "driver_data_received": driver_data is not None,
                        "data_type": type(driver_data).__name__ if driver_data else "None",
                        "data_keys": list(driver_data.keys()) if isinstance(driver_data, dict) else "N/A"
                    },
                    status="INFO",
                    extra_info="Repository response received"
                )
            
            if not driver_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_driver",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="WARNING",
                        extra_info="No driver data returned from repository"
                    )
                return None
            
            # 2. Ajouter trip_id aux données pour la validation
            driver_data['trip_id'] = trip_id
            
            # 3. Validation Pydantic
            try:
                validation_result = validate_data(TripDriverDataModel, driver_data)
                if not validation_result or not validation_result.success:
                    if debug_trips:
                        error_msg = validation_result.get_error_summary() if hasattr(validation_result, 'get_error_summary') else "Validation failed"
                        CallbackLogger.log_callback(
                            "api_get_trip_driver",
                            {
                                "trip_id": trip_id[:8] if trip_id else 'None',
                                "validation_error": error_msg
                            },
                            status="ERROR",
                            extra_info="Pydantic validation failed for driver data"
                        )
                    return None
            
                # 4. Formater pour l'affichage
                if hasattr(validation_result.data, 'model_dump'):
                    validated_data = validation_result.data.model_dump()
                else:
                    validated_data = dict(validation_result.data) if validation_result.data else driver_data
                    
            except Exception as validation_error:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_driver",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "validation_exception": str(validation_error)
                        },
                        status="ERROR",
                        extra_info="Exception during Pydantic validation - using raw data"
                    )
                # Utiliser les données brutes si la validation échoue
                validated_data = driver_data
            
            formatter = DriverDisplayFormatter()
            driver_data = formatter.format_for_display(validated_data)
            
            if driver_data and isinstance(driver_data, dict):
                # 5. Mettre en cache les données formatées avec TTL fixe
                cache_ttl = 300  # 5 minutes
                
                TripDriverCache._set_cache_data_generic(trip_id, 'driver', driver_data, cache_ttl)
                
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_driver",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "driver_found": bool(driver_data.get('name') or driver_data.get('uid')),
                            "fields_count": len(driver_data)
                        },
                        status="SUCCESS",
                        extra_info="Driver data retrieved, validated and cached from API"
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
                import traceback
                CallbackLogger.log_callback(
                    "api_get_trip_driver",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "error_message": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    },
                    status="ERROR",
                    extra_info="Exception in _fetch_driver_data_from_api"
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
            
            TripDriverCache._set_cache_data_generic(trip_id, 'driver', data, ttl)
            
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
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        # Vérification simple : si pas de trip_id, retourner None directement
        if not trip_id:
            return None
        
        # 1. Vérifier le cache d'abord
        cached_data = TripDriverCache._get_cached_data(trip_id)
        if cached_data:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_driver_data",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "cache_hit": True},
                    status="SUCCESS",
                    extra_info="Cache HIT - driver data retrieved from cache"
                )
            return cached_data
        
        # 2. Si pas en cache, récupérer depuis l'API
        api_data = TripDriverCache._fetch_driver_data_from_api(trip_id)
        if api_data:
            # 3. Mettre en cache pour les prochaines fois
            TripDriverCache._cache_data(trip_id, api_data)
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_driver_data",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "cache_hit": False},
                    status="SUCCESS",
                    extra_info="Cache MISS - driver data retrieved from API"
                )
            return api_data
        
        return None
