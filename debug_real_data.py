#!/usr/bin/env python3
"""
Debug script pour voir les vraies données de la DB et corriger le formatter
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configuration du debug
os.environ['DEBUG_TRIPS'] = 'true'

def debug_real_data():
    """Debug avec les vraies données de la DB"""
    
    test_trip_id = "TRIP-1756361288826038-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
    
    print("=== DEBUG VRAIES DONNÉES DB ===")
    
    try:
        # 1. Récupérer les vraies données via le repository
        from dash_apps.infrastructure.repositories.supabase_trip_repository import SupabaseTripRepository
        import asyncio
        
        print("1. Récupération des données via Repository...")
        repo = SupabaseTripRepository()
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, repo.get_by_trip_id(test_trip_id))
                real_data = future.result()
        except RuntimeError:
            real_data = asyncio.run(repo.get_by_trip_id(test_trip_id))
        
        if real_data:
            print(f"✅ Données récupérées: {len(real_data)} champs")
            print("Champs disponibles:")
            for key, value in real_data.items():
                print(f"   - {key}: {value} ({type(value).__name__})")
        else:
            print("❌ Aucune donnée récupérée")
            return
        
        # 2. Tester la validation Pydantic
        print("\n2. Test validation Pydantic...")
        from dash_apps.models.config_models import TripDataModel
        from dash_apps.utils.validation_utils import validate_data
        
        validation_result = validate_data(TripDataModel, real_data)
        if validation_result.success:
            print("✅ Validation réussie")
            validated_data = validation_result.data
            print(f"Données validées: {len(validated_data)} champs")
        else:
            print(f"❌ Validation échouée: {validation_result.get_error_summary()}")
            return
        
        # 3. Tester le formatter avec les vraies données
        print("\n3. Test formatter avec vraies données...")
        from dash_apps.utils.trip_details_formatter import TripDetailsFormatter
        
        formatter = TripDetailsFormatter()
        
        # Debug: vérifier les field_mappings
        print("Field mappings configurés:")
        field_mappings = formatter.display_config.get('field_mappings', {})
        for display_field, db_field in field_mappings.items():
            has_field = db_field in validated_data
            print(f"   - {display_field} <- {db_field}: {'✅' if has_field else '❌'}")
        
        formatted_data = formatter.format_for_display(validated_data)
        
        if formatted_data:
            print(f"✅ Formatage réussi: {len(formatted_data)} champs")
            print("Champs formatés:")
            for key, value in formatted_data.items():
                print(f"   - {key}: {value}")
        else:
            print("❌ Formatage échoué - dictionnaire vide")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_real_data()
