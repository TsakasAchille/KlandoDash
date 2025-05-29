import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.database import get_session, Trip, User, Chat

def check_tables():
    """Vérifie les données dans les tables PostgreSQL"""
    session = get_session()
    
    # Vérifier la table trips
    trips_count = session.query(Trip).count()
    print(f"Nombre de trajets dans la base de données: {trips_count}")
    if trips_count > 0:
        trips = session.query(Trip).limit(3).all()
        print("Exemples de trajets:")
        for trip in trips:
            print(f"  - ID: {trip.id}, De: {trip.departure_name}, À: {trip.destination_name}")
    
    # Vérifier la table users
    users_count = session.query(User).count()
    print(f"\nNombre d'utilisateurs dans la base de données: {users_count}")
    if users_count > 0:
        users = session.query(User).limit(3).all()
        print("Exemples d'utilisateurs:")
        for user in users:
            print(f"  - ID: {user.id}, Nom: {user.name}, Email: {user.email}")
    
    # Vérifier la table chats
    chats_count = session.query(Chat).count()
    print(f"\nNombre de messages dans la base de données: {chats_count}")
    if chats_count > 0:
        chats = session.query(Chat).limit(3).all()
        print("Exemples de messages:")
        for chat in chats:
            print(f"  - ID: {chat.id}, Message: {chat.message}")
    
    session.close()
    
    return trips_count, users_count, chats_count

if __name__ == "__main__":
    print("Vérification des données dans la base PostgreSQL...")
    trips_count, users_count, chats_count = check_tables()
    
    if trips_count == 0 and users_count == 0 and chats_count == 0:
        print("\nAucune donnée trouvée dans la base de données.")
        print("Vous devrez migrer vos données depuis les fichiers JSON ou créer de nouvelles données.")
    else:
        print("\nLa base de données contient des données.")
