"""
API endpoints pour l'intégration N8N avec le système de support
"""
from flask import Blueprint, request, jsonify
from dash_apps.core.database import get_session
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.services.support_cache_service import SupportCacheService
from datetime import datetime
import logging

logger = logging.getLogger("klando.support.api")

# Créer le Blueprint pour les API de support
support_api_bp = Blueprint('support_api', __name__, url_prefix='/api/support')

@support_api_bp.route('/notify-comment', methods=['POST'])
def notify_comment_added():
    """
    Endpoint pour que N8N notifie qu'un commentaire a été ajouté
    N8N remplit directement la base de données, cet endpoint invalide juste le cache
    
    Payload attendu:
    {
        "ticket_id": "uuid-du-ticket"
    }
    """
    try:
        data = request.get_json()
        
        # Validation du ticket_id requis
        if not data.get('ticket_id'):
            return jsonify({"error": "Champ requis manquant: ticket_id"}), 400
        
        # Invalider le cache pour ce ticket
        SupportCacheService.clear_ticket_cache(data['ticket_id'])
        
        logger.info(f"Notification N8N reçue: cache invalidé pour ticket={data['ticket_id']}")
        
        return jsonify({
            "success": True,
            "ticket_id": data['ticket_id'],
            "message": "Cache invalidé, commentaire pris en compte"
        }), 200
                
    except Exception as e:
        logger.error(f"Erreur API notify_comment_added: {e}")
        return jsonify({"error": str(e)}), 500


@support_api_bp.route('/refresh/<ticket_id>', methods=['POST'])
def notify_comment_update(ticket_id):
    """
    Endpoint pour que N8N notifie Dash qu'un nouveau commentaire a été ajouté
    
    Dash peut utiliser ce signal pour rafraîchir l'affichage en temps réel
    """
    try:
        # Invalider le cache pour ce ticket
        SupportCacheService.clear_ticket_cache(ticket_id)
        
        logger.info(f"Notification de rafraîchissement reçue pour ticket {ticket_id}")
        
        # Optionnel: déclencher un signal global pour tous les clients connectés
        # (nécessiterait WebSocket ou SSE pour être vraiment temps réel)
        
        return jsonify({
            "success": True,
            "ticket_id": ticket_id,
            "message": "Cache invalidé, Dash va se rafraîchir"
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur API notify_comment_update: {e}")
        return jsonify({"error": str(e)}), 500


@support_api_bp.route('/comments/latest/<ticket_id>', methods=['GET'])
def get_latest_comments(ticket_id):
    """
    Endpoint pour que Dash vérifie s'il y a de nouveaux commentaires
    Retourne le timestamp du dernier commentaire
    """
    try:
        with get_session() as session:
            comments = SupportCommentRepository.list_comments_for_ticket(session, ticket_id)
            
            if comments:
                latest_comment = max(comments, key=lambda c: c.created_at)
                return jsonify({
                    "ticket_id": ticket_id,
                    "latest_timestamp": latest_comment.created_at.isoformat(),
                    "comment_count": len(comments)
                }), 200
            else:
                return jsonify({
                    "ticket_id": ticket_id,
                    "latest_timestamp": None,
                    "comment_count": 0
                }), 200
                
    except Exception as e:
        logger.error(f"Erreur API get_latest_comments: {e}")
        return jsonify({"error": str(e)}), 500


@support_api_bp.route('/comments/<ticket_id>', methods=['GET'])
def get_ticket_comments(ticket_id):
    """
    Endpoint pour récupérer tous les commentaires d'un ticket
    Utilisé par N8N pour vérifier que les données ont bien été insérées
    
    Retourne un JSON avec tous les commentaires du ticket au format:
    [
      {
        "comment_id": "uuid",
        "ticket_id": "uuid", 
        "user_id": "string",
        "comment_text": "string",
        "comment_sent": "string|null",
        "comment_received": "string|null", 
        "comment_source": "mail|phone|null",
        "comment_type": "internal|external",
        "created_at": "ISO datetime"
      }
    ]
    """
    try:
        # Validation de l'UUID
        import uuid
        try:
            uuid.UUID(ticket_id)
        except ValueError:
            return jsonify({
                "error": f"Format d'UUID invalide: '{ticket_id}'. Utilisez un UUID valide (ex: 1522456d-2eef-41b1-8a13-e8991b592281)"
            }), 400
        
        with get_session() as session:
            comments = SupportCommentRepository.list_comments_for_ticket(session, ticket_id)
            
            # Convertir les commentaires en format JSON
            comments_data = []
            for comment in comments:
                comment_dict = {
                    "comment_id": str(comment.comment_id),
                    "ticket_id": str(comment.ticket_id),
                    "user_id": comment.user_id,
                    "comment_text": comment.comment_text or "",
                    "comment_sent": comment.comment_sent,
                    "comment_received": comment.comment_received,
                    "comment_source": comment.comment_source,
                    "comment_type": comment.comment_type,
                    "created_at": comment.created_at.isoformat()
                }
                comments_data.append(comment_dict)
            
            logger.info(f"API: Récupération de {len(comments_data)} commentaires pour ticket {ticket_id}")
            
            return jsonify(comments_data), 200
                
    except Exception as e:
        logger.error(f"Erreur API get_ticket_comments: {e}")
        return jsonify({"error": str(e)}), 500
