#!/usr/bin/env python3
"""
Test script for user trips callback with refactored UserTripsService
Tests the update_user_trips callback with real Supabase data
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

# Set environment variables for testing
os.environ['DEBUG_USERS'] = 'True'

def test_user_trips_callback():
    """Test update_user_trips callback with real data"""
    print("=" * 70)
    print("📞 TEST USER TRIPS CALLBACK - SUPABASE INTEGRATION")
    print("=" * 70)
    
    try:
        # Import callback function
        from dash_apps.callbacks.users_callbacks import update_user_trips
        
        # Test user ID
        test_uid = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        print(f"👤 Test utilisateur: {test_uid}")
        
        # Test 1: String ID format
        print("\n🧪 Test 1: Format String ID")
        print("-" * 50)
        result1 = update_user_trips(test_uid)
        print(f"✅ Type de résultat: {type(result1)}")
        
        # Analyze result
        if hasattr(result1, 'children'):
            print(f"📊 Nombre d'enfants: {len(result1.children) if result1.children else 0}")
            if result1.children:
                first_child = result1.children[0]
                print(f"🏗️  Premier enfant: {type(first_child)}")
        elif isinstance(result1, str):
            print(f"📝 Message: {result1[:100]}...")
        
        # Test 2: Dict format
        print("\n🧪 Test 2: Format Dict")
        print("-" * 50)
        result2 = update_user_trips({"uid": test_uid})
        print(f"✅ Type de résultat: {type(result2)}")
        
        # Test 3: Empty/None user
        print("\n🧪 Test 3: Utilisateur vide")
        print("-" * 50)
        result3 = update_user_trips(None)
        print(f"✅ Résultat: {result3}")
        
        # Test 4: Invalid user
        print("\n🧪 Test 4: Utilisateur invalide")
        print("-" * 50)
        result4 = update_user_trips("invalid_uid")
        print(f"✅ Type de résultat: {type(result4)}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 RÉSUMÉ DES TESTS CALLBACK")
        print("=" * 70)
        print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Utilisateur testé: {test_uid}")
        print(f"📞 Test String ID: {'✅' if result1 is not None else '❌'}")
        print(f"📞 Test Dict format: {'✅' if result2 is not None else '❌'}")
        print(f"📞 Test utilisateur vide: {'✅' if isinstance(result3, str) else '❌'}")
        print(f"📞 Test utilisateur invalide: {'✅' if result4 is not None else '❌'}")
        
        # Check if results are consistent
        same_results = (type(result1) == type(result2))
        print(f"🔄 Cohérence formats: {'✅' if same_results else '⚠️'}")
        
        # Test service integration
        print(f"\n🔧 INTÉGRATION SERVICE")
        print("-" * 50)
        
        # Import and test service directly
        from dash_apps.services.user_trips_service import UserTripsService
        service_result = UserTripsService.get_user_trips(test_uid, "all", limit=5)
        trips_count = len(service_result.get('trips', []))
        print(f"🚗 Trajets trouvés par le service: {trips_count}")
        
        # Check if callback uses service correctly
        if trips_count > 0:
            print("✅ Service fonctionne - trajets disponibles")
            if hasattr(result1, 'children') and result1.children:
                print("✅ Callback génère du contenu - intégration réussie")
            else:
                print("⚠️ Callback ne génère pas de contenu malgré les trajets")
        else:
            print("⚠️ Aucun trajet trouvé par le service")
            if isinstance(result1, str) and "Aucun trajet" in result1:
                print("✅ Callback gère correctement l'absence de trajets")
        
        print("🏁 Test callback terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test callback: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_trips_callback()
    sys.exit(0 if success else 1)
