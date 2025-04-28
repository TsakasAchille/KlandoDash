"""
Script d'initialisation de la base de données PostgreSQL/Supabase
Crée les tables nécessaires si elles n'existent pas déjà
"""
from src.core.database import init_db
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Fonction principale d'initialisation de la base de données"""
    try:
        logger.info("Initialisation de la base de données PostgreSQL...")
        init_db()
        logger.info("Base de données initialisée avec succès!")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False

if __name__ == "__main__":
    main()
