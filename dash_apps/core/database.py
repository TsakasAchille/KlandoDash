"""
Module de connexion à la base de données PostgreSQL/Supabase (compatible SQLAlchemy, services, Pydantic)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")

# Connexion à la base PostgreSQL
engine = create_engine(DATABASE_URL)

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
