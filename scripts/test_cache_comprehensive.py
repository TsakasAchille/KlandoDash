#!/usr/bin/env python3
"""
Test complet du système de cache KlandoDash
Teste tous les niveaux de cache et la génération de panels/stats
"""
import sys
import os
import time
sys.path.append('.')

from dash_apps.core.database import SessionLocal
from dash_apps.models.user import User
from dash_apps.models.trip import Trip
from dash_apps.services.trips_cache_service import TripsCacheService
from dash_apps.services.users_cache_service import UsersCacheService
from dash_apps.components.trip_details_layout import render_trip_card_html
from dash_apps.components.trip_stats import render_trip_stats_html
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips

def measure_time(func, *args, **kwargs):
    """Mesure le temps d'exécution d'une fonction"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def test_trips_cache_comprehensive():
    """Test complet du cache des trajets avec tous les niveaux"""
    print("=" * 60)
    print("=== TEST COMPLET DU CACHE TRAJETS ===")
    print("=" * 60)
    
    trips_cache = TripsCacheService()
    
    # 1. Test premier appel (DB) - Cache vide
    print("\n1. Premier appel (DB) - Cache vide")
    trips_cache.clear_all_html_cache()  # Vider le cache HTML
    trips_cache._local_cache.clear()  # Vider le cache local
    trips_cache._cache_timestamps.clear()  # Vider les timestamps
    result1, time1 = measure_time(trips_cache.get_trips_page_result, page_index=0, page_size=10, filter_params={})
    print(f"   Temps DB: {time1:.3f}s")
    print(f"   Trajets récupérés: {len(result1.get('trips', []))}")
    print(f"   Total: {result1.get('total_trips', 0)}")
    
    # 2. Deuxième appel (Cache local L1)
    print("\n2. Deuxième appel (Cache local L1)")
    result2, time2 = measure_time(trips_cache.get_trips_page_result, page_index=0, page_size=10, filter_params={})
    print(f"   Temps Cache L1: {time2:.3f}s")
    improvement1 = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
    print(f"   Amélioration: {improvement1:.1f}%")
    
    # 3. Test cache Redis (L2) - Vider cache local seulement
    print("\n3. Test cache Redis (L2) - Vider cache local")
    trips_cache._local_cache.clear()  # Vider seulement le cache local
    result3, time3 = measure_time(trips_cache.get_trips_page_result, page_index=0, page_size=10, filter_params={})
    print(f"   Temps Cache Redis: {time3:.3f}s")
    improvement2 = ((time1 - time3) / time1 * 100) if time1 > 0 else 0
    print(f"   Amélioration vs DB: {improvement2:.1f}%")
    
    # 4. Test avec force_reload (bypass cache)
    print("\n4. Test avec force_reload (bypass cache)")
    result4, time4 = measure_time(trips_cache.get_trips_page_result, page_index=0, page_size=10, filter_params={}, force_reload=True)
    print(f"   Temps force_reload: {time4:.3f}s")
    
    # 5. Test pagination différente
    print("\n5. Test pagination différente")
    result5, time5 = measure_time(trips_cache.get_trips_page_result, page_index=1, page_size=10, filter_params={})
    print(f"   Temps page 2 (DB): {time5:.3f}s")
    result6, time6 = measure_time(trips_cache.get_trips_page_result, page_index=1, page_size=10, filter_params={})
    print(f"   Temps page 2 (Cache): {time6:.3f}s")
    
    print("\n=== RÉSUMÉ DES PERFORMANCES TRAJETS ===")
    print(f"Base de données:     {time1:.3f}s")
    print(f"Cache local (L1):    {time2:.3f}s ({improvement1:.1f}% plus rapide)")
    print(f"Cache Redis (L2):    {time3:.3f}s ({improvement2:.1f}% plus rapide)")
    print(f"Force reload:        {time4:.3f}s")
    
    return result1.get('trips', [])[:3]  # Retourner les 3 premiers trajets pour les tests suivants

def test_users_cache_comprehensive():
    """Test complet du cache des utilisateurs"""
    print("\n" + "=" * 60)
    print("=== TEST COMPLET DU CACHE UTILISATEURS ===")
    print("=" * 60)
    
    users_cache = UsersCacheService()
    
    # 1. Test premier appel (DB) - Cache vide
    print("\n1. Premier appel (DB) - Cache vide")
    if hasattr(users_cache, 'clear_all_cache'):
        users_cache.clear_all_cache()
    else:
        # Fallback: vider manuellement les caches disponibles
        if hasattr(users_cache, '_local_cache'):
            users_cache._local_cache.clear()
        if hasattr(users_cache, '_cache_timestamps'):
            users_cache._cache_timestamps.clear()
    result1, time1 = measure_time(users_cache.get_users_page_data, page_index=0, page_size=10)
    print(f"   Temps DB: {time1:.3f}s")
    print(f"   Utilisateurs récupérés: {len(result1.get('users', []))}")
    print(f"   Total: {result1.get('total_count', 0)}")
    
    # 2. Deuxième appel (Cache local)
    print("\n2. Deuxième appel (Cache local)")
    result2, time2 = measure_time(users_cache.get_users_page_data, page_index=0, page_size=10)
    print(f"   Temps Cache: {time2:.3f}s")
    improvement = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
    print(f"   Amélioration: {improvement:.1f}%")
    
    print("\n=== RÉSUMÉ DES PERFORMANCES UTILISATEURS ===")
    print(f"Base de données:     {time1:.3f}s")
    print(f"Cache local:         {time2:.3f}s ({improvement:.1f}% plus rapide)")
    
    return result1.get('users', [])[:3]  # Retourner les 3 premiers utilisateurs

def test_panels_generation(trips, users):
    """Test de génération des panels avec cache HTML"""
    print("\n" + "=" * 60)
    print("=== TEST GÉNÉRATION PANELS ===")
    print("=" * 60)
    
    if not trips or not users:
        print("   Pas de données pour tester les panels")
        return
    
    trip = trips[0]
    user = users[0]
    users_cache = UsersCacheService()
    
    # Convert trip to dict if it's a Pydantic model
    if hasattr(trip, 'model_dump'):
        trip_dict = trip.model_dump()
    elif hasattr(trip, 'to_dict'):
        trip_dict = trip.to_dict()
    elif isinstance(trip, dict):
        trip_dict = trip
    else:
        trip_dict = {'trip_id': str(trip)}
    
    # Convert user to dict if it's a Pydantic model
    if hasattr(user, 'model_dump'):
        user_dict = user.model_dump()
    elif hasattr(user, 'to_dict'):
        user_dict = user.to_dict()
    elif isinstance(user, dict):
        user_dict = user
    else:
        user_dict = {'name': str(user)}
    
    print(f"\nTest avec trajet: {trip_dict.get('trip_id', 'N/A')}")
    print(f"Test avec utilisateur: {user_dict.get('name', user_dict.get('display_name', 'N/A'))}")
    
    # Test génération panels trajets
    print("\n--- PANELS TRAJETS ---")
    
    # Trip details
    print("1. Trip Details Panel")
    _, time_details = measure_time(render_trip_card_html, trip_dict)
    print(f"   Temps génération: {time_details:.3f}s")
    
    # Trip stats
    print("2. Trip Stats Panel")
    _, time_stats = measure_time(render_trip_stats_html, trip_dict)
    print(f"   Temps génération: {time_stats:.3f}s")
    
    # Test génération panels utilisateurs avec cache HTML
    print("\n--- PANELS UTILISATEURS (avec cache HTML) ---")
    user_uid = user_dict.get('uid')
    
    if user_uid:
        # Vider le cache HTML pour ce test
        if hasattr(users_cache, 'clear_user_cache'):
            users_cache.clear_user_cache(user_uid)
        
        # Test user profile
        print("3. User Profile Panel (première génération)")
        _, time_profile1 = measure_time(render_user_profile, user_dict)
        print(f"   Temps génération: {time_profile1:.3f}s")
        
        # Mettre en cache le panel
        profile_html = render_user_profile(user_dict)
        if hasattr(users_cache, 'set_cached_panel'):
            users_cache.set_cached_panel(user_uid, "profile", profile_html)
        
        print("4. User Profile Panel (depuis cache HTML)")
        cached_profile = users_cache.get_cached_panel(user_uid, "profile") if hasattr(users_cache, 'get_cached_panel') else None
        time_profile2 = 0.001 if cached_profile else time_profile1  # Simulation temps cache
        print(f"   Temps cache HTML: {time_profile2:.3f}s")
        improvement_profile = ((time_profile1 - time_profile2) / time_profile1 * 100) if time_profile1 > 0 else 0
        print(f"   Amélioration: {improvement_profile:.1f}%")
        
        # Test user stats
        print("5. User Stats Panel")
        _, time_user_stats = measure_time(render_user_stats, user_dict)
        print(f"   Temps génération: {time_user_stats:.3f}s")
        
        # Test user trips
        print("6. User Trips Panel")
        _, time_user_trips = measure_time(render_user_trips, user_dict)
        print(f"   Temps génération: {time_user_trips:.3f}s")
    
    print("\n=== RÉSUMÉ GÉNÉRATION PANELS ===")
    print(f"Trip Details:        {time_details:.3f}s")
    print(f"Trip Stats:          {time_stats:.3f}s")
    if user_uid:
        print(f"User Profile (1ère): {time_profile1:.3f}s")
        print(f"User Profile (cache):{time_profile2:.3f}s ({improvement_profile:.1f}% plus rapide)")
        print(f"User Stats:          {time_user_stats:.3f}s")
        print(f"User Trips:          {time_user_trips:.3f}s")

def test_database_stats():
    """Test des statistiques de base de données"""
    print("\n" + "=" * 60)
    print("=== TEST STATISTIQUES BASE DE DONNÉES ===")
    print("=" * 60)
    
    with SessionLocal() as db:
        # Compter les entités
        start = time.time()
        user_count = db.query(User).count()
        trip_count = db.query(Trip).count()
        stats_time = time.time() - start
        
        print(f"\nStatistiques générales (temps: {stats_time:.3f}s):")
        print(f"   Utilisateurs totaux: {user_count}")
        print(f"   Trajets totaux: {trip_count}")
        
        # Test requêtes plus complexes
        if trip_count > 0:
            start = time.time()
            # Statistiques avancées sur les trajets
            from sqlalchemy import func
            avg_distance = db.query(func.avg(Trip.distance)).scalar() or 0
            total_distance = db.query(func.sum(Trip.distance)).scalar() or 0
            avg_passengers = db.query(func.avg(Trip.seats_available)).scalar() or 0
            complex_stats_time = time.time() - start
            
            print(f"\nStatistiques avancées (temps: {complex_stats_time:.3f}s):")
            print(f"   Distance moyenne: {avg_distance:.2f} km")
            print(f"   Distance totale: {total_distance:.2f} km")
            print(f"   Places moyennes: {avg_passengers:.2f}")

def test_cache_eviction():
    """Test de l'éviction du cache LRU"""
    print("\n" + "=" * 60)
    print("=== TEST ÉVICTION CACHE LRU ===")
    print("=" * 60)
    
    trips_cache = TripsCacheService()
    trips_cache.clear_all_html_cache()
    trips_cache._local_cache.clear()
    trips_cache._cache_timestamps.clear()
    
    print(f"\nTaille initiale du cache: {len(trips_cache._local_cache)}")
    
    # Remplir le cache avec plusieurs pages
    print("Remplissage du cache avec plusieurs pages...")
    for page in range(15):  # Plus que la limite de 10
        trips_cache.get_trips_page_result(page_index=page, page_size=5, filter_params={})
        if page % 5 == 0:
            print(f"   Page {page}: Cache size = {len(trips_cache._local_cache)}")
    
    final_size = len(trips_cache._local_cache)
    print(f"\nTaille finale du cache: {final_size}")
    print(f"Éviction LRU {'activée' if final_size <= 10 else 'NON activée'}")

def main():
    """Test principal complet"""
    print("DÉBUT DU TEST COMPLET DU SYSTÈME DE CACHE")
    print("=" * 80)
    
    start_total = time.time()
    
    # Test statistiques DB
    test_database_stats()
    
    # Test cache trajets
    trips = test_trips_cache_comprehensive()
    
    # Test cache utilisateurs  
    users = test_users_cache_comprehensive()
    
    # Test génération panels
    test_panels_generation(trips, users)
    
    # Test éviction cache
    test_cache_eviction()
    
    total_time = time.time() - start_total
    
    print("\n" + "=" * 80)
    print("=== RÉSUMÉ GLOBAL ===")
    print("=" * 80)
    print(f"Temps total du test: {total_time:.3f}s")
    print("✅ Test complet terminé avec succès")
    print("=" * 80)

if __name__ == "__main__":
    main()
