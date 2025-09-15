"""
Service spécialisé pour le tableau des utilisateurs avec cache et pagination.
Suit le pattern de trips_cache_service.py avec API Supabase native.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.models.config_models import UserModel
from dash_apps.services.local_cache import local_cache as cache


class UsersTableService:
    """Service centralisé pour la gestion du tableau des utilisateurs avec cache optimisé."""
    
    # Configuration du cache
    CACHE_TTL = 300  # 5 minutes pour le tableau
    LOCAL_CACHE_TTL = 60  # 1 minute pour le cache local
    MAX_LOCAL_CACHE_SIZE = 50  # Limite du cache local
    
    # Cache local en mémoire pour éviter Redis sur les accès fréquents
    _local_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}
    
    @classmethod
    def _log_debug(cls, message: str, extra_data: Dict[str, Any] = None):
        """Log de debug avec CallbackLogger si DEBUG_USERS est activé."""
        debug_enabled = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_enabled:
            CallbackLogger.log_callback(
                "UsersTableService",
                extra_data or {},
                status="DEBUG",
                extra_info=message
            )
    
    @classmethod
    def _get_cache_key(cls, page: int, page_size: int, filters: Dict[str, Any] = None) -> str:
        """Génère une clé de cache optimisée avec partitioning."""
        # Normaliser les filtres pour une clé déterministe
        normalized_filters = filters or {}
        
        # Extraire les partitions principales pour optimiser le cache
        partition_parts = []
        
        # Partition par rôle
        if normalized_filters.get('role') and normalized_filters['role'] != 'all':
            partition_parts.append(f"role={normalized_filters['role']}")
        
        # Partition par genre
        if normalized_filters.get('gender') and normalized_filters['gender'] != 'all':
            partition_parts.append(f"gender={normalized_filters['gender']}")
        
        # Partition par recherche textuelle (hash pour éviter les clés trop longues)
        if normalized_filters.get('text'):
            import hashlib
            text_hash = hashlib.md5(normalized_filters['text'].encode()).hexdigest()[:8]
            partition_parts.append(f"text={text_hash}")
        
        # Partition par période de création
        if normalized_filters.get('date_from') and normalized_filters.get('date_to'):
            partition_parts.append(f"range={normalized_filters['date_from']}_{normalized_filters['date_to']}")
        
        partition_str = "|".join(partition_parts)
        return f"users_table:{page}:{page_size}:{partition_str}"
    
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
            # Supprimer les 10 entrées les plus anciennes
            sorted_keys = sorted(cls._cache_timestamps.items(), key=lambda x: x[1])
            for old_key, _ in sorted_keys[:10]:
                cls._local_cache.pop(old_key, None)
                cls._cache_timestamps.pop(old_key, None)
        
        cls._local_cache[cache_key] = data
        cls._cache_timestamps[cache_key] = time.time()
        cls._log_debug(f"Stored in local cache: {cache_key}")
    
    @classmethod
    def get_users_page(cls, page: int = 1, page_size: int = 20, 
                      filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Récupère une page d'utilisateurs avec cache multi-niveau."""
        cache_key = cls._get_cache_key(page, page_size, filters)
        
        # 1. Vérifier le cache local
        local_data = cls._get_from_local_cache(cache_key)
        if local_data:
            return local_data
        
        # 2. Vérifier le cache principal (local_cache comme trips)
        try:
            cached_data = cache.get('users_table', key=cache_key)
            if cached_data:
                cls._log_debug(f"Cache hit for page {page}")
                # Stocker dans le cache local pour les prochains accès
                cls._set_to_local_cache(cache_key, cached_data)
                return cached_data
        except Exception as e:
            cls._log_debug(f"Cache error: {e}")
        
        # 3. Cache miss - récupérer les données depuis Supabase
        cls._log_debug(f"Cache miss for users page {page}")
        
        try:
            data = cls._fetch_users_from_supabase(page, page_size, filters)
            
            # 4. Mettre en cache (local_cache + local)
            try:
                cache.set('users_table', key=cache_key, value=data, ttl=cls.CACHE_TTL)
                cls._log_debug(f"Cached users page {page} in local_cache")
            except Exception as e:
                cls._log_debug(f"Cache set error: {e}")
            
            cls._set_to_local_cache(cache_key, data)
            
            return data
            
        except Exception as e:
            cls._log_debug(f"Error fetching users page: {e}")
            return {
                "users": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
    
    @classmethod
    def _fetch_users_from_supabase(cls, page: int, page_size: int, 
                                  filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Récupère les utilisateurs depuis Supabase avec l'API native."""
        try:
            # Charger la configuration JSON
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('users_queries.json')
            
            if not config or 'queries' not in config:
                cls._log_debug("Configuration users_queries.json manquante")
                raise Exception("Configuration manquante")
            
            # Récupérer les champs depuis la configuration JSON
            query_config = config.get('queries', {}).get('users_paginated', {})
            json_fields = query_config.get('select', {}).get('base', [])
            select_clause = ', '.join(json_fields)
            
            cls._log_debug(f"Using fields from JSON config: {select_clause}")
            
            # Utiliser l'API Supabase directement
            from dash_apps.utils.supabase_client import supabase
            
            # Construire la requête sans transformation - garder les valeurs originales
            query = supabase.table('users').select(select_clause, count='exact')
            
            # Appliquer les filtres si présents
            if filters:
                query = cls._apply_filters(query, filters, config)
            
            # Appliquer la pagination
            offset = (page - 1) * page_size
            query = query.range(offset, offset + page_size - 1)
            
            # Ordonner par date de création (plus récent en premier)
            query = query.order('created_at', desc=True)
            
            # Exécuter la requête
            response = query.execute()
            
            cls._log_debug(f"Supabase response: {len(response.data) if response.data else 0} users")
            
            # Valider et transformer avec Pydantic
            validated_users = []
            for user_data in response.data or []:
                try:
                    user = UserModel(**user_data)
                    validated_users.append({
                        "uid": user.uid,
                        "display_name": user.display_name or "Nom non renseigné",
                        "email": user.email or "Email non renseigné",
                        "phone_number": user.phone_number or "",
                        "role": user.role or "user",
                        "gender": user.gender or "",
                        "rating": user.rating,
                        "rating_count": user.rating_count or 0,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "is_driver_doc_validated": user.is_driver_doc_validated or False,
                        "photo_url": user.photo_url
                    })
                except Exception as e:
                    cls._log_debug(f"Invalid user data: {e}", {"user_data": user_data})
                    continue
            
            # Calculer les métadonnées de pagination
            total_count = response.count if hasattr(response, 'count') else len(validated_users)
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            has_next = page < total_pages
            has_previous = page > 1
            
            result = {
                "users": validated_users,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            }
            
            cls._log_debug(f"Found {len(validated_users)} users, total: {total_count}")
            
            return result
            
        except Exception as e:
            cls._log_debug(f"Error fetching from Supabase: {e}")
            raise
    
    @classmethod
    def _apply_filters(cls, query, filters: Dict[str, Any], config: Dict[str, Any]):
        """Applique les filtres à la requête Supabase selon la configuration JSON."""
        try:
            # Filtre de texte (recherche dans plusieurs champs)
            if filters.get('text'):
                text = filters['text'].strip()
                if text:
                    # Utiliser la configuration JSON pour les champs de recherche
                    search_config = config.get('queries', {}).get('users_search', {}).get('filters', {}).get('text_search', {})
                    search_fields = search_config.get('fields', ['display_name', 'email', 'first_name', 'name'])
                    
                    # Construire la clause OR pour la recherche
                    or_conditions = []
                    for field in search_fields:
                        or_conditions.append(f"{field}.ilike.%{text}%")
                    
                    if or_conditions:
                        query = query.or_(','.join(or_conditions))
            
            # Filtre par rôle
            if filters.get('role') and filters['role'] != 'all':
                query = query.eq('role', filters['role'])
            
            # Filtre par genre
            if filters.get('gender') and filters['gender'] != 'all':
                query = query.eq('gender', filters['gender'])
            
            # Filtre par date de création
            if filters.get('date_from'):
                query = query.gte('created_at', filters['date_from'])
            
            if filters.get('date_to'):
                query = query.lte('created_at', filters['date_to'])
            
            return query
            
        except Exception as e:
            cls._log_debug(f"Error applying filters: {e}")
            return query
    
    @classmethod
    def invalidate_cache(cls, uid: str = None):
        """Invalide le cache pour un utilisateur ou tous les utilisateurs."""
        try:
            if uid:
                # Invalider les caches contenant cet utilisateur
                keys_to_remove = []
                for key in cls._local_cache.keys():
                    if f"uid:{uid}" in key:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    cls._local_cache.pop(key, None)
                    cls._cache_timestamps.pop(key, None)
                
                cls._log_debug(f"Cache invalidated for user: {uid}")
            else:
                # Invalider tout le cache local
                cls._local_cache.clear()
                cls._cache_timestamps.clear()
                cls._log_debug("All users cache invalidated")
                
        except Exception as e:
            cls._log_debug(f"Cache invalidation error: {e}")
    
    @classmethod
    def refresh_cache(cls):
        """Force le rafraîchissement du cache."""
        cls.invalidate_cache()
        cls._log_debug("Users table cache refreshed")
