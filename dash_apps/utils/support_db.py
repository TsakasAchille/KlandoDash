import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text, Table, Column, String, MetaData, insert, select, update, ForeignKey
import os
from dash_apps.utils.db_utils import engine

# Fonctions pour récupérer les tickets de support depuis la base de données SQL

def get_all_tickets():
    """
    Récupère tous les tickets de support depuis la table support_tickets.
    """
    query = text("""
        SELECT * FROM support_tickets ORDER BY updated_at DESC
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        # Convertir les données en liste de dictionnaires pour Dash
        tickets = df.to_dict('records')
        return tickets
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des tickets: {str(e)}")
        return []

def get_ticket_by_id(ticket_id):
    """
    Récupère un ticket spécifique par son ID.
    """
    query = text("""
        SELECT * FROM support_tickets WHERE ticket_id = :ticket_id
    """)
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"ticket_id": ticket_id})
        
        # S'il n'y a pas de résultat, retourner None
        if df.empty:
            return None
            
        # Sinon, retourner le premier ticket (il devrait y en avoir qu'un seul)
        return df.iloc[0].to_dict()
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération du ticket {ticket_id}: {str(e)}")
        return None

def update_ticket_status(ticket_id, new_status):
    """
    Met à jour le statut d'un ticket dans la base de données.
    """
    query = text("""
        UPDATE support_tickets 
        SET status = :new_status, updated_at = :updated_at 
        WHERE ticket_id = :ticket_id
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {
                    "ticket_id": ticket_id,
                    "new_status": new_status,
                    "updated_at": datetime.now()
                }
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] Erreur lors de la mise à jour du statut du ticket {ticket_id}: {str(e)}")
        return False

# Gestion de la table support_comments (si elle n'existe pas déjà)

def create_comments_table():
    """
    Crée la table support_comments si elle n'existe pas déjà.
    """
    try:
        query = text("""
            CREATE TABLE IF NOT EXISTS support_comments (
                comment_id UUID PRIMARY KEY,
                ticket_id UUID NOT NULL,
                user_id TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
            )
        """)
        
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
            
        # Créer un index pour les recherches rapides par ticket_id
        index_query = text("""
            CREATE INDEX IF NOT EXISTS idx_support_comments_ticket_id 
            ON support_comments(ticket_id)
        """)
        
        with engine.connect() as conn:
            conn.execute(index_query)
            conn.commit()
            
        print("[INFO] Table support_comments vérifiée/créée avec succès")
        return True
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création de la table support_comments: {str(e)}")
        return False

def get_comments_for_ticket(ticket_id):
    """
    Récupère tous les commentaires associés à un ticket spécifique.
    """
    query = text("""
        SELECT * FROM support_comments 
        WHERE ticket_id = :ticket_id 
        ORDER BY created_at ASC
    """)
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"ticket_id": ticket_id})
        
        # Convertir les données en liste de dictionnaires
        comments = df.to_dict('records')
        return comments
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des commentaires pour le ticket {ticket_id}: {str(e)}")
        return []

def add_comment(ticket_id, user_id, comment_text):
    """
    Ajoute un nouveau commentaire à un ticket.
    """
    comment_id = str(uuid.uuid4())
    created_at = datetime.now()
    
    query = text("""
        INSERT INTO support_comments 
        (comment_id, ticket_id, user_id, comment_text, created_at) 
        VALUES (:comment_id, :ticket_id, :user_id, :comment_text, :created_at)
    """)
    
    # Requête pour mettre à jour la date de mise à jour du ticket
    update_query = text("""
        UPDATE support_tickets 
        SET updated_at = :updated_at 
        WHERE ticket_id = :ticket_id
    """)
    
    try:
        with engine.connect() as conn:
            # Insérer le commentaire
            conn.execute(
                query, 
                {
                    "comment_id": comment_id,
                    "ticket_id": ticket_id,
                    "user_id": user_id,
                    "comment_text": comment_text,
                    "created_at": created_at
                }
            )
            
            # Mettre à jour le ticket
            conn.execute(
                update_query,
                {
                    "ticket_id": ticket_id,
                    "updated_at": created_at
                }
            )
            
            conn.commit()
        
        return {
            "comment_id": comment_id,
            "ticket_id": ticket_id,
            "user_id": user_id,
            "comment_text": comment_text,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'ajout d'un commentaire au ticket {ticket_id}: {str(e)}")
        return None

# Initialisation - vérifier que la table des commentaires existe
# Vous pouvez appeler cette fonction lors du démarrage de l'application
create_comments_table()
