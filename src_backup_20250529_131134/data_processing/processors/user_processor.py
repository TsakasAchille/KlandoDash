from src.core.database import User, Transaction, get_session
import pandas as pd

class UserProcessor:
    """Gestionnaire optimisé des utilisateurs (lecture seule)"""

    @staticmethod
    def get_all_users():
        """Retourne tous les utilisateurs de la base (DataFrame)"""
        with get_session() as session:
            users = session.query(User).all()
            valid_users = [u for u in users if u is not None]
            return pd.DataFrame([u.to_dict() for u in valid_users]) if valid_users else pd.DataFrame()

    @staticmethod
    def get_user_by_id(user_id):
        """Retourne un utilisateur par son ID (dict)"""
        with get_session() as session:
            user = session.query(User).filter(User.uid == user_id).first()
            return user.to_dict() if user else None

    @staticmethod
    def get_users_by_ids(user_ids):
        """Retourne tous les utilisateurs dont l'ID est dans user_ids (DataFrame)"""
        if not user_ids:
            return pd.DataFrame()
        with get_session() as session:
            users = session.query(User).filter(User.uid.in_(user_ids)).all()
            valid_users = [u for u in users if u is not None]
            return pd.DataFrame([u.to_dict() for u in valid_users]) if valid_users else pd.DataFrame()

    @staticmethod
    def get_user_transaction_types(user_id):
        with get_session() as session:
            service_codes = (
                session.query(Transaction.service_code)
                .filter(Transaction.user_id == str(user_id))  # user_id référence users.uid
                .distinct()
                .all()
            )
            types = [code[0] for code in service_codes if code[0]]
            return types if types else ["Aucune transaction"]
