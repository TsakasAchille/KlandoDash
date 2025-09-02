#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier la pagination des users ET trips
"""
import sys
import os
import math

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_users_pagination():
    """Test de la pagination des utilisateurs"""
    print("=== TEST PAGINATION USERS ===")
    
    try:
        from dash_apps.services.users_cache_service import UsersCacheService
        
        page_size = 5
        
        # Tester les 3 premières pages
        for page_index in range(3):
            print(f"\nPage {page_index + 1}:")
            result = UsersCacheService.get_users_page_result(page_index, page_size, {})
            
            users = result.get("users", [])
            total_count = result.get("total_count", 0)
            
            print(f"  - users: {len(users)} éléments")
            print(f"  - total_count: {total_count}")
            
            if page_index == 0:
                expected_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
                print(f"  - Pages attendues: {expected_pages}")
        
    except Exception as e:
        print(f"❌ Erreur users: {e}")

def test_trips_pagination():
    """Test de la pagination des trajets"""
    print("\n=== TEST PAGINATION TRIPS ===")
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        page_size = 5
        
        # Tester les 3 premières pages
        for page_index in range(3):
            print(f"\nPage {page_index + 1}:")
            result = TripsCacheService.get_trips_page_result(page_index, page_size, {})
            
            trips = result.get("trips", [])
            total_count = result.get("total_count", 0)
            
            print(f"  - trips: {len(trips)} éléments")
            print(f"  - total_count: {total_count}")
            
            if page_index == 0:
                expected_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
                print(f"  - Pages attendues: {expected_pages}")
        
    except Exception as e:
        print(f"❌ Erreur trips: {e}")

def test_direct_repositories():
    """Test direct des repositories pour comparer"""
    print("\n=== TEST DIRECT REPOSITORIES ===")
    
    try:
        from dash_apps.repositories.user_repository import UserRepository
        from dash_apps.repositories.trip_repository import TripRepository
        
        print("\n--- UserRepository ---")
        user_result = UserRepository.get_users_paginated(0, 5, {})
        print(f"Users page 1: {len(user_result.get('users', []))} users, total={user_result.get('total_count', 0)}")
        
        print("\n--- TripRepository ---")
        trip_result = TripRepository.get_trips_paginated_minimal(0, 5, {})
        print(f"Trips page 1: {len(trip_result.get('trips', []))} trips, total={trip_result.get('total_count', 0)}")
        
    except Exception as e:
        print(f"❌ Erreur repositories: {e}")

if __name__ == "__main__":
    test_users_pagination()
    test_trips_pagination()
    test_direct_repositories()
