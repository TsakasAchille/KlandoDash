"""
Service de cache pour la page Map avec persistance des sélections
Utilise le système de cache local configuré via JSON
"""
import hashlib
import time
from typing import Optional, Dict, Any, List
from dash_apps.services.local_cache import local_cache as cache
from dash_apps.services.trips_cache_service import TripsCacheService


class MapCacheService:
    """Service de cache pour la page Map avec persistance des sélections"""
    
    @staticmethod
    def get_session_id() -> str:
        """Génère un ID de session basé sur l'heure actuelle (simple mais efficace)"""
        # Pour une vraie session, on pourrait utiliser flask.session ou un UUID
        # Ici on utilise un hash basé sur l'heure pour simuler une session
        current_hour = int(time.time() // 3600)  # Change chaque heure
        return hashlib.md5(f"map_session_{current_hour}".encode()).hexdigest()[:8]
    
    @staticmethod
    def save_selected_trips(selected_trip_ids: List[str]) -> bool:
        """Sauvegarde les trajets sélectionnés dans le cache avec persistance 24h"""
        try:
            session_id = MapCacheService.get_session_id()
            data = {
                'selected_trips': selected_trip_ids,
                'timestamp': time.time(),
                'count': len(selected_trip_ids)
            }
            return cache.set('map_selections', data, session_id=session_id, ttl=86400)  # 24h
        except Exception as e:
            print(f"[MAP_CACHE] Erreur sauvegarde sélections: {e}")
            return False
    
    @staticmethod
    def save_map_settings(trip_count: int) -> bool:
        """Sauvegarde les paramètres de la carte (nombre de trajets à afficher)"""
        try:
            session_id = MapCacheService.get_session_id()
            data = {
                'trip_count': trip_count,
                'timestamp': time.time()
            }
            return cache.set('map_settings', data, session_id=session_id, ttl=86400)  # 24h
        except Exception as e:
            print(f"[MAP_CACHE] Erreur sauvegarde paramètres: {e}")
            return False
    
    @staticmethod
    def load_map_settings() -> Dict[str, Any]:
        """Charge les paramètres de la carte depuis le cache"""
        try:
            session_id = MapCacheService.get_session_id()
            data = cache.get('map_settings', session_id=session_id)
            if data and isinstance(data, dict):
                return {
                    'trip_count': data.get('trip_count', 5),  # défaut: 5 trajets
                    'timestamp': data.get('timestamp', time.time())
                }
            return {'trip_count': 5, 'timestamp': time.time()}
        except Exception as e:
            print(f"[MAP_CACHE] Erreur chargement paramètres: {e}")
            return {'trip_count': 5, 'timestamp': time.time()}
    
    @staticmethod
    def load_selected_trips() -> List[str]:
        """Charge les trajets sélectionnés depuis le cache"""
        try:
            session_id = MapCacheService.get_session_id()
            data = cache.get('map_selections', session_id=session_id)
            if data and isinstance(data, dict):
                return data.get('selected_trips', [])
            return []
        except Exception as e:
            print(f"[MAP_CACHE] Erreur chargement sélections: {e}")
            return []
    
    @staticmethod
    def get_cached_trips(count: int) -> Optional[List]:
        """Récupère les derniers N trajets depuis le cache ou via TripsCacheService"""
        try:
            # Essayer d'abord le cache map spécifique
            cached_data = cache.get('map_trips_data', count=count)
            if cached_data and isinstance(cached_data, dict):
                trips = cached_data.get('trips', [])
                if len(trips) >= count:
                    return trips[:count]
            
            # Fallback: utiliser TripsCacheService
            result = TripsCacheService.get_trips_page_result(
                page_index=0, 
                page_size=count, 
                filter_params={}
            )
            trips = result.get("trips", [])
            
            # Mettre en cache pour les prochaines fois
            if trips:
                cache_data = {
                    'trips': trips,
                    'timestamp': time.time(),
                    'count': len(trips)
                }
                cache.set('map_trips_data', cache_data, count=count, ttl=300)  # 5min
            
            return trips
            
        except Exception as e:
            print(f"[MAP_CACHE] Erreur récupération trajets: {e}")
            return []
    
    @staticmethod
    def clear_selections() -> bool:
        """Vide les sélections en cache"""
        try:
            session_id = MapCacheService.get_session_id()
            return cache.delete('map_selections', session_id=session_id)
        except Exception as e:
            print(f"[MAP_CACHE] Erreur suppression sélections: {e}")
            return False
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Retourne les statistiques du cache pour la page map"""
        try:
            stats = cache.get_stats()
            map_stats = {
                'total_entries': stats.get('total_entries', 0),
                'hit_rate': stats.get('hit_rate', 0),
                'map_selections_count': stats.get('cache_types_count', {}).get('map_selections', 0),
                'map_trips_data_count': stats.get('cache_types_count', {}).get('map_trips_data', 0)
            }
            return map_stats
        except Exception as e:
            print(f"[MAP_CACHE] Erreur récupération stats: {e}")
            return {}
