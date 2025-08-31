"""
Service de cache pour les données utilisateurs avec logique de génération centralisée
"""
from typing import Dict, List, Optional, Tuple
import time
import threading
import os
from dash import html
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.services.redis_cache import redis_cache


class UsersCacheService:
    """Service centralisé pour la gestion du cache des données utilisateurs"""
    
    # Cache en mémoire pour les panneaux HTML générés
    _html_cache = {}
    
    # Mode debug pour les logs (désactivé en production)
    _debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
    
    # Cache local rapide pour éviter Redis sur les accès fréquents
    _local_cache = {}
    _cache_timestamps = {}
    _local_cache_ttl = 60  # 1 minute en local
    
    @staticmethod
    def _get_cache_key(page_index: int, page_size: int, filter_params: Dict) -> str:
        """Génère une clé de cache optimisée sans hash MD5"""
        # Simplifier la génération de clé pour plus de rapidité
        filter_str = ""
        if filter_params:
            # Créer une chaîne simple des filtres les plus importants
            key_filters = ['text', 'role', 'date_from', 'date_to', 'gender']
            filter_parts = []
            for key in key_filters:
                if key in filter_params and filter_params[key]:
                    filter_parts.append(f"{key}:{filter_params[key]}")
            filter_str = "|".join(filter_parts)
        
        return f"users:{page_index}:{page_size}:{filter_str}"
    
    @staticmethod
    def _is_local_cache_valid(cache_key: str) -> bool:
        """Vérifie si le cache local est encore valide"""
        import time
        if cache_key not in UsersCacheService._cache_timestamps:
            return False
        
        elapsed = time.time() - UsersCacheService._cache_timestamps[cache_key]
        return elapsed < UsersCacheService._local_cache_ttl
    
    @staticmethod
    def get_users_page_result(page_index: int, page_size: int, filter_params: Dict, 
                             force_reload: bool = False) -> Dict:
        """
        Récupère le résultat brut d'une page d'utilisateurs avec cache multi-niveaux optimisé
        
        Returns:
            Dict: Résultat complet du repository (users, total_count, basic_by_uid, table_rows_data)
        """
        import time
        
        cache_key = UsersCacheService._get_cache_key(page_index, page_size, filter_params)
        
        if not force_reload:
            # Niveau 1: Cache local ultra-rapide (en mémoire)
            if (cache_key in UsersCacheService._local_cache and 
                UsersCacheService._is_local_cache_valid(cache_key)):
                print(f"[USERS][LOCAL CACHE HIT] {cache_key}")
                return UsersCacheService._local_cache[cache_key]
            
            # Niveau 2: Cache Redis
            cached_data = redis_cache.get_users_page(page_index, page_size, filter_params)
            if cached_data:
                # Stocker dans le cache local pour les prochains accès
                UsersCacheService._local_cache[cache_key] = cached_data
                UsersCacheService._cache_timestamps[cache_key] = time.time()
                
                if UsersCacheService._debug_mode:
                    try:
                        users_count = len(cached_data.get("users", []))
                        total_count = cached_data.get("total_count", 0)
                        print(f"[USERS][REDIS HIT] page_index={page_index} users={users_count} total={total_count}")
                    except Exception:
                        pass
                
                return cached_data
        
        # Niveau 3: Base de données
        result = UserRepository.get_users_paginated(page_index, page_size, filters=filter_params)
        
        # Mettre à jour tous les niveaux de cache
        UsersCacheService._local_cache[cache_key] = result
        UsersCacheService._cache_timestamps[cache_key] = time.time()
        redis_cache.set_users_page_from_result(result, page_index, page_size, filter_params, ttl_seconds=300)
        
        if UsersCacheService._debug_mode:
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
            if UsersCacheService._debug_mode:
                print(f"[CACHE HIT] Utilisateur {selected_uid[:8]}... trouvé dans le cache")
            return basic_by_uid[selected_uid]
        
        # Fallback vers le repository
        if UsersCacheService._debug_mode:
            print(f"[CACHE MISS] Chargement utilisateur {selected_uid[:8]}... depuis la DB")
        user_schema = UserRepository.get_user_by_id(selected_uid)
        if user_schema:
            return user_schema.model_dump() if hasattr(user_schema, "model_dump") else user_schema.dict()
        
        return None
    
    @staticmethod
    def get_cached_panel(user_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Récupère un panneau HTML en cache avec gestion intelligente
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            
        Returns:
            html.Div: Panneau en cache ou None si non trouvé
        """
        cache_key = f"{user_id}_{panel_type}"
        
        # Vérifier d'abord le cache HTML local
        if cache_key in UsersCacheService._html_cache:
            return UsersCacheService._html_cache[cache_key]
        
        # Essayer le cache Redis pour les panneaux HTML persistants
        try:
            cached_html = redis_cache.redis_client.get(f"html_panel:{cache_key}") if redis_cache.redis_client else None
            if cached_html:
                # Reconstruire l'objet HTML depuis le cache Redis (simplifié)
                if UsersCacheService._debug_mode:
                    print(f"[HTML CACHE][REDIS HIT] Panneau {panel_type} pour {user_id[:8]}...")
                # Note: Pour une vraie implémentation, il faudrait sérialiser/désérialiser les objets Dash
                return None  # Temporairement désactivé car complexe
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def set_cached_panel(user_id: str, panel_type: str, panel_html: html.Div):
        """
        Met en cache un panneau HTML généré avec TTL
        
        Args:
            user_id: UID de l'utilisateur
            panel_type: Type de panneau ('profile', 'stats', 'trips')
            panel_html: Panneau HTML à mettre en cache
        """
        cache_key = f"{user_id}_{panel_type}"
        
        # Cache local immédiat
        UsersCacheService._html_cache[cache_key] = panel_html
        
        # Limiter la taille du cache HTML local (LRU simple)
        if len(UsersCacheService._html_cache) > 100:  # Max 100 panneaux en mémoire
            # Supprimer les plus anciens (approximation simple)
            oldest_keys = list(UsersCacheService._html_cache.keys())[:20]
            for old_key in oldest_keys:
                del UsersCacheService._html_cache[old_key]
        
        if UsersCacheService._debug_mode:
            print(f"[HTML CACHE] Panneau {panel_type} mis en cache pour {user_id[:8]}...")
    
    @staticmethod
    def _preload_single_user(user_id: str, panel_types: List[str]):
        """
        Précharge les panneaux pour un utilisateur spécifique (fonction interne pour threading)
        
        Args:
            user_id: UID de l'utilisateur
            panel_types: Types de panneaux à précharger
        """
        try:
            # Récupérer les données utilisateur une seule fois
            user_data = UsersCacheService.get_user_data(user_id)
            if user_data:
                # Générer et cacher les panneaux si pas déjà en cache
                for panel_type in panel_types:
                    cache_key = f"{user_id}_{panel_type}"
                    if cache_key not in UsersCacheService._html_cache:
                        # Générer le panneau selon le type
                        if panel_type == 'profile':
                            from dash_apps.components.user_profile import render_user_profile
                            panel = render_user_profile(user_data)
                            UsersCacheService.set_cached_panel(user_id, panel_type, panel)
                        elif panel_type == 'stats':
                            from dash_apps.components.user_stats import render_user_stats
                            panel = render_user_stats(user_data)
                            UsersCacheService.set_cached_panel(user_id, panel_type, panel)
                        elif panel_type == 'trips':
                            from dash_apps.components.user_trips import render_user_trips
                            panel = render_user_trips(user_data)
                            UsersCacheService.set_cached_panel(user_id, panel_type, panel)
        except Exception as e:
            if UsersCacheService._debug_mode:
                print(f"[PRELOAD] Erreur préchargement {user_id[:8]}: {e}")
    
    @staticmethod
    def preload_user_panels(user_ids: List[str], panel_types: List[str] = None, async_mode: bool = True):
        """
        Précharge les panneaux pour plusieurs utilisateurs en arrière-plan
        
        Args:
            user_ids: Liste des UIDs utilisateurs
            panel_types: Types de panneaux à précharger (défaut: tous)
            async_mode: Si True, utilise threading pour préchargement asynchrone
        """
        if not panel_types:
            panel_types = ['profile', 'stats', 'trips']
        
        # Filtrer les utilisateurs qui ont déjà tous leurs panneaux en cache
        users_to_preload = []
        for user_id in user_ids[:8]:  # Limiter à 8 utilisateurs pour éviter la surcharge
            needs_preload = False
            for panel_type in panel_types:
                cache_key = f"{user_id}_{panel_type}"
                if cache_key not in UsersCacheService._html_cache:
                    needs_preload = True
                    break
            if needs_preload:
                users_to_preload.append(user_id)
        
        if not users_to_preload:
            if UsersCacheService._debug_mode:
                print("[PRELOAD] Tous les panneaux sont déjà en cache")
            return
        
        if UsersCacheService._debug_mode:
            print(f"[PRELOAD] Préchargement de {len(users_to_preload)} utilisateurs x {len(panel_types)} panneaux...")
        
        if async_mode and len(users_to_preload) > 1:
            # Préchargement asynchrone avec threading
            threads = []
            for user_id in users_to_preload:
                thread = threading.Thread(
                    target=UsersCacheService._preload_single_user,
                    args=(user_id, panel_types),
                    daemon=True  # Thread daemon pour ne pas bloquer l'arrêt de l'app
                )
                threads.append(thread)
                thread.start()
            
            # Optionnel : attendre un court délai pour les premiers threads
            for thread in threads[:3]:  # Attendre seulement les 3 premiers
                thread.join(timeout=0.1)  # Timeout très court pour ne pas bloquer
                
        else:
            # Préchargement synchrone pour un seul utilisateur ou si async désactivé
            for user_id in users_to_preload:
                UsersCacheService._preload_single_user(user_id, panel_types)
    
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
        if UsersCacheService._debug_mode:
            print(f"[HTML CACHE] Cache effacé pour utilisateur {user_id[:8]}...")
    
    @staticmethod
    def clear_all_html_cache():
        """Efface tout le cache HTML"""
        UsersCacheService._html_cache.clear()
        if UsersCacheService._debug_mode:
            print("[HTML CACHE] Tout le cache HTML effacé")
    
    @staticmethod
    def get_cache_stats() -> Dict:
        """Retourne des statistiques détaillées sur le cache"""
        return {
            "local_cache_size": len(UsersCacheService._local_cache),
            "html_cache_size": len(UsersCacheService._html_cache),
            "cache_timestamps_size": len(UsersCacheService._cache_timestamps),
            "local_cache_ttl": UsersCacheService._local_cache_ttl,
            "redis_stats": redis_cache.get_cache_stats()
        }
