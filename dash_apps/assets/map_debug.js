
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
