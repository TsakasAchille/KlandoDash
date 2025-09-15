"""
Service spécialisé pour les trajets d'un utilisateur avec cache et validation Pydantic.
Suit le pattern de passengers_service.py
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.models.config_models import TripDataModel
from dash_apps.services.redis_cache import redis_cache


class UserTripsService:
    """Service pour récupérer les trajets d'un utilisateur avec cache optimisé."""
    
    # Configuration du cache
    CACHE_TTL = 300  # 5 minutes
    LOCAL_CACHE_TTL = 60  # 1 minute pour le cache local
    MAX_LOCAL_CACHE_SIZE = 30
    
    # Cache local en mémoire
    _local_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}
    
    @classmethod
    def _log_debug(cls, message: str, extra_data: Dict[str, Any] = None):
        """Log de debug avec CallbackLogger si DEBUG_USERS est activé."""
        debug_enabled = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_enabled:
            CallbackLogger.log_callback(
                "UserTripsService",
                extra_data or {},
                status="DEBUG",
                extra_info=message
            )
    
    @classmethod
    def _get_cache_key(cls, uid: str, trip_type: str = "all") -> str:
        """Génère une clé de cache pour les trajets d'un utilisateur."""
        return f"user_trips:{uid}:{trip_type}"
    
    @classmethod
    def _get_from_local_cache(cls, cache_key: str) -> Optional[Dict]:
        """Récupère les données depuis le cache local avec TTL."""
        if cache_key in cls._local_cache:
            timestamp = cls._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < cls.LOCAL_CACHE_TTL:
                cls._log_debug(f"Local cache hit for key: {cache_key}")
                return cls._local_cache[cache_key]
            else:
                # Nettoyer l'entrée expirée
                cls._local_cache.pop(cache_key, None)
                cls._cache_timestamps.pop(cache_key, None)
        return None
    
    @classmethod
    def _set_to_local_cache(cls, cache_key: str, data: Dict):
        """Stocke les données dans le cache local avec gestion de la taille."""
        # Nettoyer le cache si trop plein
        if len(cls._local_cache) >= cls.MAX_LOCAL_CACHE_SIZE:
            # Supprimer les 5 entrées les plus anciennes
            sorted_keys = sorted(cls._cache_timestamps.items(), key=lambda x: x[1])
            for old_key, _ in sorted_keys[:5]:
                cls._local_cache.pop(old_key, None)
                cls._cache_timestamps.pop(old_key, None)
        
        cls._local_cache[cache_key] = data
        cls._cache_timestamps[cache_key] = time.time()
        cls._log_debug(f"Stored in local cache: {cache_key}")
    
    @classmethod
    def get_user_trips(cls, uid: str, trip_type: str = "all", limit: int = 10) -> Dict[str, Any]:
        """
        Récupère les trajets d'un utilisateur avec cache multi-niveau.
        
        Args:
            uid: UID de l'utilisateur
            trip_type: Type de trajets ("driver", "passenger", "all")
            limit: Nombre maximum de trajets à retourner
        """
        if not uid:
            return {"trips": [], "total_count": 0, "trip_type": trip_type}
        
        cache_key = cls._get_cache_key(uid, trip_type)
        
        # 1. Vérifier le cache local
        local_data = cls._get_from_local_cache(cache_key)
        if local_data:
            return local_data
        
        # 2. Vérifier le cache Redis
        try:
            cached_data = redis_cache.get(cache_key)
            if cached_data:
                cls._log_debug(f"Redis cache hit for user trips {uid[:8]}")
                data = json.loads(cached_data)
                cls._set_to_local_cache(cache_key, data)
                return data
        except Exception as e:
            cls._log_debug(f"Redis cache error: {e}")
        
        # 3. Cache miss - récupérer depuis Supabase
        cls._log_debug(f"Cache miss for user trips {uid[:8]}")
        
        try:
            data = cls._fetch_user_trips_from_supabase(uid, trip_type, limit)
            
            # 4. Mettre en cache
            try:
                redis_cache.setex(cache_key, cls.CACHE_TTL, json.dumps(data))
                cls._log_debug(f"Cached user trips for {uid[:8]} in Redis")
            except Exception as e:
                cls._log_debug(f"Redis cache set error: {e}")
            
            cls._set_to_local_cache(cache_key, data)
            
            return data
            
        except Exception as e:
            cls._log_debug(f"Error fetching user trips: {e}")
            return {"trips": [], "total_count": 0, "trip_type": trip_type}
    
    @classmethod
    def _fetch_user_trips_from_supabase(cls, uid: str, trip_type: str, limit: int) -> Dict[str, Any]:
        """Récupère les trajets depuis Supabase avec l'API native."""
        try:
            # Charger la configuration JSON
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('user_trips_queries.json')
            
            if not config or 'queries' not in config:
                cls._log_debug("Configuration user_trips_queries.json manquante")
                # Configuration par défaut
                config = {
                    "queries": {
                        "user_trips": {
                            "select": {
                                "base": [
                                    "trip_id", "departure_city", "arrival_city", 
                                    "departure_date", "departure_time", "price",
                                    "seats_published", "seats_available", "driver_uid",
                                    "created_at", "status"
                                ]
                            }
                        }
                    }
                }
            
            # Récupérer les champs depuis la configuration
            query_config = config.get('queries', {}).get('user_trips', {})
            json_fields = query_config.get('select', {}).get('base', [])
            select_clause = ', '.join(json_fields)
            
            cls._log_debug(f"Using fields from JSON config: {select_clause}")
            
            # Utiliser l'API Supabase directement
            from dash_apps.utils.supabase_client import supabase
            
            all_trips = []
            
            # Construire la requête selon le type de trajets
            if trip_type == "driver":
                # Trajets où l'utilisateur est conducteur
                query = supabase.table('trips').select(select_clause).eq('driver_id', uid)
                response = query.order('departure_date', desc=True).limit(limit).execute()
                all_trips = response.data or []
                
            elif trip_type == "passenger":
                # Trajets où l'utilisateur est passager (via bookings)
                # 1. Récupérer les trip_ids des bookings de l'utilisateur
                bookings_response = supabase.table('bookings').select('trip_id').eq('user_id', uid).execute()
                booking_trip_ids = [b['trip_id'] for b in (bookings_response.data or [])]
                
                if booking_trip_ids:
                    # 2. Récupérer les détails des trajets
                    query = supabase.table('trips').select(select_clause).in_('trip_id', booking_trip_ids)
                    response = query.order('departure_date', desc=True).limit(limit).execute()
                    all_trips = response.data or []
                
            else:
                # Tous les trajets (driver + passenger)
                # 1. Trajets conducteur
                driver_query = supabase.table('trips').select(select_clause).eq('driver_id', uid)
                driver_response = driver_query.order('departure_date', desc=True).limit(limit).execute()
                driver_trips = driver_response.data or []
                
                # 2. Trajets passager
                bookings_response = supabase.table('bookings').select('trip_id').eq('user_id', uid).execute()
                booking_trip_ids = [b['trip_id'] for b in (bookings_response.data or [])]
                
                passenger_trips = []
                if booking_trip_ids:
                    passenger_query = supabase.table('trips').select(select_clause).in_('trip_id', booking_trip_ids)
                    passenger_response = passenger_query.order('departure_date', desc=True).limit(limit).execute()
                    passenger_trips = passenger_response.data or []
                
                # 3. Combiner et dédupliquer
                all_trips_dict = {}
                for trip in driver_trips + passenger_trips:
                    trip_id = trip.get('trip_id')
                    if trip_id:
                        all_trips_dict[trip_id] = trip
                
                all_trips = list(all_trips_dict.values())
                # Trier par date de départ (plus récent en premier) - gérer les valeurs None
                all_trips.sort(key=lambda x: x.get('departure_date') or '1900-01-01', reverse=True)
                all_trips = all_trips[:limit]
            
            cls._log_debug(f"Supabase response: {len(all_trips)} trips")
            
            # Valider et transformer avec Pydantic
            validated_trips = []
            for trip_data in all_trips:
                try:
                    trip = TripDataModel(**trip_data)
                    
                    # Utiliser model_dump() comme dans le pattern trips
                    if hasattr(trip, 'model_dump'):
                        # Pydantic v2
                        trip_dict = trip.model_dump()
                    elif hasattr(trip, 'dict'):
                        # Pydantic v1
                        trip_dict = trip.dict()
                    else:
                        # Fallback
                        trip_dict = dict(trip_data)
                    
                    # Enrichir avec des informations calculées
                    enriched_trip = {
                        **trip_dict,
                        "is_driver": trip_dict.get("driver_id") == uid,
                        "is_passenger": trip_dict.get("driver_id") != uid,
                        "departure_datetime": f"{trip_dict.get('departure_date')} {trip_dict.get('departure_schedule')}",
                        "route": f"{trip_dict.get('departure_name')} → {trip_dict.get('destination_name')}",
                        "seats_info": f"{trip_dict.get('seats_available', 0)}/{trip_dict.get('seats_published', 0)} places"
                    }
                    
                    validated_trips.append(enriched_trip)
                    
                except Exception as e:
                    cls._log_debug(f"Invalid trip data: {e}", {"trip_data": trip_data})
                    continue
            
            result = {
                "trips": validated_trips,
                "total_count": len(validated_trips),
                "trip_type": trip_type,
                "user_uid": uid
            }
            
            cls._log_debug(f"Found {len(validated_trips)} trips for user {uid[:8]}")
            
            return result
            
        except Exception as e:
            cls._log_debug(f"Error fetching from Supabase: {e}")
            raise
    
    @classmethod
    def invalidate_cache(cls, uid: str):
        """Invalide le cache pour un utilisateur spécifique."""
        try:
            # Invalider tous les types de trajets pour cet utilisateur
            for trip_type in ["all", "driver", "passenger"]:
                cache_key = cls._get_cache_key(uid, trip_type)
                cls._local_cache.pop(cache_key, None)
                cls._cache_timestamps.pop(cache_key, None)
            
            cls._log_debug(f"Cache invalidated for user: {uid[:8]}")
            
        except Exception as e:
            cls._log_debug(f"Cache invalidation error: {e}")
    
    @classmethod
    def refresh_cache(cls):
        """Force le rafraîchissement du cache."""
        cls._local_cache.clear()
        cls._cache_timestamps.clear()
        cls._log_debug("User trips cache refreshed")
