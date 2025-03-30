# settings.py
import os
from pathlib import Path

# Chemin absolu vers le répertoire du projet
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# Chemins relatifs au répertoire du projet
RESOURCE_DIR = PROJECT_DIR /"src" / "resources"
CONFIG_PATH = RESOURCE_DIR / "config.json"
FIREBASE_KEY_PATH = RESOURCE_DIR / "keys" / "klando-d3cb3-firebase-adminsdk-uak7b-7af3798d36.json"

# Chemins pour les sorties de données
OUTPUT_DIRS = {
    "chats": PROJECT_DIR / "data" / "raw" / "chats",
    "users": PROJECT_DIR / "data" / "raw" / "users",
    "trips": PROJECT_DIR / "data" / "raw" / "trips"
}

# Configurations Firebase
FIREBASE_CONFIG = {
    "key_path": FIREBASE_KEY_PATH
}

# Fonction pour obtenir un chemin absolu
def get_abs_path(rel_path):
    """Convertit un chemin relatif en chemin absolu par rapport au répertoire du projet"""
    return os.path.join(PROJECT_DIR, rel_path)

# Fonction pour s'assurer qu'un répertoire existe
def ensure_dir(dir_path):
    """Crée un répertoire s'il n'existe pas"""
    os.makedirs(dir_path, exist_ok=True)
    return dir_path