"""
Endpoint webhook pour recevoir les notifications d'emails entrants via Gmail API
"""
import os
import logging
from flask import Blueprint, request, jsonify
from dash_apps.services.email_receiver_service import EmailReceiverService

logger = logging.getLogger("klando.email_webhook")

# Créer le blueprint pour les webhooks email
email_webhook_bp = Blueprint('email_webhook', __name__, url_prefix='/api/email')

def verify_api_key():
    """Vérifie la clé API dans les headers ou query params"""
    api_key = os.getenv('WEBHOOK_API_KEY')
    if not api_key:
        return True  # Si pas de clé configurée, on autorise (pour dev)
    
    # Vérifier dans les headers
    provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    
    if provided_key != api_key:
        logger.warning(f"DEBUG: Tentative d'accès avec clé API invalide: {provided_key}")
        return False
    
    return True

@email_webhook_bp.route('/webhook', methods=['POST'])
def gmail_webhook():
    """
    Endpoint webhook pour recevoir les notifications Gmail Push
    
    Gmail envoie une notification quand un nouvel email arrive.
    On utilise ensuite Gmail API pour récupérer et traiter l'email.
    """
    try:
        # Vérifier la clé API
        if not verify_api_key():
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
        
        logger.info("=== WEBHOOK EMAIL REÇU ===")
        
        # Récupérer les données du webhook
        webhook_data = request.get_json()
        logger.info(f"DEBUG: Données webhook: {webhook_data}")
        
        # Gmail Push notifications contiennent un message encodé
        if 'message' in webhook_data:
            import base64
            import json
            
            # Décoder le message
            message_data = base64.b64decode(webhook_data['message']['data']).decode('utf-8')
            parsed_data = json.loads(message_data)
            
            logger.info(f"DEBUG: Message décodé: {parsed_data}")
            
            # Récupérer l'ID du message Gmail
            message_id = parsed_data.get('messageId')
            if not message_id:
                logger.warning("DEBUG: Aucun messageId trouvé dans le webhook")
                return jsonify({'status': 'ignored', 'reason': 'no_message_id'}), 200
            
            # Récupérer le message complet via Gmail API
            success = process_gmail_message(message_id)
            
            if success:
                logger.info(f"DEBUG: ✅ Email {message_id} traité avec succès")
                return jsonify({'status': 'processed', 'message_id': message_id}), 200
            else:
                logger.warning(f"DEBUG: ⚠️ Email {message_id} ignoré ou erreur")
                return jsonify({'status': 'ignored', 'message_id': message_id}), 200
        
        else:
            logger.warning("DEBUG: Webhook sans message")
            return jsonify({'status': 'ignored', 'reason': 'no_message'}), 200
            
    except Exception as e:
        logger.error(f"DEBUG: Erreur traitement webhook: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

def process_gmail_message(message_id: str) -> bool:
    """
    Récupère et traite un message Gmail spécifique
    
    Args:
        message_id: ID du message Gmail
        
    Returns:
        bool: True si traité avec succès
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # Récupérer les credentials
        credentials = EmailReceiverService._get_gmail_credentials()
        if not credentials:
            logger.error("DEBUG: Impossible de récupérer les credentials Gmail")
            return False
        
        # Créer le service Gmail
        service = build('gmail', 'v1', credentials=credentials)
        
        # Récupérer le message complet
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        logger.info(f"DEBUG: Message Gmail récupéré: {message_id}")
        
        # Traiter le message avec EmailReceiverService
        return EmailReceiverService.process_incoming_email(message)
        
    except Exception as e:
        logger.error(f"DEBUG: Erreur récupération message Gmail {message_id}: {e}")
        return False

@email_webhook_bp.route('/test', methods=['POST'])
def test_email_processing():
    """
    Endpoint de test pour simuler la réception d'un email
    Utile pour tester le système sans configurer Gmail Push
    """
    try:
        # Vérifier la clé API
        if not verify_api_key():
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401
            
        test_data = request.get_json()
        
        # Données de test simulées
        fake_message = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': test_data.get('subject', 'Re: Réponse à votre ticket de support - TEST')},
                    {'name': 'From', 'value': test_data.get('from', 'client@example.com')}
                ],
                'mimeType': 'text/plain',
                'body': {
                    'data': base64.b64encode(test_data.get('body', 'Test de réponse client').encode()).decode()
                }
            }
        }
        
        success = EmailReceiverService.process_incoming_email(fake_message)
        
        return jsonify({
            'status': 'processed' if success else 'failed',
            'test_data': test_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur test email: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@email_webhook_bp.route('/status', methods=['GET'])
def webhook_status():
    """Endpoint pour vérifier le statut du webhook"""
    return jsonify({
        'status': 'active',
        'service': 'email_webhook',
        'endpoints': [
            '/api/email/webhook - Webhook Gmail Push',
            '/api/email/test - Test de traitement email',
            '/api/email/status - Statut du service'
        ]
    }), 200
