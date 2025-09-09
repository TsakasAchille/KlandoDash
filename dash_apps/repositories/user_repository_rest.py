"""
Repository pour les utilisateurs utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict, Any
import logging

# Logger
logger = logging.getLogger(__name__)

class UserRepositoryRest(SupabaseRepository):
    """
    Repository pour les utilisateurs utilisant l'API REST Supabase
    """
    
    def __init__(self):
        """
        Initialise le repository avec la table 'users'
        """
        super().__init__("users")
    
    def get_user(self, uid: str) -> Optional[Dict]:
        """
        Alias pour get_user_by_uid pour compatibilité
        
        Args:
            uid: Identifiant unique de l'utilisateur
            
        Returns:
            Dictionnaire contenant les informations de l'utilisateur ou None si non trouvé
        """
        return self.get_user_by_uid(uid)
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict]:
        """
        Récupère un utilisateur par son UID
        
        Args:
            uid: Identifiant unique de l'utilisateur
            
        Returns:
            Dictionnaire contenant les informations de l'utilisateur ou None si non trouvé
        """
        return self.get_by_id("uid", uid)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Récupère un utilisateur par son email
        
        Args:
            email: Adresse email de l'utilisateur
            
        Returns:
            Dictionnaire contenant les informations de l'utilisateur ou None si non trouvé
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            response = supabase.table(self.table_name).select("*").eq("email", email).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur par email {email}: {str(e)}")
            return None
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Liste les utilisateurs avec pagination
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            Liste d'utilisateurs
        """
        return self.get_all(offset=skip, limit=limit, order_by="created_at", order_direction="desc")
    
    def create_user(self, user_data: dict) -> Optional[Dict]:
        """
        Crée un nouvel utilisateur
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            L'utilisateur créé ou None
        """
        return self.create(user_data)
    
    def update_user(self, uid: str, updates: dict) -> Optional[Dict]:
        """
        Met à jour un utilisateur existant
        
        Args:
            uid: Identifiant de l'utilisateur
            updates: Dictionnaire avec les modifications
            
        Returns:
            L'utilisateur mis à jour ou None en cas d'erreur
        """
        if self.update("uid", uid, updates):
            return self.get_by_id("uid", uid)
        return None
    
    def delete_user(self, uid: str) -> bool:
        """
        Supprime un utilisateur
        
        Args:
            uid: Identifiant de l'utilisateur
            
        Returns:
            True si supprimé, False sinon
        """
        return self.delete("uid", uid)
    
    def count_users(self) -> int:
        """
        Compte le nombre total d'utilisateurs
        
        Returns:
            Nombre d'utilisateurs
        """
        return self.count()
    
    def get_users_with_pagination(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Récupère une page d'utilisateurs avec pagination et métadonnées
        
        Args:
            page: Numéro de page (commence à 1)
            page_size: Nombre d'éléments par page
            
        Returns:
            Un dictionnaire contenant la liste des utilisateurs et les métadonnées de pagination
        """
        try:
            # Calculer le décalage (offset)
            skip = (page - 1) * page_size
            
            # Récupérer les utilisateurs pour cette page
            users = self.get_all(
                offset=skip,
                limit=page_size,
                order_by="created_at",
                order_direction="desc"
            )
            
            # Compter le nombre total d'utilisateurs
            total_count = self.count()
            
            # Calculer le nombre total de pages
            total_pages = max(1, (total_count + page_size - 1) // page_size)
            
            return {
                "users": users,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur get_users_with_pagination: {str(e)}")
            return {
                "users": [],
                "pagination": {
                    "total_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 1
                }
            }
    
    def search_users(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Recherche des utilisateurs par nom ou email
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'utilisateurs correspondant à la recherche
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Recherche par nom ou email (utilisation de ilike pour recherche insensible à la casse)
            response = supabase.table(self.table_name)\
                .select("*")\
                .or_(f"display_name.ilike.%{query}%,email.ilike.%{query}%")\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'utilisateurs avec '{query}': {str(e)}")
            return []
    
    def get_user_stats(self, uid: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un utilisateur
        
        Args:
            uid: Identifiant de l'utilisateur
            
        Returns:
            Dictionnaire contenant les statistiques de l'utilisateur
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Récupérer les trajets en tant que conducteur
            driver_trips = supabase.table("trips").select("*").eq("driver_id", uid).execute()
            driver_count = len(driver_trips.data) if driver_trips.data else 0
            
            # Récupérer les réservations en tant que passager
            passenger_bookings = supabase.table("bookings").select("*").eq("user_id", uid).execute()
            passenger_count = len(passenger_bookings.data) if passenger_bookings.data else 0
            
            return {
                "trips_as_driver": driver_count,
                "trips_as_passenger": passenger_count,
                "total_trips": driver_count + passenger_count
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques pour l'utilisateur {uid}: {str(e)}")
            return {
                "trips_as_driver": 0,
                "trips_as_passenger": 0,
                "total_trips": 0
            }
    
    def get_users_paginated(self, page: int = 0, page_size: int = 10, filters: Dict = None) -> Dict[str, Any]:
        """
        Récupère une page d'utilisateurs avec pagination (interface compatible avec le cache service)
        
        Args:
            page: Index de page (commence à 0)
            page_size: Nombre d'éléments par page
            filters: Filtres à appliquer (optionnel)
            
        Returns:
            Dictionnaire avec users, total_count, et table_rows_data
        """
        try:
            from dash_apps.utils.supabase_client import supabase
            
            # Calculer le décalage (offset)
            skip = page * page_size
            
            # Construire la requête de base
            query = supabase.table(self.table_name).select("*")
            
            # Appliquer les filtres si fournis
            if filters:
                # Filtre par texte (nom, email, téléphone)
                if filters.get('text'):
                    text_filter = filters['text']
                    query = query.or_(f"uid.ilike.%{text_filter}%,display_name.ilike.%{text_filter}%,email.ilike.%{text_filter}%,phone_number.ilike.%{text_filter}%")
                
                # Filtre par rôle
                if filters.get('role'):
                    role_filter = filters['role']
                    if role_filter == 'driver':
                        query = query.eq("is_driver", True)
                    elif role_filter == 'passenger':
                        query = query.eq("is_driver", False)
                
                # Filtre par genre
                if filters.get('gender'):
                    query = query.eq("gender", filters['gender'])
                
                # Filtre par validation conducteur
                if filters.get('driver_validation'):
                    if filters['driver_validation'] == 'validated':
                        query = query.eq("is_driver_doc_validated", True)
                    elif filters['driver_validation'] == 'not_validated':
                        query = query.eq("is_driver_doc_validated", False)
            
            # Compter le total avant pagination
            count_response = query.execute()
            total_count = len(count_response.data) if count_response.data else 0
            
            # Appliquer la pagination
            query = query.range(skip, skip + page_size - 1).order("created_at", desc=True)
            
            # Exécuter la requête
            response = query.execute()
            users = response.data if response.data else []
            
            # Préparer les données pour le tableau (compatible avec l'interface existante)
            table_rows_data = []
            for user in users:
                table_rows_data.append({
                    'uid': user.get('uid', ''),
                    'display_name': user.get('display_name', ''),
                    'email': user.get('email', ''),
                    'phone': user.get('phone_number', ''),
                    'gender': user.get('gender', ''),
                    'is_driver': user.get('is_driver', False),
                    'is_driver_doc_validated': user.get('is_driver_doc_validated', False),
                    'created_at': user.get('created_at', ''),
                    'updated_at': user.get('updated_at', '')
                })
            
            return {
                "users": users,
                "total_count": total_count,
                "table_rows_data": table_rows_data
            }
            
        except Exception as e:
            logger.error(f"Erreur get_users_paginated: {str(e)}")
            return {
                "users": [],
                "total_count": 0,
                "table_rows_data": []
            }
