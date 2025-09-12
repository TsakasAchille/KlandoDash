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
                
                from dash_apps.utils.callback_logger import CallbackLogger
                CallbackLogger.log_callback(
                    "load_trip_config",
                    {"config_path": os.path.basename(config_path)},
                    status="SUCCESS",
                    extra_info="Trip details configuration loaded"
                )
                    
            except Exception as e:
                from dash_apps.utils.callback_logger import CallbackLogger
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
            
            if cached_data:
                from dash_apps.utils.callback_logger import CallbackLogger
                CallbackLogger.log_callback(
                    "cache_get_trip_details",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "cache_hit": True
                    },
                    status="SUCCESS",
                    extra_info="Cache hit - data retrieved"
                )
            
            return cached_data
        except Exception as e:
            from dash_apps.utils.callback_logger import CallbackLogger
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
            
            from dash_apps.utils.callback_logger import CallbackLogger
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
        Point d'entrée principal pour récupérer les données de trajet.
        Implémente le flux: Cache → DB/API → Validation → Cache → Return Data
        Validation unique à la fin pour éviter la double validation.
        """
        # 1. Validation des inputs selon JSON
        validation_error = TripDetailsCache._validate_inputs(trip_id)
        if validation_error:
            return None
        
        # 2. Vérifier le cache (sans validation)
        cached_data = TripDetailsCache._get_cached_data(trip_id)
        if cached_data:
            return cached_data
        
        # 3. Récupérer depuis l'API REST
        from dash_apps.utils.data_schema_rest import get_trip_details_configured
        data = get_trip_details_configured(trip_id)
        
        # 4. Les données sont déjà validées dans get_trip_details_configured()
        # Pas besoin de validation supplémentaire ici
        
        # 5. Mettre en cache les données validées
        TripDetailsCache._set_cache_data(trip_id, data)
        
        # 6. Retourner les données validées
        return data
