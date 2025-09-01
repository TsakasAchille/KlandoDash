"""
Script d'initialisation de la base de données SQLite/PostgreSQL
Crée les tables nécessaires si elles n'existent pas déjà
"""
import logging
from dash_apps.core.database import engine, Base
from dash_apps.models.user import User
from dash_apps.models.trip import Trip

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Initialise la base de données en créant toutes les tables"""
    try:
        logger.info("Création des tables de base de données...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès!")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables: {e}")
        return False

def main():
    """Fonction principale d'initialisation de la base de données"""
    return init_db()

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Base de données initialisée avec succès!")
    else:
        print("❌ Échec de l'initialisation de la base de données")
