#!/usr/bin/env python3
"""
Script pour vider le cache Redis des trajets et forcer le rechargement
"""
import redis
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def clear_trips_cache():
    """Vide toutes les clés de cache liées aux trajets"""
    try:
        # Connexion Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Tester la connexion
        r.ping()
        print("[REDIS] Connexion établie: localhost:6379")
        
        # Trouver toutes les clés de cache trajets
        trips_keys = r.keys("trips_page:*")
        print(f"[REDIS] Trouvé {len(trips_keys)} clés de cache trajets")
        
        if trips_keys:
            # Supprimer toutes les clés
            deleted_count = r.delete(*trips_keys)
            print(f"[REDIS] {deleted_count} clés supprimées")
        else:
            print("[REDIS] Aucune clé de cache trajets trouvée")
        
        # Vider aussi le cache local du TripsCacheService
        print("[CACHE] Vidage du cache local...")
        from dash_apps.services.trips_cache_service import TripsCacheService
        TripsCacheService._local_cache.clear()
        TripsCacheService._cache_timestamps.clear()
        print("[CACHE] Cache local vidé")
        
        print("✅ Cache trajets complètement vidé!")
        
    except redis.ConnectionError:
        print("❌ Impossible de se connecter à Redis")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    clear_trips_cache()
