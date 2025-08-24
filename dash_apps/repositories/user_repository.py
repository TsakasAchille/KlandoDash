from dash_apps.models.user import User
from dash_apps.schemas.user import UserSchema
from dash_apps.core.database import SessionLocal
from typing import List, Optional

class UserRepository:
    @staticmethod
    def get_pending_drivers():
        with SessionLocal() as db:
            users = db.query(User).filter(
                ((User.id_card_url != None) | (User.driver_license_url != None)) & 
                (User.is_driver_doc_validated == False)
            ).all()
            return [UserSchema.model_validate(u) for u in users]

    @staticmethod
    def get_validated_drivers():
        with SessionLocal() as db:
            users = db.query(User).filter(
                User.is_driver_doc_validated == True
            ).all()
            return [UserSchema.model_validate(u) for u in users]

    @staticmethod
    def get_all_users() -> List[UserSchema]:
        with SessionLocal() as db:
            users = db.query(User).all()
            return [UserSchema.model_validate(u) for u in users]

    @staticmethod
    def get_user_by_id(uid: str) -> Optional[UserSchema]:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            return UserSchema.model_validate(user) if user else None

    @staticmethod
    def validate_driver_documents(uid: str) -> bool:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            if user:
                user.is_driver_doc_validated = True
                db.commit()
                return True
            return False

    @staticmethod
    def unvalidate_driver_documents(uid: str) -> bool:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            if user:
                user.is_driver_doc_validated = False
                db.commit()
                return True
            return False

    @staticmethod
    def get_users_by_ids(user_ids: list) -> list:
        with SessionLocal() as db:
            users = db.query(User).filter(User.uid.in_(user_ids)).all()
            return [u.to_dict() for u in users] if users else []
            
    @staticmethod
    def get_users_paginated(page: int = 0, page_size: int = 10) -> dict:
        """Récupère les utilisateurs de façon paginée
        
        Args:
            page: Numéro de page (commence à 0)
            page_size: Nombre d'éléments par page
            
        Returns:
            Un dictionnaire contenant:
            - users: Liste des utilisateurs de la page
            - total_count: Nombre total d'utilisateurs
        """
        with SessionLocal() as db:
            # Calculer le nombre total d'utilisateurs
            total = db.query(User).count()
            
            # Récupérer les utilisateurs de la page demandée
            users = db.query(User).order_by(User.uid)\
                .offset(page * page_size)\
                .limit(page_size)\
                .all()
                
            # Convertir les modèles en schémas Pydantic
            user_schemas = [UserSchema.model_validate(u) for u in users]
            
            return {
                "users": user_schemas,
                "total_count": total
            }
    
    @staticmethod
    def get_user_position(user_id: str) -> Optional[int]:
        """Détermine la position absolue d'un utilisateur dans la base de données
        
        Cette fonction est utilisée pour la pagination afin de déterminer sur quelle page
        se trouve un utilisateur spécifique.
        
        Args:
            user_id: L'identifiant unique de l'utilisateur
            
        Returns:
            La position de l'utilisateur (index 0-based) ou None si non trouvé
        """
        from sqlalchemy import func
        
        with SessionLocal() as db:
            # Vérifier d'abord si l'utilisateur existe
            user = db.query(User).filter(User.uid == user_id).first()
            if not user:
                return None
                
            # Compter combien d'utilisateurs ont un UID inférieur à celui-ci
            # pour déterminer sa position dans la liste complète (triée par UID)
            position_query = db.query(func.count(User.id)).filter(User.id < user.id)
            position = position_query.scalar() or 0
            
            return position
            
    @staticmethod
    def get_users_count() -> int:
        """Retourne le nombre total d'utilisateurs dans la base de données
        
        Returns:
            Le nombre total d'utilisateurs
        """
        with SessionLocal() as db:
            return db.query(User).count()
