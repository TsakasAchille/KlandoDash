"""
Service pour gérer les données des passagers avec validation Pydantic et cache.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from dash_apps.models.config_models import (
    BookingModel, BookingsQueryResult, UserModel, 
    PassengerInfo, PassengersQueryResult, BookingsJsonQuery, UsersJsonQuery
)
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.utils.callback_logger import CallbackLogger
import os


class PassengersService:
    """Service pour gérer les données des passagers."""
    
    CACHE_TTL = 300  # 5 minutes
    
    @classmethod
    def _get_cache_key(cls, trip_id: str) -> str:
        """Génère une clé de cache pour un trajet."""
        return f"passengers:trip:{trip_id}"
    
    @classmethod
    def _log_debug(cls, message: str, extra_data: Dict[str, Any] = None):
        """Log de debug si activé."""
        debug_enabled = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        if debug_enabled:
            CallbackLogger.log_callback(
                "PassengersService",
                extra_data or {},
                status="DEBUG",
                extra_info=message
            )
    
    @classmethod
    def _query_bookings_for_trip(cls, trip_id: str) -> BookingsQueryResult:
        """Récupère les réservations pour un trajet avec l'API Supabase native."""
        try:
            cls._log_debug(f"Querying bookings for trip: {trip_id}")
            
            # Charger la configuration JSON
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('passengers_queries.json')
            
            if not config or 'queries' not in config:
                cls._log_debug("Configuration passengers_queries.json manquante")
                return BookingsQueryResult()
            
            # Récupérer les champs depuis la configuration JSON
            query_config = config.get('queries', {}).get('bookings_by_trip', {})
            json_fields = query_config.get('select', {}).get('base', [])
            
            # Construire la clause select
            select_clause = ', '.join(json_fields)
            cls._log_debug(f"Using fields from JSON config: {select_clause}")
            
            # Utiliser l'API Supabase directement comme les autres panels
            from dash_apps.utils.supabase_client import supabase
            
            # Exécuter la requête native Supabase avec les champs du JSON
            response = supabase.table('bookings').select(select_clause).eq('trip_id', trip_id).execute()
            
            cls._log_debug(f"Supabase response: {len(response.data) if response.data else 0} bookings")
            
            if not response.data:
                cls._log_debug("No bookings found in Supabase response")
                return BookingsQueryResult()
            
            # Récupérer les mappings depuis la configuration
            field_mappings = config.get('field_mappings', {})
            status_mappings = config.get('status_mappings', {})
            
            # Valider et transformer avec Pydantic
            validated_bookings = []
            for booking_data in response.data:
                try:
                    # Adapter les données pour le modèle Pydantic en utilisant les mappings
                    booking_dict = {
                        'id': booking_data.get('id'),
                        'trip_id': booking_data.get('trip_id'),
                        'user_id': booking_data.get('user_id'),
                        'seats': booking_data.get('seats', 1),
                        'status': booking_data.get('status', ''),  # Sera mappé par Pydantic
                        'created_at': booking_data.get('created_at')
                    }
                    booking = BookingModel(**booking_dict)
                    validated_bookings.append(booking)
                    cls._log_debug(f"Validated booking {booking.id} with status {booking.status}")
                except Exception as e:
                    cls._log_debug(f"Invalid booking data: {e}", {"booking_data": booking_data})
                    continue
            
            # Créer le résultat
            result = BookingsQueryResult(bookings=validated_bookings)
            cls._log_debug(f"Validated {len(result.bookings)} bookings, {result.total_seats} seats")
            
            return result
            
        except Exception as e:
            cls._log_debug(f"Error querying bookings: {e}")
            return BookingsQueryResult()
    
    @classmethod
    def _query_users_by_ids(cls, user_ids: List[str]) -> Dict[str, UserModel]:
        """Récupère les informations utilisateurs par IDs avec configuration JSON."""
        if not user_ids:
            return {}
        
        try:
            cls._log_debug(f"Querying users for IDs: {user_ids}")
            
            # Charger la configuration JSON pour les champs utilisateur
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('passengers_queries.json')
            
            # Récupérer les champs depuis la configuration JSON
            query_config = config.get('queries', {}).get('users_by_ids', {})
            json_fields = query_config.get('select', {}).get('base', [])
            select_clause = ', '.join(json_fields)
            
            cls._log_debug(f"Using user fields from JSON config: {select_clause}")
            
            # Utiliser l'API Supabase directement
            from dash_apps.utils.supabase_client import supabase
            validated_users = {}
            
            # Récupérer les utilisateurs un par un (Supabase REST ne supporte pas IN directement)
            for user_id in user_ids:
                try:
                    response = supabase.table("users").select(select_clause).eq("uid", user_id).execute()
                    if response.data:
                        user_data = response.data[0]
                        cls._log_debug(f"Found user data for {user_id}: {user_data.get('display_name', 'No name')}")
                        
                        # Adapter les données pour le modèle Pydantic
                        user_dict = {
                            'uid': user_data.get('uid'),
                            'display_name': user_data.get('display_name', ''),
                            'email': user_data.get('email', ''),
                            'phone_number': user_data.get('phone_number', ''),
                            'rating': user_data.get('rating', 0.0),
                            'photo_url': user_data.get('photo_url', ''),
                            'created_at': user_data.get('created_at')
                        }
                        user = UserModel(**user_dict)
                        validated_users[user.uid] = user
                        cls._log_debug(f"Validated user {user.uid}: {user.display_name}")
                    else:
                        cls._log_debug(f"No user data found for {user_id}")
                except Exception as e:
                    cls._log_debug(f"Error fetching user {user_id}: {e}")
                    continue
            
            cls._log_debug(f"Found {len(validated_users)} users out of {len(user_ids)} requested")
            return validated_users
            
        except Exception as e:
            cls._log_debug(f"Error querying users: {e}")
            return {}
    
    @classmethod
    def _combine_bookings_and_users(cls, bookings_result: BookingsQueryResult, 
                                   users: Dict[str, UserModel]) -> PassengersQueryResult:
        """Combine les réservations et les données utilisateurs."""
        passengers = []
        
        for booking in bookings_result.bookings:
            user = users.get(booking.user_id)
            if user:
                passenger_info = PassengerInfo(
                    user=user,
                    seats_booked=booking.seats,
                    booking_status=booking.status,
                    booking_id=booking.id,
                    booking_created_at=booking.created_at
                )
                passengers.append(passenger_info)
            else:
                cls._log_debug(f"User not found for booking: {booking.id}", 
                             {"user_id": booking.user_id})
        
        return PassengersQueryResult(
            passengers=passengers,
            trip_id=bookings_result.bookings[0].trip_id if bookings_result.bookings else None
        )
    
    @classmethod
    def get_trip_passengers(cls, trip_id: str) -> PassengersQueryResult:
        """Récupère les passagers d'un trajet avec cache."""
        if not trip_id:
            return PassengersQueryResult()
        
        cache_key = cls._get_cache_key(trip_id)
        
        # Essayer de récupérer depuis le cache
        try:
            cached_data = redis_cache.get(cache_key)
            if cached_data:
                cls._log_debug(f"Cache hit for trip: {trip_id}")
                return PassengersQueryResult(**json.loads(cached_data))
        except Exception as e:
            cls._log_debug(f"Cache error: {e}")
        
        # Cache miss - récupérer les données
        cls._log_debug(f"Cache miss for trip: {trip_id}")
        
        # 1. Récupérer les réservations
        bookings_result = cls._query_bookings_for_trip(trip_id)
        
        if not bookings_result.bookings:
            cls._log_debug(f"No bookings found for trip: {trip_id}")
            empty_result = PassengersQueryResult(trip_id=trip_id)
            # Mettre en cache le résultat vide
            try:
                redis_cache.setex(cache_key, cls.CACHE_TTL, empty_result.json())
            except Exception as e:
                cls._log_debug(f"Cache set error: {e}")
            return empty_result
        
        # 2. Récupérer les informations utilisateurs
        users = cls._query_users_by_ids(bookings_result.user_ids)
        
        # 3. Combiner les données
        result = cls._combine_bookings_and_users(bookings_result, users)
        
        # 4. Mettre en cache
        try:
            redis_cache.setex(cache_key, cls.CACHE_TTL, result.json())
            cls._log_debug(f"Cached passengers data for trip: {trip_id}")
        except Exception as e:
            cls._log_debug(f"Cache set error: {e}")
        
        return result
    
    @classmethod
    def invalidate_cache(cls, trip_id: str):
        """Invalide le cache pour un trajet."""
        cache_key = cls._get_cache_key(trip_id)
        try:
            redis_cache.delete(cache_key)
            cls._log_debug(f"Cache invalidated for trip: {trip_id}")
        except Exception as e:
            cls._log_debug(f"Cache invalidation error: {e}")
    
    @classmethod
    def get_passengers_summary(cls, trip_id: str) -> Dict[str, Any]:
        """Récupère un résumé des passagers pour affichage."""
        passengers_result = cls.get_trip_passengers(trip_id)
        
        if not passengers_result.passengers:
            return {
                "message": "Aucun passager pour ce trajet",
                "total_passengers": 0,
                "total_seats": 0,
                "passengers_list": []
            }
        
        passengers_list = []
        for passenger in passengers_result.passengers:
            passengers_list.append({
                "name": passenger.passenger_display_name,
                "seats": passenger.seats_text,
                "status": passenger.booking_status,
                "phone": passenger.user.phone_number or "Non renseigné",
                "rating": passenger.user.rating_display,
                "photo_url": passenger.user.photo_url
            })
        
        return {
            "message": f"{passengers_result.total_passengers} passager(s) - {passengers_result.total_seats} place(s)",
            "total_passengers": passengers_result.total_passengers,
            "total_seats": passengers_result.total_seats,
            "passengers_list": passengers_list
        }
