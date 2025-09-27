#!/usr/bin/env python3
"""
Service de cache local en mémoire configurable via JSON
Remplace Redis par un système de cache Python natif
"""

import json
import os
import time
import threading
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib


class LocalCache:
    """Cache local en mémoire avec configuration JSON"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'cache_config.json'
        )
        self.config = self._load_config()
        self.cache_data = {}
        self.access_times = {}
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'cleanups': 0
        }
        
        # Démarrer le nettoyage automatique si activé
        if self.config.get('cleanup_rules', {}).get('auto_cleanup', True):
            self._start_cleanup_thread()
    
    def _load_config(self) -> Dict:
        """Charge la configuration du cache depuis le JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[LOCAL_CACHE] Configuration chargée: {len(config.get('cache_types', {}))} types de cache")
            return config
        except Exception as e:
            print(f"[LOCAL_CACHE] Erreur chargement config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configuration par défaut si le JSON n'est pas disponible"""
        return {
            "cache_system": {"type": "local_memory", "settings": {"default_ttl": 300}},
            "cache_types": {},
            "cleanup_rules": {"auto_cleanup": True}
        }
    
    def _get_cache_type_config(self, cache_type: str) -> Dict:
        """Récupère la config pour un type de cache spécifique"""
        return self.config.get('cache_types', {}).get(cache_type, {
            'ttl': self.config.get('cache_system', {}).get('settings', {}).get('default_ttl', 300),
            'max_entries': 100,
            'key_pattern': f"{cache_type}:{{key}}"
        })
    
    def _build_key(self, cache_type: str, **kwargs) -> str:
        """Construit une clé de cache selon le pattern défini dans la config"""
        type_config = self._get_cache_type_config(cache_type)
        key_pattern = type_config.get('key_pattern', f"{cache_type}:{{key}}")
        
        try:
            return key_pattern.format(**kwargs)
        except KeyError as e:
            # Fallback si les paramètres ne matchent pas le pattern
            key_parts = [cache_type] + [str(v) for v in kwargs.values()]
            return ':'.join(key_parts)
    
    def get(self, cache_type: str, **kwargs) -> Optional[Any]:
        """Récupère une valeur du cache"""
        key = self._build_key(cache_type, **kwargs)
        
        with self.lock:
            if key not in self.cache_data:
                self.stats['misses'] += 1
                if self.config.get('monitoring', {}).get('log_misses', False):
                    print(f"[LOCAL_CACHE] MISS: {key}")
                return None
            
            entry = self.cache_data[key]
            
            # Vérifier TTL
            if self._is_expired(entry):
                del self.cache_data[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.stats['misses'] += 1
                return None
            
            # Mettre à jour le temps d'accès pour LRU
            self.access_times[key] = time.time()
            self.stats['hits'] += 1
            
            if self.config.get('monitoring', {}).get('log_hits', False):
                print(f"[LOCAL_CACHE] HIT: {key}")
            
            return entry['data']
    
    def set(self, cache_type: str, data: Any, ttl: int = None, **kwargs) -> bool:
        """Stocke une valeur dans le cache"""
        key = self._build_key(cache_type, **kwargs)
        type_config = self._get_cache_type_config(cache_type)
        ttl = ttl if ttl is not None else type_config.get('ttl', 300)
        
        with self.lock:
            # Vérifier les limites de taille pour ce type de cache
            max_entries = type_config.get('max_entries', 100)
            current_entries = sum(1 for k in self.cache_data.keys() if k.startswith(f"{cache_type}:"))
            
            if current_entries >= max_entries:
                self._cleanup_cache_type(cache_type, max_entries // 2)
            
            # Stocker l'entrée
            entry = {
                'data': data,
                'created_at': time.time(),
                'ttl': ttl,
                'cache_type': cache_type
            }
            
            self.cache_data[key] = entry
            self.access_times[key] = time.time()
            self.stats['sets'] += 1
            
            return True
    
    def delete(self, cache_type: str, **kwargs) -> bool:
        """Supprime une entrée du cache"""
        key = self._build_key(cache_type, **kwargs)
        
        with self.lock:
            if key in self.cache_data:
                del self.cache_data[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.stats['deletes'] += 1
                return True
            return False
    
    def clear_cache_type(self, cache_type: str) -> int:
        """Vide complètement un type de cache"""
        with self.lock:
            keys_to_delete = [k for k in self.cache_data.keys() if k.startswith(f"{cache_type}:")]
            for key in keys_to_delete:
                del self.cache_data[key]
                if key in self.access_times:
                    del self.access_times[key]
            return len(keys_to_delete)
    
    def _is_expired(self, entry: Dict) -> bool:
        """Vérifie si une entrée a expiré"""
        return time.time() - entry['created_at'] > entry['ttl']
    
    def _cleanup_cache_type(self, cache_type: str, target_size: int):
        """Nettoie un type de cache spécifique"""
        keys = [k for k in self.cache_data.keys() if k.startswith(f"{cache_type}:")]
        
        if len(keys) <= target_size:
            return
        
        # Stratégie LRU: supprimer les moins récemment utilisées
        keys_by_access = sorted(keys, key=lambda k: self.access_times.get(k, 0))
        keys_to_remove = keys_by_access[:len(keys) - target_size]
        
        for key in keys_to_remove:
            if key in self.cache_data:
                del self.cache_data[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _cleanup_expired(self):
        """Nettoie les entrées expirées"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache_data.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache_data[key]
                if key in self.access_times:
                    del self.access_times[key]
            
            if expired_keys and self.config.get('monitoring', {}).get('log_cleanup', True):
                print(f"[LOCAL_CACHE] Nettoyage: {len(expired_keys)} entrées expirées supprimées")
            
            self.stats['cleanups'] += 1
            return len(expired_keys)
    
    def _start_cleanup_thread(self):
        """Démarre le thread de nettoyage automatique"""
        cleanup_interval = self.config.get('cache_system', {}).get('settings', {}).get('cleanup_interval', 60)
        
        def cleanup_worker():
            while True:
                time.sleep(cleanup_interval)
                try:
                    self._cleanup_expired()
                except Exception as e:
                    print(f"[LOCAL_CACHE] Erreur nettoyage automatique: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques du cache"""
        with self.lock:
            total_entries = len(self.cache_data)
            cache_types_count = {}
            
            for key in self.cache_data.keys():
                cache_type = key.split(':')[0]
                cache_types_count[cache_type] = cache_types_count.get(cache_type, 0) + 1
            
            return {
                **self.stats,
                'total_entries': total_entries,
                'cache_types_count': cache_types_count,
                'hit_rate': self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            }
    
    # Méthodes compatibles avec l'interface Redis existante
    """
    def get_trip_details(self, trip_id: str) -> Optional[Any]:
        return self.get('trip_details', trip_id=trip_id)
    
    def set_trip_details(self, trip_id: str, data: Any, ttl_seconds: int = None) -> bool:
        return self.set('trip_details', data, trip_id=trip_id, ttl=ttl_seconds)
    
    def get_trip_stats(self, trip_id: str) -> Optional[Any]:
        return self.get('trip_stats', trip_id=trip_id)
    
    def set_trip_stats(self, trip_id: str, data: Any, ttl_seconds: int = None) -> bool:
        return self.set('trip_stats', data, trip_id=trip_id, ttl=ttl_seconds)
    
    def get_trip_passengers(self, trip_id: str) -> Optional[Any]:
        return self.get('trip_passengers', trip_id=trip_id)
    
    def set_trip_passengers(self, trip_id: str, data: Any, ttl_seconds: int = None) -> bool:
        return self.set('trip_passengers', data, trip_id=trip_id, ttl=ttl_seconds)
    """

# Instance globale du cache local
local_cache = LocalCache()

# Alias pour compatibilité avec les imports existants
cache = local_cache
