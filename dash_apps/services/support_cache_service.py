"""
Service de cache centralisé pour les données des tickets de support
Gère le cache HTML, Redis et les requêtes DB avec pattern Read-Through
"""
import pandas as pd
import os
from typing import Optional, Dict, Any, List
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.local_cache import cache

# Initialiser le repository de tickets via la factory
support_ticket_repository = RepositoryFactory.get_support_ticket_repository()


class SupportCacheService:
    """Service centralisé pour la gestion du cache des tickets de support"""
    
    # Cache HTML en mémoire pour les panneaux générés
    _html_cache: Dict[str, html.Div] = {}
    
    # Cache local en mémoire pour les pages de tickets
    _local_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}
    _max_local_cache_size = 50  # Limite du cache local
    _local_cache_ttl_seconds = 180  # 3 minutes
    
    # Configuration du cache
    _profile_ttl_seconds = 300  # 5 minutes
    _debug_mode = True  # Mode debug pour les logs
    
    @staticmethod
    def _get_cache_key(page_index: int, page_size: int, status: Optional[str], filter_params: Dict[str, Any]) -> str:
        """Génère une clé de cache cohérente pour les pages de tickets"""
        import hashlib
        import json
        
        # Normaliser les filtres pour une clé déterministe
        normalized_filters = filter_params or {}
        filter_str = json.dumps(normalized_filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        
        status_str = status or "all"
        return f"support_tickets:{page_index}:{page_size}:{status_str}:{filter_hash}"
    
    @staticmethod
    def _get_from_local_cache(cache_key: str) -> Optional[Dict]:
        """Récupère les données depuis le cache local avec la clé donnée"""
        return cache.get('support_tickets', key=cache_key)
    
    @staticmethod
    def _store_in_local_cache(cache_key: str, data: Dict):
        """Stocke les données dans le cache local avec timestamp"""
        import time
        SupportCacheService._local_cache[cache_key] = data
        SupportCacheService._cache_timestamps[cache_key] = time.time()
        SupportCacheService._evict_local_cache_if_needed()
    
    @staticmethod
    def _store_in_cache(cache_key: str, data: Dict, ttl_seconds: int = 300):
        """Stocke les données dans le cache local avec TTL"""
        try:
            cache.set('support_tickets', cache_key, data, ttl=ttl_seconds)
            if SupportCacheService._debug_mode:
                print(f"[CACHE] Cache support mis à jour: {cache_key} (TTL: {ttl_seconds}s)")
        except Exception as e:
            print(f"[CACHE] Erreur stockage cache: {e}")
    
    @staticmethod
    def _is_local_cache_valid(cache_key: str) -> bool:
        """Vérifie si l'entrée du cache local est encore valide"""
        import time
        if cache_key not in SupportCacheService._cache_timestamps:
            return False
        age = time.time() - SupportCacheService._cache_timestamps[cache_key]
        return age < SupportCacheService._local_cache_ttl_seconds
    
    @staticmethod
    def _evict_local_cache_if_needed():
        """Éviction LRU simple du cache local si nécessaire"""
        if len(SupportCacheService._local_cache) <= SupportCacheService._max_local_cache_size:
            return
        
        # Trier par timestamp (plus ancien en premier)
        sorted_keys = sorted(SupportCacheService._cache_timestamps.items(), key=lambda x: x[1])
        keys_to_remove = [key for key, _ in sorted_keys[:10]]  # Supprimer les 10 plus anciens
        
        for key in keys_to_remove:
            SupportCacheService._local_cache.pop(key, None)
            SupportCacheService._cache_timestamps.pop(key, None)
    
    @staticmethod
    def get_tickets_page_result(page_index: int, page_size: int, status: Optional[str], filter_params: Dict[str, Any], force_reload: bool = False) -> Dict[str, Any]:
        """
        Récupère les données d'une page de tickets avec cache multi-niveaux optimisé
        
        Args:
            page_index: Index de la page (1-based)
            page_size: Nombre d'éléments par page
            status: Statut des tickets (OPEN, CLOSED, etc.)
            filter_params: Paramètres de filtrage (category, subtype)
            force_reload: Force le rechargement depuis la DB
            
        Returns:
            Dict contenant tickets, total_count, et données pré-calculées
        """
        import time
        # Uniquement utiliser le repository REST de la factory
        # sans import de la DB SQLite
        
        # Unifier la clé L1/L2 en utilisant la méthode interne cohérente
        cache_key = SupportCacheService._get_cache_key(page_index, page_size, status, filter_params)
        
        if not force_reload:
            # Niveau 1: Cache local ultra-rapide (en mémoire)
            if (cache_key in SupportCacheService._local_cache and 
                SupportCacheService._is_local_cache_valid(cache_key)):
                
                if SupportCacheService._debug_mode:
                    try:
                        tickets_count = len(SupportCacheService._local_cache[cache_key].get("tickets", []))
                        total_count = SupportCacheService._local_cache[cache_key].get("total_count", 0)
                        print(f"[SUPPORT][LOCAL CACHE HIT] page_index={page_index} tickets={tickets_count} total={total_count}")
                    except Exception:
                        pass

                cached = SupportCacheService._local_cache[cache_key]
                return cached
            
            # Niveau 2: Cache local centralisé
            cached_data = SupportCacheService._get_from_local_cache(cache_key)
            if cached_data:
                # Stocker dans le cache local pour les prochains accès
                SupportCacheService._store_in_local_cache(cache_key, cached_data)
                
                if SupportCacheService._debug_mode:
                    try:
                        tickets_count = len(cached_data.get("tickets", []))
                        total_count = cached_data.get("total_count", 0)
                        print(f"[SUPPORT][CACHE HIT] page_index={page_index} tickets={tickets_count} total={total_count}")
                    except Exception:
                        pass
                
                return cached_data
        
        # Niveau 3: API REST (via repository)
        try:
            print(f"[SUPPORT][API FETCH] Chargement tickets page {page_index}, status={status}")
            result = support_ticket_repository.get_tickets_paginated_minimal(page_index, page_size, filters=filter_params, status=status)
            print(f"[SUPPORT][API SUCCESS] {len(result.get('tickets', []))} tickets chargés")
        except Exception as e:
            print(f"[SUPPORT][API ERROR] Erreur récupération tickets via API REST: {e}")
            result = {
                "tickets": [],
                "total_count": 0
            }
        
        # Convertir les schémas en dictionnaires pour la sérialisation
        tickets_data = []
        for ticket in result["tickets"]:
            if hasattr(ticket, 'model_dump'):
                tickets_data.append(ticket.model_dump())
            else:
                tickets_data.append(ticket)
        
        # Structure de données cohérente
        cache_data = {
            "tickets": tickets_data,
            "total_count": result["pagination"]["total_count"],
            "pagination": result["pagination"],
            "timestamp": time.time(),
            "status_filter": status
        }
        
        # Mettre à jour tous les niveaux de cache
        SupportCacheService._store_in_local_cache(cache_key, cache_data)
        SupportCacheService._store_in_cache(cache_key, cache_data, ttl_seconds=300)
        
        if SupportCacheService._debug_mode:
            try:
                tickets_count = len(cache_data.get("tickets", []))
                total_count = cache_data.get("total_count", 0)
                print(f"[SUPPORT][FETCH] page_index={page_index} tickets={tickets_count} total={total_count} refresh={force_reload}")
            except Exception:
                pass
        
        return cache_data
    
    @staticmethod
    def get_ticket_details_panel(selected_ticket_id: str):
        """Cache HTML → Redis → DB pour panneau détails ticket"""
        if not selected_ticket_id:
            return html.Div()
        
        # Validation et conversion du ticket_id
        try:
            # Si c'est un dictionnaire, extraire l'ID
            if isinstance(selected_ticket_id, dict):
                selected_ticket_id = selected_ticket_id.get('ticket_id')
                if not selected_ticket_id:
                    return html.Div("ID de ticket invalide", className="alert alert-warning")
            
            # S'assurer que selected_ticket_id est une string valide
            selected_ticket_id = str(selected_ticket_id).strip()
            if not selected_ticket_id or selected_ticket_id == 'None':
                return html.Div("ID de ticket manquant", className="alert alert-warning")
                
        except Exception as e:
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][VALIDATION ERROR] Erreur validation ID: {e}")
            return html.Div("Format d'ID de ticket invalide", className="alert alert-danger")
        
        # Cache HTML
        cached_panel = SupportCacheService.get_cached_panel(selected_ticket_id, 'details')
        if cached_panel:
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][HTML CACHE HIT] Panneau récupéré du cache pour {selected_ticket_id[:8] if selected_ticket_id else 'None'}...")
            return cached_panel
        
        # Cache local centralisé
        data = None
        try:
            cached_ticket = cache.get('support_tickets', key=f"ticket_details:{selected_ticket_id}")
            if cached_ticket:
                if SupportCacheService._debug_mode:
                    print(f"[TICKET_DETAILS][CACHE HIT] Détails récupérés pour {selected_ticket_id[:8] if selected_ticket_id else 'None'}...")
                data = cached_ticket
        except Exception:
            pass
        
        # API REST
        if not data:
            try:
                if SupportCacheService._debug_mode:
                    print(f"[TICKET_DETAILS][API FETCH] Chargement {selected_ticket_id[:8] if selected_ticket_id else 'None'}... via API REST")
                
                # Utiliser l'API REST via le repository pour récupérer le ticket
                from dash_apps.repositories.support_ticket_repository_rest import SupportTicketRepositoryRest
                
                try:
                    # Validation finale avant requête API
                    if not selected_ticket_id or len(selected_ticket_id.strip()) == 0:
                        if SupportCacheService._debug_mode:
                            print(f"[TICKET_DETAILS][API ERROR] ID de ticket vide ou invalide")
                        return html.Div("ID de ticket invalide", className="alert alert-warning")
                    
                    # Récupérer le ticket via l'API REST
                    repo = SupportTicketRepositoryRest()
                    ticket_data = repo.get_ticket(selected_ticket_id)
                    
                    if not ticket_data:
                        if SupportCacheService._debug_mode:
                            print(f"[TICKET_DETAILS][API ERROR] Ticket {selected_ticket_id[:8] if selected_ticket_id else 'None'}... non trouvé via API REST")
                        return html.Div("Ticket non trouvé", className="alert alert-warning")
                    
                    # Utiliser directement les données du ticket
                    data = ticket_data
                    
                    if SupportCacheService._debug_mode:
                        print(f"[TICKET_DETAILS][API SUCCESS] Ticket chargé: {data.get('subject', 'N/A')[:50]}...")
                
                except Exception as api_error:
                    if SupportCacheService._debug_mode:
                        print(f"[TICKET_DETAILS][API ERROR] Erreur de connexion à l'API: {api_error}")
                    
                    # Message d'erreur utilisateur friendly
                    return html.Div([
                        html.H5("⚠️ Problème de connexion", className="text-warning"),
                        html.P("Impossible de se connecter à l'API Supabase."),
                        html.P("Veuillez réessayer dans quelques instants."),
                        html.Button("🔄 Réessayer", id="retry-connection-btn", className="btn btn-primary btn-sm")
                    ], className="alert alert-warning text-center p-4")
                    
                # Cache ticket details
                try:
                    cache.set('support_tickets', f"ticket_details:{selected_ticket_id}", data, ttl=SupportCacheService._profile_ttl_seconds)
                    if SupportCacheService._debug_mode:
                        print(f"[TICKET_DETAILS][CACHE] Ticket mis en cache local")
                except Exception as cache_error:
                    if SupportCacheService._debug_mode:
                        print(f"[TICKET_DETAILS][CACHE ERROR] Erreur cache local: {cache_error}")
            except Exception as e:
                if SupportCacheService._debug_mode:
                    import traceback
                    print(f"[TICKET_DETAILS][API ERROR] Erreur lors du chargement depuis l'API: {e}")
                    print(f"[TICKET_DETAILS][API ERROR] Traceback: {traceback.format_exc()}")
                return html.Div(f"Erreur lors du chargement du ticket: {str(e)}", className="alert alert-danger")
        
        # Render
        try:
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][RENDER] Début génération panneau pour {selected_ticket_id[:8] if selected_ticket_id else 'None'}...")
            
            from dash_apps.components.support_tickets import render_ticket_details
            from dash_apps.callbacks.support_callbacks import load_comments_for_ticket
            
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][RENDER] Chargement commentaires...")
            comments = load_comments_for_ticket(selected_ticket_id)
            
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][RENDER] Génération panneau avec {len(comments) if comments else 0} commentaires...")
            panel = render_ticket_details(data, comments)
            
            if SupportCacheService._debug_mode:
                print(f"[TICKET_DETAILS][RENDER] Panneau généré avec succès, mise en cache...")
            SupportCacheService.set_cached_panel(selected_ticket_id, 'details', panel)
            return panel
        except Exception as e:
            if SupportCacheService._debug_mode:
                import traceback
                print(f"[TICKET_DETAILS] Erreur génération panneau: {e}")
                print(f"[TICKET_DETAILS] Traceback: {traceback.format_exc()}")
            return html.Div(f"Erreur lors du chargement des détails du ticket: {str(e)}", className="alert alert-danger")
    
    @staticmethod
    def get_cached_panel(ticket_id: str, panel_type: str) -> Optional[html.Div]:
        """
        Récupère un panneau HTML en cache avec gestion intelligente
        
        Args:
            ticket_id: ID du ticket
            panel_type: Type de panneau ('details', 'comments')
            
        Returns:
            html.Div: Panneau en cache ou None si non trouvé
        """
        cache_key = f"{ticket_id}_{panel_type}"
        
        # Vérifier d'abord le cache HTML local
        if cache_key in SupportCacheService._html_cache:
            if SupportCacheService._debug_mode:
                print(f"[HTML_CACHE] Cache hit pour {cache_key}")
            return SupportCacheService._html_cache[cache_key]
        
        return None
    
    @staticmethod
    def set_cached_panel(ticket_id: str, panel_type: str, panel: html.Div):
        """
        Met en cache un panneau HTML généré
        
        Args:
            ticket_id: ID du ticket
            panel_type: Type de panneau ('details', 'comments')
            panel: Panneau HTML à mettre en cache
        """
        cache_key = f"{ticket_id}_{panel_type}"
        SupportCacheService._html_cache[cache_key] = panel
        
        if SupportCacheService._debug_mode:
            print(f"[HTML_CACHE] Panneau {panel_type} mis en cache pour ticket {ticket_id[:8] if ticket_id else 'None'}...")
    
    @staticmethod
    def clear_ticket_cache(ticket_id: str):
        """
        Efface le cache pour un ticket spécifique
        
        Args:
            ticket_id: ID du ticket
        """
        keys_to_remove = [key for key in SupportCacheService._html_cache.keys() if key.startswith(f"{ticket_id}_")]
        for key in keys_to_remove:
            del SupportCacheService._html_cache[key]
        
        if SupportCacheService._debug_mode:
            print(f"[HTML_CACHE] Cache effacé pour ticket {ticket_id[:8] if ticket_id else 'None'}...")
    
    @staticmethod
    def clear_all_html_cache():
        """Efface tout le cache HTML"""
        SupportCacheService._html_cache.clear()
        if SupportCacheService._debug_mode:
            print("[HTML_CACHE] Tout le cache HTML effacé")
    
    @staticmethod
    def clear_all_cache():
        """Efface tous les caches (local + HTML)"""
        SupportCacheService._local_cache.clear()
        SupportCacheService._cache_timestamps.clear()
        SupportCacheService._html_cache.clear()
        if SupportCacheService._debug_mode:
            print("[SUPPORT_CACHE] Tous les caches effacés")
    
    @staticmethod
    def get_cache_stats() -> Dict[str, int]:
        """Retourne les statistiques du cache"""
        return {
            "local_cache_size": len(SupportCacheService._local_cache),
            "html_cache_size": len(SupportCacheService._html_cache),
            "max_local_size": SupportCacheService._max_local_cache_size,
            "ttl_seconds": SupportCacheService._local_cache_ttl_seconds
        }
