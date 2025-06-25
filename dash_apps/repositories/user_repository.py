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
            return [UserSchema.from_orm(u) for u in users]

    @staticmethod
    def get_validated_drivers():
        with SessionLocal() as db:
            users = db.query(User).filter(
                User.is_driver_doc_validated == True
            ).all()
            return [UserSchema.from_orm(u) for u in users]

    @staticmethod
    def get_all_users() -> List[UserSchema]:
        with SessionLocal() as db:
            users = db.query(User).all()
            return [UserSchema.from_orm(u) for u in users]

    @staticmethod
    def get_user_by_id(uid: str) -> Optional[UserSchema]:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            return UserSchema.from_orm(user) if user else None

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
