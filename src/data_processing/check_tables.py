import os
import sys

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.database import execute_raw_query

def check_db_tables():
    """Vu00e9rifie les tables existantes dans la base de donnu00e9es"""
    # Lister toutes les tables
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    """
    tables = execute_raw_query(tables_query)
    
    print("Tables existantes dans la base de donnu00e9es:")
    for table in tables:
        print(f"- {table[0]}")
        
        # Lister les colonnes de chaque table
        columns_query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table[0]}'
        """
        columns = execute_raw_query(columns_query)
        
        print("  Colonnes:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        print()

if __name__ == "__main__":
    print("Vu00e9rification des tables dans PostgreSQL...")
    check_db_tables()
