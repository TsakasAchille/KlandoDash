#!/usr/bin/env python3
"""
Script pour configurer Gmail OAuth2 pour KlandoDash
Ce script vous aide à obtenir les credentials nécessaires pour envoyer des emails via Gmail API
"""

import os
import json
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration OAuth2 pour Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
REDIRECT_URI = 'http://localhost:8080'

def setup_gmail_oauth():
    """
    Guide l'utilisateur pour configurer Gmail OAuth2
    """
    print("=== Configuration Gmail OAuth2 pour KlandoDash ===\n")
    
    print("1. Allez sur https://console.cloud.google.com/")
    print("2. Créez un nouveau projet ou sélectionnez un projet existant")
    print("3. Activez l'API Gmail (APIs & Services > Library > Gmail API)")
    print("4. Créez des credentials OAuth 2.0 (APIs & Services > Credentials)")
    print("5. Ajoutez http://localhost:8080 comme URI de redirection autorisée")
    print("6. Téléchargez le fichier JSON des credentials\n")
    
    # Demander le chemin vers le fichier credentials
    credentials_path = input("Chemin vers le fichier credentials.json téléchargé: ").strip()
    
    if not os.path.exists(credentials_path):
        print(f"❌ Fichier non trouvé: {credentials_path}")
        return
    
    try:
        # Créer le flow OAuth2
        flow = Flow.from_client_secrets_file(
            credentials_path,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Obtenir l'URL d'autorisation
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print(f"\n🔗 Ouvrez cette URL dans votre navigateur:")
        print(f"{auth_url}\n")
        
        # Demander le code d'autorisation
        auth_code = input("Collez le code d'autorisation ici: ").strip()
        
        # Échanger le code contre des tokens
        flow.fetch_token(code=auth_code)
        
        # Obtenir les credentials
        creds = flow.credentials
        
        # Créer le JSON des credentials pour .env
        credentials_json = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        
        print("\n✅ Configuration réussie!")
        print("\n📋 Ajoutez ces variables à votre fichier .env:")
        print(f"GMAIL_SENDER_EMAIL=votre-email@gmail.com")
        print(f"GMAIL_CREDENTIALS_JSON='{json.dumps(credentials_json)}'")
        
        # Sauvegarder dans un fichier temporaire
        with open('gmail_credentials.json', 'w') as f:
            json.dump(credentials_json, f, indent=2)
        
        print(f"\n💾 Credentials sauvegardés dans: gmail_credentials.json")
        print("⚠️  N'oubliez pas de supprimer ce fichier après avoir copié les credentials dans .env")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    setup_gmail_oauth()
