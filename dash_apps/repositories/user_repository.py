from dash_apps.models.user import User
from dash_apps.schemas.user import UserSchema
from dash_apps.core.database import SessionLocal
from typing import List, Optional

class UserRepository:
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
    def create_user(user_data: UserSchema) -> UserSchema:
        with SessionLocal() as db:
            db_user = User(**user_data.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return UserSchema.from_orm(db_user)

    @staticmethod
    def update_user(uid: str, user_data: UserSchema) -> Optional[UserSchema]:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            if not user:
                return None
            for field, value in user_data.dict(exclude_unset=True).items():
                setattr(user, field, value)
            db.commit()
            db.refresh(user)
            return UserSchema.from_orm(user)

    @staticmethod
    def delete_user(uid: str) -> bool:
        with SessionLocal() as db:
            user = db.query(User).filter(User.uid == uid).first()
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True
