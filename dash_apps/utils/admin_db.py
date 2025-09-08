# Fonctions pour gérer les utilisateurs autorisés dans la base de données
from sqlalchemy import text
import os
from sqlalchemy import create_engine

# Récupère la DATABASE_URL depuis les variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")

# Si DATABASE_URL n'est pas défini, utiliser SQLite comme fallback
if not DATABASE_URL:
    # Chemin vers la base de données locale
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dash_apps', 'users.db')
    DATABASE_URL = f"sqlite:///{sqlite_path}"
    print(f"[INFO] Utilisation de la base de données SQLite locale: {sqlite_path}")

# Créer l'engine avec l'URL appropriée
engine = create_engine(DATABASE_URL)

from datetime import datetime

def get_all_authorized_users():
    """
    Récupère tous les utilisateurs autorisés depuis la table dash_authorized_users.
    """
    query = text("""
        SELECT * FROM dash_authorized_users ORDER BY added_at DESC
    """)
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            users = [dict(row._mapping) for row in result]
            return users
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des utilisateurs autorisés: {str(e)}")
        return []

def add_authorized_user(email, role, added_by, notes=None):
    """
    Ajoute un nouvel utilisateur autorisé à la table dash_authorized_users.
    """
    # Normaliser l'email (minuscules)
    email = email.lower().strip()
    
    query = text("""
        INSERT INTO dash_authorized_users (email, active, role, added_at, updated_at, added_by, notes)
        VALUES (:email, TRUE, :role, :added_at, :updated_at, :added_by, :notes)
        ON CONFLICT (email) 
        DO UPDATE SET 
            active = TRUE,
            role = :role,
            updated_at = :updated_at,
            added_by = :added_by,
            notes = CASE 
                WHEN dash_authorized_users.notes IS NULL THEN :notes
                ELSE dash_authorized_users.notes || ' | ' || :update_note
            END
        RETURNING email, role
    """)
    
    current_time = datetime.now()
    update_note = f"Mis à jour le {current_time.strftime('%Y-%m-%d %H:%M')} par {added_by}"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {
                    "email": email,
                    "role": role,
                    "added_at": current_time,
                    "updated_at": current_time,
                    "added_by": added_by,
                    "notes": notes or "",
                    "update_note": update_note
                }
            )
            conn.commit()
            return True, "Utilisateur ajouté/mis à jour avec succès"
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'ajout de l'utilisateur autorisé: {str(e)}")
        return False, f"Erreur: {str(e)}"

def update_user_status(email, active, updated_by):
    """
    Active ou désactive un utilisateur dans la table dash_authorized_users.
    """
    query = text("""
        UPDATE dash_authorized_users
        SET active = :active, updated_at = :updated_at,
            notes = CASE 
                WHEN notes IS NULL THEN :update_note
                ELSE notes || ' | ' || :update_note
            END
        WHERE email = :email
        RETURNING email, active
    """)
    
    current_time = datetime.now()
    status_text = "activé" if active else "désactivé"
    update_note = f"Compte {status_text} le {current_time.strftime('%Y-%m-%d %H:%M')} par {updated_by}"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {
                    "email": email,
                    "active": active,
                    "updated_at": current_time,
                    "update_note": update_note
                }
            )
            conn.commit()
            return True, f"Statut de l'utilisateur mis à jour: {status_text}"
    except Exception as e:
        print(f"[ERROR] Erreur lors de la mise à jour du statut de l'utilisateur: {str(e)}")
        return False, f"Erreur: {str(e)}"

def update_user_role(email, new_role, updated_by):
    """
    Met à jour le rôle d'un utilisateur dans la table dash_authorized_users.
    """
    query = text("""
        UPDATE dash_authorized_users
        SET role = :new_role, updated_at = :updated_at,
            notes = CASE 
                WHEN notes IS NULL THEN :update_note
                ELSE notes || ' | ' || :update_note
            END
        WHERE email = :email
        RETURNING email, role
    """)
    
    current_time = datetime.now()
    update_note = f"Rôle changé à '{new_role}' le {current_time.strftime('%Y-%m-%d %H:%M')} par {updated_by}"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {
                    "email": email,
                    "new_role": new_role,
                    "updated_at": current_time,
                    "update_note": update_note
                }
            )
            conn.commit()
            return True, f"Rôle de l'utilisateur mis à jour: {new_role}"
    except Exception as e:
        print(f"[ERROR] Erreur lors de la mise à jour du rôle de l'utilisateur: {str(e)}")
        return False, f"Erreur: {str(e)}"

def is_user_authorized(email):
    """
    Vérifie si un utilisateur est autorisé (présent dans dash_authorized_users avec active = TRUE).
    """
    if not email:
        return False
        
    query = text("""
        SELECT email FROM dash_authorized_users 
        WHERE email = :email AND active = TRUE
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"email": email.lower().strip()}).fetchone()
            return result is not None
    except Exception as e:
        print(f"[ERROR] Erreur lors de la vérification de l'autorisation: {str(e)}")
        return False

def get_user_role(email):
    """
    Récupère le rôle d'un utilisateur depuis la table dash_authorized_users.
    """
    if not email:
        return None
        
    query = text("""
        SELECT role FROM dash_authorized_users 
        WHERE email = :email AND active = TRUE
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"email": email.lower().strip()}).fetchone()
            if result:
                return result[0]
            return None
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération du rôle: {str(e)}")
        return None

def is_admin(email):
    """
    Vérifie si un utilisateur a le rôle d'administrateur.
    """
    if not email:
        return False
        
    query = text("""
        SELECT role FROM dash_authorized_users 
        WHERE email = :email AND active = TRUE
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"email": email}).fetchone()
            if result and result[0] == 'admin':
                return True
            return False
    except Exception as e:
        print(f"[ERROR] Erreur lors de la vérification du rôle admin: {str(e)}")
        return False

def delete_user(email, deleted_by):
    """
    Supprime définitivement un utilisateur de la table dash_authorized_users.
    
    Args:
        email (str): Email de l'utilisateur à supprimer
        deleted_by (str): Email de l'administrateur qui effectue la suppression
        
    Returns:
        tuple: (success, message)
    """
    # Vérifier d'abord si l'utilisateur existe
    check_query = text("""
        SELECT email FROM dash_authorized_users WHERE email = :email
    """)
    
    delete_query = text("""
        DELETE FROM dash_authorized_users WHERE email = :email RETURNING email
    """)
    
    try:
        with engine.connect() as conn:
            # Vérifier si l'utilisateur existe
            check_result = conn.execute(check_query, {"email": email}).fetchone()
            if not check_result:
                return False, f"Utilisateur {email} non trouvé"
            
            # Logger l'action de suppression (optionnel)
            current_time = datetime.now()
            log_message = f"Utilisateur {email} supprimé le {current_time.strftime('%Y-%m-%d %H:%M')} par {deleted_by}"
            print(f"[INFO] {log_message}")
            
            # Exécuter la suppression
            result = conn.execute(delete_query, {"email": email})
            conn.commit()
            
            return True, f"Utilisateur {email} supprimé avec succès"
    except Exception as e:
        print(f"[ERROR] Erreur lors de la suppression de l'utilisateur: {str(e)}")
        return False, f"Erreur: {str(e)}"
