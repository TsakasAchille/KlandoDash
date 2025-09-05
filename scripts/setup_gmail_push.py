#!/usr/bin/env python3
"""
Script pour configurer Gmail Push notifications
Permet de recevoir des notifications en temps réel quand un email arrive
"""

import os
import sys
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def setup_gmail_push_notifications():
    """Configure Gmail Push notifications pour recevoir les emails entrants"""
    
    print("🔧 Configuration Gmail Push Notifications")
    print("=" * 50)
    
    # 1. Récupérer les credentials
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
    
    # 3. Configurer le topic Pub/Sub (vous devez créer ce topic dans Google Cloud)
    # Pour Render, utilisez l'URL de votre application déployée
    webhook_url = input("Entrez l'URL de votre webhook (ex: https://votre-app.onrender.com/api/email/webhook): ")
    
    if not webhook_url:
        print("❌ URL webhook requise")
        return False
    
    # 4. Configurer la surveillance (watch)
    try:
        # Note: Pour une vraie implémentation, vous devez configurer Google Cloud Pub/Sub
        # Ici on montre la structure, mais il faut un topic Pub/Sub réel
        
        print("⚠️  IMPORTANT: Configuration manuelle requise")
        print()
        print("Pour activer Gmail Push notifications:")
        print("1. Créez un projet Google Cloud Console")
        print("2. Activez l'API Gmail")
        print("3. Créez un topic Pub/Sub")
        print("4. Configurez les permissions")
        print("5. Utilisez ce code pour activer la surveillance:")
        print()
        print("request_body = {")
        print("    'labelIds': ['INBOX'],")
        print("    'topicName': 'projects/YOUR_PROJECT/topics/YOUR_TOPIC'")
        print("}")
        print("service.users().watch(userId='me', body=request_body).execute()")
        print()
        print(f"📧 Webhook URL configurée: {webhook_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration Push: {e}")
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
            return Credentials(
                token=gmail_token,
                refresh_token=gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=gmail_client_id,
                client_secret=gmail_client_secret,
                scopes=['https://www.googleapis.com/auth/gmail.readonly']
            )
        
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

def test_webhook_endpoint():
    """Teste l'endpoint webhook localement"""
    import requests
    import json
    
    print("\n🧪 Test de l'endpoint webhook")
    print("=" * 30)
    
    # URL locale pour test
    test_url = "http://localhost:8050/api/email/test"
    
    # Données de test
    test_data = {
        "subject": "Re: Réponse à votre ticket de support - TEST DE TICKET",
        "from": "client@example.com",
        "body": f"""Bonjour,

Merci pour votre réponse rapide. J'ai une question supplémentaire...

Cordialement,
Client Test

---
Ticket ID: 4e4745ab-9aff-4025-b003-16a2f99ff300
"""
    }
    
    try:
        response = requests.post(test_url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test réussi: {result}")
            return True
        else:
            print(f"❌ Test échoué: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'application")
        print("Assurez-vous que l'application Dash est démarrée (python -m dash_apps.app)")
        return False
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    print("Gmail Push Notifications Setup")
    print("=" * 40)
    
    choice = input("Choisissez une option:\n1. Configurer Push notifications\n2. Tester webhook\n3. Les deux\nChoix (1/2/3): ")
    
    if choice in ['1', '3']:
        setup_gmail_push_notifications()
    
    if choice in ['2', '3']:
        test_webhook_endpoint()
    
    print("\n✅ Script terminé")
