#!/usr/bin/env python3
"""
Script pour extraire les tokens Gmail OAuth2 du fichier pickle
et les afficher pour configuration sur Render
"""

import pickle
import os
import sys

def extract_gmail_tokens():
    """Extrait les tokens Gmail du fichier pickle"""
    
    token_file = 'klando_gmail_token.pickle'
    
    if not os.path.exists(token_file):
        print(f"❌ Fichier {token_file} non trouvé")
        print("Exécutez d'abord: python3 scripts/gmail_oauth_server.py")
        return False
    
    try:
        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)
        
        if not credentials:
            print("❌ Credentials vides dans le fichier pickle")
            return False
        
        print("🔑 TOKENS GMAIL OAUTH2 POUR RENDER")
        print("=" * 50)
        print()
        print("Copiez ces valeurs dans les variables d'environnement de Render :")
        print()
        print(f"GMAIL_TOKEN={credentials.token}")
        print(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}")
        print(f"GMAIL_CLIENT_ID={credentials.client_id}")
        print(f"GMAIL_CLIENT_SECRET={credentials.client_secret}")
        print()
        print("=" * 50)
        print("✅ Tokens extraits avec succès")
        print()
        print("📋 Instructions pour Render :")
        print("1. Allez dans votre dashboard Render")
        print("2. Sélectionnez votre service KlandoDash")
        print("3. Allez dans 'Environment'")
        print("4. Ajoutez ces 4 variables d'environnement")
        print("5. Redéployez votre application")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return False

if __name__ == "__main__":
    extract_gmail_tokens()
