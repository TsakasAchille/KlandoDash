"""
Service de cache Redis avec TTL pour optimiser les performances
"""
import redis
import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import timedelta
import os
from dash_apps.config import Config


class RedisCache:
    """Service de cache Redis avec TTL automatique"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Établir la connexion Redis"""
        try:
            # Configuration Redis depuis les variables d'environnement ou valeurs par défaut
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_db = int(os.getenv('REDIS_DB', 0))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test de connexion
            self.redis_client.ping()
            print(f"[REDIS] Connexion établie: {redis_host}:{redis_port}")
            
        except Exception as e:
            print(f"[REDIS] Erreur de connexion: {e}")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Générer une clé de cache unique basée sur les paramètres"""
        # Créer un hash des paramètres pour une clé unique
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"{prefix}:{params_hash}"
    
    def get_users_page(self, page_index: int, page_size: int, filters: Dict = None) -> Optional[Dict]:
        """Récupérer une page d'utilisateurs depuis le cache"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_key(
                "users_page",
                page_index=page_index,
                page_size=page_size,
                filters=filters or {}
            )
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            print(f"[REDIS] Erreur get_users_page: {e}")
            return None
    
    def set_users_page(self, page_index: int, page_size: int, users: List, total_count: int, 
                      filters: Dict = None, basic_by_uid: Dict = None, table_rows_data: List = None,
                      ttl_seconds: int = 300) -> bool:
        """Mettre en cache une page d'utilisateurs avec les données traitées"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_key(
                "users_page",
                page_index=page_index,
                page_size=page_size,
                filters=filters or {}
            )
            
            cache_data = {
                "users": users,
                "total_count": total_count,
                "page_index": page_index,
                "page_size": page_size,
                "filters": filters,
                "basic_by_uid": basic_by_uid or {},
                "table_rows_data": table_rows_data or []
            }
            
            # Stocker avec TTL
            self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cache_data, default=str)
            )
            
            print(f"[REDIS] Cache mis à jour: {cache_key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            print(f"[REDIS] Erreur set_users_page: {e}")
            return False
    
    def set_users_page_from_result(self, result: Dict, page_index: int, page_size: int, 
                                  filters: Dict = None, ttl_seconds: int = 300) -> bool:
        """Mettre en cache une page d'utilisateurs à partir du résultat complet du repository"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_key(
                "users_page",
                page_index=page_index,
                page_size=page_size,
                filters=filters or {}
            )
            
            # Préparer les données de cache directement depuis le résultat
            cache_data = {
                "users": result.get("users", []),
                "total_count": result.get("total_count", 0),
                "page_index": page_index,
                "page_size": page_size,
                "filters": filters,
                "basic_by_uid": result.get("basic_by_uid", {}),
                "table_rows_data": result.get("table_rows_data", [])
            }
            
            # Stocker avec TTL
            self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(cache_data, default=str)
            )
            
            print(f"[REDIS] Cache mis à jour depuis result: {cache_key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            print(f"[REDIS] Erreur set_users_page_from_result: {e}")
            return False
    
    def get_user_profile(self, uid: str) -> Optional[Dict]:
        """Récupérer un profil utilisateur depuis le cache"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = f"user_profile:{uid}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            print(f"[REDIS] Erreur get_user_profile: {e}")
            return None
    
    def set_user_profile(self, uid: str, profile_data: Dict, ttl_seconds: int = 600) -> bool:
        """Mettre en cache un profil utilisateur avec TTL"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = f"user_profile:{uid}"
            self.redis_client.setex(
                cache_key,
                ttl_seconds,
                json.dumps(profile_data, default=str)
            )
            return True
            
        except Exception as e:
            print(f"[REDIS] Erreur set_user_profile: {e}")
            return False
    
    def invalidate_users_cache(self) -> bool:
        """Invalider tout le cache des utilisateurs"""
        if not self.redis_client:
            return False
            
        try:
            # Supprimer toutes les clés commençant par "users_page:"
            keys = self.redis_client.keys("users_page:*")
            if keys:
                self.redis_client.delete(*keys)
                print(f"[REDIS] {len(keys)} clés users_page supprimées")
            return True
            
        except Exception as e:
            print(f"[REDIS] Erreur invalidate_users_cache: {e}")
            return False
    
    def invalidate_user_profile(self, uid: str) -> bool:
        """Invalider le cache d'un profil utilisateur spécifique"""
        if not self.redis_client:
            return False
            
        try:
            cache_key = f"user_profile:{uid}"
            self.redis_client.delete(cache_key)
            return True
            
        except Exception as e:
            print(f"[REDIS] Erreur invalidate_user_profile: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Obtenir des statistiques sur le cache"""
        if not self.redis_client:
            return {"error": "Redis non disponible"}
            
        try:
            info = self.redis_client.info()
            users_keys = len(self.redis_client.keys("users_page:*"))
            profile_keys = len(self.redis_client.keys("user_profile:*"))
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "users_page_keys": users_keys,
                "user_profile_keys": profile_keys,
                "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0
            }
            
        except Exception as e:
            return {"error": str(e)}


# Instance globale du cache Redis
redis_cache = RedisCache()
