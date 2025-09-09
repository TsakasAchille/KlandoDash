#!/usr/bin/env python3
"""
Script pour tester et corriger les problèmes de tuiles de la carte
"""

import os
import sys
import requests
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from dash_apps.config import Config

def test_different_tile_coordinates():
    """Test différentes coordonnées de tuiles pour trouver celles qui fonctionnent"""
    print("=== TEST DE DIFFÉRENTES COORDONNÉES DE TUILES ===")
    
    base_url = "https://geo.klando-carpool.com/data/klando-carpool-map-sn-v1.1"
    api_key = Config.MAPLIBRE_API_KEY
    
    # Coordonnées à tester (zoom, x, y)
    test_coords = [
        (0, 0, 0),    # Monde entier
        (1, 0, 0),    # Quadrant
        (1, 1, 0),    # Quadrant
        (2, 1, 1),    # Plus détaillé
        (4, 8, 8),    # Afrique de l'Ouest approximative
        (5, 16, 16),  # Plus précis
        (6, 32, 32),  # Sénégal approximatif
    ]
    
    working_coords = []
    
    for z, x, y in test_coords:
        url = f"{base_url}/{z}/{x}/{y}.pbf?api_key={api_key}"
        print(f"Test {z}/{x}/{y}: ", end="")
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ OK ({len(response.content)} bytes)")
                working_coords.append((z, x, y))
            else:
                print(f"❌ {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return working_coords

def test_alternative_tile_sources():
    """Test de sources de tuiles alternatives"""
    print("\n=== TEST DE SOURCES ALTERNATIVES ===")
    
    # Sources alternatives à tester
    alternatives = [
        {
            "name": "OpenStreetMap",
            "url": "https://tile.openstreetmap.org/0/0/0.png",
            "type": "raster"
        },
        {
            "name": "MapTiler Basic",
            "url": "https://api.maptiler.com/maps/basic/0/0/0.png",
            "type": "raster"
        },
        {
            "name": "Stamen Terrain",
            "url": "https://stamen-tiles.a.ssl.fastly.net/terrain/0/0/0.png",
            "type": "raster"
        }
    ]
    
    working_alternatives = []
    
    for alt in alternatives:
        print(f"Test {alt['name']}: ", end="")
        try:
            response = requests.get(alt['url'], timeout=5)
            if response.status_code == 200:
                print(f"✅ OK ({len(response.content)} bytes)")
                working_alternatives.append(alt)
            else:
                print(f"❌ {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    return working_alternatives

def create_fallback_style():
    """Crée un style de fallback avec des sources qui fonctionnent"""
    print("\n=== CRÉATION D'UN STYLE DE FALLBACK ===")
    
    fallback_style = {
        "version": 8,
        "name": "Klando Fallback",
        "sources": {
            "osm": {
                "type": "raster",
                "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "attribution": "© OpenStreetMap contributors"
            }
        },
        "layers": [
            {
                "id": "osm-tiles",
                "type": "raster",
                "source": "osm",
                "minzoom": 0,
                "maxzoom": 18
            }
        ]
    }
    
    # Sauvegarder le style de fallback
    fallback_path = Path(__file__).parent / "fallback_map_style.json"
    with open(fallback_path, 'w') as f:
        json.dump(fallback_style, f, indent=2)
    
    print(f"✅ Style de fallback créé: {fallback_path}")
    return fallback_path

def test_current_style_modification():
    """Test de modification du style actuel pour utiliser des sources alternatives"""
    print("\n=== TEST DE MODIFICATION DU STYLE ACTUEL ===")
    
    try:
        # Récupérer le style actuel
        style_url = Config.MAPLIBRE_STYLE_URL
        api_key = Config.MAPLIBRE_API_KEY
        
        if api_key and 'api_key=' not in style_url:
            separator = '&' if '?' in style_url else '?'
            test_url = f"{style_url}{separator}api_key={api_key}"
        else:
            test_url = style_url
        
        response = requests.get(test_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Impossible de récupérer le style: {response.status_code}")
            return None
        
        style_json = response.json()
        
        # Modifier les sources problématiques
        modified_style = style_json.copy()
        
        # Remplacer la source vectorielle par une source raster
        if "klando-carpool-map-sn-v1.1" in modified_style.get("sources", {}):
            modified_style["sources"]["klando-carpool-map-sn-v1.1"] = {
                "type": "raster",
                "tiles": ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                "tileSize": 256,
                "attribution": "© OpenStreetMap contributors"
            }
            
            # Modifier les couches qui utilisent cette source
            for layer in modified_style.get("layers", []):
                if layer.get("source") == "klando-carpool-map-sn-v1.1":
                    layer["type"] = "raster"
                    # Supprimer les propriétés spécifiques aux couches vectorielles
                    layer.pop("source-layer", None)
                    layer.pop("filter", None)
                    layer.pop("layout", None)
                    layer.pop("paint", None)
        
        # Sauvegarder le style modifié
        modified_path = Path(__file__).parent / "modified_map_style.json"
        with open(modified_path, 'w') as f:
            json.dump(modified_style, f, indent=2)
        
        print(f"✅ Style modifié créé: {modified_path}")
        return modified_path
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return None

def generate_fix_recommendations():
    """Génère des recommandations pour corriger le problème"""
    print("\n" + "=" * 60)
    print("🔧 RECOMMANDATIONS POUR CORRIGER LA CARTE")
    print("=" * 60)
    
    # Test des coordonnées
    working_coords = test_different_tile_coordinates()
    
    # Test des alternatives
    working_alternatives = test_alternative_tile_sources()
    
    # Créer un style de fallback
    fallback_path = create_fallback_style()
    
    # Modifier le style actuel
    modified_path = test_current_style_modification()
    
    print("\n📋 RÉSUMÉ DES SOLUTIONS:")
    
    if working_coords:
        print(f"✅ Tuiles fonctionnelles trouvées: {len(working_coords)} coordonnées")
        print("   → Le serveur de tuiles fonctionne partiellement")
    else:
        print("❌ Aucune tuile fonctionnelle trouvée")
        print("   → Problème avec le serveur de tuiles Klando")
    
    if working_alternatives:
        print(f"✅ Sources alternatives disponibles: {len(working_alternatives)}")
        for alt in working_alternatives:
            print(f"   - {alt['name']}")
    
    print("\n🎯 ACTIONS RECOMMANDÉES:")
    print("1. SOLUTION TEMPORAIRE:")
    print(f"   - Utiliser le style de fallback: {fallback_path}")
    print("   - Modifier MAPLIBRE_STYLE_URL pour pointer vers ce fichier local")
    
    print("\n2. SOLUTION PERMANENTE:")
    print("   - Contacter l'administrateur du serveur geo.klando-carpool.com")
    print("   - Vérifier la configuration des tuiles vectorielles")
    print("   - Ou migrer vers une source de tuiles alternative")
    
    print("\n3. SOLUTION HYBRIDE:")
    if modified_path:
        print(f"   - Utiliser le style modifié: {modified_path}")
        print("   - Garde la structure originale avec des sources alternatives")

if __name__ == "__main__":
    generate_fix_recommendations()
