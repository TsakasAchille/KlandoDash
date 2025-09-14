#!/usr/bin/env python3
"""
Test de validation de la correction SQLQueryBuilder.execute_raw_query
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sql_query_builder_methods():
    """Test que SQLQueryBuilder a toutes les méthodes nécessaires"""
    print("=== Test SQLQueryBuilder ===")
    
    try:
        from dash_apps.services.sql_query_builder import SQLQueryBuilder
        
        # Vérifier que la méthode execute_raw_query existe
        if hasattr(SQLQueryBuilder, 'execute_raw_query'):
            print("✓ Méthode execute_raw_query présente")
        else:
            print("✗ Méthode execute_raw_query manquante")
            return False
        
        # Vérifier que la méthode est callable
        if callable(getattr(SQLQueryBuilder, 'execute_raw_query')):
            print("✓ Méthode execute_raw_query callable")
        else:
            print("✗ Méthode execute_raw_query non callable")
            return False
        
        # Vérifier les autres méthodes importantes
        required_methods = [
            'build_select_query',
            'execute_panel_query', 
            'get_panel_data_via_sql'
        ]
        
        for method_name in required_methods:
            if hasattr(SQLQueryBuilder, method_name):
                print(f"✓ Méthode {method_name} présente")
            else:
                print(f"✗ Méthode {method_name} manquante")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test SQLQueryBuilder: {e}")
        return False

def test_trips_cache_service_import():
    """Test que TripsCacheService peut s'importer sans erreur"""
    print("\n=== Test TripsCacheService Import ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        print("✓ TripsCacheService importé avec succès")
        
        # Vérifier que les méthodes génériques existent
        if hasattr(TripsCacheService, '_get_cached_panel_generic'):
            print("✓ Méthode _get_cached_panel_generic présente")
        else:
            print("✗ Méthode _get_cached_panel_generic manquante")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de l'import TripsCacheService: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test de validation des corrections SQLQueryBuilder")
    print("=" * 50)
    
    tests = [
        ("SQLQueryBuilder Methods", test_sql_query_builder_methods),
        ("TripsCacheService Import", test_trips_cache_service_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 50)
    print("RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ RÉUSSI" if result else "✗ ÉCHOUÉ"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Corrections SQLQueryBuilder validées!")
    else:
        print("⚠️  Certains tests ont échoué")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
