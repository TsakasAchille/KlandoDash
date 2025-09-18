#!/usr/bin/env python3
"""
Script de test pour diagnostiquer le problème des passagers
"""
import os
import sys
import json
from typing import Dict, Any, List, Optional

# Ajouter le chemin du projet
sys.path.insert(0, '/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

def test_passengers_fetch():
    """Test direct de récupération des passagers"""
    
    trip_id = "TRIP-1757948516580768-8ciC1I4db5f48vcJ1KWJyY9R65C3"
    
    print(f"🔍 TEST PASSENGERS FETCH - {trip_id}")
    print("=" * 80)
    
    try:
        # 1. Test de la requête Supabase directe
        print("\n1️⃣ TEST REQUÊTE SUPABASE DIRECTE")
        print("-" * 50)
        
        from dash_apps.utils.supabase_client import supabase
        
        # Requête simple d'abord
        print("📋 Requête simple bookings...")
        simple_response = supabase.table('bookings').select('*').eq('trip_id', trip_id).execute()
        
        print(f"✅ Réponse simple: {len(simple_response.data)} résultats")
        if simple_response.data:
            print("📄 Premier résultat simple:")
            print(json.dumps(simple_response.data[0], indent=2, default=str))
        
        # Requête avec jointure comme dans la config
        print("\n📋 Requête avec jointure users...")
        join_query = "trip_id, user_id, seats, status, created_at, users!inner(uid, name, display_name, first_name, email, phone_number, photo_url, role)"
        
        join_response = supabase.table('bookings').select(join_query).eq('trip_id', trip_id).execute()
        
        print(f"✅ Réponse jointure: {len(join_response.data)} résultats")
        if join_response.data:
            print("📄 Premier résultat jointure:")
            print(json.dumps(join_response.data[0], indent=2, default=str))
            
            # Analyser la structure
            first_result = join_response.data[0]
            print(f"\n🔍 Structure du premier résultat:")
            for key, value in first_result.items():
                print(f"  - {key}: {type(value)} = {value}")
        
        # 2. Test de la configuration
        print("\n2️⃣ TEST CONFIGURATION")
        print("-" * 50)
        
        from dash_apps.utils.settings import load_json_config
        config = load_json_config('trip_passengers.json')
        
        print("📋 Configuration chargée:")
        print(f"  - Queries: {list(config.get('queries', {}).keys())}")
        print(f"  - Field mappings: {len(config.get('field_mappings', {}))}")
        print(f"  - Cache TTL: {config.get('cache', {}).get('ttl_seconds')}")
        
        # 3. Test de transformation
        print("\n3️⃣ TEST TRANSFORMATION")
        print("-" * 50)
        
        if join_response.data:
            from dash_apps.services.trip_passengers_cache_service import TripPassengersCache
            
            field_mappings = config.get('field_mappings', {})
            print(f"📋 Field mappings: {field_mappings}")
            
            for i, passenger in enumerate(join_response.data):
                print(f"\n🧑‍🤝‍🧑 Passager {i+1}:")
                print(f"  Données brutes: {passenger}")
                
                transformed = TripPassengersCache._transform_passenger_data(passenger, field_mappings)
                print(f"  Données transformées: {transformed}")
        
        # 4. Test de validation Pydantic
        print("\n4️⃣ TEST VALIDATION PYDANTIC")
        print("-" * 50)
        
        if join_response.data:
            from dash_apps.models.config_models import TripPassengersDataModel
            
            for i, passenger in enumerate(join_response.data):
                transformed = TripPassengersCache._transform_passenger_data(passenger, field_mappings)
                
                try:
                    validated = TripPassengersDataModel.model_validate(transformed, strict=False)
                    print(f"✅ Passager {i+1} validé: {validated.dict()}")
                except Exception as e:
                    print(f"❌ Erreur validation passager {i+1}: {e}")
                    print(f"   Données: {transformed}")
        
        # 5. Test du service complet
        print("\n5️⃣ TEST SERVICE COMPLET")
        print("-" * 50)
        
        # Activer le debug
        os.environ['DEBUG_TRIP_PASSENGERS'] = 'true'
        
        result = TripPassengersCache.get_trip_passengers_data(trip_id)
        
        print(f"✅ Résultat service: {len(result) if result else 0} passagers")
        if result:
            print("📄 Premier passager du service:")
            print(json.dumps(result[0], indent=2, default=str))
        
    except Exception as e:
        print(f"❌ ERREUR GLOBALE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_passengers_fetch()
