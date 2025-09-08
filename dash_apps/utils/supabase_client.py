"""
Client Supabase pour KlandoDash
Fournit une instance du client Supabase pour l'API REST
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Créer l'instance du client
supabase: Client = create_client(supabase_url, supabase_key)
