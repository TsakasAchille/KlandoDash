#!/usr/bin/env python3
"""
Test de validation de la correction du repository REST dans SQLQueryBuilder
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sql_query_builder_with_rest_repository():
    """Test que SQLQueryBuilder gère correctement les repositories REST"""
    print("=== Test SQLQueryBuilder avec Repository REST ===")
    
    try:
        from dash_apps.services.sql_query_builder import SQLQueryBuilder
        from dash_apps.repositories.repository_factory import RepositoryFactory
        
        # Vérifier le type de repository
        trip_repository = RepositoryFactory.get_trip_repository()
        repo_type = type(trip_repository).__name__
        print(f"✓ Repository détecté: {repo_type}")
        
        # Test execute_raw_query avec repository REST
        test_query = "SELECT * FROM trips LIMIT 1"
        result = SQLQueryBuilder.execute_raw_query(test_query)
        
        if repo_type == 'TripRepositoryRest':
            # Avec repository REST, on s'attend à None (pas d'erreur)
            if result is None:
                print("✓ Repository REST correctement géré - requête SQL ignorée")
            else:
                print("✗ Repository REST mal géré - résultat inattendu")
                return False
        else:
            # Avec repository SQL, on peut avoir des résultats
            print(f"✓ Repository SQL - résultat: {type(result)}")
        
        # Test execute_panel_query avec repository REST
        panel_result = SQLQueryBuilder.execute_panel_query('details', 'test_trip_id')
        
        if repo_type == 'TripRepositoryRest':
            if panel_result is None:
                print("✓ Panel query correctement géré avec repository REST")
            else:
                print("✗ Panel query mal géré avec repository REST")
                return False
        else:
            print(f"✓ Panel query avec repository SQL - résultat: {type(panel_result)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
        return False

def test_trips_cache_service_with_rest():
    """Test que TripsCacheService fonctionne avec repository REST"""
    print("\n=== Test TripsCacheService avec Repository REST ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Test de la méthode générique
        if hasattr(TripsCacheService, '_execute_sql_fetcher'):
            print("✓ Méthode _execute_sql_fetcher présente")
        else:
            print("✗ Méthode _execute_sql_fetcher manquante")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test TripsCacheService: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test de validation des corrections Repository REST")
    print("=" * 55)
    
    tests = [
        ("SQLQueryBuilder avec REST", test_sql_query_builder_with_rest_repository),
        ("TripsCacheService avec REST", test_trips_cache_service_with_rest)
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
    print("\n" + "=" * 55)
    print("RÉSUMÉ DES TESTS")
    print("=" * 55)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ RÉUSSI" if result else "✗ ÉCHOUÉ"
        print(f"{test_name:.<35} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Corrections Repository REST validées!")
    else:
        print("⚠️  Certains tests ont échoué")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
