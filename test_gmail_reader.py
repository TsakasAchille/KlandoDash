#!/usr/bin/env python3
"""
Script de test pour lire les emails reçus via Gmail API
Teste la réception et le traitement des emails entrants
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire racine au PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dash_apps.services.email_receiver_service import EmailReceiverService
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_gmail_service():
    """Récupère le service Gmail API"""
    try:
        credentials = EmailReceiverService._get_gmail_credentials()
        if not credentials:
            logger.error("❌ Impossible de récupérer les credentials Gmail")
            return None
        
        service = build('gmail', 'v1', credentials=credentials)
        logger.info("✅ Service Gmail API initialisé")
        return service
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Gmail API: {e}")
        return None

def list_recent_emails(service, max_results=10):
    """Liste les emails récents"""
    try:
        # Récupérer les emails des dernières 24h
        yesterday = datetime.now() - timedelta(days=1)
        query = f'after:{yesterday.strftime("%Y/%m/%d")}'
        
        logger.info(f"🔍 Recherche des emails avec query: {query}")
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        logger.info(f"📧 {len(messages)} emails trouvés")
        
        return messages
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération emails: {e}")
        return []

def get_email_details(service, message_id):
    """Récupère les détails d'un email"""
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extraire les headers
        headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
        subject = headers.get('Subject', 'Pas de sujet')
        sender = headers.get('From', 'Expéditeur inconnu')
        date = headers.get('Date', 'Date inconnue')
        
        logger.info(f"📨 Email: {subject[:50]}...")
        logger.info(f"👤 De: {sender}")
        logger.info(f"📅 Date: {date}")
        
        return message, headers
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération détails email {message_id}: {e}")
        return None, None

def test_email_processing(service, message_id):
    """Teste le traitement d'un email avec EmailReceiverService"""
    try:
        logger.info(f"🧪 Test traitement email {message_id}")
        
        # Récupérer le message complet
        message, headers = get_email_details(service, message_id)
        if not message:
            return False
        
        # Tester le traitement avec EmailReceiverService
        success = EmailReceiverService.process_incoming_email(message)
        
        if success:
            logger.info(f"✅ Email {message_id} traité avec succès")
        else:
            logger.warning(f"⚠️ Email {message_id} ignoré ou erreur de traitement")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur test traitement email {message_id}: {e}")
        return False

def test_ticket_extraction(subject, body=""):
    """Teste l'extraction d'ID de ticket"""
    logger.info(f"🎯 Test extraction ticket depuis: {subject}")
    
    ticket_id = EmailReceiverService.extract_ticket_id_from_email(subject, body)
    
    if ticket_id:
        logger.info(f"✅ Ticket ID trouvé: {ticket_id}")
    else:
        logger.warning(f"⚠️ Aucun ticket ID trouvé")
    
    return ticket_id

def main():
    """Fonction principale"""
    logger.info("🚀 Démarrage du test de lecture Gmail")
    
    # 1. Initialiser le service Gmail
    service = get_gmail_service()
    if not service:
        logger.error("❌ Impossible d'initialiser Gmail API")
        return
    
    # 2. Lister les emails récents
    messages = list_recent_emails(service, max_results=5)
    if not messages:
        logger.warning("⚠️ Aucun email récent trouvé")
        return
    
    # 3. Analyser chaque email
    for i, message in enumerate(messages, 1):
        logger.info(f"\n--- EMAIL {i}/{len(messages)} ---")
        message_id = message['id']
        
        # Récupérer les détails
        message_data, headers = get_email_details(service, message_id)
        if not message_data:
            continue
        
        subject = headers.get('Subject', '')
        
        # Tester l'extraction de ticket
        ticket_id = test_ticket_extraction(subject)
        
        # Si c'est potentiellement une réponse de ticket, tester le traitement
        if any(keyword in subject.lower() for keyword in ['re:', 'réponse', 'ticket', 'support']):
            logger.info("📝 Email identifié comme réponse potentielle")
            test_email_processing(service, message_id)
        else:
            logger.info("📄 Email non identifié comme réponse de ticket")
    
    logger.info("\n✅ Test terminé")

if __name__ == "__main__":
    main()
