#!/usr/bin/env python3
"""
Script pour vider le cache local des trajets (Redis removed)
"""
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def clear_trips_cache():
    """Vide le cache local des trajets"""
    try:
        print("[CACHE] Redis removed - clearing local cache only...")
        
        # Vider le cache local du TripsCacheService
        from dash_apps.services.trips_cache_service import TripsCacheService
        TripsCacheService._local_cache.clear()
        TripsCacheService._cache_timestamps.clear()
        print("[CACHE] Cache local vidé")
        
        # Vider aussi le cache centralisé
        from dash_apps.services.local_cache import cache
        cache.clear_all()
        print("[CACHE] Cache centralisé vidé")
        
        print("✅ Cache trajets complètement vidé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    clear_trips_cache()
