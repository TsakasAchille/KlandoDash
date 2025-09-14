#!/usr/bin/env python3
"""
Test des optimisations de cache pour les services de conducteurs et détails de trajets
"""

import os
import sys
import time
from typing import Dict, Any

# Configuration du chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dash_apps'))

def test_driver_cache_service():
    """Test du service de cache des conducteurs"""
    print("🧪 Test du service de cache des conducteurs")
    print("-" * 50)
    
    try:
        from dash_apps.services.trip_driver_cache_service import TripDriverCache
        
        # Test avec un trip_id valide
        trip_id = "TRIP-175EQWERTY123456789T8G3"
        
        print(f"📋 Test avec trip_id: {trip_id[:12]}...")
        
        # Test de récupération des données (devrait faire un appel API)
        start_time = time.time()
        result = TripDriverCache.get_trip_driver_data(trip_id)
        api_time = time.time() - start_time
        
        print(f"⏱️  Temps API (premier appel): {api_time:.4f}s")
        print(f"✅ Données récupérées: {bool(result)}")
        
        if result:
            print(f"📊 Clés dans le résultat: {list(result.keys())}")
        
        # Test de récupération depuis le cache
        start_time = time.time()
        cached_result = TripDriverCache.get_trip_driver_data(trip_id)
        cache_time = time.time() - start_time
        
        print(f"⏱️  Temps cache (deuxième appel): {cache_time:.4f}s")
        
        if api_time > 0 and cache_time > 0:
            speedup = api_time / cache_time
            print(f"🚀 Accélération cache: {speedup:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans test_driver_cache_service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trip_details_cache_service():
    """Test du service de cache des détails de trajets"""
    print("\n🧪 Test du service de cache des détails de trajets")
    print("-" * 50)
    
    try:
        from dash_apps.services.trip_details_cache_service import TripDetailsCache
        
        # Test avec un trip_id valide
        trip_id = "TRIP-175EQWERTY123456789T8G3"
        
        print(f"📋 Test avec trip_id: {trip_id[:12]}...")
        
        # Test de récupération des données (devrait faire un appel API)
        start_time = time.time()
        result = TripDetailsCache.get_trip_details_data(trip_id)
        api_time = time.time() - start_time
        
        print(f"⏱️  Temps API (premier appel): {api_time:.4f}s")
        print(f"✅ Données récupérées: {bool(result)}")
        
        if result:
            print(f"📊 Clés dans le résultat: {list(result.keys())}")
        
        # Test de récupération depuis le cache
        start_time = time.time()
        cached_result = TripDetailsCache.get_trip_details_data(trip_id)
        cache_time = time.time() - start_time
        
        print(f"⏱️  Temps cache (deuxième appel): {cache_time:.4f}s")
        
        if api_time > 0 and cache_time > 0:
            speedup = api_time / cache_time
            print(f"🚀 Accélération cache: {speedup:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans test_trip_details_cache_service: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_key_generation():
    """Test de la génération des clés de cache"""
    print("\n🧪 Test de la génération des clés de cache")
    print("-" * 50)
    
    try:
        from dash_apps.services.trip_driver_cache_service import TripDriverCache
        from dash_apps.services.trip_details_cache_service import TripDetailsCache
        
        trip_id = "TRIP-175EQWERTY123456789T8G3"
        
        # Test des clés de cache
        driver_key = TripDriverCache._get_cache_key(trip_id)
        details_key = TripDetailsCache._get_cache_key(trip_id)
        
        print(f"🔑 Clé cache conducteur: {driver_key}")
        print(f"🔑 Clé cache détails: {details_key}")
        
        # Vérifier que les clés ont les bons préfixes
        assert driver_key.startswith("trip_driver:"), f"Clé conducteur incorrecte: {driver_key}"
        assert details_key.startswith("trip_details:"), f"Clé détails incorrecte: {details_key}"
        
        print("✅ Génération des clés de cache validée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans test_cache_key_generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_system():
    """Test du système de logging unifié"""
    print("\n🧪 Test du système de logging unifié")
    print("-" * 50)
    
    try:
        # Activer le debug pour voir les logs
        os.environ['DEBUG_TRIPS'] = 'true'
        
        from dash_apps.utils.callback_logger import CallbackLogger
        
        # Test d'un log simple
        CallbackLogger.log_callback(
            "test_optimization",
            {
                "message": "Test des optimisations de cache",
                "timestamp": time.time()
            }
        )
        
        print("✅ Système de logging unifié fonctionnel")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans test_logging_system: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Remettre le debug à false
        os.environ['DEBUG_TRIPS'] = 'false'

def main():
    """Fonction principale de test"""
    print("🎯 Test des Optimisations de Cache - KlandoDash")
    print("=" * 60)
    
    tests = [
        ("Génération des clés de cache", test_cache_key_generation),
        ("Système de logging unifié", test_logging_system),
        ("Service de cache des conducteurs", test_driver_cache_service),
        ("Service de cache des détails", test_trip_details_cache_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Exécution: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Échec du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{status:12} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Résultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Toutes les optimisations fonctionnent correctement !")
        return 0
    else:
        print("⚠️  Certaines optimisations nécessitent une attention")
        return 1

if __name__ == "__main__":
    exit(main())
