#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes d'initialisation de la page Map
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_trip_repository():
    """Test de récupération des trajets"""
    print("🔍 Test du repository des trajets")
    print("=" * 40)
    
    try:
        from dash_apps.repositories.repository_factory import RepositoryFactory
        
        print("✅ Import RepositoryFactory réussi")
        
        trip_repository = RepositoryFactory.get_trip_repository()
        print("✅ Repository des trajets créé")
        
        trips = trip_repository.list_trips(limit=5)
        print(f"✅ Trajets récupérés: {len(trips)} trajets")
        
        if trips:
            first_trip = trips[0]
            print(f"Premier trajet: {getattr(first_trip, 'trip_id', 'N/A')}")
            print(f"Départ: {getattr(first_trip, 'departure_name', 'N/A')}")
            print(f"Arrivée: {getattr(first_trip, 'destination_name', 'N/A')}")
        else:
            print("⚠️  Aucun trajet trouvé dans la base de données")
            
        return trips
        
    except Exception as e:
        print(f"❌ Erreur lors du test du repository: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_map_initialization():
    """Test d'initialisation de la page Map"""
    print("\n🗺️  Test d'initialisation de la page Map")
    print("=" * 40)
    
    try:
        # Import direct de la page Map
        from dash_apps.pages.map import _get_last_trips, _initialize_trips_data
        
        print("✅ Import des fonctions Map réussi")
        
        # Test de récupération des trajets
        trips = _get_last_trips(5)
        print(f"✅ _get_last_trips: {len(trips)} trajets")
        
        # Test d'initialisation
        _initialize_trips_data()
        print("✅ _initialize_trips_data exécuté")
        
        return trips
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'initialisation Map: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_maplibre_files():
    """Test de présence des fichiers MapLibre"""
    print("\n🗺️  Test des fichiers MapLibre")
    print("=" * 40)
    
    files_to_check = [
        "dash_apps/core/assets/maplibre_init.js",
        "dash_apps/core/assets/maplibre_bridge.js",
        "dash_apps/core/assets/maplibre-gl.css"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} - MANQUANT")

def test_environment_config():
    """Test de la configuration d'environnement"""
    print("\n⚙️  Test de la configuration")
    print("=" * 40)
    
    try:
        from dash_apps.config import Config
        
        print(f"MAPLIBRE_STYLE_URL: {Config.MAPLIBRE_STYLE_URL}")
        print(f"MAPLIBRE_API_KEY: {'***' if Config.MAPLIBRE_API_KEY else 'NON DÉFINI'}")
        
        # Test d'accès à l'URL du style
        import requests
        if Config.MAPLIBRE_STYLE_URL:
            try:
                response = requests.get(Config.MAPLIBRE_STYLE_URL, timeout=5)
                print(f"✅ Style URL accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Style URL inaccessible: {e}")
        
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")

if __name__ == "__main__":
    print("🧪 DIAGNOSTIC DE LA PAGE MAP")
    print("=" * 50)
    
    # Test 1: Repository des trajets
    trips = test_trip_repository()
    
    # Test 2: Initialisation Map
    test_map_initialization()
    
    # Test 3: Fichiers MapLibre
    test_maplibre_files()
    
    # Test 4: Configuration
    test_environment_config()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC TERMINÉ")
