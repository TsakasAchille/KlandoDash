#!/usr/bin/env python3
"""
Script de debug spécifique pour la page 00_map
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from dash_apps.config import Config
from dotenv import load_dotenv

def check_current_config():
    """Vérifie la configuration actuelle après le fix"""
    print("=== VÉRIFICATION DE LA CONFIGURATION ACTUELLE ===")
    
    # Recharger les variables d'environnement
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"✅ Fichier .env rechargé: {env_path}")
    
    print(f"MAPLIBRE_STYLE_URL (env): {os.environ.get('MAPLIBRE_STYLE_URL')}")
    print(f"MAPLIBRE_API_KEY (env): {'***' if os.environ.get('MAPLIBRE_API_KEY') else 'Non définie'}")
    print(f"Config.MAPLIBRE_STYLE_URL: {Config.MAPLIBRE_STYLE_URL}")
    print(f"Config.MAPLIBRE_API_KEY: {'***' if Config.MAPLIBRE_API_KEY else 'Non définie'}")

def debug_maplibre_container():
    """Debug de la fonction create_maplibre_container"""
    print("\n=== DEBUG DE create_maplibre_container ===")
    
    try:
        from dash_apps.pages.map_00 import create_maplibre_container
        
        # Simuler l'appel de la fonction
        container = create_maplibre_container()
        
        # Extraire les attributs data
        data_attrs = {k: v for k, v in container.children[0].to_plotly_json().items() if k.startswith('data-')}
        
        print(f"Attributs data du container:")
        for key, value in data_attrs.items():
            if 'api-key' in key:
                print(f"  {key}: {'***' if value else 'Vide'}")
            else:
                print(f"  {key}: {value}")
        
        return True
        
    except ImportError:
        print("❌ Impossible d'importer create_maplibre_container")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du debug: {e}")
        return False

def check_maplibre_js_init():
    """Vérifie le fichier d'initialisation MapLibre JS"""
    print("\n=== VÉRIFICATION DU FICHIER MAPLIBRE JS ===")
    
    js_file = Path(__file__).parent / 'dash_apps' / 'core' / 'assets' / 'maplibre_init.js'
    
    if not js_file.exists():
        print(f"❌ Fichier JS non trouvé: {js_file}")
        return False
    
    print(f"✅ Fichier JS trouvé: {js_file}")
    
    # Lire le contenu pour vérifier les erreurs
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Chercher les messages d'erreur
    if "Erreur de chargement du style" in content:
        print("⚠️  Message d'erreur trouvé dans le JS")
        
        # Extraire la section d'erreur
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Erreur de chargement du style" in line:
                print(f"Ligne {i+1}: {line.strip()}")
                # Afficher le contexte
                start = max(0, i-5)
                end = min(len(lines), i+6)
                print("\nContexte:")
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"{marker}{j+1:3}: {lines[j]}")
                break
    
    return True

def add_debug_logging():
    """Ajoute du logging de debug au fichier JS"""
    print("\n=== AJOUT DE DEBUG LOGGING ===")
    
    js_file = Path(__file__).parent / 'dash_apps' / 'core' / 'assets' / 'maplibre_init.js'
    
    if not js_file.exists():
        print(f"❌ Fichier JS non trouvé: {js_file}")
        return False
    
    # Lire le contenu actuel
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Vérifier si le debug est déjà ajouté
    if "DEBUG_MAP_CONFIG" in content:
        print("✅ Debug déjà présent dans le fichier JS")
        return True
    
    # Ajouter du debug au début de la fonction d'initialisation
    debug_code = '''
    // DEBUG_MAP_CONFIG - Ajouté par debug_map_page.py
    console.log('[MAP_DEBUG] Configuration détectée:', {
      styleUrl: styleUrl,
      apiKey: apiKey ? '***' : 'Non définie',
      container: container.id
    });
    
    // Log des erreurs de style plus détaillé
    map.on('error', (e) => {
      console.error('[MAP_DEBUG] Erreur MapLibre détaillée:', e);
      console.error('[MAP_DEBUG] Style URL utilisée:', styleUrl);
      console.error('[MAP_DEBUG] API Key présente:', !!apiKey);
    });
    '''
    
    # Trouver où insérer le debug (après la déclaration de la map)
    lines = content.split('\n')
    new_lines = []
    debug_inserted = False
    
    for line in lines:
        new_lines.append(line)
        if 'new maplibregl.Map(' in line and not debug_inserted:
            # Insérer le debug après la création de la map
            new_lines.extend(debug_code.split('\n'))
            debug_inserted = True
    
    if debug_inserted:
        # Sauvegarder le fichier modifié
        backup_file = js_file.with_suffix('.js.backup')
        js_file.rename(backup_file)
        print(f"✅ Backup créé: {backup_file}")
        
        with open(js_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Debug logging ajouté au fichier JS")
        return True
    else:
        print("❌ Impossible de trouver où insérer le debug")
        return False

def create_test_page():
    """Crée une page de test simple pour la carte"""
    print("\n=== CRÉATION D'UNE PAGE DE TEST ===")
    
    test_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test MapLibre</title>
    <script src="https://unpkg.com/maplibre-gl@3.6.1/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@3.6.1/dist/maplibre-gl.css" rel="stylesheet">
    <style>
        #map { height: 400px; width: 100%; }
        .debug { margin: 20px; padding: 10px; background: #f0f0f0; }
    </style>
</head>
<body>
    <div class="debug">
        <h2>Test MapLibre Direct</h2>
        <p>Style URL: <span id="style-url"></span></p>
        <p>Status: <span id="status">Initialisation...</span></p>
    </div>
    <div id="map"></div>
    
    <script>
        const styleUrl = 'https://demotiles.maplibre.org/globe.json';
        document.getElementById('style-url').textContent = styleUrl;
        
        console.log('Initialisation de la carte de test...');
        
        const map = new maplibregl.Map({
            container: 'map',
            style: styleUrl,
            center: [-14.7, 14.7], // Sénégal
            zoom: 6
        });
        
        map.on('load', () => {
            console.log('Carte chargée avec succès');
            document.getElementById('status').textContent = 'Carte chargée avec succès';
            document.getElementById('status').style.color = 'green';
        });
        
        map.on('error', (e) => {
            console.error('Erreur de carte:', e);
            document.getElementById('status').textContent = 'Erreur: ' + e.error.message;
            document.getElementById('status').style.color = 'red';
        });
    </script>
</body>
</html>'''
    
    test_file = Path(__file__).parent / 'test_map.html'
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"✅ Page de test créée: {test_file}")
    print(f"📖 Ouvrez {test_file} dans votre navigateur pour tester")
    
    return test_file

def main():
    print("🗺️  DEBUG DE LA PAGE MAP")
    print("=" * 40)
    
    # 1. Vérifier la configuration
    check_current_config()
    
    # 2. Debug du container MapLibre
    debug_maplibre_container()
    
    # 3. Vérifier le fichier JS
    check_maplibre_js_init()
    
    # 4. Ajouter du debug logging
    add_debug_logging()
    
    # 5. Créer une page de test
    create_test_page()
    
    print("\n" + "=" * 40)
    print("📋 ACTIONS RECOMMANDÉES:")
    print("1. Redémarrez l'application Dash")
    print("2. Ouvrez la console du navigateur (F12)")
    print("3. Naviguez vers la page Map")
    print("4. Vérifiez les logs [MAP_DEBUG] dans la console")
    print("5. Testez aussi test_map.html pour comparaison")

if __name__ == "__main__":
    main()
