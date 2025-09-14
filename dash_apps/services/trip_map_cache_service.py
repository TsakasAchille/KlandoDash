"""
Service de cache pour les données de carte des trajets.
Gère la récupération, validation et mise en cache des données de polyline et route.
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.validation_utils import validate_data
from dash_apps.models.config_models import TripDataModel, TripMapDataModel
from dash_apps.utils.settings import load_json_config


class TripMapCache:
    """Service de cache pour les données de carte des trajets"""
    
    def __init__(self):
        self.config = load_json_config('trip_map_config.json')
        self.cache_config = self.config.get('trip_map', {}).get('cache', {})
        self.cache_enabled = self.cache_config.get('enabled', True)
        self.cache_ttl = self.cache_config.get('ttl_seconds', 600)
        self.key_prefix = self.cache_config.get('key_prefix', 'trip_map')
        
    def get_trip_map_data(self, trip_id: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Récupère les données de carte pour un trajet avec cache
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            Tuple[données_carte, cache_hit]
        """
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "get_trip_map_data_start",
                {"trip_id": trip_id, "cache_enabled": self.cache_enabled},
                status="INFO",
                extra_info="Starting map data retrieval"
            )
        
        # Vérifier le cache en premier
        if self.cache_enabled:
            cached_data = self._get_cached_data(trip_id)
            if cached_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "get_trip_map_data",
                        {"trip_id": trip_id, "cache_hit": True},
                        status="SUCCESS",
                        extra_info="Cache HIT - map data retrieved from cache"
                    )
                return cached_data, True
        
        # Cache miss - récupérer depuis l'API
        map_data = self._fetch_map_data_from_api(trip_id)
        
        if map_data:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_map_data",
                    {"trip_id": trip_id, "cache_hit": False},
                    status="SUCCESS", 
                    extra_info="Cache MISS - map data retrieved from API"
                )
            return map_data, False
        else:
            if debug_trips:
                CallbackLogger.log_callback(
                    "get_trip_map_data",
                    {"trip_id": trip_id, "cache_hit": False},
                    status="ERROR",
                    extra_info="Failed to retrieve map data from API"
                )
            return None, False
    
    @staticmethod
    def _get_cache_key(trip_id: str) -> str:
        """Génère la clé de cache pour un trajet"""
        return f"trip_map_{trip_id}"
    
    def _get_cached_data(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = self._get_cache_key(trip_id)
            cached_data = cache.get('trip_map', key=cache_key)
            
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if cached_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_map",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": True,
                            "cache_key": cache_key
                        },
                        status="INFO",
                        extra_info="Cache HIT - map data retrieved from cache"
                    )
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "cache_get_trip_map",
                        {
                            "trip_id": trip_id[:8] if trip_id else 'None',
                            "cache_hit": False,
                            "cache_key": cache_key
                        },
                        status="INFO",
                        extra_info="Cache MISS - map data not in cache"
                    )
            
            return cached_data
            
        except Exception as e:
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_get_trip_map",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error retrieving map data from cache"
                )
            return None
    
    def _fetch_map_data_from_api(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données de carte depuis l'API avec validation
        """
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_map",
                    {"trip_id": trip_id},
                    status="INFO",
                    extra_info="Starting API call for map data"
                )
            
            # Récupérer les données du trajet depuis Supabase
            from dash_apps.infrastructure.repositories.supabase_trip_repository import SupabaseTripRepository
            trip_repository = SupabaseTripRepository()
            
            # Obtenir les données de base du trajet
            trip_data = trip_repository.get_by_id(trip_id)
            
            if not trip_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_map",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="ERROR",
                        extra_info="Trip not found in repository"
                    )
                return None
            
            # Extraire les coordonnées de départ et destination
            departure_coords = None
            destination_coords = None
            
            # Vérifier les champs de coordonnées possibles
            if hasattr(trip_data, 'departure_latitude') and hasattr(trip_data, 'departure_longitude'):
                departure_coords = [float(trip_data.departure_longitude), float(trip_data.departure_latitude)]
            elif 'departure_latitude' in trip_data and 'departure_longitude' in trip_data:
                departure_coords = [float(trip_data['departure_longitude']), float(trip_data['departure_latitude'])]
            
            if hasattr(trip_data, 'destination_latitude') and hasattr(trip_data, 'destination_longitude'):
                destination_coords = [float(trip_data.destination_longitude), float(trip_data.destination_latitude)]
            elif 'destination_latitude' in trip_data and 'destination_longitude' in trip_data:
                destination_coords = [float(trip_data['destination_longitude']), float(trip_data['destination_latitude'])]
            
            # Fallback vers des coordonnées par défaut si non disponibles
            if not departure_coords:
                departure_coords = [14.6937, -17.4441]  # Dakar par défaut
            if not destination_coords:
                destination_coords = [14.7167, -17.4667]  # Pikine par défaut
            
            # Récupérer la polyline depuis les données du trajet
            polyline_data = None
            route_points = [departure_coords, destination_coords]  # Fallback ligne droite
            
            # Extraire la polyline du trajet
            if hasattr(trip_data, 'polyline') and trip_data.polyline:
                polyline_data = trip_data.polyline
            elif isinstance(trip_data, dict) and trip_data.get('polyline'):
                polyline_data = trip_data.get('polyline')
            
            # Si polyline disponible, décoder les coordonnées
            if polyline_data:
                try:
                    import polyline as polyline_lib
                    
                    # Gérer le format bytes si nécessaire
                    if isinstance(polyline_data, bytes):
                        polyline_data = polyline_data.decode('utf-8')
                    
                    # Décoder la polyline : [(lat, lon), ...] -> [[lon, lat], ...]
                    coords_latlon = polyline_lib.decode(polyline_data)
                    route_points = [[lon, lat] for (lat, lon) in coords_latlon]
                    
                    if debug_trips:
                        CallbackLogger.log_callback(
                            "polyline_decoded",
                            {"trip_id": trip_id[:8], "points_count": len(route_points)},
                            status="SUCCESS",
                            extra_info="Polyline decoded successfully"
                        )
                        
                except Exception as e:
                    if debug_trips:
                        CallbackLogger.log_callback(
                            "polyline_decode_error",
                            {"trip_id": trip_id[:8], "error": str(e)},
                            status="ERROR",
                            extra_info="Failed to decode polyline, using fallback"
                        )
                    # Garder le fallback ligne droite
                    route_points = [departure_coords, destination_coords]
            
            # Construire les données de carte
            map_data = {
                "trip_id": trip_id,
                "polyline": polyline_data,  # Polyline encodée originale
                "departure_coords": departure_coords,
                "destination_coords": destination_coords,
                "distance_km": getattr(trip_data, 'distance', None) or trip_data.get('distance', 15.0),
                "estimated_duration": "00:25:00",  # Durée estimée par défaut
                "route_points": route_points  # Points décodés de la polyline ou ligne droite
            }
            
            # Validation Pydantic
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_map",
                    {"trip_id": trip_id},
                    status="INFO", 
                    extra_info="Starting Pydantic validation"
                )
            
            validated_data = validate_data(map_data, TripMapDataModel, strict=False)
            
            if validated_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "validation_success",
                        {"trip_id": trip_id},
                        status="SUCCESS",
                        extra_info="Validation Pydantic réussie"
                    )
                
                # Mettre en cache les données validées
                self._cache_data(trip_id, validated_data)
                
                if debug_trips:
                    CallbackLogger.log_callback(
                        "api_get_trip_map",
                        {"trip_id": trip_id, "map_found": True},
                        status="SUCCESS",
                        extra_info="Map data retrieved and validated from API"
                    )
                
                return validated_data
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "validation_failed",
                        {"trip_id": trip_id},
                        status="ERROR",
                        extra_info="Validation Pydantic échouée"
                    )
                return None
                
        except Exception as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "api_get_trip_map",
                    {"trip_id": trip_id, "error": str(e)},
                    status="ERROR",
                    extra_info="Error fetching map data from API"
                )
            return None
    
    def _cache_data(self, trip_id: str, data: Dict[str, Any]) -> None:
        """Met en cache les données de carte"""
        if not self.cache_enabled:
            return
            
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cache_key = self._get_cache_key(trip_id)
            
            # Utiliser la méthode set_trip_map du cache local
            method_name = "set_trip_map"
            if hasattr(cache, method_name):
                getattr(cache, method_name)(trip_id, data, self.cache_ttl)
            else:
                # Fallback vers la méthode générique
                cache.set('trip_map', key=cache_key, value=data, ttl_seconds=self.cache_ttl)
            
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_map",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "cache_key": cache_key, "ttl": self.cache_ttl},
                    status="SUCCESS",
                    extra_info="Map data cached successfully"
                )
                
        except Exception as e:
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            if debug_trips:
                CallbackLogger.log_callback(
                    "cache_set_trip_map",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error caching map data"
                )


# Instance globale du service
trip_map_cache = TripMapCache()
