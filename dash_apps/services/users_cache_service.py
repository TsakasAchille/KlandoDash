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
    _local_cache_ttl = int(os.getenv('LOCAL_CACHE_TTL', '45'))  # TTL local configurable (par défaut 45s)
    _local_max_entries = int(os.getenv('LOCAL_CACHE_MAX_ENTRIES', '200'))  # Limite max d'entrées en L1
    _profile_ttl_seconds = 600  # 10 minutes pour le profil utilisateur en Redis
    
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
    def _get_from_local_cache(cache_key: str) -> Optional[Dict]:
        """Récupère les données du cache local si valides"""
        if (cache_key in UsersCacheService._local_cache and 
            UsersCacheService._is_local_cache_valid(cache_key)):
            return UsersCacheService._local_cache[cache_key]
        return None
    
    @staticmethod
    def _get_from_redis_cache(cache_key: str, page_index: int, page_size: int, filters: Dict) -> Optional[Dict]:
        """Récupère les données du cache Redis"""
        try:
            return redis_cache.get_json_by_key(cache_key)
        except Exception:
            return None
    
    @staticmethod
    def _store_in_local_cache(cache_key: str, result: Dict):
        """Stocke les données dans le cache local"""
        UsersCacheService._local_cache[cache_key] = result
        UsersCacheService._cache_timestamps[cache_key] = time.time()
        UsersCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def _store_in_redis_cache(cache_key: str, result: Dict, page_index: int, page_size: int, filters: Dict):
        """Stocke les données dans le cache Redis"""
        try:
            redis_cache.set_users_page_from_result(result, page_index, page_size, filters, ttl_seconds=300)
        except Exception:
            pass
    
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
                             force_reload: bool = False, selected_uid: Optional[str] = None) -> Dict:
        """
        Récupère le résultat brut d'une page d'utilisateurs avec cache multi-niveaux optimisé
        
        Returns:
            Dict: Résultat complet du repository (users, total_count, basic_by_uid, table_rows_data)
        """
        import time
        
        # Unifier la clé L1/L2 en utilisant la clé publique de Redis
        cache_key = redis_cache.make_users_page_key(page_index, page_size, filter_params)
        
        if not force_reload:
            # Niveau 1: Cache local ultra-rapide (en mémoire)
            if (cache_key in UsersCacheService._local_cache and 
                UsersCacheService._is_local_cache_valid(cache_key)):
                
                if UsersCacheService._debug_mode:
                    try:
                        users_count = len(UsersCacheService._local_cache[cache_key].get("users", []))
                        total_count = UsersCacheService._local_cache[cache_key].get("total_count", 0)
                        print(f"[USERS][LOCAL CACHE HIT] page_index={page_index} users={users_count} total={total_count}")
                    except Exception:
                        pass

                cached = UsersCacheService._local_cache[cache_key]
                return cached
            
            # Niveau 2: Cache Redis
            cached_data = redis_cache.get_json_by_key(cache_key)
            if cached_data:
                # Stocker dans le cache local pour les prochains accès
                UsersCacheService._local_cache[cache_key] = cached_data
                UsersCacheService._cache_timestamps[cache_key] = time.time()
                # Éviction LRU simple si nécessaire
                UsersCacheService._evict_local_cache_if_needed()
                
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
        # Éviction LRU simple si nécessaire
        UsersCacheService._evict_local_cache_if_needed()
        
        if UsersCacheService._debug_mode:
            try:
                users_count = len(result.get("users", []))
                total_count = result.get("total_count", 0)
                print(f"[USERS][FETCH] page_index={page_index} users={users_count} total={total_count} refresh={force_reload}")
            except Exception:
                pass
        
        return result

    @staticmethod
    def _evict_local_cache_if_needed():
        """
        Évite la dérive mémoire du cache local par une éviction LRU approximative
        basée sur les timestamps. Supprime les plus anciens jusqu'à rentrer
        sous la limite _local_max_entries.
        """
        try:
            size = len(UsersCacheService._local_cache)
            if size <= UsersCacheService._local_max_entries:
                return
            # Trier les clés par ancienneté (timestamp croissant)
            items = sorted(
                UsersCacheService._cache_timestamps.items(), key=lambda kv: kv[1]
            )
            to_remove = size - UsersCacheService._local_max_entries
            removed = 0
            for key, _ in items:
                if key in UsersCacheService._local_cache:
                    del UsersCacheService._local_cache[key]
                if key in UsersCacheService._cache_timestamps:
                    del UsersCacheService._cache_timestamps[key]
                removed += 1
                if removed >= to_remove:
                    break
            if UsersCacheService._debug_mode:
                print(f"[USERS][LOCAL CACHE EVICT] removed={removed} size={len(UsersCacheService._local_cache)}")
        except Exception:
            # Éviter tout crash dû à l'éviction
            pass

    @staticmethod
    def invalidate_local_users_pages(predicate=None):
        """
        Invalide (supprime) des entrées du cache local L1.
        predicate: callable optionnel de signature (key: str, value: Dict) -> bool
                   si None, invalide toutes les entrées.
        """
        try:
            keys = list(UsersCacheService._local_cache.keys())
            for key in keys:
                value = UsersCacheService._local_cache.get(key)
                if predicate is None or (callable(predicate) and predicate(key, value)):
                    del UsersCacheService._local_cache[key]
                    if key in UsersCacheService._cache_timestamps:
                        del UsersCacheService._cache_timestamps[key]
            if UsersCacheService._debug_mode:
                print(f"[USERS][LOCAL CACHE INVALIDATE] size={len(UsersCacheService._local_cache)}")
        except Exception:
            pass

    
    @staticmethod
    def extract_table_data(result: Dict) -> Tuple[List, int, List]:
        """
        Extrait les données nécessaires pour le rendu du tableau
        
        Returns:
            Tuple[users, total_users, table_rows_data]
        """
        users = result.get("users", [])
        total_users = int(result.get("total_count", 0))
        table_rows_data = result.get("table_rows_data", [])
        
        return users, total_users, table_rows_data

    def get_users_page_data(self, page_index: int = 0, page_size: int = 10, filters: dict = None, force_reload: bool = False, selected_uid: str = None) -> dict:
        """
        Récupère les données complètes pour une page d'utilisateurs avec cache intelligent
        
        Args:
            page_index: Index de la page (0-based)
            page_size: Nombre d'utilisateurs par page
            filters: Filtres à appliquer
            force_reload: Force le rechargement depuis la DB
            selected_uid: UID de l'utilisateur sélectionné
            
        Returns:
            Dict contenant users, total_count, table_rows_data
        """
        print(f"[DEBUG] get_users_page_data called with page_index={page_index}, page_size={page_size}, filters={filters}, force_reload={force_reload}")
        
        # Générer une clé de cache basée sur les paramètres
        cache_key = UsersCacheService._get_cache_key(page_index, page_size, filters)
        
        # Vérifier le cache local d'abord (si pas de force reload)
        if not force_reload:
            cached_result = UsersCacheService._get_from_local_cache(cache_key)
            if cached_result:
                print(f"[LOCAL CACHE HIT] Page {page_index} récupérée du cache local")
                return cached_result
            else:
                print(f"[LOCAL CACHE MISS] Pas de cache local pour page {page_index}")
        
        # Vérifier le cache Redis
        if not force_reload:
            cached_result = UsersCacheService._get_from_redis_cache(cache_key, page_index, page_size, filters)
            if cached_result:
                print(f"[REDIS CACHE HIT] Page {page_index} récupérée du cache Redis")
                # Stocker en cache local pour les prochains accès
                UsersCacheService._store_in_local_cache(cache_key, cached_result)
                return cached_result
            else:
                print(f"[REDIS CACHE MISS] Pas de cache Redis pour page {page_index}")
        
        # Charger depuis la base de données
        print(f"[DEBUG] Chargement depuis la base de données...")
        try:
            result = UserRepository.get_users_paginated(page_index, page_size, filters=filters)
            print(f"[DEBUG] Résultat DB: {len(result.get('users', []))} utilisateurs, total={result.get('total_count', 0)}")
            
            # Stocker le résultat dans les caches
            UsersCacheService._store_in_local_cache(cache_key, result)
            UsersCacheService._store_in_redis_cache(cache_key, result, page_index, page_size, filters)
            
            return result
            
        except Exception as e:
            print(f"[DB ERROR] Erreur chargement page {page_index}: {e}")
            return {
                "users": [],
                "total_count": 0,
                "table_rows_data": []
            }
    
    @staticmethod
    def get_user_profile_panel(selected_uid: str):
        """Cache HTML → Redis → DB pour panneau profil"""
        if not selected_uid:
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'profile')
        if cached_panel:
            if UsersCacheService._debug_mode:
                print(f"[PROFILE][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_profile = redis_cache.get_user_profile(selected_uid)
            if cached_profile:
                if UsersCacheService._debug_mode:
                    print(f"[PROFILE][REDIS HIT] Profil récupéré pour {selected_uid[:8]}...")
                data = cached_profile
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if UsersCacheService._debug_mode:
                    print(f"[PROFILE][DB FETCH] Chargement {selected_uid[:8]}... depuis la DB")
                user_schema = UserRepository.get_user_by_id(selected_uid)
                if not user_schema:
                    return html.Div()
                data = user_schema.model_dump() if hasattr(user_schema, "model_dump") else user_schema.dict()
                # Cache profile
                try:
                    redis_cache.set_user_profile(selected_uid, data, ttl_seconds=UsersCacheService._profile_ttl_seconds)
                except Exception:
                    pass
            except Exception:
                return html.Div()
        
        # Render
        try:
            from dash_apps.components.user_profile import render_user_profile
            panel = render_user_profile(data)
            UsersCacheService.set_cached_panel(selected_uid, 'profile', panel)
            return panel
        except Exception as e:
            if UsersCacheService._debug_mode:
                print(f"[PROFILE] Erreur génération panneau: {e}")
            return html.Div()
    
    @staticmethod
    def get_user_stats_panel(selected_uid: str):
        """Cache HTML → Redis → DB pour panneau stats"""
        if not selected_uid:
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'stats')
        if cached_panel:
            if UsersCacheService._debug_mode:
                print(f"[STATS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_stats = redis_cache.get_user_stats(selected_uid)
            if cached_stats:
                if UsersCacheService._debug_mode:
                    print(f"[STATS][REDIS HIT] Stats récupérées pour {selected_uid[:8]}...")
                data = {'uid': selected_uid, 'stats': cached_stats}
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if UsersCacheService._debug_mode:
                    print(f"[STATS][DB FETCH] Chargement {selected_uid[:8]}... depuis la DB")
                from dash_apps.utils.data_schema import get_user_stats_optimized
                stats = get_user_stats_optimized(selected_uid)
                data = {'uid': selected_uid, 'stats': stats}
                # Cache stats
                try:
                    redis_cache.set_user_stats(selected_uid, stats, ttl_seconds=UsersCacheService._profile_ttl_seconds)
                except Exception:
                    pass
            except Exception:
                return html.Div()
        
        # Render
        try:
            from dash_apps.components.user_stats import render_user_stats
            panel = render_user_stats(data)
            UsersCacheService.set_cached_panel(selected_uid, 'stats', panel)
            return panel
        except Exception as e:
            if UsersCacheService._debug_mode:
                print(f"[STATS] Erreur génération panneau: {e}")
            return html.Div()
    
    @staticmethod
    def get_user_trips_panel(selected_uid: str):
        """Cache HTML → Redis → DB pour panneau trips"""
        if not selected_uid:
            return html.Div()
        
        # Cache HTML
        cached_panel = UsersCacheService.get_cached_panel(selected_uid, 'trips')
        if cached_panel:
            if UsersCacheService._debug_mode:
                print(f"[TRIPS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_uid[:8]}...")
            return cached_panel
        
        # Redis
        data = None
        try:
            cached_trips = redis_cache.get_user_trips(selected_uid)
            if cached_trips:
                if UsersCacheService._debug_mode:
                    print(f"[TRIPS][REDIS HIT] Trips récupérés pour {selected_uid[:8]}...")
                import pandas as pd
                data = {'uid': selected_uid, 'trips': pd.DataFrame(cached_trips)}
        except Exception:
            pass
        
        # DB
        if not data:
            try:
                if UsersCacheService._debug_mode:
                    print(f"[TRIPS][DB FETCH] Chargement {selected_uid[:8]}... depuis la DB")
                from dash_apps.utils.data_schema import get_user_trips_with_role
                trips_df = get_user_trips_with_role(str(selected_uid), limit=50)
                data = {'uid': selected_uid, 'trips': trips_df}
                # Cache trips
                try:
                    redis_cache.set_user_trips(selected_uid, trips_df, ttl_seconds=UsersCacheService._profile_ttl_seconds)
                except Exception:
                    pass
            except Exception:
                return html.Div()
        
        # Render
        try:
            from dash_apps.components.user_trips import render_user_trips
            panel = render_user_trips(data)
            UsersCacheService.set_cached_panel(selected_uid, 'trips', panel)
            return panel
        except Exception as e:
            if UsersCacheService._debug_mode:
                print(f"[TRIPS] Erreur génération panneau: {e}")
            return html.Div()
    
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
            # Précharger chaque panneau via get_user_panel (Read-Through cohérent)
            for panel_type in panel_types:
                cache_key = f"{user_id}_{panel_type}"
                if cache_key not in UsersCacheService._html_cache:
                    # Utiliser la méthode Read-Through pour cohérence
                    UsersCacheService.get_user_panel(user_id, panel_type)
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
