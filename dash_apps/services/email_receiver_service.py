"""
Service pour recevoir et traiter les réponses email des clients
"""
import os
import re
import logging
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import email
from email.mime.text import MIMEText

logger = logging.getLogger("klando.email_receiver")

class EmailReceiverService:
    """Service pour recevoir les réponses email via Gmail API"""
    
    @staticmethod
    def _get_gmail_credentials() -> Optional[Credentials]:
        """Récupère les credentials Gmail (même logique que EmailService)"""
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
                    scopes=['https://www.googleapis.com/auth/gmail.readonly']
                )
                
                # Vérifier et rafraîchir si nécessaire
                if not credentials.valid and credentials.refresh_token:
                    try:
                        from google.auth.transport.requests import Request
                        credentials.refresh(Request())
                        logger.info("DEBUG: Token rafraîchi avec succès")
                    except Exception as refresh_error:
                        logger.error(f"DEBUG: Erreur lors du rafraîchissement: {refresh_error}")
                        return None
                
                return credentials
            
            # Fallback sur le fichier pickle (pour le développement local)
            TOKEN_FILE = 'klando_gmail_token.pickle'
            if not os.path.exists(TOKEN_FILE):
                logger.error(f"DEBUG: Fichier token non trouvé: {TOKEN_FILE}")
                return None
            
            import pickle
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
            
            return credentials
            
        except Exception as e:
            logger.error(f"DEBUG: Erreur lors de la récupération des credentials Gmail: {e}")
            return None
    
    @staticmethod
    def extract_ticket_id_from_email(subject: str, body: str) -> Optional[str]:
        """
        Extrait l'ID du ticket depuis le sujet ou le corps de l'email
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email
            
        Returns:
            str: ID du ticket si trouvé, None sinon
        """
        # Pattern pour UUID (format ticket ID)
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        
        # 1. Chercher dans le sujet (Re: Réponse à votre ticket...)
        # Le sujet peut contenir l'ID directement ou dans le titre original
        subject_match = re.search(uuid_pattern, subject, re.IGNORECASE)
        if subject_match:
            logger.info(f"DEBUG: Ticket ID trouvé dans le sujet: {subject_match.group()}")
            return subject_match.group()
        
        # 1b. Chercher un token de référence dans le sujet
        from dash_apps.services.ticket_reference_service import TicketReferenceService
        
        token = TicketReferenceService.extract_token_from_subject(subject)
        if token:
            ticket_id = TicketReferenceService.resolve_reference_token(token)
            if ticket_id:
                logger.info(f"DEBUG: Token {token} résolu vers ticket {ticket_id[:8] if ticket_id else 'None'}...")
                return ticket_id
        
        # 1c. Fallback pour les tests (TEST DE TICKET -> ID connu)
        if "TEST DE TICKET" in subject:
            test_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
            logger.info(f"DEBUG: Ticket de test identifié: {test_ticket_id}")
            return test_ticket_id
        
        # 2. Chercher dans le corps (Référence: xxx ou Ticket ID: xxx)
        body_patterns = [
            r'Référence:\s*([A-Z]{2,3}-\d{4}-[A-Z0-9]{4})',  # Référence: TK-2024-A7B9
            r'Ticket ID:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',  # Fallback UUID
            r'ticket\s*[:#]\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',  # Fallback UUID
        ]
        
        for pattern in body_patterns:
            body_match = re.search(pattern, body, re.IGNORECASE)
            if body_match:
                found_value = body_match.group(1)
                
                # Si c'est un token de référence, le résoudre
                if re.match(r'[A-Z]{2,3}-\d{4}-[A-Z0-9]{4}', found_value):
                    ticket_id = TicketReferenceService.resolve_reference_token(found_value)
                    if ticket_id:
                        logger.info(f"DEBUG: Token {found_value} du corps résolu vers {ticket_id[:8] if ticket_id else 'None'}...")
                        return ticket_id
                else:
                    # C'est un UUID direct
                    logger.info(f"DEBUG: UUID trouvé dans le corps: {found_value}")
                    return found_value
        
        logger.warning(f"DEBUG: Aucun ticket ID trouvé dans l'email")
        logger.warning(f"DEBUG: Sujet: {subject[:100]}...")
        logger.warning(f"DEBUG: Corps: {body[:200]}...")
        return None
    
    @staticmethod
    def extract_reply_content(body: str) -> str:
        """
        Extrait le contenu de la réponse du client (sans l'historique)
        
        Args:
            body: Corps complet de l'email
            
        Returns:
            str: Contenu de la réponse nettoyé
        """
        # Patterns pour détecter le début de l'historique
        history_markers = [
            r'-----Original Message-----',
            r'Le .* a écrit :',
            r'On .* wrote:',
            r'From:.*To:.*Subject:',
            r'---\s*Ticket ID:',
            r'Cordialement,\s*.*\s*Équipe Support Klando',
        ]
        
        # Diviser par lignes
        lines = body.split('\n')
        reply_lines = []
        
        for line in lines:
            # Vérifier si on atteint l'historique
            is_history = False
            for marker in history_markers:
                if re.search(marker, line, re.IGNORECASE):
                    is_history = True
                    break
            
            if is_history:
                break
                
            # Ignorer les lignes de citation (> ou |)
            if line.strip().startswith(('>', '|')):
                continue
                
            reply_lines.append(line)
        
        # Rejoindre et nettoyer
        reply_content = '\n'.join(reply_lines).strip()
        
        # Nettoyer les espaces multiples
        reply_content = re.sub(r'\n\s*\n\s*\n', '\n\n', reply_content)
        
        return reply_content
    
    @staticmethod
    def process_incoming_email(message_data: Dict[str, Any]) -> bool:
        """
        Traite un email entrant et l'ajoute comme commentaire si c'est une réponse à un ticket
        
        Args:
            message_data: Données du message Gmail API
            
        Returns:
            bool: True si traité avec succès, False sinon
        """
        try:
            logger.info("=== DEBUG EMAIL RECEIVER ===")
            
            # Extraire les headers
            headers = {h['name']: h['value'] for h in message_data.get('payload', {}).get('headers', [])}
            subject = headers.get('Subject', '')
            sender = headers.get('From', '')
            
            logger.info(f"DEBUG: Email reçu de {sender}")
            logger.info(f"DEBUG: Sujet: {subject}")
            
            # Vérifier si c'est une réponse à un ticket de support
            if not any(keyword in subject.lower() for keyword in ['re:', 'réponse', 'ticket', 'support']):
                logger.info("DEBUG: Email ignoré (pas une réponse de ticket)")
                return False
            
            # Extraire le corps du message
            body = EmailReceiverService._extract_email_body(message_data.get('payload', {}))
            
            # Extraire l'ID du ticket
            ticket_id = EmailReceiverService.extract_ticket_id_from_email(subject, body)
            if not ticket_id:
                logger.warning("DEBUG: Impossible d'identifier le ticket associé")
                return False
            
            # Extraire le contenu de la réponse
            reply_content = EmailReceiverService.extract_reply_content(body)
            if not reply_content.strip():
                logger.warning("DEBUG: Contenu de réponse vide")
                return False
            
            logger.info(f"DEBUG: Ticket ID identifié: {ticket_id}")
            logger.info(f"DEBUG: Contenu réponse: {reply_content[:100]}...")
            
            # Ajouter le commentaire en base de données
            success = EmailReceiverService._add_reply_to_database(ticket_id, reply_content, sender)
            
            if success:
                logger.info(f"DEBUG: ✅ Réponse ajoutée au ticket {ticket_id}")
                return True
            else:
                logger.error(f"DEBUG: ❌ Échec ajout réponse au ticket {ticket_id}")
                return False
                
        except Exception as e:
            logger.error(f"DEBUG: Erreur traitement email entrant: {e}")
            return False
    
    @staticmethod
    def _extract_email_body(payload: Dict[str, Any]) -> str:
        """Extrait le corps du message depuis le payload Gmail"""
        try:
            # Message simple (text/plain)
            if payload.get('mimeType') == 'text/plain':
                data = payload.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Message multipart
            if payload.get('mimeType', '').startswith('multipart/'):
                parts = payload.get('parts', [])
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return ""
            
        except Exception as e:
            logger.error(f"Erreur extraction corps email: {e}")
            return ""
    
    @staticmethod
    def _add_reply_to_database(ticket_id: str, reply_content: str, sender_email: str) -> bool:
        """Ajoute la réponse client comme commentaire en base de données"""
        try:
            from dash_apps.core.database import get_session
            from dash_apps.repositories.repository_factory import RepositoryFactory
            from dash_apps.services.support_cache_service import SupportCacheService
            
            # Utiliser le repository REST
            comment_repo = RepositoryFactory.get_support_comment_repository()
            comment_data = {
                'ticket_id': ticket_id,
                'user_id': 'client',
                'comment_text': reply_content,
                'user_name': sender_email,
                'comment_type': 'external_received'
            }
            comment = comment_repo.create_comment(comment_data)
            
            if comment:
                logger.info(f"DEBUG: Commentaire client ajouté via REST API")
                
                # Mettre à jour le timestamp du ticket principal
                EmailReceiverService._update_ticket_timestamp(ticket_id)
                
                # Invalider le cache du ticket pour affichage immédiat
                SupportCacheService.clear_ticket_cache(ticket_id)
                
                return True
            else:
                logger.error("DEBUG: Échec création commentaire")
                return False
                
        except Exception as e:
            logger.error(f"DEBUG: Erreur ajout réponse en base: {e}")
            return False

