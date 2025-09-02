"""
Service d'envoi d'emails via Gmail API avec OAuth2
"""
import os
import pickle
import logging
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dash_apps.core.database import get_session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

# Cache manager non nécessaire pour EmailService

logger = logging.getLogger("klando.email")

class EmailService:
    """Service pour envoyer des emails via Gmail API avec OAuth2"""
    
    TOKEN_FILE = 'klando_gmail_token.pickle'
    
    @staticmethod
    def _get_gmail_credentials() -> Optional[Credentials]:
        """
        Récupère les credentials Gmail depuis le fichier token généré par le serveur OAuth2
        """
        try:
            if not os.path.exists(EmailService.TOKEN_FILE):
                logger.error(f"DEBUG: Fichier token non trouvé: {EmailService.TOKEN_FILE}")
                logger.error("DEBUG: Exécutez d'abord: python3 scripts/gmail_oauth_server.py")
                return None
            
            logger.info(f"DEBUG: Lecture du fichier token: {EmailService.TOKEN_FILE}")
            
            with open(EmailService.TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            
            logger.info(f"DEBUG: Credentials chargés - valid: {credentials.valid if credentials else 'None'}")
            logger.info(f"DEBUG: Token: {credentials.token[:50] if credentials and credentials.token else 'None'}...")
            logger.info(f"DEBUG: Refresh token: {'Présent' if credentials and credentials.refresh_token else 'Absent'}")
            
            if not credentials:
                logger.error("DEBUG: Credentials sont None")
                return None
                
            if not credentials.valid:
                logger.warning("DEBUG: Credentials expirés, tentative de rafraîchissement...")
                if credentials.refresh_token:
                    try:
                        from google.auth.transport.requests import Request
                        credentials.refresh(Request())
                        logger.info("DEBUG: Token rafraîchi avec succès")
                        
                        # Sauvegarder le token rafraîchi
                        with open(EmailService.TOKEN_FILE, 'wb') as token:
                            pickle.dump(credentials, token)
                        logger.info("DEBUG: Token rafraîchi sauvegardé")
                        
                    except Exception as refresh_error:
                        logger.error(f"DEBUG: Erreur lors du rafraîchissement: {refresh_error}")
                        return None
                else:
                    logger.error("DEBUG: Pas de refresh_token disponible")
                    return None
            
            logger.info("DEBUG: Credentials valides et prêts")
            return credentials
            
        except Exception as e:
            logger.error(f"DEBUG: Erreur lors de la récupération des credentials Gmail: {e}")
            return None
    
    @staticmethod
    def send_email_to_client(ticket_data: Dict[str, Any], message_content: str) -> bool:
        """
        Envoie un email au client via Gmail API avec OAuth2
        
        Args:
            ticket_data: Données du ticket contenant email et infos client
            message_content: Contenu du message à envoyer
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            logger.info("=== DEBUG EMAIL SERVICE ===")
            logger.info(f"DEBUG: ticket_data = {ticket_data}")
            logger.info(f"DEBUG: message_content = '{message_content}'")
            
            # Vérifier que le client préfère être contacté par email
            contact_preference = ticket_data.get('contact_preference', '').lower()
            logger.info(f"DEBUG: contact_preference = '{contact_preference}'")
            
            if contact_preference != 'mail':
                logger.warning(f"Client ne souhaite pas être contacté par email (préférence: {contact_preference})")
                return False
            
            # Récupérer l'email du client
            client_email = ticket_data.get('mail')
            logger.info(f"DEBUG: client_email = '{client_email}'")
            
            if not client_email:
                logger.error("Aucun email trouvé pour ce ticket")
                return False
            
            # Récupérer les credentials Gmail OAuth2
            credentials = EmailService._get_gmail_credentials()
            if not credentials:
                logger.error("Impossible de récupérer les credentials Gmail")
                logger.error("Exécutez: python3 scripts/gmail_oauth_server.py pour configurer OAuth2")
                return False
            
            # Créer le service Gmail
            service = build('gmail', 'v1', credentials=credentials)
            logger.info("DEBUG: Service Gmail créé avec succès")
            
            # Récupérer l'ID de l'utilisateur qui envoie le message
            from flask import session
            sender_user_name = session.get('user_name', 'Support Klando')
            gmail_email = os.getenv('GMAIL_SENDER_EMAIL', 'support@klando-sn.com')
            
            logger.info(f"DEBUG: sender_user_name = '{sender_user_name}'")
            logger.info(f"DEBUG: gmail_email = '{gmail_email}'")
            
            # Créer le message email
            message = MIMEMultipart()
            message['to'] = client_email
            message['from'] = gmail_email
            message['subject'] = f"Réponse à votre ticket de support - {ticket_data.get('subject', 'Support Klando')}"
            
            logger.info(f"DEBUG: Email sera envoyé:")
            logger.info(f"DEBUG:   FROM: {gmail_email}")
            logger.info(f"DEBUG:   TO: {client_email}")
            logger.info(f"DEBUG:   SUBJECT: Réponse à votre ticket de support - {ticket_data.get('subject', 'Support Klando')}")
            
            # Corps du message
            body = f"""
Bonjour,

Voici une réponse à votre ticket de support :

{message_content}

Cordialement,
{sender_user_name}
Équipe Support Klando

---
Ticket ID: {ticket_data.get('ticket_id')}
"""
            
            logger.info(f"DEBUG: Corps du message:")
            logger.info(f"DEBUG: {body}")
            
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Encoder le message pour l'API Gmail
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            logger.info("DEBUG: Message encodé pour Gmail API")
            
            # Envoyer l'email via Gmail API
            logger.info("DEBUG: Tentative d'envoi via Gmail API...")
            send_result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"DEBUG: ✅ Email envoyé avec succès!")
            logger.info(f"DEBUG: Gmail Message ID: {send_result['id']}")
            logger.info(f"DEBUG: Ticket ID: {ticket_data.get('ticket_id')}")
            logger.info(f"DEBUG: Destinataire: {client_email}")
            logger.info("=== FIN DEBUG EMAIL SERVICE ===")
            
            # Ajouter le commentaire en base de données
            EmailService._add_comment_to_database(ticket_data, message_content, 'external_sent')
            
            return True
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi email: {e}")
            return False
    
    @staticmethod
    def _add_comment_to_database(ticket_data: Dict[str, Any], message_content: str, comment_type: str):
        """
        Ajoute le commentaire en base de données
        """
        try:
            from dash_apps.core.database import get_session
            from dash_apps.repositories.support_comment_repository import SupportCommentRepository
            from flask import session
            
            with get_session() as db_session:
                sender_user_id = session.get('user_id', 'system')
                sender_user_name = session.get('user_name', 'Support Klando')
                
                SupportCommentRepository.add_comment_with_type(
                    db_session,
                    str(ticket_data.get('ticket_id')),
                    sender_user_id,
                    message_content,
                    sender_user_name,
                    comment_type
                )
                
                # Invalider le cache
                from dash_apps.services.support_cache_service import SupportCacheService
                SupportCacheService.clear_ticket_cache(ticket_data.get('ticket_id'))
                
                logger.info(f"Commentaire ajouté en base pour ticket {ticket_data.get('ticket_id')}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du commentaire en base: {e}")
    
    @staticmethod
    def can_send_email(ticket_data: Dict[str, Any]) -> bool:
        """
        Vérifie si un email peut être envoyé pour ce ticket
        
        Args:
            ticket_data: Données du ticket
            
        Returns:
            bool: True si un email peut être envoyé
        """
        contact_preference = ticket_data.get('contact_preference', '').lower()
        client_email = ticket_data.get('mail')
        
        return contact_preference == 'mail' and bool(client_email)
