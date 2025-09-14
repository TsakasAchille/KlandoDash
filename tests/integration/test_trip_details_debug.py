#!/usr/bin/env python3
"""
Test du système trip details avec debug
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dash_apps.services.trip_details_cache_service import TripDetailsCache

def test_trip_details_system():
    """Test complet du système trip details avec debug"""
    print("🧪 TEST DU SYSTÈME TRIP DETAILS AVEC DEBUG")
    print("=" * 60)
    
    # Test avec un ID de trajet fictif
    test_trip_id = "TRIP-123456789"
    
    print(f"🎯 Test avec trip_id: {test_trip_id}")
    print("-" * 40)
    
    try:
        # Appel du système complet
        result = TripDetailsCache.get_trip_details_panel(test_trip_id)
        
        print(f"✅ Résultat obtenu: {type(result)}")
        if hasattr(result, 'children'):
            print(f"📋 Nombre d'enfants: {len(result.children) if result.children else 0}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trip_details_system()
