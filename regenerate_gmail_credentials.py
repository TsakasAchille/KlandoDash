#!/usr/bin/env python3
"""
Script pour régénérer les credentials Gmail OAuth2 avec les bons scopes
ATTENTION: Ce script contient des informations sensibles - ne pas committer !
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration OAuth2 pour Gmail avec TOUS les scopes nécessaires
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def regenerate_gmail_credentials():
    """
    Régénère les credentials Gmail avec les bons scopes
    """
    print("=== Régénération des credentials Gmail OAuth2 ===\n")
    
    # Récupérer les credentials depuis les variables d'environnement
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Variables GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET requises")
        print("Ajoutez-les à votre fichier .env")
        return
    
    # Créer la configuration client OAuth2
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    try:
        # Créer le flow OAuth2
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        
        # Obtenir l'URL d'autorisation
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print(f"🔗 Ouvrez cette URL dans votre navigateur:")
        print(f"{auth_url}\n")
        
        # Demander le code d'autorisation
        auth_code = input("Collez le code d'autorisation ici: ").strip()
        
        # Échanger le code contre des tokens
        flow.fetch_token(code=auth_code)
        
        # Obtenir les credentials
        creds = flow.credentials
        
        print("\n✅ Credentials régénérés avec succès!")
        print(f"📋 Scopes autorisés: {creds.scopes}")
        
        # Sauvegarder en pickle pour développement local
        with open('klando_gmail_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("💾 Token sauvegardé dans: klando_gmail_token.pickle")
        
        # Afficher les variables d'environnement pour production
        print("\n📋 Variables d'environnement pour production:")
        print(f"GMAIL_TOKEN={creds.token}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print(f"GMAIL_CLIENT_ID={creds.client_id}")
        print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
        
        print("\n⚠️  Copiez ces variables dans votre .env ou sur Render")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    regenerate_gmail_credentials()
