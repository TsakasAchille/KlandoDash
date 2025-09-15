"""
Service de cache spécialisé pour les profils utilisateur avec configuration JSON dynamique.
Suit le pattern de trip_driver_cache_service.py
"""
import json
import os
from typing import Dict, Any, Optional
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.supabase_client import supabase
from dash_apps.models.config_models import UserModel


class UserProfileCache:
    """Service de cache pour les profils utilisateur avec configuration JSON"""
    
    _config_cache = None
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration JSON pour les profils utilisateur"""
        if UserProfileCache._config_cache is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'user_profile_config.json'
            )
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    UserProfileCache._config_cache = json.load(f)
                
                debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
                
                if debug_users:
                    CallbackLogger.log_callback(
                        "load_user_profile_config",
                        {"config_path": os.path.basename(config_path)},
                        status="SUCCESS",
                        extra_info="User profile configuration loaded"
                    )
                    
            except Exception as e:
                debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
                
                if debug_users:
                    CallbackLogger.log_callback(
                        "load_user_profile_config",
                        {"error": str(e)},
                        status="ERROR",
                        extra_info="Failed to load user profile configuration"
                    )
                
                # Configuration par défaut
                UserProfileCache._config_cache = {
                    "cache": {
                        "key_prefix": "user_profile",
                        "ttl": 600
                    },
                    "validation": {
                        "uid": {
                            "required": True,
                            "min_length": 5
                        }
                    },
                    "template_style": {
                        "height": "600px",
                        "width": "100%",
                        "card_height": "550px",
                        "card_width": "100%"
                    }
                }
        
        return UserProfileCache._config_cache
    
    @staticmethod
    def _get_cache_key(uid: str) -> str:
        """Génère la clé de cache pour un profil utilisateur"""
        return f"user_profile:{uid}"
    
    @staticmethod
    def _get_cached_data(uid: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = UserProfileCache._get_cache_key(uid)
            cached_data = cache.get('user_profile', key=cache_key)
            
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            
            if cached_data:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_profile_cache_hit",
                        {"uid": uid[:8] if uid else 'None'},
                        status="SUCCESS",
                        extra_info="User profile retrieved from cache"
                    )
                return cached_data
            else:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_profile_cache_miss",
                        {"uid": uid[:8] if uid else 'None'},
                        status="INFO",
                        extra_info="User profile not found in cache"
                    )
                return None
                
        except Exception as e:
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_cache_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Error accessing user profile cache"
                )
            return None
    
    @staticmethod
    def get_user_profile_data(uid: str) -> Dict[str, Any]:
        """
        Récupère les données de profil d'un utilisateur avec cache intelligent
        
        Args:
            uid: UID de l'utilisateur
            
        Returns:
            Dict contenant les données de profil ou un dict vide si erreur
        """
        if not uid:
            return {}
        
        # Charger la configuration
        #config = UserProfileCache._load_config()
        
        # Vérifier le cache d'abord
        cached_data = UserProfileCache._get_cached_data(uid)
        if cached_data:
            return cached_data
        
        debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        
        try:
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_fetch_start",
                    {"uid": uid[:8] if uid else 'None'},
                    status="INFO",
                    extra_info="Fetching user profile from database"
                )
            
            # Récupérer les données utilisateur directement depuis Supabase
            response = supabase.table('users').select('*').eq('uid', uid).execute()
            user_data = response.data[0] if response.data else None
            
            if not user_data:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_profile_not_found",
                        {"uid": uid[:8] if uid else 'None'},
                        status="WARNING",
                        extra_info="User profile not found in database"
                    )
                return {}
            
            # Valider les données avec Pydantic
            try:
                validated_user = UserModel(**user_data)
                
                # Utiliser model_dump() comme dans le pattern trips
                if hasattr(validated_user, 'model_dump'):
                    # Pydantic v2
                    validated_data = validated_user.model_dump()
                elif hasattr(validated_user, 'dict'):
                    # Pydantic v1
                    validated_data = validated_user.dict()
                else:
                    # Fallback si ce n'est pas un modèle Pydantic
                    validated_data = dict(user_data)
                
                # Enrichir avec des données calculées pour le profil
                profile_data = {
                    **validated_data,
                    "full_name": validated_user.full_name,
                    "rating_display": validated_user.rating_display,
                    "is_driver": validated_user.is_driver,
                    "profile_completion": UserProfileCache._calculate_profile_completion(validated_user),
                    "account_age_days": UserProfileCache._calculate_account_age(validated_user),
                    "has_photo": bool(validated_user.photo_url),
                    "has_documents": bool(validated_user.driver_license_url or validated_user.id_card_url)
                }
                
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_profile_validation_success",
                        {
                            "uid": uid[:8] if uid else 'None',
                            "full_name": validated_user.full_name,
                            "profile_completion": profile_data["profile_completion"]
                        },
                        status="SUCCESS",
                        extra_info="User profile data validated successfully"
                    )
                
            except Exception as validation_error:
                if debug_users:
                    CallbackLogger.log_callback(
                        "user_profile_validation_error",
                        {
                            "uid": uid[:8] if uid else 'None',
                            "error": str(validation_error)
                        },
                        status="ERROR",
                        extra_info="User profile data validation failed"
                    )
                # Utiliser les données brutes si la validation échoue
                profile_data = user_data
            
            # Mettre en cache
            cache_ttl = config.get('cache', {}).get('ttl', 600)
            UserProfileCache._set_cache_data(uid, profile_data, cache_ttl)
            
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_cached",
                    {"uid": uid[:8] if uid else 'None', "ttl": cache_ttl},
                    status="SUCCESS",
                    extra_info="User profile cached successfully"
                )
            
            return profile_data
            
        except Exception as e:
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_fetch_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to fetch user profile"
                )
            return {}
    
    @staticmethod
    def get_user_profile(uid: str) -> Dict[str, Any]:
        """
        Méthode principale pour récupérer le profil utilisateur
        Alias pour get_user_profile_data pour compatibilité avec les callbacks
        
        Args:
            uid: UID de l'utilisateur
            
        Returns:
            Dict contenant les données de profil ou un dict vide si erreur
        """
        return UserProfileCache.get_user_profile_data(uid)
    
    @staticmethod
    def _set_cache_data(uid: str, data: Dict[str, Any], ttl_seconds: int):
        """Stocke les données dans le cache local"""
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cache_key = UserProfileCache._get_cache_key(uid)
            cache.set('user_profile', key=cache_key, value=data, ttl=ttl_seconds)
        except Exception as e:
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_cache_set_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to cache user profile"
                )
    
    @staticmethod
    def _calculate_profile_completion(user: UserModel) -> int:
        """Calcule le pourcentage de complétion du profil"""
        total_fields = 10
        completed_fields = 0
        
        # Champs obligatoires
        if user.display_name or user.first_name or user.name:
            completed_fields += 1
        if user.email:
            completed_fields += 1
        if user.phone_number:
            completed_fields += 1
        
        # Champs optionnels mais importants
        if user.photo_url:
            completed_fields += 1
        if user.bio:
            completed_fields += 1
        if user.birth:
            completed_fields += 1
        if user.gender and user.gender != 'NOT_SPECIFIED':
            completed_fields += 1
        if user.driver_license_url:
            completed_fields += 1
        if user.id_card_url:
            completed_fields += 1
        if user.rating and user.rating_count > 0:
            completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)
    
    @staticmethod
    def _calculate_account_age(user: UserModel) -> int:
        """Calcule l'âge du compte en jours"""
        if user.created_at:
            from datetime import datetime
            now = datetime.now()
            if user.created_at.tzinfo:
                now = now.replace(tzinfo=user.created_at.tzinfo)
            delta = now - user.created_at
            return delta.days
        return 0
    
    @staticmethod
    def invalidate_cache(uid: str):
        """Invalide le cache pour un utilisateur spécifique"""
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cache_key = UserProfileCache._get_cache_key(uid)
            cache.delete('user_profile', key=cache_key)
            
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_cache_invalidated",
                    {"uid": uid[:8] if uid else 'None'},
                    status="INFO",
                    extra_info="User profile cache invalidated"
                )
                
        except Exception as e:
            debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
            if debug_users:
                CallbackLogger.log_callback(
                    "user_profile_cache_invalidation_error",
                    {"uid": uid[:8] if uid else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to invalidate user profile cache"
                )
