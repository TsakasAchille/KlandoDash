import os
import sys
from pathlib import Path

# Ajouter automatiquement le répertoire racine du projet au PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ces imports seront disponibles quand on importe 'src'
from src.core.settings import FIREBASE_KEY_PATH