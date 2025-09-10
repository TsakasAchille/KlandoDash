#!/usr/bin/env python3
"""
Solution Python simple pour forcer le chargement de la carte MapLibre
"""

import sys
import os
sys.path.append('/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

from dash import html
from dash_apps.config import Config

def create_simple_map_component():
    """Crée un composant de carte simple qui fonctionne"""
    
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/style.json"
    api_key = Config.MAPLIBRE_API_KEY or ""
    
    # Script JavaScript simple et direct
    map_script = f"""
    console.log('🚀 [SIMPLE MAP] Initialisation directe');
    
    // Attendre que MapLibre soit chargé
    function initSimpleMap() {{
        if (typeof maplibregl === 'undefined') {{
            console.log('⏳ [SIMPLE MAP] Attente MapLibre GL JS...');
            setTimeout(initSimpleMap, 100);
            return;
        }}
        
        console.log('✅ [SIMPLE MAP] MapLibre GL JS disponible');
        
        const container = document.getElementById('simple-map-container');
        if (!container) {{
            console.error('❌ [SIMPLE MAP] Container non trouvé');
            return;
        }}
        
        console.log('📦 [SIMPLE MAP] Container trouvé, création carte...');
        
        try {{
            const map = new maplibregl.Map({{
                container: 'simple-map-container',
                style: '{style_url}',
                center: [2.3522, 48.8566], // Paris
                zoom: 10
            }});
            
            map.on('load', () => {{
                console.log('🎉 [SIMPLE MAP] Carte chargée avec succès!');
            }});
            
            map.on('error', (e) => {{
                console.error('❌ [SIMPLE MAP] Erreur:', e);
            }});
            
            // Ajouter contrôles de navigation
            map.addControl(new maplibregl.NavigationControl());
            
        }} catch (error) {{
            console.error('❌ [SIMPLE MAP] Erreur création:', error);
        }}
    }}
    
    // Démarrer l'initialisation
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initSimpleMap);
    }} else {{
        initSimpleMap();
    }}
    """
    
    return html.Div([
        html.H3("🗺️ Carte MapLibre Simple", style={"marginBottom": "20px"}),
        html.Div(
            id="simple-map-container",
            style={
                "height": "500px",
                "width": "100%",
                "border": "2px solid #ddd",
                "borderRadius": "8px",
                "backgroundColor": "#f5f5f5"
            }
        ),
        html.Script(map_script, type="text/javascript")
    ])

def patch_map_page():
    """Modifie la page map.py pour utiliser notre composant simple"""
    
    map_file = "/home/achille.tsakas/Klando/KlandoDash2/KlandoDash/dash_apps/pages/map.py"
    
    # Lire le fichier actuel
    with open(map_file, 'r') as f:
        content = f.read()
    
    # Ajouter notre import et fonction
    new_content = f'''from dash import html
from dash_apps.config import Config
import dash

def create_simple_map_component():
    """Crée un composant de carte simple qui fonctionne"""
    
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/style.json"
    
    map_script = f"""
    console.log('🚀 [SIMPLE MAP] Initialisation directe');
    
    function initSimpleMap() {{
        if (typeof maplibregl === 'undefined') {{
            setTimeout(initSimpleMap, 100);
            return;
        }}
        
        const container = document.getElementById('simple-map-container');
        if (!container) return;
        
        try {{
            const map = new maplibregl.Map({{
                container: 'simple-map-container',
                style: '{style_url}',
                center: [2.3522, 48.8566],
                zoom: 10
            }});
            
            map.on('load', () => {{
                console.log('🎉 [SIMPLE MAP] Carte chargée!');
            }});
            
            map.addControl(new maplibregl.NavigationControl());
            
        }} catch (error) {{
            console.error('❌ [SIMPLE MAP] Erreur:', error);
        }}
    }}
    
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initSimpleMap);
    }} else {{
        initSimpleMap();
    }}
    """.replace('{style_url}', style_url)
    
    return html.Div([
        html.H3("🗺️ Carte MapLibre Simple"),
        html.Div(
            id="simple-map-container",
            style={{
                "height": "500px",
                "width": "100%",
                "border": "2px solid #ddd",
                "borderRadius": "8px"
            }}
        ),
        html.Script(map_script, type="text/javascript")
    ])

{content}

# Remplacer le layout pour utiliser notre carte simple
layout = html.Div([
    html.H1("🗺️ Carte MapLibre - Version Simple", style={{"textAlign": "center", "marginBottom": "30px"}}),
    create_simple_map_component()
])
'''
    
    # Sauvegarder le fichier modifié
    with open(map_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Page map.py modifiée avec succès")

def main():
    """Fonction principale"""
    print("🔧 Création d'une solution de carte simple...")
    
    # Modifier la page map.py
    patch_map_page()
    
    print("✅ Solution appliquée!")
    print("📝 La page /maps utilise maintenant une carte simple et directe")
    print("🔄 Redémarrez l'application pour voir les changements")

if __name__ == "__main__":
    main()
