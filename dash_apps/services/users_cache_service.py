"""
Service de cache pour les données utilisateurs avec logique de génération centralisée
"""
from typing import Dict, List, Tuple, Optional
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.services.redis_cache import redis_cache
from dash import html


class UsersCacheService:
    """Service centralisé pour la gestion du cache des données utilisateurs"""
    
    # Cache en mémoire pour les panneaux HTML générés
    _html_cache = {}
    
    @staticmethod
    def get_users_page_result(page_index: int, page_size: int, filter_params: Dict, 
                             force_reload: bool = False) -> Dict:
        """
        Récupère le résultat brut d'une page d'utilisateurs avec cache intelligent
        
        Returns:
            Dict: Résultat complet du repository (users, total_count, basic_by_uid, table_rows_data)
        """
        # Essayer d'abord le cache Redis (sauf si refresh forcé)
        if not force_reload:
            cached_data = redis_cache.get_users_page(page_index, page_size, filter_params)
            if cached_data:
                try:
                    users_count = len(cached_data.get("users", []))
                    total_count = cached_data.get("total_count", 0)
                    print(f"[USERS][REDIS HIT] page_index={page_index} users={users_count} total={total_count}")
                except Exception:
                    pass
                
                return cached_data
        
        # Si pas de cache ou refresh forcé, appeler le repository
        result = UserRepository.get_users_paginated(page_index, page_size, filters=filter_params)
        
        # Mettre à jour le cache Redis avec le résultat complet
        redis_cache.set_users_page_from_result(result, page_index, page_size, filter_params, ttl_seconds=300)
        
        try:
            users_count = len(result.get("users", []))
            total_count = result.get("total_count", 0)
            print(f"[USERS][FETCH] page_index={page_index} users={users_count} total={total_count} refresh={force_reload}")
        except Exception:
            pass
        
        return result
    
    @staticmethod
    def extract_table_data(result: Dict) -> Tuple[List, int, Dict, List]:
        """
        Extrait les données nécessaires pour le rendu du tableau
        
        Returns:
            Tuple[users, total_users, basic_by_uid, table_rows_data]
        """
        users = result.get("users", [])
        total_users = int(result.get("total_count", 0))
        basic_by_uid = result.get("basic_by_uid", {})
        table_rows_data = result.get("table_rows_data", [])
        
        return users, total_users, basic_by_uid, table_rows_data
    
    @staticmethod
    def extract_stats_data(result: Dict) -> Dict:
        """
        Extrait les données nécessaires pour les statistiques
        
        Returns:
            Dict: Données pour les stats (total_users, users avec métriques)
        """
        return {
            "total_users": result.get("total_count", 0),
            "users": result.get("users", []),
            "page_info": {
                "page_index": result.get("page_index", 0),
                "page_size": result.get("page_size", 20)
            }
        }
    
    @staticmethod
    def extract_basic_data(result: Dict) -> Dict:
        """
        Extrait uniquement les données basiques des utilisateurs
        
        Returns:
            Dict: basic_by_uid pour les composants qui n'ont besoin que des infos de base
        """
        return result.get("basic_by_uid", {})
    
    @staticmethod
    def get_user_data(selected_uid: str, basic_by_uid: Dict = None) -> Optional[Dict]:
        """
        Récupère les données d'un utilisateur spécifique avec cache intelligent
        
        Args:
            selected_uid: UID de l'utilisateur à récupérer
            basic_by_uid: Cache des données basiques (optionnel)
            
        Returns:
            Dict: Données de l'utilisateur ou None si non trouvé
        """
        if not selected_uid:
            return None
            
        # Chercher d'abord dans le cache fourni
        if basic_by_uid and selected_uid in basic_by_uid:
            print(f"[CACHE HIT] Utilisateur {selected_uid[:8]}... trouvé dans le cache")
            return basic_by_uid[selected_uid]
        
        # Fallback vers le repository
        print(f"[CACHE MISS] Chargement utilisateur {selected_uid[:8]}... depuis la DB")
        user_schema = UserRepository.get_user_by_id(selected_uid)
        if user_schema:
            return user_schema.model_dump() if hasattr(user_schema, "model_dump") else user_schema.dict()
        
        return None
    
    @staticmethod
    def get_cached_panel(user_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Récupère un panneau HTML en cache
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            
        Returns:
            html.Div: Panneau en cache ou None si non trouvé
        """
        cache_key = f"{user_id}_{panel_type}"
        return UsersCacheService._html_cache.get(cache_key)
    
    @staticmethod
    def set_cached_panel(user_id: str, panel_type: str, panel_html: html.Div):
        """
        Met en cache un panneau HTML généré
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            panel_html: Panneau HTML à mettre en cache
        """
        cache_key = f"{user_id}_{panel_type}"
        UsersCacheService._html_cache[cache_key] = panel_html
        print(f"[HTML CACHE] Panneau {panel_type} mis en cache pour {user_id[:8]}...")
    
    @staticmethod
    def clear_user_cache(user_id: str):
        """
        Efface le cache HTML pour un utilisateur spécifique
        
        Args:
            user_id: UID de l'utilisateur
        """
        keys_to_remove = [key for key in UsersCacheService._html_cache.keys() 
                         if key.startswith(f"{user_id}_")]
        for key in keys_to_remove:
            del UsersCacheService._html_cache[key]
        print(f"[HTML CACHE] Cache effacé pour utilisateur {user_id[:8]}...")
    
    @staticmethod
    def clear_all_html_cache():
        """Efface tout le cache HTML"""
        UsersCacheService._html_cache.clear()
        print("[HTML CACHE] Tout le cache HTML effacé")
