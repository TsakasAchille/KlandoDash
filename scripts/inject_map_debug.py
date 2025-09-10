#!/usr/bin/env python3
"""
Script pour injecter du code de diagnostic JavaScript directement dans la page
"""

def create_debug_js():
    """Crée le code JavaScript de diagnostic"""
    return """
// DIAGNOSTIC MAPLIBRE - Injecté par Python
console.log('🔍 [DIAGNOSTIC] Script de diagnostic chargé');

// Vérifier MapLibre GL JS
if (typeof maplibregl === 'undefined') {
    console.error('❌ [DIAGNOSTIC] MapLibre GL JS non chargé');
} else {
    console.log('✅ [DIAGNOSTIC] MapLibre GL JS version:', maplibregl.version);
}

// Vérifier les containers
function checkContainers() {
    const containers = document.querySelectorAll('.maplibre-container');
    console.log(`🔍 [DIAGNOSTIC] Containers trouvés: ${containers.length}`);
    
    containers.forEach((container, index) => {
        console.log(`📦 [DIAGNOSTIC] Container ${index}:`, {
            id: container.id,
            className: container.className,
            styleUrl: container.getAttribute('data-style-url'),
            apiKey: container.getAttribute('data-api-key') ? '***' : 'Non définie',
            mapInited: container.dataset.mapInited,
            hasMap: !!container.__map
        });
    });
    
    return containers.length;
}

// Vérifier immédiatement
checkContainers();

// Observer les changements DOM
const observer = new MutationObserver(() => {
    console.log('🔄 [DIAGNOSTIC] DOM modifié, re-vérification...');
    checkContainers();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Forcer l'initialisation après 2 secondes
setTimeout(() => {
    console.log('⏰ [DIAGNOSTIC] Timeout - Forcer initialisation');
    const containers = document.querySelectorAll('.maplibre-container');
    
    if (containers.length === 0) {
        console.error('❌ [DIAGNOSTIC] Aucun container trouvé après 2s');
        return;
    }
    
    containers.forEach(container => {
        if (!container.__map && typeof maplibregl !== 'undefined') {
            console.log('🚀 [DIAGNOSTIC] Initialisation forcée pour:', container.id);
            
            try {
                const map = new maplibregl.Map({
                    container: container,
                    style: 'https://demotiles.maplibre.org/style.json',
                    center: [0, 0],
                    zoom: 2
                });
                
                map.on('load', () => {
                    console.log('✅ [DIAGNOSTIC] Carte chargée avec succès!');
                });
                
                map.on('error', (e) => {
                    console.error('❌ [DIAGNOSTIC] Erreur carte:', e);
                });
                
            } catch (error) {
                console.error('❌ [DIAGNOSTIC] Erreur initialisation:', error);
            }
        }
    });
}, 2000);

console.log('🔍 [DIAGNOSTIC] Script de diagnostic configuré');
"""

def inject_debug_into_page():
    """Injecte le code de diagnostic dans la page map.py"""
    
    from dash import html
    
    # Créer un script tag avec le code de diagnostic
    debug_script = html.Script(
        create_debug_js(),
        type="text/javascript"
    )
    
    return debug_script

def main():
    """Fonction principale"""
    print("🔧 Génération du code de diagnostic JavaScript...")
    
    js_code = create_debug_js()
    
    # Sauvegarder dans un fichier
    debug_file = "/home/achille.tsakas/Klando/KlandoDash2/KlandoDash/dash_apps/assets/map_debug.js"
    
    with open(debug_file, 'w') as f:
        f.write(js_code)
    
    print(f"✅ Code de diagnostic sauvé dans: {debug_file}")
    print("📝 Le fichier sera automatiquement chargé par Dash")
    print("\n🔍 Pour voir les logs:")
    print("1. Ouvrir http://127.0.0.1:8050")
    print("2. Ouvrir la console du navigateur (F12)")
    print("3. Chercher les messages [DIAGNOSTIC]")

if __name__ == "__main__":
    main()
