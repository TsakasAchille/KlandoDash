from dash_apps.models.user import User
from dash_apps.schemas.user import UserSchema
from dash_apps.core.database import SessionLocal
from sqlalchemy import text, func, or_, and_
from typing import Dict, List, Optional
import math
import os


class UserRepository:
    # Mode debug pour les logs (désactivé en production)
    _debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
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
    def get_users_paginated(page: int = 0, page_size: int = 10, filters: dict = None) -> dict:
        print(f"[DEBUG] UserRepository.get_users_paginated called with page={page}, page_size={page_size}, filters={filters}")
        """Récupère les utilisateurs de façon paginée avec filtrage optionnel
        
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
            - basic_by_uid: Dictionnaire {uid: données_de_base}
            - table_rows_data: Données formatées pour le tableau
        """
        try:
            print("[DEBUG] Tentative de connexion à la base de données...")
            with SessionLocal() as db:
                print("[DEBUG] Connexion à la base de données réussie")
                # Commencer avec une requête de base
                query = db.query(User)
                
                # Appliquer les filtres si spécifiés
                if filters:
                    # Filtre texte (nom, prénom, email, UID)
                    if filters.get("text"):
                        search_term = f'%{filters["text"]}%'
                        query = query.filter(
                            or_(
                                User.name.ilike(search_term),
                                User.first_name.ilike(search_term),
                                User.email.ilike(search_term),
                                User.display_name.ilike(search_term),
                                User.uid.ilike(search_term)
                            )
                        )
                
                    # Filtrage par date d'inscription
                    # Gestion des filtres de date selon le type
                    date_filter_type = filters.get("date_filter_type", "range")
                    
                    if date_filter_type == "after" and filters.get("single_date"):
                        # Filtrer après une date spécifique
                        single_date = filters["single_date"]
                        if isinstance(single_date, str):
                            single_date = datetime.datetime.fromisoformat(single_date.replace('Z', '+00:00'))
                        query = query.filter(User.created_at >= single_date)
                        
                    elif date_filter_type == "before" and filters.get("single_date"):
                        # Filtrer avant une date spécifique
                        single_date = filters["single_date"]
                        if isinstance(single_date, str):
                            single_date = datetime.datetime.fromisoformat(single_date.replace('Z', '+00:00'))
                            # Ajuster pour inclure toute la journée
                            single_date = single_date.replace(hour=23, minute=59, second=59)
                        query = query.filter(User.created_at <= single_date)
                        
                    else:
                        # Filtrage par période (comportement par défaut)
                        if filters.get("date_from"):
                            date_from = filters["date_from"]
                            if isinstance(date_from, str):
                                date_from = datetime.datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                            query = query.filter(User.created_at >= date_from)
                            
                        if filters.get("date_to"):
                            date_to = filters["date_to"]
                            if isinstance(date_to, str):
                                date_to = datetime.datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                                date_to = date_to.replace(hour=23, minute=59, second=59)
                            query = query.filter(User.created_at <= date_to)
                    
                    # Filtrage par rôle
                    if filters.get("role") and filters["role"] != "all":
                        role = filters["role"]
                        query = query.filter(User.role == role)
                    
                    # Filtrage par validation conducteur
                    if filters.get("driver_validation") and filters["driver_validation"] != "all":
                        validation_status = filters["driver_validation"]
                        if validation_status == "validated":
                            query = query.filter(User.is_driver_doc_validated == True)
                        elif validation_status == "not_validated":
                            query = query.filter(User.is_driver_doc_validated == False)
                            
                    # Filtrage par genre
                    if filters.get("gender") and filters["gender"] != "all":
                        gender = filters["gender"]
                        query = query.filter(User.gender == gender)
                    
                    # Filtrage par rating
                    if filters.get("rating_operator") and filters["rating_operator"] != "all" and filters.get("rating_value") is not None:
                        rating_value = float(filters["rating_value"])
                        operator = filters["rating_operator"]
                        if UserRepository._debug_mode:
                            print("On est ici quoi")
                        if operator == "gt":
                            # Filter rating not null AND greater or equal to rating_value
                            query = query.filter(User.rating.isnot(None), User.rating >= rating_value)
                        elif operator == "lt":
                            # Filter rating not null AND less or equal to rating_value
                            query = query.filter(User.rating.isnot(None), User.rating <= rating_value)
                
                # Appliquer le tri selon les préférences
                date_sort = filters.get("date_sort", "desc") if filters else "desc"
                if date_sort == "asc":
                    query = query.order_by(User.created_at.asc())
                elif date_sort == "desc":
                    query = query.order_by(User.created_at.desc())
                # Si date_sort == "none", pas de tri spécifique par date
                
                # Calculer le nombre total d'utilisateurs après filtrage
                total = query.count()
                
                # Récupérer les utilisateurs de la page demandée
                users = query.offset(page * page_size)\
                    .limit(page_size)\
                    .all()
                    
                # Convertir les modèles en schémas Pydantic puis en dictionnaires JSON-serializable
                user_schemas = [UserSchema.model_validate(u) for u in users]
                users_json = [schema.model_dump() for schema in user_schemas]
                
                # Préparer les données de ligne pour le tableau
                table_rows_data = []
                
                try:
                    for u in users_json:
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
                except Exception:
                    table_rows_data = []
                
                print(f"[DEBUG] Récupéré {len(users_json)} utilisateurs, total={total}")
                
                return {
                    "users": users_json,
                "total_count": total,
                "table_rows_data": table_rows_data
            }
        except Exception as e:
            print(f"[ERROR] Erreur lors de la récupération des utilisateurs: {e}")
            return {
                "users": [],
                "total_count": 0,
                "table_rows_data": []
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
                               ROW_NUMBER() OVER (ORDER BY created_at DESC) - 1 AS position
                        FROM users
                    )
                    SELECT position FROM user_rank WHERE uid = :user_id
                """)
                
                result = db.execute(query, {"user_id": user_id}).first()
                
                if result:
                    return result[0]
                return None
                
            except Exception as e:
                if UserRepository._debug_mode:
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

    @staticmethod
    def get_user_position_in_validation_group(user_id: str, group: str) -> Optional[int]:
        """Retourne la position (0-based) d'un utilisateur dans un sous-ensemble
        filtré par statut de validation, trié par created_at DESC.

        Args:
            user_id: uid de l'utilisateur
            group: 'pending' ou 'validated'

        Returns:
            Index 0-based ou None si non trouvé.
        """
        from sqlalchemy import text
        where_clause = ""
        if group == "validated":
            where_clause = "WHERE is_driver_doc_validated IS TRUE"
        elif group == "pending":
            where_clause = "WHERE (is_driver_doc_validated IS FALSE OR is_driver_doc_validated IS NULL)"
        else:
            return None
        sql = text(f"""
            WITH ranked AS (
              SELECT uid,
                     ROW_NUMBER() OVER (ORDER BY created_at DESC) - 1 AS position
              FROM users
              {where_clause}
            )
            SELECT position FROM ranked WHERE uid = :uid
        """)
        with SessionLocal() as db:
            try:
                res = db.execute(sql, {"uid": user_id}).first()
                return int(res[0]) if res else None
            except Exception as e:
                if UserRepository._debug_mode:
                    print(f"Erreur get_user_position_in_validation_group: {e}")
                return None
