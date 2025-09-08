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
    # Supprimer le print qui ralentit chaque import
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
                # Configuration optimisée pour la performance
                pool_size=5,               # Réduire le pool pour éviter les timeouts
                max_overflow=10,           # Moins de connexions supplémentaires
                pool_pre_ping=False,       # Désactiver pour éviter les délais
                pool_recycle=3600,         # Recycler moins souvent (1h)
                pool_timeout=2,            # Timeout très court (2s au lieu de 10s)
                
                # Optimisations des requêtes
                echo=False,                # Désactiver le logging SQL
                future=True,               # Utiliser SQLAlchemy 2.0
                
                # Paramètres de connexion PostgreSQL optimisés pour la vitesse
                connect_args={
                    "application_name": "KlandoDash",
                    "connect_timeout": 2,   # Timeout très court (2s au lieu de 5s)
                }
            )
            
            # Tester la connexion
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            
            logger.info("Connexion PostgreSQL/Supabase réussie")
            return engine
            
        except (OperationalError, Exception) as e:
            from dash_apps.config import Config
            # Si REST API est forcé, on n'utilise pas de fallback vers SQLite
            if Config.use_rest_api():
                logger.warning(f"Échec de connexion à PostgreSQL/Supabase: {e}")
                logger.info("Utilisation exclusive de l'API REST Supabase comme demandé")
                # Renvoyer un moteur factice pour ne pas casser les imports
                from sqlalchemy.pool import NullPool
                return create_engine('sqlite:///:memory:', poolclass=NullPool)
            else:
                # Ce code ne devrait plus être exécuté car Config.use_rest_api() retourne toujours True
                # On le garde pour la compatibilité ascendante
                logger.warning(f"Échec de connexion à PostgreSQL/Supabase: {e}")
                raise ConnectionError("La connexion à la base de données a échoué et l'application est configurée pour n'utiliser que l'API REST.")
    
    return engine

# Lazy initialization - engine créé seulement quand nécessaire
_engine = None

def get_engine():
    """Récupère l'engine de base de données (lazy loading)"""
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine

# Base ORM commune à tous les modèles
Base = declarative_base()

# Session locale avec lazy loading
def get_session_local():
    """Récupère SessionLocal avec lazy loading"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# Compatibilité - propriété qui charge l'engine seulement si nécessaire
class LazySessionLocal:
    def __call__(self):
        return get_session_local()()
    
    def __enter__(self):
        self._session = get_session_local()()
        return self._session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

SessionLocal = LazySessionLocal()

# Utilisation :
# from dash_apps.core.database import SessionLocal, Base, get_engine
# with SessionLocal as db:
#     ...

def get_session():
    """Compatibilité descendante : retourne une session SQLAlchemy (à fermer manuellement ou à utiliser avec 'with')."""
    return SessionLocal()

# Compatibilité pour l'accès direct à engine
def engine():
    """Propriété pour accès direct à l'engine (lazy loading)"""
    return get_engine()

# Rendre engine accessible comme attribut module
class _EngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)

engine = _EngineProxy()
