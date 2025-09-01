"""
Module de connexion à la base de données PostgreSQL/Supabase (compatible SQLAlchemy, services, Pydantic)
"""
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Charger les variables d'environnement depuis .env
load_dotenv()
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

def get_database_url():
    """Récupère l'URL de la base de données depuis les variables d'environnement"""
    db_url = os.getenv('DATABASE_URL')
    print(f"[DEBUG] DATABASE_URL: {'***' if db_url else 'NOT SET'}")
    return db_url

def create_database_engine():
    """Crée l'engine de base de données avec fallback vers SQLite local"""
    # Essayer d'abord la base de données configurée
    DATABASE_URL = get_database_url()
    
    if DATABASE_URL:
        try:
            # Tenter de créer l'engine PostgreSQL/Supabase
            engine = create_engine(
                DATABASE_URL,
                # Configuration du pool de connexions optimisée pour Supabase
                pool_size=5,               # 5 connexions de base
                max_overflow=10,           # 10 connexions supplémentaires max
                pool_pre_ping=True,        # Vérifier la validité des connexions
                pool_recycle=300,          # Recycler toutes les 5min
                pool_timeout=30,           # Timeout plus généreux
                
                # Gestion agressive des connexions
                pool_reset_on_return='commit',  # Reset à chaque retour
                
                # Optimisations des requêtes
                echo=False,                # Désactiver le logging SQL en production
                future=True,               # Utiliser la nouvelle API SQLAlchemy 2.0
                
                # Paramètres de connexion PostgreSQL optimisés
                connect_args={
                    "options": "-c default_transaction_isolation=read_committed",
                    "application_name": "KlandoDash",
                    "connect_timeout": 10,
                }
            )
            
            # Tester la connexion
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            
            logger.info("Connexion PostgreSQL/Supabase réussie")
            return engine
            
        except (OperationalError, Exception) as e:
            logger.warning(f"Échec de connexion à PostgreSQL/Supabase: {e}")
            logger.info("Basculement vers la base de données SQLite locale...")
    
    # Fallback vers SQLite local
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.db')
    sqlite_url = f"sqlite:///{sqlite_path}"
    
    logger.info(f"Utilisation de la base de données SQLite locale: {sqlite_path}")
    
    engine = create_engine(
        sqlite_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}  # Pour SQLite
    )
    
    return engine

# Créer l'engine avec fallback
engine = create_database_engine()

# Base ORM commune à tous les modèles
Base = declarative_base()

# Session locale (pattern standard SQLAlchemy)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Utilisation :
# from dash_apps.core.database import SessionLocal, Base, engine
# with SessionLocal() as db:
#     ...

def get_session():
    """Compatibilité descendante : retourne une session SQLAlchemy (à fermer manuellement ou à utiliser avec 'with')."""
    return SessionLocal()
