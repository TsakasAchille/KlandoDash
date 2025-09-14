#!/usr/bin/env python3
"""
Script pour tester la connexion à Supabase
"""
import time
import psycopg2
import sys

# URL de connexion
DATABASE_URL = "postgresql://postgres.zzxeimcchndnrildeefl:tZkeDbCUZADB@aws-0-eu-west-3.pooler.supabase.com:5432/postgres?sslmode=require"

print("Tentative de connexion à Supabase...")
start_time = time.time()

try:
    # Établir une connexion avec un timeout court
    connection = psycopg2.connect(DATABASE_URL, connect_timeout=5)
    
    # Créer un curseur
    cursor = connection.cursor()
    
    # Exécuter une requête simple
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    # Fermer le curseur et la connexion
    cursor.close()
    connection.close()
    
    # Calculer le temps écoulé
    elapsed_time = time.time() - start_time
    
    print(f"✅ Connexion réussie en {elapsed_time:.2f} secondes.")
    print(f"Résultat du test: {result[0]}")
    sys.exit(0)
    
except Exception as e:
    # Calculer le temps écoulé jusqu'à l'erreur
    elapsed_time = time.time() - start_time
    
    print(f"❌ Échec de la connexion après {elapsed_time:.2f} secondes.")
    print(f"Erreur: {e}")
    sys.exit(1)
