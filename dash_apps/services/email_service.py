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
        Récupère les credentials Gmail depuis les variables d'environnement ou le fichier token
        """
        try:
            # Essayer d'abord les variables d'environnement (pour la production)
            gmail_token = os.getenv('GMAIL_TOKEN')
            gmail_refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
            gmail_client_id = os.getenv('GMAIL_CLIENT_ID')
            gmail_client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if all([gmail_token, gmail_refresh_token, gmail_client_id, gmail_client_secret]):
                logger.info("DEBUG: Utilisation des credentials depuis les variables d'environnement")
                
                credentials = Credentials(
                    token=gmail_token,
                    refresh_token=gmail_refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=gmail_client_id,
                    client_secret=gmail_client_secret,
                    scopes=['https://www.googleapis.com/auth/gmail.send']
                )
                
                # Vérifier et rafraîchir si nécessaire
                if not credentials.valid and credentials.refresh_token:
                    try:
                        from google.auth.transport.requests import Request
                        credentials.refresh(Request())
                        logger.info("DEBUG: Token rafraîchi avec succès depuis les variables d'environnement")
                    except Exception as refresh_error:
                        logger.error(f"DEBUG: Erreur lors du rafraîchissement: {refresh_error}")
                        return None
                
                return credentials
            
            # Fallback sur le fichier pickle (pour le développement local)
            if not os.path.exists(EmailService.TOKEN_FILE):
                logger.error(f"DEBUG: Fichier token non trouvé: {EmailService.TOKEN_FILE}")
                logger.error("DEBUG: Configurez les variables d'environnement GMAIL_* ou exécutez: python3 scripts/gmail_oauth_server.py")
                return None
            
            logger.info(f"DEBUG: Lecture du fichier token: {EmailService.TOKEN_FILE}")
            
            with open(EmailService.TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            
            logger.info(f"DEBUG: Credentials chargés - valid: {credentials.valid if credentials else 'None'}")
            
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
            # Utiliser un token de référence sécurisé au lieu de l'ID interne
            from dash_apps.services.ticket_reference_service import TicketReferenceService
            
            ticket_id = ticket_data.get('ticket_id', '')
            reference_token = TicketReferenceService.get_reference_for_ticket(ticket_id)
            
            if reference_token:
                message['subject'] = f"Réponse à votre ticket #{reference_token} - {ticket_data.get('subject', 'Support Klando')}"
            else:
                # Fallback si le token ne peut pas être généré
                message['subject'] = f"Réponse à votre ticket de support - {ticket_data.get('subject', 'Support Klando')}"
            
            logger.info(f"DEBUG: Email sera envoyé:")
            logger.info(f"DEBUG:   FROM: {gmail_email}")
            logger.info(f"DEBUG:   TO: {client_email}")
            logger.info(f"DEBUG:   SUBJECT: Réponse à votre ticket de support - {ticket_data.get('subject', 'Support Klando')}")
            
            # Corps du message avec token de référence sécurisé
            body = f"""
Bonjour,

Voici une réponse à votre ticket de support :

{message_content}

Cordialement,
{sender_user_name}
Équipe Support Klando

---
Référence: {reference_token or 'N/A'}
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
            
            # Ajouter le commentaire en base de données ET mettre à jour le ticket
            EmailService._add_comment_to_database(ticket_data, message_content, 'external_sent')
            EmailService._update_ticket_timestamp(ticket_data.get('ticket_id'))
            
            return True
                
        except Exception as e:
            # Analyser le type d'erreur pour donner un message plus précis
            error_message = str(e).lower()
            
            if "invalid_grant" in error_message:
                logger.error("❌ Token OAuth2 invalide ou expiré")
                logger.error("Solution: Régénérez le token avec python3 scripts/gmail_oauth_server.py")
            elif "recipient address rejected" in error_message or "invalid recipient" in error_message:
                logger.error(f"❌ Adresse email invalide ou inexistante: {client_email}")
                logger.error("L'adresse email du destinataire n'existe pas ou est mal formatée")
            elif "quota exceeded" in error_message or "rate limit" in error_message:
                logger.error("❌ Limite de quota Gmail dépassée")
                logger.error("Attendez quelques minutes avant de réessayer")
            elif "insufficient authentication scopes" in error_message:
                logger.error("❌ Permissions insuffisantes pour envoyer des emails")
                logger.error("Vérifiez que le scope 'gmail.send' est autorisé")
            elif "user not found" in error_message:
                logger.error("❌ Compte Gmail non trouvé ou inaccessible")
            elif "message too large" in error_message:
                logger.error("❌ Message trop volumineux pour Gmail")
            elif "daily sending quota exceeded" in error_message:
                logger.error("❌ Quota quotidien d'envoi Gmail dépassé")
            elif "blocked" in error_message or "spam" in error_message:
                logger.error(f"❌ Email bloqué par Gmail (possible spam): {client_email}")
            else:
                logger.error(f"❌ Erreur lors de l'envoi email: {e}")
                logger.error(f"Type d'erreur: {type(e).__name__}")
            
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
                
                # Ajouter le commentaire avec les bonnes colonnes
                comment = SupportCommentRepository.add_comment_with_type(
                    db_session,
                    str(ticket_data.get('ticket_id')),
                    sender_user_id,
                    "",  # comment_text vide car on utilise comment_sent
                    sender_user_name,
                    comment_type,
                    comment_sent=message_content  # Le message envoyé va dans comment_sent
                )
                
                logger.info(f"DEBUG: Commentaire ajouté - ID: {comment.comment_id if comment else 'None'}")
                logger.info(f"DEBUG: comment_sent: '{message_content[:50]}...'")
                logger.info(f"DEBUG: comment_type: '{comment_type}'")
                
                # Invalider le cache pour rafraîchir l'affichage
                from dash_apps.services.support_cache_service import SupportCacheService
                ticket_id = ticket_data.get('ticket_id')
                SupportCacheService.clear_ticket_cache(ticket_id)
                
                logger.info(f"DEBUG: Cache invalidé pour ticket {ticket_id}")
                logger.info(f"DEBUG: Commentaire ajouté en base pour ticket {ticket_id}")
                
                # Forcer le rafraîchissement du cache HTML pour affichage immédiat
                try:
                    from dash_apps.services.support_cache_service import SupportCacheService
                    # Effacer aussi le cache HTML des détails du ticket
                    cache_key = f"ticket_details_{ticket_id}"
                    SupportCacheService.cache_manager.delete(cache_key)
                    logger.info(f"DEBUG: Cache HTML effacé pour {cache_key}")
                except Exception as cache_error:
                    logger.warning(f"DEBUG: Erreur effacement cache HTML: {cache_error}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du commentaire en base: {e}")
    
    @staticmethod
    def _update_ticket_timestamp(ticket_id: str):
        """Met à jour le timestamp updated_at du ticket principal"""
        try:
            from dash_apps.core.database import get_session
            from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
            from datetime import datetime
            
            with get_session() as db_session:
                # Import du modèle nécessaire
                from dash_apps.models.support_ticket import SupportTicket
                
                # Utiliser la méthode existante pour mettre à jour le ticket
                ticket = db_session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
                if ticket:
                    ticket.updated_at = datetime.now()
                    db_session.commit()
                    logger.info(f"DEBUG: Ticket {ticket_id[:8] if ticket_id else 'None'}... updated_at mis à jour")
                else:
                    logger.warning(f"DEBUG: Ticket {ticket_id} non trouvé pour mise à jour timestamp")
                    
        except Exception as e:
            logger.error(f"Erreur mise à jour timestamp ticket {ticket_id}: {e}")
    
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
