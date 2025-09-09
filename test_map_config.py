#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes de configuration de la carte MapLibre
"""

import os
import sys
import requests
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent))

from dash_apps.config import Config
from dotenv import load_dotenv

def test_environment_variables():
    """Test des variables d'environnement de la carte"""
    print("=== TEST DES VARIABLES D'ENVIRONNEMENT ===")
    
    # Charger le .env
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Fichier .env trouvé: {env_path}")
    else:
        print(f"❌ Fichier .env non trouvé: {env_path}")
    
    # Vérifier les variables MapLibre
    maplibre_style_url = os.environ.get('MAPLIBRE_STYLE_URL')
    maplibre_api_key = os.environ.get('MAPLIBRE_API_KEY')
    map_api_url = os.environ.get('MAP_API_URL')  # Ancienne variable
    
    print(f"MAPLIBRE_STYLE_URL: {maplibre_style_url}")
    print(f"MAPLIBRE_API_KEY: {'***' if maplibre_api_key else 'Non définie'}")
    print(f"MAP_API_URL (legacy): {map_api_url}")
    
    # Vérifier la configuration
    print(f"\nConfig.MAPLIBRE_STYLE_URL: {Config.MAPLIBRE_STYLE_URL}")
    print(f"Config.MAPLIBRE_API_KEY: {'***' if Config.MAPLIBRE_API_KEY else 'Non définie'}")
    
    return maplibre_style_url, maplibre_api_key

def test_style_url_access(style_url, api_key=None):
    """Test d'accès à l'URL du style de carte"""
    print("\n=== TEST D'ACCÈS AU STYLE DE CARTE ===")
    
    if not style_url:
        print("❌ Aucune URL de style définie")
        return False
    
    print(f"URL testée: {style_url}")
    
    try:
        # Construire l'URL avec la clé API si nécessaire
        test_url = style_url
        if api_key and 'api_key=' not in test_url:
            separator = '&' if '?' in test_url else '?'
            test_url = f"{test_url}{separator}api_key={api_key}"
        
        # Faire la requête
        response = requests.get(test_url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Non défini')}")
        
        if response.status_code == 200:
            print("✅ Style accessible")
            
            # Vérifier si c'est du JSON valide
            try:
                style_json = response.json()
                print(f"✅ JSON valide - Version: {style_json.get('version', 'Non définie')}")
                print(f"✅ Sources: {len(style_json.get('sources', {}))}")
                print(f"✅ Layers: {len(style_json.get('layers', []))}")
                return True
            except Exception as e:
                print(f"❌ JSON invalide: {e}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_tile_sources(style_url, api_key=None):
    """Test d'accès aux sources de tuiles"""
    print("\n=== TEST DES SOURCES DE TUILES ===")
    
    if not style_url:
        print("❌ Aucune URL de style pour tester les sources")
        return False
    
    try:
        # Récupérer le style
        test_url = style_url
        if api_key and 'api_key=' not in test_url:
            separator = '&' if '?' in test_url else '?'
            test_url = f"{test_url}{separator}api_key={api_key}"
        
        response = requests.get(test_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Impossible de récupérer le style: {response.status_code}")
            return False
        
        style_json = response.json()
        sources = style_json.get('sources', {})
        
        print(f"Sources trouvées: {len(sources)}")
        
        for source_name, source_config in sources.items():
            print(f"\n--- Source: {source_name} ---")
            source_type = source_config.get('type', 'unknown')
            print(f"Type: {source_type}")
            
            if source_type == 'vector':
                tiles = source_config.get('tiles', [])
                if tiles:
                    # Tester la première tuile
                    tile_template = tiles[0]
                    # Remplacer les placeholders par des valeurs de test
                    test_tile_url = tile_template.replace('{z}', '0').replace('{x}', '0').replace('{y}', '0')
                    
                    if api_key and 'api_key=' not in test_tile_url:
                        separator = '&' if '?' in test_tile_url else '?'
                        test_tile_url = f"{test_tile_url}{separator}api_key={api_key}"
                    
                    print(f"URL de test: {test_tile_url}")
                    
                    try:
                        tile_response = requests.get(test_tile_url, timeout=5)
                        if tile_response.status_code == 200:
                            print(f"✅ Tuile accessible (taille: {len(tile_response.content)} bytes)")
                        else:
                            print(f"❌ Tuile inaccessible: {tile_response.status_code}")
                    except Exception as e:
                        print(f"❌ Erreur tuile: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des sources: {e}")
        return False

def test_fallback_style():
    """Test du style de fallback"""
    print("\n=== TEST DU STYLE DE FALLBACK ===")
    
    fallback_url = "https://demotiles.maplibre.org/globe.json"
    print(f"URL de fallback: {fallback_url}")
    
    return test_style_url_access(fallback_url)

def test_proxy_configuration():
    """Test de la configuration du proxy"""
    print("\n=== TEST DE LA CONFIGURATION PROXY ===")
    
    try:
        from dash_apps.core.proxy import ALLOWED_HOSTS
        print(f"Hosts autorisés: {ALLOWED_HOSTS}")
        
        # Vérifier si les hosts de la carte sont autorisés
        style_url = Config.MAPLIBRE_STYLE_URL
        if style_url:
            from urllib.parse import urlparse
            parsed = urlparse(style_url)
            host = parsed.netloc
            
            if host in ALLOWED_HOSTS:
                print(f"✅ Host {host} autorisé dans le proxy")
            else:
                print(f"❌ Host {host} NON autorisé dans le proxy")
                print(f"Ajouter '{host}' à ALLOWED_HOSTS dans dash_apps/core/proxy.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur proxy: {e}")
        return False

def generate_test_report():
    """Génère un rapport de test complet"""
    print("🗺️  DIAGNOSTIC DE LA CARTE MAPLIBRE")
    print("=" * 50)
    
    # Test 1: Variables d'environnement
    style_url, api_key = test_environment_variables()
    
    # Test 2: Accès au style
    style_ok = test_style_url_access(style_url, api_key)
    
    # Test 3: Sources de tuiles
    if style_ok:
        test_tile_sources(style_url, api_key)
    
    # Test 4: Style de fallback
    fallback_ok = test_fallback_style()
    
    # Test 5: Configuration proxy
    test_proxy_configuration()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ")
    print("=" * 50)
    
    if not style_url:
        print("❌ PROBLÈME CRITIQUE: Aucune URL de style configurée")
        print("   → Définir MAPLIBRE_STYLE_URL dans le fichier .env")
    elif not style_ok:
        print("❌ PROBLÈME CRITIQUE: Style principal inaccessible")
        if fallback_ok:
            print("   → Le style de fallback fonctionne, vérifier la configuration")
        else:
            print("   → Même le fallback ne fonctionne pas, problème de réseau?")
    else:
        print("✅ Configuration de la carte OK")
    
    print("\n🔧 ACTIONS RECOMMANDÉES:")
    if not style_url:
        print("1. Créer/modifier le fichier .env avec MAPLIBRE_STYLE_URL")
    if not style_ok and style_url:
        print("1. Vérifier la validité de l'URL de style")
        print("2. Vérifier la clé API si nécessaire")
        print("3. Vérifier la connectivité réseau")
    
    print("4. Redémarrer l'application après les modifications")

if __name__ == "__main__":
    generate_test_report()
