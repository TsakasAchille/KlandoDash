#!/usr/bin/env python3
"""
Test avec un vrai trip_id depuis la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dash_apps.utils.data_schema_rest import get_trips
from dash_apps.services.trip_details_cache_service import TripDetailsCache

def test_with_real_trip():
    """Test avec un vrai trip_id"""
    print("🔍 RECHERCHE D'UN VRAI TRIP_ID")
    print("=" * 50)
    
    try:
        # Récupérer quelques trajets réels
        trips_df = get_trips()
        
        if trips_df.empty:
            print("❌ Aucun trajet trouvé dans la base de données")
            return
        
        print(f"✅ {len(trips_df)} trajets trouvés")
        
        # Prendre le premier trajet
        first_trip = trips_df.iloc[0]
        real_trip_id = first_trip['trip_id']
        
        print(f"🎯 Test avec trip_id réel: {real_trip_id}")
        print("-" * 50)
        
        # Test du système complet
        result = TripDetailsCache.get_trip_details_panel(real_trip_id)
        
        print(f"✅ Résultat: {type(result)}")
        if hasattr(result, 'children') and result.children:
            print(f"📋 Nombre d'enfants: {len(result.children)}")
            
            # Analyser le contenu
            child = result.children[0]
            if hasattr(child, 'color'):
                print(f"🎨 Type d'alerte: {child.color}")
            if hasattr(child, 'children') and child.children:
                print(f"📝 Contenu présent")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_real_trip()
