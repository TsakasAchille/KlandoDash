#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion à l'API Klando MapLibre
Teste la clé API KLANDO_API_KEY définie dans .env
"""

import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

def test_klando_api():
    """Test de connexion à l'API Klando MapLibre"""
    
    # Récupérer l'URL avec clé API intégrée depuis .env
    api_url = os.environ.get('KLANDO_MAP_API_URL')
    api_key = os.environ.get('KLANDO_API_KEY')
    
    if api_url:
        print(f"🔗 URL avec clé API trouvée: {api_url[:50]}...{api_url[-20:]}")
        # Extraire l'URL de base pour les tests
        if '?' in api_url:
            base_url = api_url.split('?')[0]
            api_params = api_url.split('?')[1]
        else:
            base_url = api_url
            api_params = ""
        style_url = api_url  # URL complète avec clé
        tile_url = f"https://geo.klando-carpool.com/data/klando-carpool-map-sn-v1.1/0/0/0.pbf?{api_params}" if api_params else "https://geo.klando-carpool.com/data/klando-carpool-map-sn-v1.1/0/0/0.pbf"
    elif api_key:
        print(f"🔑 Clé API trouvée: {api_key[:8]}...{api_key[-8:]}")
        # URLs de test avec clé séparée
        style_url = f"https://geo.klando-carpool.com/styles/carpool/style.json?api_key={api_key}"
        tile_url = f"https://geo.klando-carpool.com/data/klando-carpool-map-sn-v1.1/0/0/0.pbf?api_key={api_key}"
    else:
        print("❌ ERREUR: Ni KLANDO_MAP_API_URL ni KLANDO_API_KEY trouvées dans .env")
        return False
    
    print("\n📋 Tests de connexion:")
    print("=" * 50)
    
    # Test 1: Style JSON
    print(f"\n1️⃣ Test du style JSON:")
    print(f"   URL: {style_url}")
    
    try:
        response = requests.get(style_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                style_data = response.json()
                print(f"   ✅ Style JSON valide")
                print(f"   Version: {style_data.get('version', 'Non spécifiée')}")
                print(f"   Nom: {style_data.get('name', 'Non spécifié')}")
                if 'sources' in style_data:
                    print(f"   Sources: {len(style_data['sources'])} trouvées")
                if 'layers' in style_data:
                    print(f"   Layers: {len(style_data['layers'])} trouvés")
            except json.JSONDecodeError:
                print(f"   ⚠️ Réponse reçue mais JSON invalide")
        elif response.status_code == 401:
            print(f"   ❌ Erreur d'autorisation - Clé API invalide")
            return False
        elif response.status_code == 403:
            print(f"   ❌ Accès interdit - Vérifiez les permissions")
            return False
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            print(f"   Réponse: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout - Serveur trop lent")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Erreur de connexion - Serveur inaccessible")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False
    
    # Test 2: Tuile de test
    print(f"\n2️⃣ Test d'une tuile:")
    print(f"   URL: {tile_url}")
    
    try:
        response = requests.get(tile_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Tuile accessible")
            print(f"   Taille: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type', 'Non spécifié')}")
        elif response.status_code == 401:
            print(f"   ❌ Erreur d'autorisation - Clé API invalide")
            return False
        elif response.status_code == 404:
            print(f"   ⚠️ Tuile non trouvée (normal pour niveau 0)")
        else:
            print(f"   ❌ Erreur HTTP: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout - Serveur trop lent")
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Erreur de connexion - Serveur inaccessible")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test 3: Vérification de la configuration
    print(f"\n3️⃣ Vérification de la configuration:")
    
    maplibre_style_url = os.environ.get('MAPLIBRE_STYLE_URL')
    maplibre_api_key = os.environ.get('MAPLIBRE_API_KEY')
    klando_map_url = os.environ.get('KLANDO_MAP_API_URL')
    
    print(f"   MAPLIBRE_STYLE_URL: {maplibre_style_url}")
    print(f"   MAPLIBRE_API_KEY: {'✅ Définie' if maplibre_api_key else '❌ Non définie'}")
    print(f"   KLANDO_MAP_API_URL: {'✅ Définie' if klando_map_url else '❌ Non définie'}")
    
    if klando_map_url and maplibre_style_url != klando_map_url:
        print(f"   ⚠️ MAPLIBRE_STYLE_URL différente de KLANDO_MAP_API_URL")
        print(f"   Recommandation: Utiliser KLANDO_MAP_API_URL pour MapLibre")
    
    print(f"\n📊 Résumé:")
    print("=" * 50)
    
    if response.status_code in [200, 404]:  # 404 acceptable pour les tuiles
        print("✅ Connexion API réussie")
        print("✅ Clé API valide")
        print("✅ Serveur accessible")
        
        # Suggestions de configuration
        print(f"\n💡 Configuration recommandée pour .env:")
        if api_url:
            print(f"MAPLIBRE_STYLE_URL={api_url}")
            print(f"# Clé API déjà intégrée dans l'URL")
        else:
            print(f"MAPLIBRE_API_KEY={api_key}")
            print(f"MAPLIBRE_STYLE_URL=https://geo.klando-carpool.com/styles/carpool/style.json")
        
        return True
    else:
        print("❌ Problème de connexion détecté")
        print("❌ Vérifiez votre clé API")
        return False

def update_config():
    """Mettre à jour la configuration MapLibre avec KLANDO_MAP_API_URL"""
    
    klando_url = os.environ.get('KLANDO_MAP_API_URL')
    klando_key = os.environ.get('KLANDO_API_KEY')
    
    if not klando_url and not klando_key:
        print("❌ Ni KLANDO_MAP_API_URL ni KLANDO_API_KEY trouvées")
        return
    
    print(f"\n🔧 Mise à jour de la configuration:")
    
    # Lire le fichier .env
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return
    
    lines = env_file.read_text().splitlines()
    updated_lines = []
    updated_maplibre_url = False
    updated_maplibre_key = False
    
    for line in lines:
        if line.startswith('MAPLIBRE_STYLE_URL='):
            if klando_url:
                updated_lines.append(f'MAPLIBRE_STYLE_URL={klando_url}')
                updated_maplibre_url = True
                print(f"   ✅ MAPLIBRE_STYLE_URL mise à jour avec KLANDO_MAP_API_URL")
            else:
                updated_lines.append('MAPLIBRE_STYLE_URL=https://geo.klando-carpool.com/styles/carpool/style.json')
                updated_maplibre_url = True
                print(f"   ✅ MAPLIBRE_STYLE_URL mise à jour")
        elif line.startswith('MAPLIBRE_API_KEY='):
            if klando_url:
                # Si on utilise l'URL avec clé intégrée, on peut vider MAPLIBRE_API_KEY
                updated_lines.append('# MAPLIBRE_API_KEY= # Clé intégrée dans MAPLIBRE_STYLE_URL')
                print(f"   ✅ MAPLIBRE_API_KEY commentée (clé dans URL)")
            else:
                updated_lines.append(f'MAPLIBRE_API_KEY={klando_key}')
                print(f"   ✅ MAPLIBRE_API_KEY mise à jour")
            updated_maplibre_key = True
        else:
            updated_lines.append(line)
    
    # Ajouter les variables si elles n'existent pas
    if not updated_maplibre_url:
        if klando_url:
            updated_lines.append(f'MAPLIBRE_STYLE_URL={klando_url}')
            print(f"   ✅ MAPLIBRE_STYLE_URL ajoutée avec KLANDO_MAP_API_URL")
        else:
            updated_lines.append('MAPLIBRE_STYLE_URL=https://geo.klando-carpool.com/styles/carpool/style.json')
            print(f"   ✅ MAPLIBRE_STYLE_URL ajoutée")
    
    if not updated_maplibre_key:
        if klando_url:
            updated_lines.append('# MAPLIBRE_API_KEY= # Clé intégrée dans MAPLIBRE_STYLE_URL')
            print(f"   ✅ MAPLIBRE_API_KEY commentée (clé dans URL)")
        else:
            updated_lines.append(f'MAPLIBRE_API_KEY={klando_key}')
            print(f"   ✅ MAPLIBRE_API_KEY ajoutée")
    
    # Sauvegarder
    env_file.write_text('\n'.join(updated_lines) + '\n')
    print(f"   💾 Fichier .env sauvegardé")

if __name__ == "__main__":
    print("🧪 Test de l'API Klando MapLibre")
    print("=" * 50)
    
    success = test_klando_api()
    
    if success:
        print(f"\n🎉 Test réussi ! L'API fonctionne correctement.")
        
        # Proposer de mettre à jour la config
        response = input("\n❓ Voulez-vous mettre à jour la configuration MapLibre ? (y/N): ")
        if response.lower() in ['y', 'yes', 'oui', 'o']:
            update_config()
            print(f"\n🔄 Redémarrez l'application pour appliquer les changements.")
    else:
        print(f"\n❌ Test échoué. Vérifiez votre clé API.")
