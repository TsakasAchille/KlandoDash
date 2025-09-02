"""
Service d'envoi d'emails via webhook N8N
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("klando.email")

class EmailService:
    """Service pour envoyer des emails via webhook N8N"""
    
    WEBHOOK_URL = "https://klando.app.n8n.cloud/webhook-test/de44f31a-6fd0-46f0-a6a7-dfbbb55d40c3"
    
    @staticmethod
    def send_email_to_client(ticket_data: Dict[str, Any], message_content: str) -> bool:
        """
        Envoie un email au client via le webhook N8N
        
        Args:
            ticket_data: Données du ticket contenant email et infos client
            message_content: Contenu du message à envoyer
            
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Vérifier que le client préfère être contacté par email
            contact_preference = ticket_data.get('contact_preference', '').lower()
            if contact_preference != 'mail':
                logger.warning(f"Client ne souhaite pas être contacté par email (préférence: {contact_preference})")
                return False
            
            # Récupérer l'email du client
            client_email = ticket_data.get('mail')
            if not client_email:
                logger.error("Aucun email trouvé pour ce ticket")
                return False
            
            # Préparer les données pour le webhook
            payload = {
                "to": client_email,
                "subject": f"Réponse à votre ticket de support - {ticket_data.get('subject', 'Support Klando')}",
                "message": message_content,
                "ticket_id": ticket_data.get('ticket_id'),
                "user_id": ticket_data.get('user_id')
            }
            
            logger.info(f"Envoi email via webhook pour ticket {ticket_data.get('ticket_id')} vers {client_email}")
            
            # Envoyer la requête GET au webhook avec paramètres
            response = requests.get(
                EmailService.WEBHOOK_URL,
                params=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Email envoyé avec succès pour ticket {ticket_data.get('ticket_id')}")
                return True
            else:
                logger.error(f"Erreur webhook: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau lors de l'envoi email: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'envoi email: {e}")
            return False
    
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
