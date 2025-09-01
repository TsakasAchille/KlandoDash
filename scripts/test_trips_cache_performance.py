#!/usr/bin/env python3
"""
Script de test pour évaluer les performances du cache multi-niveaux des trajets
"""
import time
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, '/home/tsakas/Desktop/KlandoDash')

from dash_apps.services.trips_cache_service import TripsCacheService

def test_cache_performance():
    """Test de performance du cache des trajets"""
    print("=== TEST DE PERFORMANCE DU CACHE TRAJETS ===\n")
    
    # Paramètres de test
    page_index = 0
    page_size = 10
    filter_params = {}
    
    print("1. Premier appel (DB) - Cache vide")
    start_time = time.time()
    result1 = TripsCacheService.get_trips_page_result(page_index, page_size, filter_params)
    db_time = time.time() - start_time
    print(f"   Temps DB: {db_time:.3f}s")
    print(f"   Trajets récupérés: {len(result1.get('trips', []))}")
    print(f"   Total: {result1.get('total_count', 0)}")
    
    print("\n2. Deuxième appel (Cache local L1)")
    start_time = time.time()
    result2 = TripsCacheService.get_trips_page_result(page_index, page_size, filter_params)
    local_cache_time = time.time() - start_time
    print(f"   Temps Cache L1: {local_cache_time:.3f}s")
    print(f"   Amélioration: {((db_time - local_cache_time) / db_time * 100):.1f}%")
    
    # Vider le cache local pour tester Redis
    print("\n3. Test cache Redis (L2) - Vider cache local")
    TripsCacheService._local_cache.clear()
    TripsCacheService._cache_timestamps.clear()
    
    start_time = time.time()
    result3 = TripsCacheService.get_trips_page_result(page_index, page_size, filter_params)
    redis_time = time.time() - start_time
    print(f"   Temps Cache Redis: {redis_time:.3f}s")
    print(f"   Amélioration vs DB: {((db_time - redis_time) / db_time * 100):.1f}%")
    
    print("\n4. Test avec force_reload (bypass cache)")
    start_time = time.time()
    result4 = TripsCacheService.get_trips_page_result(page_index, page_size, filter_params, force_reload=True)
    reload_time = time.time() - start_time
    print(f"   Temps force_reload: {reload_time:.3f}s")
    
    print("\n5. Test pagination différente")
    start_time = time.time()
    result5 = TripsCacheService.get_trips_page_result(1, page_size, filter_params)  # Page 2
    page2_time = time.time() - start_time
    print(f"   Temps page 2 (DB): {page2_time:.3f}s")
    
    start_time = time.time()
    result6 = TripsCacheService.get_trips_page_result(1, page_size, filter_params)  # Page 2 cache
    page2_cache_time = time.time() - start_time
    print(f"   Temps page 2 (Cache): {page2_cache_time:.3f}s")
    
    print("\n=== RÉSUMÉ DES PERFORMANCES ===")
    print(f"Base de données:     {db_time:.3f}s")
    print(f"Cache local (L1):    {local_cache_time:.3f}s ({((db_time - local_cache_time) / db_time * 100):.1f}% plus rapide)")
    print(f"Cache Redis (L2):    {redis_time:.3f}s ({((db_time - redis_time) / db_time * 100):.1f}% plus rapide)")
    print(f"Force reload:        {reload_time:.3f}s")
    
    # Test de conversion des données
    print("\n=== TEST CONVERSION DONNÉES ===")
    trips, total_count, table_rows_data = TripsCacheService.extract_table_data(result1)
    print(f"Trips type: {type(trips)}")
    print(f"Table rows type: {type(table_rows_data)}")
    if table_rows_data:
        print(f"First row type: {type(table_rows_data[0])}")
        if isinstance(table_rows_data[0], dict):
            print(f"Keys: {list(table_rows_data[0].keys())[:5]}...")
            print("✓ Conversion en dictionnaires réussie")
        else:
            print("✗ Échec de conversion en dictionnaires")
    
    print("\n=== TEST TERMINÉ ===")

if __name__ == "__main__":
    test_cache_performance()
