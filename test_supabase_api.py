#!/usr/bin/env python3
"""
Script pour tester la connexion à Supabase via l'API REST
"""
import os
import time
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Récupérer les informations de connexion
# URL correcte du projet Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Erreur: Variables d'environnement SUPABASE_URL ou SUPABASE_KEY non définies.")
    print("Veuillez vérifier votre fichier .env")
    sys.exit(1)

print(f"Tentative de connexion à Supabase via API REST...")
print(f"URL: {supabase_url}")
start_time = time.time()

try:
    # Initialiser le client Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Effectuer une requête simple
    response = supabase.table("dash_authorized_users").select("*").limit(1).execute()
    
    # Calculer le temps écoulé
    elapsed_time = time.time() - start_time
    
    print(f"✅ Connexion API réussie en {elapsed_time:.2f} secondes.")
    print(f"Données récupérées: {len(response.data)} enregistrements")
    if response.data:
        # Afficher un exemple d'enregistrement (sans afficher d'emails réels)
        sample = response.data[0].copy()
        if 'email' in sample:
            sample['email'] = "***@***.***"  # Masquer l'email pour la confidentialité
        print(f"Exemple de données: {sample}")
    
    sys.exit(0)
    
except Exception as e:
    # Calculer le temps écoulé jusqu'à l'erreur
    elapsed_time = time.time() - start_time
    
    print(f"❌ Échec de la connexion API après {elapsed_time:.2f} secondes.")
    print(f"Erreur: {e}")
    sys.exit(1)
