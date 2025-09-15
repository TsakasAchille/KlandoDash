#!/usr/bin/env python3
"""
Test script for UserTripsService with Supabase integration
Tests the refactored service with real data from user bk17O0BBAndQR7xxSZxDvAGkSWU2
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

# Set environment variables for testing
os.environ['DEBUG_USERS'] = 'True'

def test_user_trips_service():
    """Test UserTripsService with real Supabase data"""
    print("=" * 70)
    print("🚗 TEST USER TRIPS SERVICE - SUPABASE INTEGRATION")
    print("=" * 70)
    
    try:
        from dash_apps.services.user_trips_service import UserTripsService
        
        # Test user ID
        test_uid = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        print(f"👤 Test utilisateur: {test_uid}")
        
        # Test 1: All trips
        print("\n🧪 Test 1: Tous les trajets")
        print("-" * 50)
        all_trips = UserTripsService.get_user_trips(test_uid, "all", limit=5)
        print(f"✅ Résultat: {len(all_trips.get('trips', []))} trajets trouvés")
        print(f"📊 Type: {all_trips.get('trip_type')}")
        print(f"📈 Total count: {all_trips.get('total_count')}")
        
        if all_trips.get('trips'):
            first_trip = all_trips['trips'][0]
            print(f"🚗 Premier trajet:")
            print(f"   - ID: {first_trip.get('trip_id')}")
            print(f"   - Route: {first_trip.get('route')}")
            print(f"   - Date: {first_trip.get('departure_datetime')}")
            print(f"   - Conducteur: {first_trip.get('is_driver')}")
            print(f"   - Passager: {first_trip.get('is_passenger')}")
        
        # Test 2: Driver trips only
        print("\n🧪 Test 2: Trajets conducteur uniquement")
        print("-" * 50)
        driver_trips = UserTripsService.get_user_trips(test_uid, "driver", limit=5)
        print(f"✅ Résultat: {len(driver_trips.get('trips', []))} trajets conducteur")
        
        # Test 3: Passenger trips only
        print("\n🧪 Test 3: Trajets passager uniquement")
        print("-" * 50)
        passenger_trips = UserTripsService.get_user_trips(test_uid, "passenger", limit=5)
        print(f"✅ Résultat: {len(passenger_trips.get('trips', []))} trajets passager")
        
        # Test 4: Cache behavior
        print("\n🧪 Test 4: Comportement du cache")
        print("-" * 50)
        start_time = datetime.now()
        cached_trips = UserTripsService.get_user_trips(test_uid, "all", limit=5)
        end_time = datetime.now()
        cache_time = (end_time - start_time).total_seconds()
        print(f"⚡ Temps de réponse (cache): {cache_time:.3f}s")
        print(f"📊 Même nombre de trajets: {len(cached_trips.get('trips', [])) == len(all_trips.get('trips', []))}")
        
        # Test 5: Invalid user
        print("\n🧪 Test 5: Utilisateur invalide")
        print("-" * 50)
        invalid_trips = UserTripsService.get_user_trips("invalid_uid", "all", limit=5)
        print(f"✅ Résultat: {len(invalid_trips.get('trips', []))} trajets (attendu: 0)")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 70)
        print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Utilisateur testé: {test_uid}")
        print(f"🚗 Tous les trajets: {len(all_trips.get('trips', []))}")
        print(f"🎯 Trajets conducteur: {len(driver_trips.get('trips', []))}")
        print(f"🎫 Trajets passager: {len(passenger_trips.get('trips', []))}")
        print(f"⚡ Cache fonctionnel: {'✅' if cache_time < 0.1 else '⚠️'}")
        print(f"🔍 Gestion erreurs: {'✅' if len(invalid_trips.get('trips', [])) == 0 else '❌'}")
        
        # Detailed trip analysis
        if all_trips.get('trips'):
            print(f"\n📊 ANALYSE DÉTAILLÉE DES TRAJETS")
            print("-" * 50)
            for i, trip in enumerate(all_trips['trips'][:3], 1):
                print(f"🚗 Trajet {i}:")
                print(f"   - ID: {trip.get('trip_id')}")
                print(f"   - Route: {trip.get('departure_city')} → {trip.get('arrival_city')}")
                print(f"   - Date: {trip.get('departure_date')} {trip.get('departure_time')}")
                print(f"   - Prix: {trip.get('price')}€")
                print(f"   - Places: {trip.get('seats_info')}")
                print(f"   - Statut: {trip.get('status')}")
                print(f"   - Rôle: {'Conducteur' if trip.get('is_driver') else 'Passager'}")
                print()
        
        print("🏁 Test terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_trips_service()
    sys.exit(0 if success else 1)
