"""Service de cache spécialisé pour les détails de trajet avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
"""
import json
import os
from typing import Dict, Any, Optional
from dash_apps.utils.callback_logger import CallbackLogger


class TripDetailsCache:
    """Service de cache pour les détails de trajet avec configuration JSON"""
    
    _config_cache = None
    
    
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
        """Génère la clé de cache - utilise directement l'ID avec préfixe fixe"""
        return f"trip_details:{trip_id}"
    
    @staticmethod
    def _get_cached_data(trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            cache_key = TripDetailsCache._get_cache_key(trip_id)
            cached_data = cache.get('trip_details', key=cache_key)
            
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
        from dash_apps.services.local_cache import local_cache as cache
        
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            cache_key = TripDetailsCache._get_cache_key(trip_id)
            ttl = 300  # 5 minutes
            
            cache.set('trip_details', data, ttl=ttl, key=cache_key)
            
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
            from dash_apps.utils.callback_logger import CallbackLogger
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Cache set operation failed"
                )
    
    @staticmethod
    def _fetch_details_data_from_api(trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données détails depuis l'API REST avec validation"""
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Fetching details data from API"
                )
            
            # 1. Récupérer les données conducteur via le repository
            from dash_apps.infrastructure.repositories.supabase_trip_repository import SupabaseTripRepository
            repository = SupabaseTripRepository()
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Calling repository.get_by_trip_id"
                )
            
            # Gérer l'appel asynchrone selon le contexte
            import asyncio
            try:
                # Essayer d'utiliser la boucle existante
                loop = asyncio.get_running_loop()
                # Si on est dans une boucle, créer une tâche
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, repository.get_by_trip_id(trip_id))
                    data = future.result()
            except RuntimeError:
                # Pas de boucle en cours, utiliser asyncio.run directement
                data = asyncio.run(repository.get_by_trip_id(trip_id))
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "data_received": data is not None,
                        "data_type": type(data).__name__ if data else "None"
                    },
                    status="INFO",
                    extra_info="API response received"
                )
            
            if not data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_details",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="WARNING",
                        extra_info="No details data returned from repository"
                    )
                return None
            
            # Afficher les données brutes de la DB
            if debug_trips:
                CallbackLogger.log_data_dict(
                    f"Données brutes DB - Trip {trip_id[:8]}",
                    data
                )
            
            # 2. Validation avec Pydantic
            from dash_apps.models.config_models import TripDataModel
            from dash_apps.utils.validation_utils import validate_data
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Starting Pydantic validation"
                )
            
            # Valider les données avec le modèle Pydantic
            validation_result = validate_data(TripDataModel, data)
            
            if not validation_result.success:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "validation_error",
                        {"trip_id": trip_id[:8] if trip_id else 'None', "errors": validation_result.get_error_summary()},
                        status="ERROR",
                        extra_info="Échec de la validation Pydantic"
                    )
                return None
            
            # Utiliser les données validées (convertir le modèle Pydantic en dict)
            validated_data = validation_result.data
            if hasattr(validated_data, 'model_dump'):
                # Pydantic v2
                validated_data_dict = validated_data.model_dump()
            elif hasattr(validated_data, 'dict'):
                # Pydantic v1
                validated_data_dict = validated_data.dict()
            else:
                # Fallback si ce n'est pas un modèle Pydantic
                validated_data_dict = dict(validated_data)
            
            if debug_trips:
                CallbackLogger.log_data_dict(
                    f"Données après validation Pydantic - Trip {trip_id[:8]}",
                    validated_data_dict
                )
                
                CallbackLogger.log_callback(
                    "validation_success",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="SUCCESS",
                    extra_info="Validation Pydantic réussie"
                )
            
            # 3. Formater les données pour l'affichage
            from dash_apps.utils.trip_details_formatter import TripDetailsFormatter
            formatter = TripDetailsFormatter()
            formatted_data = formatter.format_for_display(validated_data_dict)
            
            # Afficher les données après transformation
            if debug_trips:
                CallbackLogger.log_data_dict(
                    f"Données après transformation Formatter - Trip {trip_id[:8]}",
                    formatted_data
                )
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "formatter_debug",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "formatted_data_type": type(formatted_data).__name__,
                        "formatted_data_bool": bool(formatted_data),
                        "is_dict": isinstance(formatted_data, dict),
                        "fields_count": len(formatted_data) if formatted_data else 0
                    },
                    status="INFO",
                    extra_info="Debug formatter output"
                )
            
            if formatted_data and isinstance(formatted_data, dict):
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_details",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "details_found": bool(formatted_data),
                            "fields_count": len(formatted_data)
                        },
                        status="SUCCESS",
                        extra_info="Details data retrieved and formatted from API"
                    )
                
                return formatted_data
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="WARNING",
                    extra_info="No details data found or formatting failed"
                )
            return None
            
        except Exception as e:
            if debug_trips:
                import traceback
                CallbackLogger.log_callback(
                    "api_get_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "error_message": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    },
                    status="ERROR",
                    extra_info="Exception in _fetch_details_data_from_api"
                )
            return None
    
    @staticmethod
    def _cache_data(trip_id: str, data: Dict[str, Any]) -> None:
        """Met en cache les données détails"""
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            cache_key = TripDetailsCache._get_cache_key(trip_id)
            config = TripDetailsCache._load_config()
            cache_config = config.get('cache', {})
            ttl = cache_config.get('ttl', 300)  # 5 minutes par défaut
            
            TripDetailsCache._set_cache_data(trip_id, data)
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "cache_key": cache_key,
                        "ttl": ttl
                    },
                    status="SUCCESS",
                    extra_info="Details data cached successfully"
                )
                
        except Exception as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_details",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error caching details data"
                )
    
    @staticmethod
    def get_trip_details_data(trip_id: str) -> Dict[str, Any]:
        """
        Point d'entrée principal pour récupérer les données détails d'un trajet.
        Implémente le pattern: Cache → API → Cache
        """
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        # Vérification simple : si pas de trip_id, retourner dict vide
        if not trip_id:
            return {}
        
        # 1. Vérifier le cache d'abord
        cached_data = TripDetailsCache._get_cached_data(trip_id)
        if cached_data:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_details_data",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "cache_hit": True},
                    status="SUCCESS",
                    extra_info="Cache HIT - details data retrieved from cache"
                )
            return cached_data
        
        # 2. Si pas en cache, récupérer depuis l'API
        api_data = TripDetailsCache._fetch_details_data_from_api(trip_id)
        if api_data:
            # 3. Mettre en cache pour les prochaines fois
            TripDetailsCache._cache_data(trip_id, api_data)
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_details_data",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "cache_hit": False},
                    status="SUCCESS",
                    extra_info="Cache MISS - details data retrieved from API"
                )
            return api_data
        
        return {}
