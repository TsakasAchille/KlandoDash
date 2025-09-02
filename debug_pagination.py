#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier la pagination des trajets
"""
import os
import sys
sys.path.append('/home/tsakas/Desktop/KlandoDash')

from dash_apps.config import Config
import math

def test_pagination_calculation():
    print("=== TEST CALCUL PAGINATION ===")
    
    # Paramètres de test
    total_trips = 10
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    print(f"Total trajets: {total_trips}")
    print(f"Taille page: {page_size}")
    
    # Méthode 1 (trips_table_custom.py)
    page_count_1 = (total_trips - 1) // page_size + 1 if total_trips > 0 else 1
    print(f"Méthode 1: (total-1) // page_size + 1 = ({total_trips}-1) // {page_size} + 1 = {page_count_1}")
    
    # Méthode 2 (02_trips.py)
    page_count_2 = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    print(f"Méthode 2: math.ceil(total/page_size) = math.ceil({total_trips}/{page_size}) = {page_count_2}")
    
    print(f"\nRésultats:")
    print(f"- Méthode 1: {page_count_1} pages")
    print(f"- Méthode 2: {page_count_2} pages")
    print(f"- Cohérent: {'✅' if page_count_1 == page_count_2 else '❌'}")
    
    # Test avec différents totaux
    print(f"\n=== TESTS AVEC DIFFÉRENTS TOTAUX ===")
    for total in [1, 2, 4, 5, 6, 9, 10, 11, 15, 16]:
        method1 = (total - 1) // page_size + 1 if total > 0 else 1
        method2 = math.ceil(total / page_size) if total > 0 else 1
        status = "✅" if method1 == method2 else "❌"
        print(f"Total {total:2d}: Méthode1={method1}, Méthode2={method2} {status}")
        
        # Vérifier les trajets par page
        if method1 == method2:
            for page in range(1, method1 + 1):
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, total)
                trips_on_page = end_idx - start_idx
                print(f"  Page {page}: trajets {start_idx+1}-{end_idx} ({trips_on_page} trajets)")

def test_real_data():
    print("\n=== TEST DONNÉES RÉELLES ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Test avec les vraies données
        result = TripsCacheService.get_trips_page_result(0, 5, {}, False)
        trips = result.get("trips", [])
        total_count = result.get("total_count", 0)
        table_rows_data = result.get("table_rows_data", [])
        
        print(f"Page 1:")
        print(f"  - trips: {len(trips)} éléments")
        print(f"  - total_count: {total_count}")
        print(f"  - table_rows_data: {len(table_rows_data)} éléments")
        
        # Test page 2
        result2 = TripsCacheService.get_trips_page_result(1, 5, {}, False)
        trips2 = result2.get("trips", [])
        total_count2 = result2.get("total_count", 0)
        table_rows_data2 = result2.get("table_rows_data", [])
        
        print(f"Page 2:")
        print(f"  - trips: {len(trips2)} éléments")
        print(f"  - total_count: {total_count2}")
        print(f"  - table_rows_data: {len(table_rows_data2)} éléments")
        
        # Test page 3
        result3 = TripsCacheService.get_trips_page_result(2, 5, {}, False)
        trips3 = result3.get("trips", [])
        total_count3 = result3.get("total_count", 0)
        table_rows_data3 = result3.get("table_rows_data", [])
        
        print(f"Page 3:")
        print(f"  - trips: {len(trips3)} éléments")
        print(f"  - total_count: {total_count3}")
        print(f"  - table_rows_data: {len(table_rows_data3)} éléments")
        
        # Calcul attendu vs réel
        expected_pages = math.ceil(total_count / 5) if total_count > 0 else 1
        print(f"\nAnalyse:")
        print(f"  - Total trajets: {total_count}")
        print(f"  - Pages attendues: {expected_pages}")
        print(f"  - Page 3 devrait être vide: {'✅' if expected_pages <= 2 else '❌'}")
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pagination_calculation()
    test_real_data()
