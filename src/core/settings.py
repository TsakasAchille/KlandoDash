# Modification proposée pour settings.py
import os
import json
from pathlib import Path

# Chemin absolu vers le répertoire du projet
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# Chemins relatifs au répertoire du projet
RESOURCE_DIR = PROJECT_DIR / "src" / "resources"
CONFIG_PATH = RESOURCE_DIR / "config.json"
FIREBASE_KEY_PATH = RESOURCE_DIR / "keys" / "klando-d3cb3-firebase-adminsdk-uak7b-7af3798d36.json"

# Chemins pour les sorties de données
OUTPUT_DIRS = {
    "chats": PROJECT_DIR / "data" / "raw" / "chats",
    "users": PROJECT_DIR / "data" / "raw" / "users",
    "trips": PROJECT_DIR / "data" / "raw" / "trips"
}

# Configurations Firebase - Maintenant avec support des variables d'environnement
def get_firebase_config():
    """Récupère la configuration Firebase depuis le fichier local ou les variables d'environnement"""
    if os.environ.get('FIREBASE_CREDENTIALS'):
        print("Utilisation des credentials Firebase depuis la variable d'environnement")
        return {
            "credentials_json": json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
        }
    elif os.path.exists(FIREBASE_KEY_PATH):
        print("Utilisation des credentials Firebase depuis le fichier local")
        return {
            "key_path": FIREBASE_KEY_PATH
        }
    else:
        raise Exception("Aucune information d'authentification Firebase trouvée")

FIREBASE_CONFIG = get_firebase_config()

# Fonction pour obtenir un chemin absolu
def get_abs_path(rel_path):
    """Convertit un chemin relatif en chemin absolu par rapport au répertoire du projet"""
    return os.path.join(PROJECT_DIR, rel_path)

# Fonction pour s'assurer qu'un répertoire existe
def ensure_dir(dir_path):
    """Crée un répertoire s'il n'existe pas"""
    os.makedirs(dir_path, exist_ok=True)
    return dir_path