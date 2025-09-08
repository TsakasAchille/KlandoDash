"""
Fonctions pour gérer les tickets de support via l'API REST Supabase
Version adaptée de support_db.py qui utilise l'API REST au lieu de la connexion PostgreSQL directe
"""
import pandas as pd
import uuid
from datetime import datetime
import logging
from dash_apps.utils.supabase_client import supabase

# Logger
logger = logging.getLogger(__name__)

def get_all_tickets():
    """
    Récupère tous les tickets de support depuis la table support_tickets.
    """
    try:
        response = supabase.table("support_tickets").select("*").order("updated_at", desc=True).execute()
        
        if not response.data:
            return []
        
        # Convertir en DataFrame puis en liste de dictionnaires pour garder le même format
        df = pd.DataFrame(response.data)
        tickets = df.to_dict('records')
        return tickets
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la récupération des tickets: {str(e)}")
        return []

def get_ticket_by_id(ticket_id):
    """
    Récupère un ticket spécifique par son ID.
    """
    try:
        response = supabase.table("support_tickets").select("*").eq("ticket_id", ticket_id).execute()
        
        # S'il n'y a pas de résultat, retourner None
        if not response.data:
            return None
            
        # Sinon, retourner le premier ticket (il devrait y en avoir qu'un seul)
        return response.data[0]
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la récupération du ticket {ticket_id}: {str(e)}")
        return None

def update_ticket_status(ticket_id, new_status):
    """
    Met à jour le statut d'un ticket dans la base de données.
    """
    try:
        response = supabase.table("support_tickets").update({
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        }).eq("ticket_id", ticket_id).execute()
        
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la mise à jour du statut du ticket {ticket_id}: {str(e)}")
        return False

# Pour la gestion des commentaires, nous n'avons pas besoin de créer la table
# car elle est déjà définie dans Supabase. La fonction create_comments_table
# est donc supprimée dans cette version REST.

def get_comments_for_ticket(ticket_id):
    """
    Récupère tous les commentaires associés à un ticket spécifique.
    """
    try:
        response = supabase.table("support_comments").select("*").eq("ticket_id", ticket_id).order("created_at", desc=False).execute()
        
        if not response.data:
            return []
        
        # Convertir en DataFrame puis en liste de dictionnaires pour garder le même format
        df = pd.DataFrame(response.data)
        comments = df.to_dict('records')
        return comments
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la récupération des commentaires pour le ticket {ticket_id}: {str(e)}")
        return []

def add_comment(ticket_id, user_id, comment_text):
    """
    Ajoute un nouveau commentaire à un ticket.
    """
    comment_id = str(uuid.uuid4())
    created_at = datetime.now()
    
    try:
        # Insérer le commentaire
        comment_response = supabase.table("support_comments").insert({
            "comment_id": comment_id,
            "ticket_id": ticket_id,
            "user_id": user_id,
            "comment_text": comment_text,
            "created_at": created_at.isoformat()
        }).execute()
        
        # Mettre à jour la date de mise à jour du ticket
        ticket_response = supabase.table("support_tickets").update({
            "updated_at": created_at.isoformat()
        }).eq("ticket_id", ticket_id).execute()
        
        if not comment_response.data:
            return None
        
        return {
            "comment_id": comment_id,
            "ticket_id": ticket_id,
            "user_id": user_id,
            "comment_text": comment_text,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de l'ajout d'un commentaire au ticket {ticket_id}: {str(e)}")
        return None
