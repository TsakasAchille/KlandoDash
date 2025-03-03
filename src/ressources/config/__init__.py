import json
import os

# Chemin vers le fichier de configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

# Charger la configuration
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

__all__ = ['CONFIG']