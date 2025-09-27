#!/usr/bin/env python3
"""
Test pour vérifier que le display_name des passagers fonctionne correctement
"""
import os
import sys
sys.path.append('.')

# Activer le debug
os.environ['DEBUG_TRIP_PASSENGERS'] = 'true'

from dash_apps.services.trip_passengers_cache_service import TripPassengersCache

def test_passengers_display_name():
    """Test le display_name des passagers"""
    # Utiliser un trip_id qui a des passagers (d'après les logs)
    trip_id = "TRIP-1758214129289639-SoMfalwk5yRq7GqCXJZjSkogDJr1"
    
    print(f"=== TEST PASSENGERS DISPLAY NAME ===")
    print(f"Trip ID: {trip_id}")
    print()
    
    # Récupérer les données des passagers
    passengers_data = TripPassengersCache.get_trip_passengers_data(trip_id)
    
    if passengers_data:
        print(f"✅ {len(passengers_data)} passager(s) trouvé(s)")
        for i, passenger in enumerate(passengers_data, 1):
            print(f"\n--- PASSAGER {i} ---")
            print(f"display_name: {passenger.get('display_name', 'N/A')}")
            print(f"first_name: {passenger.get('first_name', 'N/A')}")
            print(f"name: {passenger.get('name', 'N/A')}")
            print(f"email: {passenger.get('email', 'N/A')}")
            print(f"photo_url: {passenger.get('photo_url', 'N/A')}")
            print(f"photo_url length: {len(passenger.get('photo_url', '')) if passenger.get('photo_url') else 0}")
    else:
        print("❌ Aucun passager trouvé")
    
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    test_passengers_display_name()
