#!/usr/bin/env python3
"""
Script pour configurer Gmail Watch API avec Pub/Sub
"""
import os
import sys
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def setup_gmail_watch():
    """Configure Gmail Watch pour recevoir les notifications Push"""
    
    print("🔧 Configuration Gmail Watch API")
    print("=" * 50)
    
    # 1. Récupérer les credentials Gmail
    credentials = get_gmail_credentials()
    if not credentials:
        print("❌ Impossible de récupérer les credentials Gmail")
        return False
    
    # 2. Créer le service Gmail
    try:
        service = build('gmail', 'v1', credentials=credentials)
        print("✅ Service Gmail créé")
    except Exception as e:
        print(f"❌ Erreur création service Gmail: {e}")
        return False
    
    # 3. Configurer la surveillance avec votre topic Pub/Sub
    topic_name = "projects/dashmails/topics/gmail-push-notifications"
    
    try:
        # Configuration de la surveillance
        request_body = {
            'labelIds': ['INBOX'],  # Surveiller seulement la boîte de réception
            'topicName': topic_name
        }
        
        print(f"📧 Configuration de la surveillance...")
        print(f"Topic: {topic_name}")
        
        # Activer la surveillance
        result = service.users().watch(userId='me', body=request_body).execute()
        
        print("✅ Gmail Watch configuré avec succès!")
        print(f"📋 Détails de la surveillance:")
        print(f"   - History ID: {result.get('historyId')}")
        print(f"   - Expiration: {result.get('expiration')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration Gmail Watch: {e}")
        print("\n🔍 Vérifications nécessaires:")
        print("1. Le topic Pub/Sub existe-t-il dans Google Cloud?")
        print("2. Les permissions sont-elles configurées?")
        print("3. L'API Gmail est-elle activée?")
        return False

def get_gmail_credentials():
    """Récupère les credentials Gmail"""
    try:
        # Essayer les variables d'environnement d'abord
        gmail_token = os.getenv('GMAIL_TOKEN')
        gmail_refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        gmail_client_id = os.getenv('GMAIL_CLIENT_ID')
        gmail_client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        
        if all([gmail_token, gmail_refresh_token, gmail_client_id, gmail_client_secret]):
            print("✅ Utilisation des variables d'environnement")
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
                    print("✅ Token rafraîchi")
                except Exception as refresh_error:
                    print(f"❌ Erreur rafraîchissement: {refresh_error}")
                    return None
            
            return credentials
        
        # Fallback sur le fichier pickle
        token_file = 'klando_gmail_token.pickle'
        if os.path.exists(token_file):
            print("✅ Utilisation du fichier token local")
            with open(token_file, 'rb') as f:
                return pickle.load(f)
        
        print("❌ Aucun credential trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur récupération credentials: {e}")
        return None

def test_webhook():
    """Teste l'endpoint webhook"""
    import requests
    
    print("\n🧪 Test de l'endpoint webhook")
    print("=" * 30)
    
    webhook_url = "https://bumpy-colts-repair.loca.lt/api/email/test"
    
    test_data = {
        "subject": "Re: Réponse à votre ticket de support",
        "from": "client@test.com",
        "body": f"Test de réponse pour le ticket.\n\n---\nTicket ID: 1522456d-2eef-41b1-8a13-e8991b592281"
    }
    
    try:
        print(f"📤 Envoi vers: {webhook_url}")
        response = requests.post(webhook_url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test réussi: {result}")
            return True
        else:
            print(f"❌ Test échoué: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    print("Gmail Watch Configuration")
    print("=" * 40)
    
    choice = input("Choisissez:\n1. Configurer Gmail Watch\n2. Tester webhook\n3. Les deux\nChoix (1/2/3): ")
    
    if choice in ['1', '3']:
        success = setup_gmail_watch()
        if not success:
            print("\n⚠️  Configuration échouée. Vérifiez les prérequis.")
    
    if choice in ['2', '3']:
        test_webhook()
    
    print("\n✅ Script terminé")
