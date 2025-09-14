"""
Service de cache optimisé pour les données de trajets de la page Map.
Récupère uniquement les champs nécessaires pour l'affichage des polylines.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.validation_utils import validate_data
from dash_apps.models.config_models import MapTripDataModel, MapDataCollectionModel
from dash_apps.utils.settings import load_json_config


class MapTripsCache:
    """Service de cache pour les données de trajets optimisées pour la carte"""
    
    def __init__(self):
        self.config = load_json_config('map_trips_config.json')
        self.cache_config = self.config.get('map_trips', {}).get('cache', {})
        self.cache_enabled = self.cache_config.get('enabled', True)
        self.cache_ttl = self.cache_config.get('ttl_seconds', 300)
        self.key_prefix = self.cache_config.get('key_prefix', 'map_trips')
        
    def get_map_trips_data(self, limit: int = 10) -> Tuple[Optional[List[Dict[str, Any]]], bool]:
        """
        Récupère les données de trajets optimisées pour la carte avec cache
        
        Args:
            limit: Nombre maximum de trajets à récupérer
            
        Returns:
            Tuple[données_trajets, cache_hit]
        """
        debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
        
        if debug_maps:
            CallbackLogger.log_callback(
                "get_map_trips_data_start",
                {"limit": limit, "cache_enabled": self.cache_enabled},
                status="INFO",
                extra_info="Starting map trips data retrieval"
            )
        
        # Vérifier le cache en premier
        if self.cache_enabled:
            cached_data = self._get_cached_data(limit)
            if cached_data:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "get_map_trips_data",
                        {"limit": limit, "cache_hit": True, "trips_count": len(cached_data)},
                        status="SUCCESS",
                        extra_info="Cache HIT - map trips data retrieved from cache"
                    )
                return cached_data, True
        
        # Cache miss - récupérer depuis l'API
        trips_data = self._fetch_map_trips_from_api(limit)
        
        if trips_data:
            if debug_maps:
                CallbackLogger.log_callback(
                    "get_map_trips_data",
                    {"limit": limit, "cache_hit": False, "trips_count": len(trips_data)},
                    status="SUCCESS", 
                    extra_info="Cache MISS - map trips data retrieved from API"
                )
            return trips_data, False
        else:
            if debug_maps:
                CallbackLogger.log_callback(
                    "get_map_trips_data",
                    {"limit": limit, "cache_hit": False},
                    status="ERROR",
                    extra_info="Failed to retrieve map trips data from API"
                )
            return None, False
    
    @staticmethod
    def _get_cache_key(limit: int) -> str:
        """Génère la clé de cache pour les trajets map"""
        return f"map_trips_limit_{limit}"
    
    def _get_cached_data(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = self._get_cache_key(limit)
            cached_data = cache.get('map_trips', key=cache_key)
            
            debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
            
            if cached_data:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "cache_get_map_trips",
                        {
                            "limit": limit,
                            "cache_hit": True,
                            "cache_key": cache_key,
                            "trips_count": len(cached_data) if isinstance(cached_data, list) else 0
                        },
                        status="INFO",
                        extra_info="Cache HIT - map trips data retrieved from cache"
                    )
            else:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "cache_get_map_trips",
                        {
                            "limit": limit,
                            "cache_hit": False,
                            "cache_key": cache_key
                        },
                        status="INFO",
                        extra_info="Cache MISS - map trips data not in cache"
                    )
            
            return cached_data
            
        except Exception as e:
            debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
            if debug_maps:
                CallbackLogger.log_callback(
                    "cache_get_map_trips",
                    {"limit": limit, "error": str(e)},
                    status="ERROR",
                    extra_info="Error retrieving map trips data from cache"
                )
            return None
    
    def _fetch_map_trips_from_api(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les données de trajets optimisées depuis l'API avec validation
        """
        debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
        
        try:
            if debug_maps:
                CallbackLogger.log_callback(
                    "api_get_map_trips",
                    {"limit": limit},
                    status="INFO",
                    extra_info="Starting API call for map trips data"
                )
            
            # Récupérer les trajets depuis Supabase avec requête optimisée
            from dash_apps.infrastructure.repositories.supabase_trip_repository import SupabaseTripRepository
            trip_repository = SupabaseTripRepository()
            
            # Requête optimisée : seulement les champs nécessaires pour la carte
            trips_data = trip_repository.get_trips_for_map(limit=limit)
            
            if not trips_data:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "api_get_map_trips",
                        {"limit": limit},
                        status="ERROR",
                        extra_info="No trips found in repository"
                    )
                return None
            
            # Valider et transformer chaque trajet
            validated_trips = []
            
            for trip_data in trips_data:
                try:
                    # Validation Pydantic directe
                    validated_trip = MapTripDataModel(**trip_data)
                    validated_trips.append(validated_trip.model_dump())
                    
                except Exception as validation_error:
                    if debug_maps:
                        CallbackLogger.log_callback(
                            "map_trip_validation_error",
                            {
                                "trip_id": trip_data.get('trip_id', 'Unknown')[:8],
                                "error": str(validation_error)
                            },
                            status="WARNING",
                            extra_info="Skipping invalid trip data"
                        )
                    # Continuer avec les autres trajets
                    continue
            
            if validated_trips:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "api_get_map_trips",
                        {
                            "limit": limit,
                            "trips_found": len(validated_trips),
                            "validation_success": True
                        },
                        status="SUCCESS",
                        extra_info="Map trips data retrieved and validated from API"
                    )
                
                # Mettre en cache les données validées
                self._cache_data(limit, validated_trips)
                
                return validated_trips
            else:
                if debug_maps:
                    CallbackLogger.log_callback(
                        "api_get_map_trips",
                        {"limit": limit},
                        status="ERROR",
                        extra_info="No valid trips after validation"
                    )
                return None
                
        except Exception as e:
            if debug_maps:
                CallbackLogger.log_callback(
                    "api_get_map_trips",
                    {"limit": limit, "error": str(e)},
                    status="ERROR",
                    extra_info="Error fetching map trips data from API"
                )
            return None
    
    def _cache_data(self, limit: int, data: List[Dict[str, Any]]) -> None:
        """Met en cache les données de trajets map"""
        if not self.cache_enabled:
            return
            
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cache_key = self._get_cache_key(limit)
            
            # Utiliser la méthode set du cache local
            cache.set('map_trips', key=cache_key, value=data, ttl_seconds=self.cache_ttl)
            
            debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
            if debug_maps:
                CallbackLogger.log_callback(
                    "cache_set_map_trips",
                    {
                        "limit": limit,
                        "cache_key": cache_key,
                        "trips_count": len(data),
                        "ttl": self.cache_ttl
                    },
                    status="SUCCESS",
                    extra_info="Map trips data cached successfully"
                )
                
        except Exception as e:
            debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
            if debug_maps:
                CallbackLogger.log_callback(
                    "cache_set_map_trips",
                    {"limit": limit, "error": str(e)},
                    status="ERROR",
                    extra_info="Error caching map trips data"
                )


# Instance globale du service
map_trips_cache = MapTripsCache()
