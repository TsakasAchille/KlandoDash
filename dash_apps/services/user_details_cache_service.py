"""
Service de cache spécialisé pour les détails utilisateur avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
Suit le pattern de trip_details_cache_service.py
"""
import json
import os
from typing import Dict, Any, Optional
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.settings import load_json_config
from dash_apps.models.config_models import UserModel


class UserDetailsCache:
    """Service de cache pour les détails utilisateur avec configuration JSON"""
    
    _config_cache = None
    
    @staticmethod
    def _execute_user_query(uid: str, debug_users: bool = False) -> Optional[Dict[str, Any]]:
        """Exécute une requête utilisateur optimisée avec retry automatique"""
        # Récupérer les champs configurés depuis user_queries.json
        config = UserDetailsCache._load_config()
        query_config = config.get('queries', {}).get('user_details', {})
        json_base_fields = query_config.get('select', {}).get('base', [])
        field_mappings = config.get('field_mappings', {})
        
        # Utiliser les champs configurés ou tous les champs si pas de config
        base_fields = json_base_fields if json_base_fields else ["*"]
        select_clause = ', '.join(base_fields) if base_fields != ["*"] else "*"
        
        if debug_users:
            CallbackLogger.log_callback(
                "user_query_with_config",
                {
                    "uid": uid[:8] if uid else 'None',
                    "json_fields": json_base_fields,
                    "select_clause": select_clause,
                    "field_mappings_count": len(field_mappings)
                },
                status="INFO",
                extra_info="Using JSON config for user query optimization"
            )
        
        # Exécuter la requête avec retry automatique
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = supabase.table('users').select(select_clause).eq('uid', uid).execute()
                return response.data[0] if response.data else None
                
            except Exception as retry_error:
                retry_count += 1
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_query_retry",
                        {
                            "uid": uid[:8] if uid else 'None',
                            "retry_attempt": retry_count,
                            "max_retries": max_retries,
                            "error": str(retry_error)
                        },
                        status="WARNING",
                        extra_info=f"Retry {retry_count}/{max_retries} after connection error"
                    )
                
                if retry_count >= max_retries:
                    raise retry_error
                
                # Attendre avec backoff progressif
                import time
                time.sleep(0.5 * retry_count)
        
        return None
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON consolidé"""
        if UserDetailsCache._config_cache is None:
            UserDetailsCache._config_cache = load_json_config('user_details.json')
        
        return UserDetailsCache._config_cache
    
    @staticmethod
    def _get_cache_key(uid: str) -> str:
        """Génère la clé de cache - utilise directement l'UID avec préfixe fixe"""
        return f"user_details:{uid}"
    
    @staticmethod
    def _set_cache_data_generic(uid: str, data_type: str, data, ttl_seconds: int):
        """Fonction cache générique pour stocker les données utilisateur"""
        from dash_apps.services.local_cache import local_cache as cache
        method_name = f"set_user_{data_type}"
        if hasattr(cache, method_name):
            return getattr(cache, method_name)(uid, data, ttl_seconds)
        return None
    
    @staticmethod
    def _get_cached_data(uid: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache
        
        try:
            # Utiliser la même méthode que pour l'écriture avec uid
            cached_data = local_cache.get('user_details', uid=uid)
            
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            
            if cached_data:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_details_cache_hit",
                        {"uid": uid[:8] if uid else 'None'},
                        status="SUCCESS",
                        extra_info="User details retrieved from cache"
                    )
                return cached_data
            else:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_details_cache_miss",
                        {"uid": uid[:8] if uid else 'None'},
                        status="INFO",
                        extra_info="User details not found in cache"
                    )
                return None
                
        except Exception as e:
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_details_cache_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error accessing user details cache"
                )
            return None
    
    @staticmethod
    def get_user_details_data(uid: str) -> Dict[str, Any]:
        """
        Récupère les données détaillées d'un utilisateur avec cache intelligent
        
        Args:
            uid: UID de l'utilisateur
            
        Returns:
            Dict contenant les données utilisateur ou un dict vide si erreur
        """
        if not uid:
            return {}
        
        # Charger la configuration
        config = UserDetailsCache._load_config()
        
        # Vérifier le cache d'abord
        cached_data = UserDetailsCache._get_cached_data(uid)
        if cached_data:
            return cached_data
        
        debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        
        try:
            if debug_users:
                CallbackLogger.log_callback(
                    "user_details_fetch_start",
                    {"uid": uid[:8] if uid else 'None'},
                    status="INFO",
                    extra_info="Fetching user details from database"
                )
            
            # Exécuter la requête optimisée avec configuration JSON
            user_data = UserDetailsCache._execute_user_query(uid, debug_users)
            
            if not user_data:
                return {}
            
            # Afficher les données brutes de la DB
            if debug_users:
                CallbackLogger.log_data_dict(
                    f"Données brutes DB - User {uid[:8]}",
                    user_data
                )
            
            # 2. Validation avec Pydantic
            from dash_apps.utils.validation_utils import validate_data
            
            if debug_users:
                CallbackLogger.log_callback(
                    "api_get_user_details",
                    {"uid": uid[:8] if uid else 'None'},
                    status="INFO",
                    extra_info="Starting Pydantic validation"
                )
            
            # Valider les données avec le modèle Pydantic
            validation_result = validate_data(UserModel, user_data)
            
            if not validation_result.success:
                if debug_users:
                    CallbackLogger.log_callback(
                        "validation_error",
                        {"uid": uid[:8] if uid else 'None', "errors": validation_result.get_error_summary()},
                        status="ERROR",
                        extra_info="Échec de la validation Pydantic"
                    )
                return None
            
            # Utiliser les données validées (convertir le modèle Pydantic en dict)
            validated_data = validation_result.data
            if hasattr(validated_data, 'model_dump'):
                # Pydantic v2
                validated_data_dict = validated_data.model_dump()
            elif hasattr(validated_data, 'dict'):
                # Pydantic v1
                validated_data_dict = validated_data.dict()
            else:
                # Fallback si ce n'est pas un modèle Pydantic
                validated_data_dict = dict(validated_data)
            
            if debug_users:
                CallbackLogger.log_data_dict(
                    f"Données après validation Pydantic - User {uid[:8]}",
                    validated_data_dict
                )
                
                CallbackLogger.log_callback(
                    "validation_success",
                    {"uid": uid[:8] if uid else 'None'},
                    status="SUCCESS",
                    extra_info="Validation Pydantic réussie"
                )
            
            # 3. Formater les données pour l'affichage
            from dash_apps.utils.user_details_formatter import UserDetailsFormatter
            formatter = UserDetailsFormatter()
            formatted_data = formatter.format_for_display(validated_data_dict)
            
            # Afficher les données après transformation
            if debug_users:
                CallbackLogger.log_data_dict(
                    f"Données après transformation Formatter - User {uid[:8]}",
                    formatted_data
                )
            
            if debug_users:
                CallbackLogger.log_callback(
                    "formatter_debug",
                    {
                        "uid": uid[:8] if uid else 'None',
                        "formatted_data_type": type(formatted_data).__name__,
                        "formatted_data_bool": bool(formatted_data),
                        "is_dict": isinstance(formatted_data, dict),
                        "fields_count": len(formatted_data) if formatted_data else 0
                    },
                    status="INFO",
                    extra_info="Debug formatter output"
                )
            
            # Mettre en cache avec le cache local
            from dash_apps.services.local_cache import local_cache
            cache_ttl = config.get('cache', {}).get('ttl', 300)
            
            try:
                # Utiliser le cache local comme pour les trips - stocker les données formatées
                local_cache.set('user_details', formatted_data, ttl=cache_ttl, uid=uid)
                
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_details_cached",
                        {"uid": uid[:8] if uid else 'None', "ttl": cache_ttl},
                        status="SUCCESS",
                        extra_info="User details cached successfully with local cache"
                    )
            except Exception as cache_error:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_details_cache_error",
                        {"uid": uid[:8] if uid else 'None', "error": str(cache_error)},
                        status="ERROR",
                        extra_info="Failed to cache user details"
                    )
            
            return formatted_data
            
        except Exception as e:
            if debug_users:
                CallbackLogger.log_callback(
                    "user_details_fetch_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to fetch user details"
                )
            return {}
    
    @staticmethod
    def get_user_details(uid: str) -> Dict[str, Any]:
        """
        Méthode principale pour récupérer les détails utilisateur
        Alias pour get_user_details_data pour compatibilité avec les callbacks
        
        Args:
            uid: UID de l'utilisateur
            
        Returns:
            Dict contenant les données utilisateur ou un dict vide si erreur
        """
        return UserDetailsCache.get_user_details_data(uid)
    
    @staticmethod
    def invalidate_cache(uid: str):
        """Invalide le cache pour un utilisateur spécifique"""
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cache_key = UserDetailsCache._get_cache_key(uid)
            cache.delete('user_details', key=cache_key)
            
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_details_cache_invalidated",
                    {"uid": uid[:8] if uid else 'None'},
                    status="INFO",
                    extra_info="User details cache invalidated"
                )
                
        except Exception as e:
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_details_cache_invalidation_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to invalidate user details cache"
                )
