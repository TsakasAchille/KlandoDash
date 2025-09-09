#!/usr/bin/env python3
"""
Test du système sans Redis - validation que le cache local fonctionne complètement
Valide que toutes les fonctionnalités marchent sans dépendance Redis
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_no_redis_imports():
    """Test que le système peut s'importer sans Redis"""
    print("=== Test des imports sans Redis ===")
    
    try:
        # Test import du cache local
        from dash_apps.services.local_cache import LocalCache, local_cache
        print("✓ LocalCache importé avec succès")
        
        # Test import du service principal
        from dash_apps.services.trips_cache_service import TripsCacheService
        print("✓ TripsCacheService importé avec succès")
        
        # Vérifier qu'on utilise bien le cache local
        import dash_apps.services.trips_cache_service as tcs_module
        if hasattr(tcs_module, 'cache'):
            cache_type = type(tcs_module.cache).__name__
            if cache_type == 'LocalCache':
                print("✓ Cache local utilisé correctement")
            else:
                print(f"✗ Type de cache incorrect: {cache_type}")
                return False
        else:
            print("✗ Variable cache non trouvée")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur d'import: {e}")
        return False

def test_cache_operations_without_redis():
    """Test des opérations de cache sans Redis"""
    print("\n=== Test des opérations de cache ===")
    
    try:
        from dash_apps.services.local_cache import local_cache
        
        # Test des opérations de base
        test_data = {
            "trip_id": "test_123",
            "driver": "Test Driver",
            "status": "completed",
            "distance": 42.5
        }
        
        # Test set/get trip details
        success = local_cache.set_trip_details("test_123", test_data, ttl_seconds=60)
        if not success:
            print("✗ Erreur lors du stockage des détails")
            return False
        print("✓ Détails de trajet stockés")
        
        retrieved_data = local_cache.get_trip_details("test_123")
        if retrieved_data != test_data:
            print(f"✗ Données incorrectes: {retrieved_data}")
            return False
        print("✓ Détails de trajet récupérés")
        
        # Test set/get trip stats
        stats_data = {"avg_speed": 35.2, "efficiency": 0.87}
        local_cache.set_trip_stats("test_123", stats_data, ttl_seconds=60)
        retrieved_stats = local_cache.get_trip_stats("test_123")
        if retrieved_stats != stats_data:
            print(f"✗ Stats incorrectes: {retrieved_stats}")
            return False
        print("✓ Statistiques de trajet stockées et récupérées")
        
        # Test set/get trip passengers
        passengers_data = [
            {"name": "John Doe", "pickup": "Location A"},
            {"name": "Jane Smith", "pickup": "Location B"}
        ]
        local_cache.set_trip_passengers("test_123", passengers_data, ttl_seconds=60)
        retrieved_passengers = local_cache.get_trip_passengers("test_123")
        if retrieved_passengers != passengers_data:
            print(f"✗ Passagers incorrects: {retrieved_passengers}")
            return False
        print("✓ Passagers de trajet stockés et récupérés")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors des opérations de cache: {e}")
        return False

def test_trips_cache_service_methods():
    """Test des méthodes du TripsCacheService sans Redis"""
    print("\n=== Test du TripsCacheService ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Test du chargement de configuration
        config = TripsCacheService._load_panel_config()
        if not isinstance(config, dict):
            print("✗ Configuration des panneaux non chargée")
            return False
        print("✓ Configuration des panneaux chargée")
        
        # Test des méthodes génériques de cache
        if not hasattr(TripsCacheService, '_get_cache_data_generic'):
            print("✗ Méthode _get_cache_data_generic manquante")
            return False
        print("✓ Méthode _get_cache_data_generic présente")
        
        if not hasattr(TripsCacheService, '_set_cache_data_generic'):
            print("✗ Méthode _set_cache_data_generic manquante")
            return False
        print("✓ Méthode _set_cache_data_generic présente")
        
        # Test de la méthode générique principale
        if not hasattr(TripsCacheService, '_get_cached_panel_generic'):
            print("✗ Méthode _get_cached_panel_generic manquante")
            return False
        print("✓ Méthode _get_cached_panel_generic présente")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test du TripsCacheService: {e}")
        return False

def test_configuration_consistency():
    """Test de cohérence des configurations"""
    print("\n=== Test de cohérence des configurations ===")
    
    try:
        import json
        
        # Vérifier la configuration du cache
        with open('dash_apps/config/cache_config.json', 'r', encoding='utf-8') as f:
            cache_config = json.load(f)
        
        if cache_config.get('cache_system', {}).get('type') != 'local_memory':
            print("✗ Type de cache incorrect dans la configuration")
            return False
        print("✓ Configuration cache cohérente")
        
        # Vérifier la configuration des panneaux
        with open('dash_apps/config/panels_config.json', 'r', encoding='utf-8') as f:
            panels_config = json.load(f)
        
        # Vérifier que les panneaux ont des configurations de cache
        for panel_name, panel_config in panels_config.items():
            if 'methods' not in panel_config:
                print(f"✗ Panneau {panel_name} sans méthodes")
                return False
            
            methods = panel_config['methods']
            if 'cache' not in methods:
                print(f"✗ Panneau {panel_name} sans configuration cache")
                return False
        
        print("✓ Configuration des panneaux cohérente")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test de configuration: {e}")
        return False

def test_memory_usage_and_cleanup():
    """Test de l'utilisation mémoire et du nettoyage"""
    print("\n=== Test de gestion mémoire ===")
    
    try:
        from dash_apps.services.local_cache import local_cache
        import time
        
        # Obtenir les stats initiales
        initial_stats = local_cache.get_stats()
        initial_entries = initial_stats.get('total_entries', 0)
        
        # Ajouter plusieurs entrées avec TTL court
        for i in range(10):
            local_cache.set_trip_details(f"temp_trip_{i}", {"id": f"temp_{i}"}, ttl_seconds=1)
        
        # Vérifier que les entrées sont ajoutées
        after_add_stats = local_cache.get_stats()
        if after_add_stats.get('total_entries', 0) <= initial_entries:
            print("✗ Entrées non ajoutées au cache")
            return False
        print("✓ Entrées ajoutées au cache")
        
        # Attendre l'expiration
        time.sleep(2)
        
        # Forcer un nettoyage en essayant de récupérer une entrée expirée
        expired_data = local_cache.get_trip_details("temp_trip_0")
        if expired_data is not None:
            print("✗ Entrée expirée non nettoyée")
            return False
        print("✓ Nettoyage TTL fonctionne")
        
        # Vérifier les statistiques finales
        final_stats = local_cache.get_stats()
        print(f"✓ Statistiques finales: {final_stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test de gestion mémoire: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test du système sans Redis")
    print("=" * 40)
    
    tests = [
        ("Imports sans Redis", test_no_redis_imports),
        ("Opérations de cache", test_cache_operations_without_redis),
        ("Méthodes TripsCacheService", test_trips_cache_service_methods),
        ("Cohérence des configurations", test_configuration_consistency),
        ("Gestion mémoire", test_memory_usage_and_cleanup)
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
    print("\n" + "=" * 40)
    print("RÉSUMÉ DES TESTS")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ RÉUSSI" if result else "✗ ÉCHOUÉ"
        print(f"{test_name:.<25} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Système sans Redis opérationnel!")
        print("✅ Le cache local remplace complètement Redis")
    else:
        print("⚠️  Certains tests ont échoué")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
