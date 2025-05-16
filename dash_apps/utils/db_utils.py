import pandas as pd
from sqlalchemy import create_engine, text
import os

# Récupère la DATABASE_URL depuis les variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_trip_passengers(trip_id):
    """
    Récupère la liste des IDs passagers pour un trip_id depuis la table trip_passengers (comme Streamlit).
    """
    query = text("""
        SELECT passenger_id FROM trip_passengers WHERE trip_id = :trip_id
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"trip_id": trip_id})
    return df["passenger_id"].tolist() if not df.empty else []
