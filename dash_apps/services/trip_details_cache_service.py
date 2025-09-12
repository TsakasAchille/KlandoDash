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
        """Charge la configuration JSON pour les détails de trajet avec validation Supabase"""
        if TripDetailsCache._config_cache is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'trip_details_config.json'
            )
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    TripDetailsCache._config_cache = json.load(f)
                
                # Validation automatique contre le schéma avec Pydantic
                from dash_apps.services.config_validator import ConfigValidator
                validation_result = ConfigValidator.validate_config_file(config_path)
                
                if not validation_result.success:
                    print(f"[TRIP_DETAILS_CONFIG] ⚠️  ERREURS DE VALIDATION DÉTECTÉES:")
                    for error in validation_result.errors:
                        print(f"  - {error}")
                    print(f"[TRIP_DETAILS_CONFIG] Utilisation de la configuration malgré les erreurs")
                else:
                    if TripDetailsCache._debug_mode:
                        print(f"[TRIP_DETAILS_CONFIG] ✅ Configuration validée contre le schéma")
                
                if TripDetailsCache._debug_mode:
                    print(f"[TRIP_DETAILS_CONFIG] Configuration chargée depuis {config_path}")
                    
            except Exception as e:
                print(f"[TRIP_DETAILS_CONFIG] Erreur chargement config: {e}")
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
            
            if cached_data and TripDetailsCache._debug_mode:
                print(f"[TRIP_DETAILS_CACHE][HIT] Données récupérées pour {trip_id[:8] if trip_id else 'None'}")
            
            return cached_data
        except Exception as e:
            if TripDetailsCache._debug_mode:
                print(f"[TRIP_DETAILS_CACHE][ERROR] Erreur lecture cache: {e}")
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
            
            if TripDetailsCache._debug_mode:
                print(f"[TRIP_DETAILS_CACHE][SET] Données mises en cache pour {trip_id[:8] if trip_id else 'None'} (TTL: {ttl}s)")
        
        except Exception as e:
            if TripDetailsCache._debug_mode:
                print(f"[TRIP_DETAILS_CACHE][ERROR] Erreur mise en cache: {e}")
    
    @staticmethod
    def get_trip_details_data(trip_id: str) -> Dict[str, Any]:
        """
        Point d'entrée principal pour récupérer les données de trajet.
        Implémente le flux: Cache → JSON Config → DB/API → Cache → Return Data
        Retourne None en cas d'erreur ou données invalides.
        """
        # 1. Validation des inputs selon JSON
        validation_error = TripDetailsCache._validate_inputs(trip_id)
        if validation_error:
            return None
        
        # 2. Vérifier le cache
        cached_data = TripDetailsCache._get_cached_data(trip_id)
        if cached_data:
            return cached_data
        
        # 3. Récupérer depuis l'API REST avec validation
        from dash_apps.utils.data_schema_rest import get_trip_details_configured
        data = get_trip_details_configured(trip_id)
        
        # 4. Mettre en cache (même si data est None ou vide)
        TripDetailsCache._set_cache_data(trip_id, data)
        
        # 5. Retourner les données (peut être None si validation Pydantic échoue)
        return data
