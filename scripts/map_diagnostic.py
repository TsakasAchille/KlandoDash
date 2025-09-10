#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes de chargement de la carte MapLibre
"""

import requests
import json
from dash_apps.config import Config

def test_maplibre_config():
    """Teste la configuration MapLibre"""
    print("=== Test Configuration MapLibre ===")
    
    style_url = Config.MAPLIBRE_STYLE_URL
    api_key = Config.MAPLIBRE_API_KEY
    
    print(f"Style URL: {style_url}")
    print(f"API Key présente: {'Oui' if api_key else 'Non'}")
    
    if not style_url:
        print("❌ ERREUR: Aucune style URL configurée")
        return False
    
    return True

def test_style_url_access():
    """Teste l'accès à l'URL du style"""
    print("\n=== Test Accès Style URL ===")
    
    style_url = Config.MAPLIBRE_STYLE_URL
    if not style_url:
        print("❌ Pas de style URL à tester")
        return False
    
    try:
        # Ajouter la clé API si présente
        test_url = style_url
        if Config.MAPLIBRE_API_KEY and 'api_key' not in style_url:
            separator = '&' if '?' in style_url else '?'
            test_url = f"{style_url}{separator}api_key={Config.MAPLIBRE_API_KEY}"
        
        print(f"Test URL: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                style_data = response.json()
                print("✅ Style JSON valide")
                print(f"Version: {style_data.get('version', 'N/A')}")
                print(f"Sources: {len(style_data.get('sources', {}))}")
                print(f"Layers: {len(style_data.get('layers', []))}")
                return True
            except json.JSONDecodeError:
                print("❌ Réponse n'est pas un JSON valide")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text[:200]}...")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_proxy_access():
    """Teste l'accès au proxy local"""
    print("\n=== Test Proxy Local ===")
    
    try:
        # Test du proxy avec une URL simple
        test_url = "http://127.0.0.1:8050/proxy/map?u=https://demotiles.maplibre.org/style.json"
        print(f"Test proxy: {test_url}")
        
        response = requests.get(test_url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Proxy fonctionne")
            return True
        else:
            print(f"❌ Proxy erreur: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Proxy inaccessible: {e}")
        return False

def test_maplibre_container():
    """Vérifie la création du container MapLibre"""
    print("\n=== Test Container MapLibre ===")
    
    from dash_apps.pages.map import create_maplibre_container
    
    try:
        container = create_maplibre_container()
        print("✅ Container créé avec succès")
        print(f"ID: {container.id}")
        print(f"Class: {container.className}")
        
        # Vérifier les attributs data
        if hasattr(container, 'children') and hasattr(container.children[0] if container.children else None, 'get'):
            attrs = container.children[0] if container.children else {}
        else:
            attrs = getattr(container, '_namespace', {})
        
        print(f"Attributs data: {list(attrs.keys()) if isinstance(attrs, dict) else 'N/A'}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création container: {e}")
        return False

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC MAPLIBRE - KLANDODASH")
    print("=" * 50)
    
    results = []
    
    # Tests
    results.append(("Configuration", test_maplibre_config()))
    results.append(("Style URL", test_style_url_access()))
    results.append(("Proxy", test_proxy_access()))
    results.append(("Container", test_maplibre_container()))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{test_name:15} : {status}")
    
    failed_tests = [name for name, success in results if not success]
    
    if failed_tests:
        print(f"\n⚠️  Tests échoués: {', '.join(failed_tests)}")
        print("\n🔧 ACTIONS RECOMMANDÉES:")
        
        if "Configuration" in failed_tests:
            print("- Vérifier les variables d'environnement MAPLIBRE_STYLE_URL et MAPLIBRE_API_KEY")
        
        if "Style URL" in failed_tests:
            print("- Vérifier la connectivité réseau vers geo.klando-carpool.com")
            print("- Vérifier la validité de la clé API")
        
        if "Proxy" in failed_tests:
            print("- Vérifier que l'application Dash est démarrée sur le port 8050")
            print("- Vérifier le module proxy.py")
        
        if "Container" in failed_tests:
            print("- Vérifier le module map.py et ses imports")
    else:
        print("\n🎉 Tous les tests sont passés !")
        print("Le problème pourrait être côté client (JavaScript/DOM)")

if __name__ == "__main__":
    main()
