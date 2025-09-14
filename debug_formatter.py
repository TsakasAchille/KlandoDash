#!/usr/bin/env python3
"""
Debug script pour identifier le problème avec TripDetailsFormatter
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configuration du debug
os.environ['DEBUG_TRIPS'] = 'true'

def debug_formatter():
    """Debug du TripDetailsFormatter"""
    
    # Données de test (format réel de la DB)
    test_data = {
        "trip_id": "TRIP-1756361288826038-n739xt2Uy0Qb5hP30AJ1G3dnT8G3",
        "driver_id": "n739xt2Uy0Qb5hP30AJ1G3dnT8G3",
        "departure_name": "Abidjan",
        "destination_name": "Bouaké",
        "departure_schedule": "2024-09-14T12:00:00+00:00",
        "status": "active",
        "distance": 350,
        "seats_published": 4,
        "seats_available": 2,
        "seats_booked": 2,
        "passenger_price": 5000,
        "driver_price": 15000,
        "created_at": "2024-09-14T10:00:00+00:00",
        "updated_at": "2024-09-14T11:00:00+00:00"
    }
    
    print("=== DEBUG TRIPDETAILSFORMATTER ===")
    print(f"Données d'entrée: {test_data}")
    
    try:
        from dash_apps.utils.trip_details_formatter import TripDetailsFormatter
        
        print("\n1. Initialisation du formatter...")
        formatter = TripDetailsFormatter()
        print("✅ Formatter initialisé")
        
        print("\n2. Test du formatage...")
        formatted_data = formatter.format_for_display(test_data)
        
        print(f"✅ Données formatées: {formatted_data}")
        print(f"Type: {type(formatted_data)}")
        print(f"Nombre de champs: {len(formatted_data) if formatted_data else 0}")
        
        if formatted_data:
            print("\n3. Détail des champs formatés:")
            for key, value in formatted_data.items():
                print(f"   - {key}: {value} ({type(value).__name__})")
        else:
            print("❌ Aucune donnée formatée retournée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_formatter()
