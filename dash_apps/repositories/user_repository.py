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
        from sqlalchemy import func, text
        
        with SessionLocal() as db:
            try:
                # Effectuer tout le travail en une seule requête SQL optimisée
                # en utilisant une requête SQL brute pour plus d'efficacité
                query = text("""
                    WITH user_rank AS (
                        SELECT uid, 
                               ROW_NUMBER() OVER (ORDER BY uid) - 1 AS position
                        FROM users
                    )
                    SELECT position FROM user_rank WHERE uid = :user_id
                """)
                
                result = db.execute(query, {"user_id": user_id}).first()
                
                if result:
                    return result[0]
                return None
                
            except Exception as e:
                print(f"Erreur lors de la récupération de la position de l'utilisateur: {e}")
                return None
            
    @staticmethod
    def get_users_count() -> int:
        """Retourne le nombre total d'utilisateurs dans la base de données
        
        Returns:
            Le nombre total d'utilisateurs
        """
        with SessionLocal() as db:
            return db.query(User).count()
