import json
import os
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, ForeignKey
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, TIMESTAMP
import importlib.resources as pkg_resources
from pathlib import Path

# Récupère la DATABASE_URL depuis les variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Chemin vers les fichiers de définition
DATA_DEF_DIR = Path("/home/tsakas/Desktop/KlandoDash/dash_apps/utils/data_definition")

def get_type_mapping(type_str):
    """Convertit le type de données PostgreSQL en type SQLAlchemy"""
    type_map = {
        'text': String,
        'varchar': String,
        'integer': Integer,
        'bigint': Integer,
        'double precision': Float,
        'numeric': Float,
        'boolean': Boolean,
        'date': Date,
        'timestamp with time zone': DateTime,
        'timestamp without time zone': DateTime,
        'uuid': String,
    }
    return type_map.get(type_str.lower(), String)

def load_table_definition(table_name):
    """Charge la définition d'une table à partir du fichier JSON correspondant"""
    try:
        file_path = DATA_DEF_DIR / f"{table_name}.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la définition de {table_name}: {e}")
        return []

def load_keys():
    """Charge les relations de clés étrangères à partir du fichier keys.json"""
    try:
        file_path = DATA_DEF_DIR / "keys.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des clés: {e}")
        return []

def get_table_schema(table_name):
    """Retourne le schéma d'une table basé sur sa définition JSON"""
    table_def = load_table_definition(table_name)
    return {col["column_name"]: col["data_type"] for col in table_def}

def execute_query(query, params=None):
    """Exécute une requête SQL et retourne le résultat sous forme de DataFrame"""
    try:
        with engine.connect() as conn:
            result = pd.read_sql(text(query), conn, params=params)
            return result
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête: {e}")
        return pd.DataFrame()

def get_all_from_table(table_name, conditions=None, limit=None):
    """Récupère toutes les données d'une table avec conditions optionnelles"""
    query = f"SELECT * FROM {table_name}"
    
    if conditions:
        query += f" WHERE {conditions}"
    
    if limit:
        query += f" LIMIT {limit}"
        
    return execute_query(query)

def get_trips():
    """Récupère tous les trajets de la base de données"""
    return get_all_from_table("trips")

def get_trip_by_id(trip_id):
    """Récupère un trajet par son ID"""
    query = "SELECT * FROM trips WHERE trip_id = :trip_id"
    result = execute_query(query, {"trip_id": trip_id})
    return result.to_dict('records')[0] if not result.empty else None

def get_bookings_for_trip(trip_id):
    """Récupère toutes les réservations pour un trajet donné"""
    query = "SELECT * FROM bookings WHERE trip_id = :trip_id"
    return execute_query(query, {"trip_id": trip_id})

def get_passengers_for_trip(trip_id):
    """Récupère tous les passagers d'un trajet (avec leurs informations)"""
    query = """
    SELECT u.* 
    FROM users u
    JOIN bookings b ON u.uid = b.user_id
    WHERE b.trip_id = :trip_id
    """
    return execute_query(query, {"trip_id": trip_id})

def get_trips_for_user(user_id, as_driver=False, as_passenger=False):
    """
    Récupère tous les trajets d'un utilisateur
    Si as_driver=True, retourne uniquement les trajets où l'utilisateur est conducteur
    Si as_passenger=True, retourne uniquement les trajets où l'utilisateur est passager
    Si les deux sont False, retourne tous les trajets de l'utilisateur
    """
    if as_driver and not as_passenger:
        query = "SELECT * FROM trips WHERE driver_id = :user_id"
        return execute_query(query, {"user_id": user_id})
    elif as_passenger and not as_driver:
        query = """
        SELECT t.* 
        FROM trips t
        JOIN bookings b ON t.trip_id = b.trip_id
        WHERE b.user_id = :user_id
        """
        return execute_query(query, {"user_id": user_id})
    else:
        # Les deux ou aucun des deux
        query = """
        SELECT DISTINCT t.* 
        FROM trips t
        LEFT JOIN bookings b ON t.trip_id = b.trip_id
        WHERE t.driver_id = :user_id OR b.user_id = :user_id
        """
        return execute_query(query, {"user_id": user_id})

def get_support_tickets(user_id=None):
    """Récupère tous les tickets de support, optionnellement filtrés par utilisateur"""
    if user_id:
        return get_all_from_table("support_tickets", f"user_id = '{user_id}'")
    else:
        return get_all_from_table("support_tickets")
