import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.database import get_session, Trip

def check_trips():
    """Vu00e9rifie les donnu00e9es dans la table trips"""
    session = get_session()
    
    # Vu00e9rifier la table trips
    trips_count = session.query(Trip).count()
    print(f"Nombre de trajets dans la base de donnu00e9es: {trips_count}")
    
    if trips_count > 0:
        trips = session.query(Trip).limit(5).all()
        print("\nExemples de trajets:")
        for trip in trips:
            print(f"  - ID: {trip.trip_id}")
            print(f"    De: {trip.departure_name} u00e0 {trip.destination_name}")
            print(f"    Distance: {trip.trip_distance} km")
            print(f"    Prix par siu00e8ge: {trip.price_per_seat} FCFA")
            print(f"    Siu00e8ges: {trip.available_seats}/{trip.number_of_seats}")
            print()
    
    session.close()
    
    return trips_count

if __name__ == "__main__":
    print("Vu00e9rification des trajets dans PostgreSQL...")
    trips_count = check_trips()
    
    if trips_count == 0:
        print("\nAucun trajet trouvu00e9 dans la base de donnu00e9es.")
    else:
        print(f"\nTotal: {trips_count} trajets dans la base de donnu00e9es.")
