"""
Service centralisé pour la gestion des utilisateurs avec cache, validation Pydantic et API Supabase native.
Suit le même pattern que PassengersService avec configuration JSON.
"""
import os
import json
from typing import Dict, Any, List, Optional
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.models.config_models import UserModel
from dash_apps.services.redis_cache import redis_cache


class UsersQueryResult:
    """Résultat d'une requête sur les utilisateurs avec pagination."""
    
    def __init__(self, users: List[UserModel] = None, total_count: int = 0, 
                 page: int = 1, page_size: int = 20, has_next: bool = False):
        self.users = users or []
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.has_next = has_next
        self.total_pages = max(1, (total_count + page_size - 1) // page_size)


class UsersService:
    """Service centralisé pour la gestion des utilisateurs."""
    
    CACHE_TTL = 600  # 10 minutes
    
    @classmethod
    def _log_debug(cls, message: str, extra_data: Dict[str, Any] = None):
        """Log de debug avec CallbackLogger si DEBUG_USERS est activé."""
        debug_enabled = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_enabled:
            CallbackLogger.log_callback(
                "UsersService",
                extra_data or {},
                status="DEBUG",
                extra_info=message
            )
    
    @classmethod
    def _get_cache_key(cls, page: int, page_size: int, filters: Dict[str, Any] = None) -> str:
        """Génère une clé de cache pour les utilisateurs."""
        filter_str = ""
        if filters:
            # Créer une chaîne des filtres principaux
            key_filters = ['text', 'role', 'gender', 'date_from', 'date_to']
            filter_parts = []
            for key in key_filters:
                if key in filters and filters[key]:
                    filter_parts.append(f"{key}:{filters[key]}")
            filter_str = "|".join(filter_parts)
        
        return f"users:page:{page}:{page_size}:{filter_str}"
    
    @classmethod
    def get_users_paginated(cls, page: int = 1, page_size: int = 20, 
                           filters: Dict[str, Any] = None) -> UsersQueryResult:
        """Récupère les utilisateurs avec pagination et cache."""
        cache_key = cls._get_cache_key(page, page_size, filters)
        
        # Vérifier le cache
        try:
            cached_data = redis_cache.get(cache_key)
            if cached_data:
                cls._log_debug(f"Cache hit for users page {page}")
                data = json.loads(cached_data)
                users = [UserModel(**user_data) for user_data in data['users']]
                return UsersQueryResult(
                    users=users,
                    total_count=data['total_count'],
                    page=data['page'],
                    page_size=data['page_size'],
                    has_next=data['has_next']
                )
        except Exception as e:
            cls._log_debug(f"Cache error: {e}")
        
        # Cache miss - récupérer les données
        cls._log_debug(f"Cache miss for users page {page}")
        
        try:
            # Charger la configuration JSON
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('users_queries.json')
            
            if not config or 'queries' not in config:
                cls._log_debug("Configuration users_queries.json manquante")
                return UsersQueryResult()
            
            # Récupérer les champs depuis la configuration JSON
            query_config = config.get('queries', {}).get('users_paginated', {})
            json_fields = query_config.get('select', {}).get('base', [])
            select_clause = ', '.join(json_fields)
            
            cls._log_debug(f"Using fields from JSON config: {select_clause}")
            
            # Utiliser l'API Supabase directement
            from dash_apps.utils.supabase_client import supabase
            
            # Construire la requête avec filtres
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
            
            if not response.data:
                cls._log_debug("No users found in Supabase response")
                return UsersQueryResult()
            
            # Valider et transformer avec Pydantic
            validated_users = []
            for user_data in response.data:
                try:
                    user = UserModel(**user_data)
                    validated_users.append(user)
                    cls._log_debug(f"Validated user {user.uid}: {user.display_name}")
                except Exception as e:
                    cls._log_debug(f"Invalid user data: {e}", {"user_data": user_data})
                    continue
            
            # Calculer les métadonnées de pagination
            total_count = response.count if hasattr(response, 'count') else len(validated_users)
            has_next = len(validated_users) == page_size and (page * page_size) < total_count
            
            result = UsersQueryResult(
                users=validated_users,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=has_next
            )
            
            cls._log_debug(f"Found {len(result.users)} users, total: {result.total_count}")
            
            # Mettre en cache
            try:
                cache_data = {
                    'users': [user.model_dump() for user in validated_users],
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'has_next': has_next
                }
                redis_cache.setex(cache_key, cls.CACHE_TTL, json.dumps(cache_data))
                cls._log_debug(f"Cached users data for page {page}")
            except Exception as e:
                cls._log_debug(f"Cache set error: {e}")
            
            return result
            
        except Exception as e:
            cls._log_debug(f"Error querying users: {e}")
            return UsersQueryResult()
    
    @classmethod
    def _apply_filters(cls, query, filters: Dict[str, Any], config: Dict[str, Any]):
        """Applique les filtres à la requête Supabase."""
        try:
            # Filtre de texte (recherche dans plusieurs champs)
            if filters.get('text'):
                text = filters['text'].strip()
                if text:
                    # Recherche dans display_name, email, first_name, name
                    query = query.or_(f"display_name.ilike.%{text}%,email.ilike.%{text}%,first_name.ilike.%{text}%,name.ilike.%{text}%")
            
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
    def get_user_by_uid(cls, uid: str) -> Optional[UserModel]:
        """Récupère un utilisateur par son UID."""
        if not uid:
            return None
        
        cache_key = f"user:uid:{uid}"
        
        # Vérifier le cache
        try:
            cached_data = redis_cache.get(cache_key)
            if cached_data:
                cls._log_debug(f"Cache hit for user {uid}")
                return UserModel(**json.loads(cached_data))
        except Exception as e:
            cls._log_debug(f"Cache error: {e}")
        
        # Cache miss - récupérer les données
        cls._log_debug(f"Cache miss for user {uid}")
        
        try:
            # Charger la configuration JSON
            from dash_apps.utils.settings import load_json_config
            config = load_json_config('users_queries.json')
            
            # Récupérer les champs depuis la configuration JSON
            query_config = config.get('queries', {}).get('user_by_uid', {})
            json_fields = query_config.get('select', {}).get('base', [])
            select_clause = ', '.join(json_fields)
            
            # Utiliser l'API Supabase directement
            from dash_apps.utils.supabase_client import supabase
            
            response = supabase.table('users').select(select_clause).eq('uid', uid).limit(1).execute()
            
            if not response.data:
                cls._log_debug(f"No user found for UID: {uid}")
                return None
            
            user_data = response.data[0]
            user = UserModel(**user_data)
            
            cls._log_debug(f"Found user {user.uid}: {user.display_name}")
            
            # Mettre en cache
            try:
                redis_cache.setex(cache_key, cls.CACHE_TTL, user.model_dump_json())
                cls._log_debug(f"Cached user data for {uid}")
            except Exception as e:
                cls._log_debug(f"Cache set error: {e}")
            
            return user
            
        except Exception as e:
            cls._log_debug(f"Error querying user {uid}: {e}")
            return None
    
    @classmethod
    def invalidate_cache(cls, uid: str = None):
        """Invalide le cache pour un utilisateur ou tous les utilisateurs."""
        try:
            if uid:
                # Invalider le cache d'un utilisateur spécifique
                cache_key = f"user:uid:{uid}"
                redis_cache.delete(cache_key)
                cls._log_debug(f"Cache invalidated for user: {uid}")
            else:
                # Invalider tous les caches users (pattern matching)
                # Note: Redis pattern deletion nécessiterait une implémentation spécifique
                cls._log_debug("Cache invalidation requested for all users")
        except Exception as e:
            cls._log_debug(f"Cache invalidation error: {e}")
    
    @classmethod
    def get_users_summary(cls, page: int = 1, page_size: int = 20, 
                         filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Récupère un résumé des utilisateurs pour affichage."""
        result = cls.get_users_paginated(page, page_size, filters)
        
        users_list = []
        for user in result.users:
            users_list.append({
                "uid": user.uid,
                "display_name": user.display_name or "Nom non renseigné",
                "email": user.email or "Email non renseigné",
                "role": user.role or "user",
                "rating": user.rating or 0.0,
                "rating_count": user.rating_count or 0,
                "photo_url": user.photo_url,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "is_driver_validated": user.is_driver_doc_validated or False
            })
        
        return {
            "users": users_list,
            "total_count": result.total_count,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
            "has_next": result.has_next,
            "has_previous": result.page > 1
        }
