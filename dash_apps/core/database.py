"""
Module de connexion à la base de données PostgreSQL/Supabase (compatible SQLAlchemy, services, Pydantic)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Récupérer l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

# Créer l'engine SQLAlchemy avec optimisations de performance
engine = create_engine(
    DATABASE_URL,
    # Configuration du pool de connexions pour optimiser les performances
    pool_size=20,              # Nombre de connexions permanentes dans le pool
    max_overflow=30,           # Connexions supplémentaires autorisées
    pool_pre_ping=True,        # Vérifier la validité des connexions
    pool_recycle=3600,         # Recycler les connexions après 1h
    pool_timeout=30,           # Timeout pour obtenir une connexion
    
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
