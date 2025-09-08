"""
Repository de base pour l'accès à Supabase via l'API REST
Fournit les opérations CRUD de base et des fonctions utilitaires
"""
from dash_apps.utils.supabase_client import supabase
from typing import Dict, List, Any, Optional, TypeVar, Generic, Type
import logging
import json
from datetime import datetime

# Logger
logger = logging.getLogger(__name__)

# Type générique pour les modèles
T = TypeVar('T')

class SupabaseRepository:
    """
    Classe de base pour accéder à Supabase via l'API REST
    """
    
    def __init__(self, table_name: str):
        """
        Initialise le repository avec le nom de la table Supabase
        
        Args:
            table_name: Nom de la table dans Supabase
        """
        self.table_name = table_name
    
    def _format_data(self, data: Dict) -> Dict:
        """
        Formate les données avant insertion/mise à jour
        Convertit les dates en ISO format pour Supabase
        
        Args:
            data: Dictionnaire de données à formater
        
        Returns:
            Dictionnaire formaté
        """
        formatted_data = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                formatted_data[key] = value.isoformat()
            else:
                formatted_data[key] = value
        return formatted_data
    
    def get_all(self, limit: int = None, offset: int = None, order_by: str = None, 
                order_direction: str = "asc", filters: Dict = None) -> List[Dict]:
        """
        Récupère tous les enregistrements avec pagination et filtres optionnels
        
        Args:
            limit: Nombre d'enregistrements à récupérer
            offset: Décalage pour la pagination
            order_by: Champ pour le tri
            order_direction: Direction du tri ('asc' ou 'desc')
            filters: Dictionnaire des filtres {champ: valeur}
        
        Returns:
            Liste d'enregistrements sous forme de dictionnaires
        """
        try:
            query = supabase.table(self.table_name).select("*")
            
            # Appliquer les filtres
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            # Appliquer l'ordre
            if order_by:
                query = query.order(order_by, desc=(order_direction.lower() == "desc"))
            
            # Appliquer la pagination
            if offset is not None:
                query = query.range(offset, offset + (limit or 100) - 1)
            elif limit is not None:
                query = query.limit(limit)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de {self.table_name}: {str(e)}")
            return []
    
    def count(self, filters: Dict = None) -> int:
        """
        Compte le nombre d'enregistrements correspondant aux filtres
        
        Args:
            filters: Dictionnaire des filtres {champ: valeur}
        
        Returns:
            Nombre d'enregistrements
        """
        try:
            query = supabase.table(self.table_name).select("*", count="exact")
            
            # Appliquer les filtres
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            response = query.execute()
            return response.count
            
        except Exception as e:
            logger.error(f"Erreur lors du comptage des données de {self.table_name}: {str(e)}")
            return 0
    
    def get_by_id(self, id_field: str, id_value: Any) -> Optional[Dict]:
        """
        Récupère un enregistrement par son ID
        
        Args:
            id_field: Nom du champ ID
            id_value: Valeur de l'ID
        
        Returns:
            Dictionnaire des données ou None si non trouvé
        """
        try:
            response = supabase.table(self.table_name).select("*").eq(id_field, id_value).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {id_field}={id_value} depuis {self.table_name}: {str(e)}")
            return None
    
    def create(self, data: Dict) -> Optional[Dict]:
        """
        Crée un nouvel enregistrement
        
        Args:
            data: Données à insérer
        
        Returns:
            Données insérées avec l'ID généré ou None en cas d'erreur
        """
        try:
            formatted_data = self._format_data(data)
            response = supabase.table(self.table_name).insert(formatted_data).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la création dans {self.table_name}: {str(e)}")
            return None
    
    def update(self, id_field: str, id_value: Any, data: Dict) -> bool:
        """
        Met à jour un enregistrement existant
        
        Args:
            id_field: Nom du champ ID
            id_value: Valeur de l'ID
            data: Données à mettre à jour
        
        Returns:
            True si réussi, False sinon
        """
        try:
            formatted_data = self._format_data(data)
            response = supabase.table(self.table_name).update(formatted_data).eq(id_field, id_value).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de {id_field}={id_value} dans {self.table_name}: {str(e)}")
            return False
    
    def delete(self, id_field: str, id_value: Any) -> bool:
        """
        Supprime un enregistrement
        
        Args:
            id_field: Nom du champ ID
            id_value: Valeur de l'ID
        
        Returns:
            True si réussi, False sinon
        """
        try:
            response = supabase.table(self.table_name).delete().eq(id_field, id_value).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {id_field}={id_value} dans {self.table_name}: {str(e)}")
            return False
