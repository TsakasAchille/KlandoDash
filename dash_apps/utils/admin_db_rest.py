"""
Fonctions pour gérer les utilisateurs autorisés via l'API REST Supabase
Version adaptée de admin_db.py qui utilise l'API REST au lieu de la connexion PostgreSQL directe
"""
from datetime import datetime
from dash_apps.utils.supabase_client import supabase

def get_all_authorized_users():
    """
    Récupère tous les utilisateurs autorisés depuis la table dash_authorized_users.
    """
    try:
        response = supabase.table("dash_authorized_users").select("*").order("added_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des utilisateurs autorisés: {str(e)}")
        return []

def add_authorized_user(email, role, added_by, notes=None):
    """
    Ajoute un nouvel utilisateur autorisé à la table dash_authorized_users.
    """
    # Normaliser l'email (minuscules)
    email = email.lower().strip()
    
    current_time = datetime.now().isoformat()
    update_note = f"Mis à jour le {datetime.now().strftime('%Y-%m-%d %H:%M')} par {added_by}"
    
    try:
        # Vérifier si l'utilisateur existe déjà
        response = supabase.table("dash_authorized_users").select("*").eq("email", email).execute()
        
        if response.data:
            # Mise à jour d'un utilisateur existant
            user = response.data[0]
            notes_updated = user.get("notes") + f" | {update_note}" if user.get("notes") else update_note
            
            response = supabase.table("dash_authorized_users").update({
                "active": True,
                "role": role,
                "updated_at": current_time,
                "added_by": added_by,
                "notes": notes_updated
            }).eq("email", email).execute()
            
            return True, "Utilisateur mis à jour avec succès"
        else:
            # Ajout d'un nouvel utilisateur
            response = supabase.table("dash_authorized_users").insert({
                "email": email,
                "active": True,
                "role": role,
                "added_at": current_time,
                "updated_at": current_time,
                "added_by": added_by,
                "notes": notes or ""
            }).execute()
            
            return True, "Utilisateur ajouté avec succès"
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'ajout de l'utilisateur autorisé: {str(e)}")
        return False, f"Erreur: {str(e)}"

def update_user_status(email, active, updated_by):
    """
    Active ou désactive un utilisateur dans la table dash_authorized_users.
    """
    current_time = datetime.now().isoformat()
    status_text = "activé" if active else "désactivé"
    update_note = f"Compte {status_text} le {datetime.now().strftime('%Y-%m-%d %H:%M')} par {updated_by}"
    
    try:
        # Récupérer les notes actuelles
        response = supabase.table("dash_authorized_users").select("notes").eq("email", email).execute()
        
        if not response.data:
            return False, f"Utilisateur {email} non trouvé"
            
        current_notes = response.data[0].get("notes") or ""
        updated_notes = f"{current_notes} | {update_note}" if current_notes else update_note
        
        # Mise à jour du statut
        response = supabase.table("dash_authorized_users").update({
            "active": active,
            "updated_at": current_time,
            "notes": updated_notes
        }).eq("email", email).execute()
        
        return True, f"Statut de l'utilisateur mis à jour: {status_text}"
    except Exception as e:
        print(f"[ERROR] Erreur lors de la mise à jour du statut de l'utilisateur: {str(e)}")
        return False, f"Erreur: {str(e)}"

def update_user_role(email, new_role, updated_by):
    """
    Met à jour le rôle d'un utilisateur dans la table dash_authorized_users.
    """
    current_time = datetime.now().isoformat()
    update_note = f"Rôle changé à '{new_role}' le {datetime.now().strftime('%Y-%m-%d %H:%M')} par {updated_by}"
    
    try:
        # Récupérer les notes actuelles
        response = supabase.table("dash_authorized_users").select("notes").eq("email", email).execute()
        
        if not response.data:
            return False, f"Utilisateur {email} non trouvé"
            
        current_notes = response.data[0].get("notes") or ""
        updated_notes = f"{current_notes} | {update_note}" if current_notes else update_note
        
        # Mise à jour du rôle
        response = supabase.table("dash_authorized_users").update({
            "role": new_role,
            "updated_at": current_time,
            "notes": updated_notes
        }).eq("email", email).execute()
        
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
        
    try:
        response = supabase.table("dash_authorized_users").select("email").eq("email", email.lower().strip()).eq("active", True).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"[ERROR] Erreur lors de la vérification de l'autorisation: {str(e)}")
        return False

def get_user_role(email):
    """
    Récupère le rôle d'un utilisateur depuis la table dash_authorized_users.
    """
    if not email:
        return None
        
    try:
        response = supabase.table("dash_authorized_users").select("role").eq("email", email.lower().strip()).eq("active", True).execute()
        if response.data:
            return response.data[0].get("role")
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
        
    try:
        response = supabase.table("dash_authorized_users").select("role").eq("email", email).eq("active", True).execute()
        if response.data and response.data[0].get("role") == "admin":
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
    try:
        # Vérifier d'abord si l'utilisateur existe
        response = supabase.table("dash_authorized_users").select("email").eq("email", email).execute()
        
        if not response.data:
            return False, f"Utilisateur {email} non trouvé"
        
        # Logger l'action de suppression (optionnel)
        current_time = datetime.now()
        log_message = f"Utilisateur {email} supprimé le {current_time.strftime('%Y-%m-%d %H:%M')} par {deleted_by}"
        print(f"[INFO] {log_message}")
        
        # Exécuter la suppression
        response = supabase.table("dash_authorized_users").delete().eq("email", email).execute()
        
        return True, f"Utilisateur {email} supprimé avec succès"
    except Exception as e:
        print(f"[ERROR] Erreur lors de la suppression de l'utilisateur: {str(e)}")
        return False, f"Erreur: {str(e)}"
