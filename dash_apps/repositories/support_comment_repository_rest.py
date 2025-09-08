"""
Repository pour les commentaires de support utilisant l'API REST Supabase
"""
from dash_apps.repositories.supabase_repository import SupabaseRepository
from typing import List, Optional, Dict
import logging
from datetime import datetime
import flask

# Fonction helper pour accéder à la session Flask en toute sécurité
def get_flask_session_value(key, default=None):
    """Récupère une valeur de la session Flask s'il y a un contexte de requête actif, sinon retourne default"""
    try:
        if flask.has_request_context():
            return flask.session.get(key, default)
        return default
    except Exception:
        return default

# Logger
logger = logging.getLogger(__name__)

class SupportCommentRepositoryRest(SupabaseRepository):
    """
    Repository pour les commentaires de support utilisant l'API REST Supabase
    """
    
    def __init__(self):
        """
        Initialise le repository avec la table 'support_comments'
        """
        super().__init__("support_comments")
    
    def list_comments_for_ticket(self, ticket_id: str) -> List[Dict]:
        """
        Liste les commentaires pour un ticket donné
        
        Args:
            ticket_id: Identifiant du ticket
            
        Returns:
            Liste des commentaires pour ce ticket, triés par date de création (desc)
        """
        try:
            # Récupérer les commentaires depuis Supabase
            comments = self.get_all(
                order_by="created_at",
                order_direction="desc",
                filters={"ticket_id": ticket_id}
            )
            
            # Enrichir avec le nom d'utilisateur
            enriched_comments = []
            for comment in comments:
                # Assurer que les IDs sont bien des chaînes
                if 'comment_id' in comment and not isinstance(comment['comment_id'], str):
                    comment['comment_id'] = str(comment['comment_id'])
                if 'ticket_id' in comment and not isinstance(comment['ticket_id'], str):
                    comment['ticket_id'] = str(comment['ticket_id'])
                
                # Enrichir avec le nom d'utilisateur
                user_id = comment.get('user_id')
                
                # Dans tous les cas, utiliser le nom complet s'il est disponible
                # Le nom est peut-être déjà stocké dans le champ user_id
                if user_id and len(str(user_id).split()) > 1:
                    # Si user_id ressemble déjà à un nom (contient des espaces)
                    comment['user_name'] = user_id
                elif user_id == get_flask_session_value('user_id'):
                    # Si c'est l'utilisateur courant, prendre son nom de la session
                    comment['user_name'] = get_flask_session_value('user_name', user_id)
                else:
                    # Pour les autres cas, afficher le nom complet disponible ou "Système" par défaut
                    comment['user_name'] = user_id if user_id else "Système"
                
                enriched_comments.append(comment)
            
            return enriched_comments
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des commentaires: {str(e)}")
            return []
    
    def add_comment(self, ticket_id: str, user_id: str, comment_text: str, user_name: str = None) -> Optional[Dict]:
        """
        Ajoute un commentaire à un ticket
        
        Args:
            ticket_id: Identifiant du ticket
            user_id: Identifiant de l'utilisateur
            comment_text: Texte du commentaire
            user_name: Nom de l'utilisateur (optionnel)
            
        Returns:
            Le commentaire créé ou None en cas d'erreur
        """
        try:
            # Créer le commentaire en base de données (type internal par défaut)
            comment_data = {
                "ticket_id": ticket_id,
                "user_id": user_name or user_id,  # Stocker le nom d'utilisateur s'il est disponible
                "comment_text": comment_text,
                "comment_type": "internal",
                "created_at": datetime.now().isoformat()
            }
            
            # Insérer le commentaire
            comment = self.create(comment_data)
            
            if comment:
                # Ajouter le nom d'utilisateur pour l'affichage (non stocké en base)
                comment['user_name'] = user_name or user_id
                
                return comment
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'un commentaire: {str(e)}")
            return None
    
    def add_comment_with_type(self, ticket_id: str, user_id: str, comment_text: str, user_name: str = None, 
                            comment_type: str = "internal", comment_sent: str = None, 
                            comment_received: str = None, comment_source: str = None) -> Optional[Dict]:
        """
        Ajoute un commentaire avec un type spécifique (pour emails)
        
        Args:
            ticket_id: ID du ticket
            user_id: ID de l'utilisateur
            comment_text: Contenu du commentaire
            user_name: Nom d'affichage de l'utilisateur
            comment_type: Type de commentaire (internal, external_sent, external_received)
            comment_sent: Contenu du message envoyé (pour emails)
            comment_received: Contenu du message reçu (pour réponses clients)
            comment_source: Source du commentaire (mail, phone, etc.)
            
        Returns:
            Le commentaire créé ou None en cas d'erreur
        """
        try:
            # Créer le commentaire en base de données avec type spécifique
            comment_data = {
                "ticket_id": ticket_id,
                "user_id": user_name or user_id,
                "comment_text": comment_text,
                "comment_type": comment_type,
                "comment_sent": comment_sent,
                "comment_received": comment_received,
                "comment_source": comment_source or ("mail" if (comment_sent or comment_received) else None),
                "created_at": datetime.now().isoformat()
            }
            
            # Insérer le commentaire
            comment = self.create(comment_data)
            
            if comment:
                # Ajouter le nom d'utilisateur pour l'affichage (non stocké en base)
                comment['user_name'] = user_name or user_id
                
                return comment
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'un commentaire avec type: {str(e)}")
            return None