@staticmethod
def process_incoming_email(message_data: Dict[str, Any]) -> bool:
    """
    Traite un email entrant et l'ajoute comme commentaire si c'est une réponse à un ticket
    
    Args:
        message_data: Données du message Gmail API
        
    Returns:
        bool: True si traité avec succès, False sinon
    """
    try:
        logger.info("=== DEBUG EMAIL RECEIVER ===")
        
        # Extraire les headers
        headers = {h['name']: h['value'] for h in message_data.get('payload', {}).get('headers', [])}
        subject = headers.get('Subject', '')
        sender = headers.get('From', '')
        
        logger.info(f"DEBUG: Email reçu de {sender}")
        logger.info(f"DEBUG: Sujet: {subject}")
        
        # Vérifier si c'est une réponse à un ticket de support
        if not any(keyword in subject.lower() for keyword in ['re:', 'réponse', 'ticket', 'support']):
            logger.info("DEBUG: Email ignoré (pas une réponse de ticket)")
            return False
        
        # Extraire le corps du message
        body = EmailReceiverService._extract_email_body(message_data.get('payload', {}))
        
        # Extraire l'ID du ticket
        ticket_id = EmailReceiverService.extract_ticket_id_from_email(subject, body)
        if not ticket_id:
            logger.warning("DEBUG: Impossible d'identifier le ticket associé")
            return False
        
        # Extraire le contenu de la réponse
        reply_content = EmailReceiverService.extract_reply_content(body)
        if not reply_content.strip():
            logger.warning("DEBUG: Contenu de réponse vide")
            return False
        
        logger.info(f"DEBUG: Ticket ID identifié: {ticket_id}")
        logger.info(f"DEBUG: Contenu réponse: {reply_content[:100]}...")
        
        # Ajouter le commentaire en base de données
        success = EmailReceiverService._add_reply_to_database(ticket_id, reply_content, sender)
        
        if success:
            logger.info(f"DEBUG: ✅ Réponse ajoutée au ticket {ticket_id}")
            return True
        else:
            logger.error(f"DEBUG: ❌ Échec ajout réponse au ticket {ticket_id}")
            return False
                
    except Exception as e:
        logger.error(f"DEBUG: Erreur traitement email entrant: {e}")
        return False

@staticmethod
def _extract_email_body(payload: Dict[str, Any]) -> str:
    """Extrait le corps du message depuis le payload Gmail"""
    try:
        # Message simple (text/plain)
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        
        # Message multipart
        if payload.get('mimeType', '').startswith('multipart/'):
            parts = payload.get('parts', [])
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return ""
        
    except Exception as e:
        logger.error(f"Erreur extraction corps email: {e}")
        return ""

    @staticmethod
    def _update_ticket_timestamp(ticket_id: str):
        """Met à jour le timestamp updated_at du ticket principal"""
        try:
            from dash_apps.core.database import get_session
            from dash_apps.models.support_ticket import SupportTicket
            from datetime import datetime
            
            with get_session() as db_session:
                ticket = db_session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
                if ticket:
                    ticket.updated_at = datetime.now()
                    db_session.commit()
                    logger.info(f"DEBUG: Ticket {ticket_id[:8] if ticket_id else 'None'}... updated_at mis à jour (réponse reçue)")
                else:
                    logger.warning(f"DEBUG: Ticket {ticket_id} non trouvé pour mise à jour timestamp")
                    
        except Exception as e:
            logger.error(f"Erreur mise à jour timestamp ticket {ticket_id}: {e}")
