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

@support_api_bp.route('/comment', methods=['POST'])
def add_comment_from_n8n():
    """
    Endpoint pour que N8N ajoute des commentaires en base de données
    
    Payload attendu:
    {
        "ticket_id": "uuid-du-ticket",
        "user_id": "id-utilisateur",
        "user_name": "nom-utilisateur", 
        "comment_text": "contenu-du-commentaire",
        "comment_type": "external_sent" ou "external_received"
    }
    """
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['ticket_id', 'user_id', 'comment_text', 'comment_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Champ requis manquant: {field}"}), 400
        
        # Validation du type de commentaire
        valid_types = ['internal', 'external_sent', 'external_received']
        if data['comment_type'] not in valid_types:
            return jsonify({"error": f"Type de commentaire invalide. Valeurs autorisées: {valid_types}"}), 400
        
        # Ajouter le commentaire en base
        with get_session() as session:
            comment = SupportCommentRepository.add_comment_with_type(
                session,
                str(data['ticket_id']),
                str(data['user_id']),
                data['comment_text'],
                data.get('user_name', data['user_id']),
                data['comment_type']
            )
            
            if comment:
                # Invalider le cache pour ce ticket
                SupportCacheService.clear_ticket_cache(data['ticket_id'])
                
                logger.info(f"Commentaire ajouté par N8N: ticket={data['ticket_id']}, type={data['comment_type']}")
                
                return jsonify({
                    "success": True,
                    "comment_id": comment.comment_id,
                    "message": "Commentaire ajouté avec succès"
                }), 200
            else:
                return jsonify({"error": "Erreur lors de l'ajout du commentaire"}), 500
                
    except Exception as e:
        logger.error(f"Erreur API add_comment_from_n8n: {e}")
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
