"""
User Stats Cache Service

This service calculates and caches user statistics from Supabase,
including passenger trips, driver trips, and total distance traveled.
"""

import os
from typing import Dict, Any, Optional
from dash_apps.services.local_cache import local_cache
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.supabase_client import supabase


class UserStatsCache:
    """Cache service for user statistics with database queries"""
    
    # Cache configuration
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX = "user_stats"
    
    @classmethod
    def _get_cache_kwargs(cls, user_id: str) -> dict:
        """Generate cache kwargs for user stats"""
        return {"user_id": user_id}
    
    @classmethod
    def _debug_log(cls, operation: str, data: Dict[str, Any], level: str = "INFO", message: str = ""):
        """Debug logging utility"""
        debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_users:
            CallbackLogger.log_callback(
                f"user_stats_cache_{operation}",
                data,
                status=level,
                extra_info=message
            )
    
    @classmethod
    def _calculate_user_stats(cls, user_id: str) -> Dict[str, Any]:
        """Calculate user statistics from Supabase"""
        cls._debug_log(
            "calculate_start",
            {"user_id": str(user_id)[:8] if user_id else None},
            "INFO",
            "Starting user stats calculation from Supabase"
        )
        
        try:
            # Query passenger trips (bookings where user is passenger)
            passenger_bookings_response = supabase.table('bookings').select('trip_id').eq('user_id', user_id).execute()
            passenger_bookings = passenger_bookings_response.data if passenger_bookings_response.data else []
            passenger_trips_count = len(passenger_bookings)
            
            # Query driver trips (trips where user is driver)
            driver_trips_response = supabase.table('trips').select('trip_id, distance').eq('driver_id', user_id).execute()
            driver_trips = driver_trips_response.data if driver_trips_response.data else []
            driver_trips_count = len(driver_trips)
            
            # Calculate driver distance
            driver_distance = 0.0
            for trip in driver_trips:
                if trip.get('distance') and isinstance(trip['distance'], (int, float)):
                    driver_distance += float(trip['distance'])
            
            # Calculate passenger distance
            passenger_distance = 0.0
            if passenger_bookings:
                # Get trip_ids from bookings
                trip_ids = [booking.get('trip_id') for booking in passenger_bookings if booking.get('trip_id')]
                
                if trip_ids:
                    # Query trips for passenger bookings to get distances
                    passenger_trips_response = supabase.table('trips').select('distance').in_('trip_id', trip_ids).execute()
                    passenger_trips = passenger_trips_response.data if passenger_trips_response.data else []
                    
                    for trip in passenger_trips:
                        if trip.get('distance') and isinstance(trip['distance'], (int, float)):
                            passenger_distance += float(trip['distance'])
            
            # Total distance and trips
            total_distance = driver_distance + passenger_distance
            total_trips = passenger_trips_count + driver_trips_count
            
            stats = {
                "passenger_trips": int(passenger_trips_count),
                "driver_trips": int(driver_trips_count),
                "total_trips": int(total_trips),
                "total_distance": round(total_distance, 2),
                "driver_distance": round(driver_distance, 2),
                "passenger_distance": round(passenger_distance, 2)
            }
            
            cls._debug_log(
                "calculate_success",
                {
                    "user_id": str(user_id)[:8] if user_id else None,
                    "stats": stats
                },
                "SUCCESS",
                "User stats calculated successfully from Supabase"
            )
            
            return stats
                
        except Exception as e:
            cls._debug_log(
                "calculate_error",
                {
                    "user_id": str(user_id)[:8] if user_id else None,
                    "error": str(e)
                },
                "ERROR",
                "Failed to calculate user stats from Supabase"
            )
            # Return default stats on error
            return {
                "passenger_trips": 0,
                "driver_trips": 0,
                "total_trips": 0,
                "total_distance": 0.0,
                "driver_distance": 0.0,
                "passenger_distance": 0.0
            }
    
    @classmethod
    def get_user_stats(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user statistics with caching
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            Dictionary containing user statistics or None if error
        """
        if not user_id:
            cls._debug_log(
                "get_stats_invalid_id",
                {"user_id": None},
                "WARNING",
                "Invalid user ID provided"
            )
            return None
        
        cache_kwargs = cls._get_cache_kwargs(user_id)
        
        # Try to get from cache first
        cached_stats = local_cache.get(cls.CACHE_PREFIX, **cache_kwargs)
        if cached_stats is not None:
            cls._debug_log(
                "get_stats_cache_hit",
                {"user_id": str(user_id)[:8], "cache_kwargs": cache_kwargs},
                "INFO",
                "User stats found in cache"
            )
            return cached_stats
        
        # Calculate stats from database
        cls._debug_log(
            "get_stats_cache_miss",
            {"user_id": str(user_id)[:8], "cache_kwargs": cache_kwargs},
            "INFO",
            "User stats not in cache, calculating from database"
        )
        
        stats = cls._calculate_user_stats(user_id)
        
        # Cache the results
        local_cache.set(cls.CACHE_PREFIX, stats, ttl=cls.CACHE_TTL, **cache_kwargs)
        
        cls._debug_log(
            "get_stats_cached",
            {
                "user_id": str(user_id)[:8],
                "cache_kwargs": cache_kwargs,
                "ttl": cls.CACHE_TTL
            },
            "SUCCESS",
            "User stats calculated and cached"
        )
        
        return stats
    
    @classmethod
    def invalidate_user_stats(cls, user_id: str) -> bool:
        """
        Invalidate cached user statistics
        
        Args:
            user_id: User ID to invalidate cache for
            
        Returns:
            True if cache was invalidated successfully
        """
        if not user_id:
            return False
        
        cache_kwargs = cls._get_cache_kwargs(user_id)
        result = local_cache.delete(cls.CACHE_PREFIX, **cache_kwargs)
        
        cls._debug_log(
            "invalidate_cache",
            {
                "user_id": str(user_id)[:8],
                "cache_kwargs": cache_kwargs,
                "result": result
            },
            "INFO",
            "User stats cache invalidated"
        )
        
        return result
    
    @classmethod
    def clear_all_stats_cache(cls) -> int:
        """
        Clear all user stats from cache
        
        Returns:
            Number of cache entries cleared
        """
        cleared_count = local_cache.clear_cache_type(cls.CACHE_PREFIX)
        
        cls._debug_log(
            "clear_all_cache",
            {"cache_type": cls.CACHE_PREFIX, "cleared_count": cleared_count},
            "INFO",
            "All user stats cache cleared"
        )
        
        return cleared_count
