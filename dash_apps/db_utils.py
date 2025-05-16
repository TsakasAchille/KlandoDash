import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import os

# Exemple: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def get_trip_passengers(trip_id):
    """
    Récupère la liste des IDs passagers pour un trip_id depuis la table trip_passengers (comme Streamlit).
    """
    from sqlalchemy import text
    query = text("""
        SELECT passenger_id FROM trip_passengers WHERE trip_id = :trip_id
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"trip_id": trip_id})
    return df["passenger_id"].tolist() if not df.empty else []
