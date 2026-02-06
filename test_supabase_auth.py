from supabase import create_client, Client
import os

# === LA COMMANDE DE CONFIGURATION POUR BYPASSER LA RLS ===

# 1. Récupérez vos credentials depuis le dashboard Supabase (Settings > API)
SUPABASE_URL = "VOTRE_URL_SUPABASE"
# IMPORTANT: Utilisez la 'service_role' key, PAS la 'anon' key
SUPABASE_SERVICE_ROLE_KEY = "VOTRE_SERVICE_ROLE_KEY"

def get_admin_client() -> Client:
    """
    Crée un client Supabase avec les droits d'administration.
    Ce client ignore les règles RLS.
    """
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 2. LA COMMANDE D'INSERTION
def example_sync():
    supabase = get_admin_client()
    
    # Cette commande fonctionnera même si la RLS est activée
    data = {
        "uid": "test_user_123",
        "display_name": "Test User",
        "email": "test@example.com"
    }
    
    try:
        # La commande exacte pour insérer
        response = supabase.table("users").insert(data).execute()
        print(f"Succès : {response}")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    print("Configuration du client Supabase avec Service Role Key...")
    # example_sync()
