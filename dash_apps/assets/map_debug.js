
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

// Observer les changements DOM - optimisé pour éviter le spam
let observerTimeout = null;
const observer = new MutationObserver(() => {
    // Debounce les vérifications pour éviter le spam
    if (observerTimeout) {
        clearTimeout(observerTimeout);
    }
    
    observerTimeout = setTimeout(() => {
        console.log('🔄 [DIAGNOSTIC] DOM modifié, re-vérification...');
        const containerCount = checkContainers();
        
        // Arrêter l'observation si des containers sont trouvés et initialisés
        if (containerCount > 0) {
            const containers = document.querySelectorAll('.maplibre-container');
            const initializedContainers = Array.from(containers).filter(c => c.__map || c.dataset.mapInited);
            
            if (initializedContainers.length > 0) {
                observer.disconnect();
                console.log('🔍 [DIAGNOSTIC] Observer arrêté - containers initialisés détectés');
            }
        }
    }, 500); // Debounce de 500ms
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Forcer l'initialisation après 5 secondes (réduit la fréquence)
setTimeout(() => {
    console.log('⏰ [DIAGNOSTIC] Timeout - Vérification finale des containers');
    const containers = document.querySelectorAll('.maplibre-container');
    
    if (containers.length === 0) {
        console.error('❌ [DIAGNOSTIC] Aucun container trouvé après 5s');
        return;
    }
    
    // Seulement initialiser si aucune carte n'existe déjà
    const uninitializedContainers = Array.from(containers).filter(c => !c.__map && !c.dataset.mapInited);
    
    if (uninitializedContainers.length === 0) {
        console.log('✅ [DIAGNOSTIC] Tous les containers sont déjà initialisés');
        return;
    }
    
    uninitializedContainers.forEach(container => {
        if (typeof maplibregl !== 'undefined') {
            console.log('🚀 [DIAGNOSTIC] Initialisation forcée pour:', container.id);
            
            try {
                const map = new maplibregl.Map({
                    container: container,
                    style: 'https://demotiles.maplibre.org/style.json',
                    center: [0, 0],
                    zoom: 2
                });
                
                // Marquer le container comme initialisé
                container.dataset.mapInited = 'true';
                container.__map = map;
                
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
}, 5000); // Augmenté de 2s à 5s

console.log('🔍 [DIAGNOSTIC] Script de diagnostic configuré');
