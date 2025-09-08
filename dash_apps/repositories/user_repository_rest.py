"""
Repository pour les utilisateurs utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from dash_apps.schemas.user import UserSchema
from typing import Dict, List, Optional
import math
import os
import logging
from datetime import datetime

# Logger
logger = logging.getLogger(__name__)

class UserRepositoryRest(SupabaseRepository):
    """
    Repository pour les utilisateurs utilisant l'API REST Supabase
    """
    # Mode debug pour les logs (désactivé en production)
    _debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
    
    def __init__(self):
        """
        Initialise le repository avec la table 'users'
        """
        super().__init__("users")
    
    def get_pending_drivers(self) -> List[dict]:
        """
        Récupère les conducteurs en attente de validation
        """
        try:
            # La requête SQL équivalente serait:
            # SELECT * FROM users WHERE
            #   ((id_card_url IS NOT NULL) OR (driver_license_url IS NOT NULL)) AND
            #   (is_driver_doc_validated = FALSE OR is_driver_doc_validated IS NULL)
            
            # Comme les requêtes OR/AND sont complexes avec l'API Supabase,
            # nous allons filtrer en post-traitement
            response = self.get_all()
            
            # Filtrer les utilisateurs qui ont au moins un document et ne sont pas validés
            pending_drivers = []
            for user in response:
                has_document = (user.get("id_card_url") or user.get("driver_license_url"))
                not_validated = (user.get("is_driver_doc_validated") is False or user.get("is_driver_doc_validated") is None)
                
                if has_document and not_validated:
                    pending_drivers.append(user)
            
            return pending_drivers
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des conducteurs en attente: {str(e)}")
            return []
    
    def get_validated_drivers(self) -> List[dict]:
        """
        Récupère les conducteurs validés
        """
        try:
            # Utiliser le filtre 'is_driver_doc_validated' = TRUE
            return self.get_all(filters={"is_driver_doc_validated": True})
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des conducteurs validés: {str(e)}")
            return []
    
    def get_all_users(self) -> List[dict]:
        """
        Récupère tous les utilisateurs
        """
        return self.get_all()
    
    def get_user_by_id(self, uid: str) -> Optional[dict]:
        """
        Récupère un utilisateur par son ID
        """
        return self.get_by_id("uid", uid)
    
    def validate_driver_documents(self, uid: str) -> bool:
        """
        Valide les documents d'un conducteur
        """
        return self.update("uid", uid, {"is_driver_doc_validated": True})
    
    def unvalidate_driver_documents(self, uid: str) -> bool:
        """
        Invalide les documents d'un conducteur
        """
        return self.update("uid", uid, {"is_driver_doc_validated": False})
    
    def get_users_by_ids(self, user_ids: list) -> List[dict]:
        """
        Récupère plusieurs utilisateurs par leurs IDs
        """
        if not user_ids:
            return []
        
        result = []
        for uid in user_ids:
            user = self.get_by_id("uid", uid)
            if user:
                result.append(user)
        
        return result
    
    def get_users_paginated(self, page: int = 0, page_size: int = 10, filters: dict = None) -> dict:
        """
        Récupère les utilisateurs de façon paginée avec filtrage optionnel
        
        Args:
            page: Numéro de page (commence à 0)
            page_size: Nombre d'éléments par page
            filters: Dictionnaire des filtres à appliquer avec les clés suivantes:
                - text: Recherche par nom, prénom ou email
                - date_from: Date d'inscription minimale
                - date_to: Date d'inscription maximale
                - role: Filtrer par rôle (admin, driver, passenger, user)
                - status: Filtrer par statut (active, inactive, suspended)
                - verified: Filtrer par statut de vérification (true/false)
                - has_trips: Filtrer les utilisateurs ayant des trajets
                - has_signalement: Filtrer les utilisateurs avec signalements
        
        Returns:
            Un dictionnaire contenant:
            - users: Liste des utilisateurs de la page
            - total_count: Nombre total d'utilisateurs après filtrage
            - table_rows_data: Données formatées pour le tableau
        """
        if self._debug_mode:
            print(f"[DEBUG] UserRepository.get_users_paginated called with page={page}, page_size={page_size}, filters={filters}")
        
        try:
            print("[DEBUG] Tentative de connexion à Supabase...")
            
            # Initialiser nos paramètres de requête
            supabase_filters = {}
            order_by = "created_at"
            order_direction = "desc"
            
            # Appliquer les filtres de base qui correspondent directement à des colonnes
            if filters:
                # Filtrage par rôle
                if filters.get("role") and filters["role"] != "all":
                    supabase_filters["role"] = filters["role"]
                
                # Filtrage par validation conducteur
                if filters.get("driver_validation") and filters["driver_validation"] != "all":
                    if filters["driver_validation"] == "validated":
                        supabase_filters["is_driver_doc_validated"] = True
                    elif filters["driver_validation"] == "not_validated":
                        supabase_filters["is_driver_doc_validated"] = False
                
                # Filtrage par genre
                if filters.get("gender") and filters["gender"] != "all":
                    supabase_filters["gender"] = filters["gender"]
                
                # Tri par date
                date_sort = filters.get("date_sort", "desc")
                if date_sort in ["asc", "desc"]:
                    order_direction = date_sort
            
            # Récupérer tous les utilisateurs avec les filtres de base
            # Les autres filtres plus complexes seront appliqués en post-traitement
            all_users = self.get_all(order_by=order_by, order_direction=order_direction, filters=supabase_filters)
            
            # Appliquer les filtres complexes en mémoire
            filtered_users = all_users
            
            # Post-filtrage pour les filtres complexes
            if filters:
                # Filtre texte (nom, prénom, email, UID)
                if filters.get("text"):
                    search_term = filters["text"].lower()
                    filtered_users = [
                        u for u in filtered_users if
                        search_term in (u.get("name", "") or "").lower() or
                        search_term in (u.get("first_name", "") or "").lower() or
                        search_term in (u.get("email", "") or "").lower() or
                        search_term in (u.get("display_name", "") or "").lower() or
                        search_term in (u.get("uid", "") or "").lower()
                    ]
                
                # Filtrage par date d'inscription
                date_filter_type = filters.get("date_filter_type", "range")
                
                if date_filter_type == "after" and filters.get("single_date"):
                    # Filtrer après une date spécifique
                    single_date_str = filters["single_date"]
                    if isinstance(single_date_str, str):
                        single_date = datetime.fromisoformat(single_date_str.replace('Z', '+00:00'))
                        filtered_users = [
                            u for u in filtered_users if
                            u.get("created_at") and datetime.fromisoformat(u["created_at"].replace('Z', '+00:00')) >= single_date
                        ]
                        
                elif date_filter_type == "before" and filters.get("single_date"):
                    # Filtrer avant une date spécifique
                    single_date_str = filters["single_date"]
                    if isinstance(single_date_str, str):
                        single_date = datetime.fromisoformat(single_date_str.replace('Z', '+00:00'))
                        single_date = single_date.replace(hour=23, minute=59, second=59)
                        filtered_users = [
                            u for u in filtered_users if
                            u.get("created_at") and datetime.fromisoformat(u["created_at"].replace('Z', '+00:00')) <= single_date
                        ]
                        
                else:
                    # Filtrage par période (comportement par défaut)
                    if filters.get("date_from"):
                        date_from_str = filters["date_from"]
                        if isinstance(date_from_str, str):
                            date_from = datetime.fromisoformat(date_from_str.replace('Z', '+00:00'))
                            filtered_users = [
                                u for u in filtered_users if
                                u.get("created_at") and datetime.fromisoformat(u["created_at"].replace('Z', '+00:00')) >= date_from
                            ]
                            
                    if filters.get("date_to"):
                        date_to_str = filters["date_to"]
                        if isinstance(date_to_str, str):
                            date_to = datetime.fromisoformat(date_to_str.replace('Z', '+00:00'))
                            date_to = date_to.replace(hour=23, minute=59, second=59)
                            filtered_users = [
                                u for u in filtered_users if
                                u.get("created_at") and datetime.fromisoformat(u["created_at"].replace('Z', '+00:00')) <= date_to
                            ]
                
                # Filtrage par rating
                if filters.get("rating_operator") and filters["rating_operator"] != "all" and filters.get("rating_value") is not None:
                    rating_value = float(filters["rating_value"])
                    operator = filters["rating_operator"]
                    
                    if operator == "gt":
                        filtered_users = [
                            u for u in filtered_users if
                            u.get("rating") is not None and u.get("rating") >= rating_value
                        ]
                    elif operator == "lt":
                        filtered_users = [
                            u for u in filtered_users if
                            u.get("rating") is not None and u.get("rating") <= rating_value
                        ]
            
            # Calculer le nombre total d'utilisateurs après filtrage
            total = len(filtered_users)
            
            # Appliquer la pagination
            start_idx = page * page_size
            end_idx = start_idx + page_size
            paginated_users = filtered_users[start_idx:end_idx]
            
            # Préparer les données de ligne pour le tableau
            table_rows_data = []
            
            try:
                for u in paginated_users:
                    uid = u.get("uid")
                    if not uid:
                        continue
                    
                    # Fallback pour phone_number
                    phone_number = u.get("phone_number") or u.get("phone")
                    # Fallback pour created_at
                    created_at = u.get("created_at") or u.get("created_time")
                    
                    # Préparer les données de ligne pour le tableau
                    table_rows_data.append({
                        "uid": uid,
                        "display_name": u.get("display_name", ""),
                        "email": u.get("email", ""),
                        "phone_number": phone_number or "",
                        "role": u.get("role", ""),
                        "gender": u.get("gender", ""),
                        "rating": u.get("rating", None),
                        "created_at": created_at or ""
                    })
            except Exception as e:
                logger.error(f"Erreur lors de la préparation des données de tableau: {str(e)}")
                table_rows_data = []
            
            print(f"[DEBUG] Récupéré {len(paginated_users)} utilisateurs, total={total}")
            
            return {
                "users": paginated_users,
                "total_count": total,
                "table_rows_data": table_rows_data
            }
        except Exception as e:
            logger.error(f"[ERROR] Erreur lors de la récupération des utilisateurs: {str(e)}")
            return {
                "users": [],
                "total_count": 0,
                "table_rows_data": []
            }
    
    def get_user_position(self, user_id: str) -> Optional[int]:
        """
        Détermine la position absolue d'un utilisateur dans la base de données
        
        Cette fonction est utilisée pour la pagination afin de déterminer sur quelle page
        se trouve un utilisateur spécifique.
        
        Args:
            user_id: L'identifiant unique de l'utilisateur
            
        Returns:
            La position de l'utilisateur (index 0-based) ou None si non trouvé
        """
        try:
            # Récupérer tous les utilisateurs triés par date de création
            users = self.get_all(order_by="created_at", order_direction="desc")
            
            # Chercher la position de l'utilisateur
            for i, user in enumerate(users):
                if user.get("uid") == user_id:
                    return i
            
            return None
                
        except Exception as e:
            if self._debug_mode:
                print(f"Erreur lors de la récupération de la position de l'utilisateur: {e}")
            return None
            
    def get_users_count(self) -> int:
        """
        Retourne le nombre total d'utilisateurs dans la base de données
        
        Returns:
            Le nombre total d'utilisateurs
        """
        return self.count()

    def get_user_position_in_validation_group(self, user_id: str, group: str) -> Optional[int]:
        """
        Retourne la position (0-based) d'un utilisateur dans un sous-ensemble
        filtré par statut de validation, trié par created_at DESC.

        Args:
            user_id: uid de l'utilisateur
            group: 'pending' ou 'validated'

        Returns:
            Index 0-based ou None si non trouvé.
        """
        try:
            users = []
            if group == "validated":
                # Récupérer tous les utilisateurs validés
                users = self.get_all(
                    order_by="created_at",
                    order_direction="desc", 
                    filters={"is_driver_doc_validated": True}
                )
            elif group == "pending":
                # Récupérer tous les utilisateurs en attente (pas de filtrage direct possible pour OR)
                all_users = self.get_all(order_by="created_at", order_direction="desc")
                users = [u for u in all_users if not u.get("is_driver_doc_validated", False)]
            else:
                return None
            
            # Chercher la position de l'utilisateur
            for i, user in enumerate(users):
                if user.get("uid") == user_id:
                    return i
            
            return None
                
        except Exception as e:
            if self._debug_mode:
                print(f"Erreur get_user_position_in_validation_group: {e}")
            return None
