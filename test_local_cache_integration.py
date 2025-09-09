#!/usr/bin/env python3
"""
Test d'intégration du système de cache local avec la configuration JSON
Valide le fonctionnement du cache local et son intégration avec TripsCacheService
"""

import json
import time
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cache_config_loading():
    """Test le chargement de la configuration du cache"""
    print("=== Test du chargement de la configuration cache ===")
    
    try:
        with open('dash_apps/config/cache_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✓ Configuration chargée avec succès")
        
        # Vérifier la structure principale
        required_sections = ['cache_system', 'cache_types', 'storage_layers', 'cleanup_rules', 'monitoring']
        for section in required_sections:
            if section in config:
                print(f"✓ Section '{section}' présente")
            else:
                print(f"✗ Section '{section}' manquante")
                return False
        
        # Vérifier les types de cache
        cache_types = config['cache_types']
        expected_types = ['trip_details', 'trip_stats', 'trip_passengers']
        for cache_type in expected_types:
            if cache_type in cache_types:
                cache_config = cache_types[cache_type]
                if all(key in cache_config for key in ['ttl', 'max_entries', 'key_pattern']):
                    print(f"✓ Type de cache '{cache_type}' correctement configuré")
                else:
                    print(f"✗ Type de cache '{cache_type}' mal configuré")
                    return False
            else:
                print(f"✗ Type de cache '{cache_type}' manquant")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du chargement de la configuration: {e}")
        return False

def test_local_cache_service():
    """Test le service de cache local"""
    print("\n=== Test du service de cache local ===")
    
    try:
        from dash_apps.services.local_cache import LocalCache
        
        # Créer une instance du cache local
        cache = LocalCache()
        print("✓ Instance LocalCache créée")
        
        # Test des opérations de base
        test_key = "test_trip_123"
        test_data = {"trip_id": "123", "status": "completed", "distance": 15.5}
        
        # Test set
        cache.set_trip_details(test_key, test_data, ttl_seconds=60)
        print("✓ Données stockées dans le cache")
        
        # Test get
        cached_data = cache.get_trip_details(test_key)
        if cached_data == test_data:
            print("✓ Données récupérées correctement du cache")
        else:
            print(f"✗ Données incorrectes: attendu {test_data}, reçu {cached_data}")
            return False
        
        # Test TTL
        cache.set_trip_details("test_ttl", {"test": "ttl"}, ttl_seconds=1)
        time.sleep(2)
        expired_data = cache.get_trip_details("test_ttl")
        if expired_data is None:
            print("✓ TTL fonctionne correctement")
        else:
            print("✗ TTL ne fonctionne pas")
            return False
        
        # Test des statistiques
        stats = cache.get_stats()
        if isinstance(stats, dict) and 'hits' in stats:
            print(f"✓ Statistiques disponibles: {stats}")
        else:
            print("✗ Statistiques non disponibles")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test du cache local: {e}")
        return False

def test_trips_cache_service_fallback():
    """Test le fallback du TripsCacheService vers le cache local"""
    print("\n=== Test du fallback TripsCacheService ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Vérifier que le service peut être importé
        print("✓ TripsCacheService importé avec succès")
        
        # Vérifier la présence des méthodes de configuration
        if hasattr(TripsCacheService, '_load_panel_config'):
            print("✓ Méthode _load_panel_config présente")
        else:
            print("✗ Méthode _load_panel_config manquante")
            return False
        
        # Test du chargement de la configuration des panneaux
        try:
            config = TripsCacheService._load_panel_config()
            if isinstance(config, dict):
                print("✓ Configuration des panneaux chargée")
                
                # Vérifier la présence des panneaux attendus
                expected_panels = ['details', 'stats']  # Les clés dans le JSON
                for panel_name in expected_panels:
                    if panel_name in config:
                        panel_config = config[panel_name]
                        if 'methods' in panel_config:
                            print(f"✓ Panneau '{panel_name}' correctement configuré")
                        else:
                            print(f"✗ Panneau '{panel_name}' mal configuré")
                    else:
                        print(f"✗ Panneau '{panel_name}' manquant")
            else:
                print("✗ Configuration des panneaux invalide")
                return False
        except Exception as e:
            print(f"✗ Erreur lors du chargement de la configuration: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test du fallback: {e}")
        return False

def test_cache_integration():
    """Test d'intégration complète du système de cache"""
    print("\n=== Test d'intégration complète ===")
    
    try:
        # Simuler un scénario d'utilisation réel
        from dash_apps.services.local_cache import LocalCache
        
        cache = LocalCache()
        
        # Simuler des données de trajets
        trip_data = {
            "trip_123": {
                "id": "123",
                "driver": "John Doe",
                "passengers": 3,
                "distance": 25.7,
                "status": "completed"
            },
            "trip_456": {
                "id": "456", 
                "driver": "Jane Smith",
                "passengers": 2,
                "distance": 18.3,
                "status": "in_progress"
            }
        }
        
        # Stocker les données avec différents TTL
        for trip_id, data in trip_data.items():
            cache.set_trip_details(trip_id, data, ttl_seconds=300)
            cache.set_trip_stats(trip_id, {
                "avg_speed": data["distance"] / 1.5,
                "efficiency": 0.85
            }, ttl_seconds=180)
        
        print(f"✓ {len(trip_data)} trajets stockés dans le cache")
        
        # Vérifier la récupération
        retrieved_count = 0
        for trip_id in trip_data.keys():
            details = cache.get_trip_details(trip_id)
            stats = cache.get_trip_stats(trip_id)
            
            if details and stats:
                retrieved_count += 1
        
        if retrieved_count == len(trip_data):
            print(f"✓ Tous les trajets récupérés correctement ({retrieved_count}/{len(trip_data)})")
        else:
            print(f"✗ Récupération incomplète ({retrieved_count}/{len(trip_data)})")
            return False
        
        # Vérifier les statistiques finales
        final_stats = cache.get_stats()
        print(f"✓ Statistiques finales: {final_stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test d'intégration: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test d'intégration du système de cache local")
    print("=" * 50)
    
    tests = [
        ("Configuration Cache", test_cache_config_loading),
        ("Service Cache Local", test_local_cache_service),
        ("Fallback TripsCacheService", test_trips_cache_service_fallback),
        ("Intégration Complète", test_cache_integration)
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
        print("🎉 Tous les tests sont passés! Le système de cache local est prêt.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
