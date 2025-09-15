// MapLibre pour la page trips - JavaScript séparé
// Utilise le même système que la page d'accueil mais avec des IDs différents

const TRIPS_MAP_CONTAINER_ID = 'trips-maplibre-map';
let tripsMapInitStarted = false;
let tripsMapInstance = null;

function ensureMapLibreLoadedForTrips(callback) {
    if (typeof maplibregl !== 'undefined') {
        callback();
        return;
    }
    const existing = document.querySelector('script[data-maplibre-gl]');
    if (existing) {
        existing.addEventListener('load', callback, { once: true });
        return;
    }
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js';
    script.async = true;
    script.defer = true;
    script.setAttribute('data-maplibre-gl', 'true');
    script.onload = callback;
    script.onerror = function () {
        console.error('[TRIPS_MAP] Échec du chargement de maplibre-gl.js');
    };
    document.head.appendChild(script);
}

function tryInitTripsMap() {
    const container = document.getElementById(TRIPS_MAP_CONTAINER_ID);
    if (!container) {
        console.log('[TRIPS_MAP] Container pas encore disponible');
        return;
    }
    
    // Vérifier si le container est visible et a des dimensions
    const rect = container.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
        if (!tryInitTripsMap.retryCount) tryInitTripsMap.retryCount = 0;
        tryInitTripsMap.retryCount++;
        
        if (tryInitTripsMap.retryCount <= 5) {
            console.log('[TRIPS_MAP] Container pas encore dimensionné, retry', tryInitTripsMap.retryCount, '/5 dans 500ms');
            setTimeout(tryInitTripsMap, 500);
        } else {
            console.warn('[TRIPS_MAP] Abandon après 5 tentatives - container toujours pas dimensionné');
            tripsMapInitStarted = false;
        }
        return;
    }
    
    // Réinitialiser le compteur de retry
    tryInitTripsMap.retryCount = 0;
    
    // Éviter les initialisations multiples
    if (tripsMapInstance && tripsMapInstance.getContainer() === container && !tripsMapInstance._removed) {
        console.log('[TRIPS_MAP] Carte déjà initialisée sur ce container');
        setTimeout(function() {
            if (tripsMapInstance && !tripsMapInstance._removed) {
                tripsMapInstance.resize();
                console.log('[TRIPS_MAP] Resize forcé de la carte existante');
            }
        }, 100);
        return;
    }
    
    // Nettoyer l'ancienne instance si nécessaire
    if (tripsMapInstance && (tripsMapInstance.getContainer() !== container || tripsMapInstance._removed)) {
        console.log('[TRIPS_MAP] Nettoyage ancienne instance de carte');
        try {
            tripsMapInstance.remove();
        } catch (e) {
            console.warn('[TRIPS_MAP] Erreur lors du nettoyage:', e);
        }
        tripsMapInstance = null;
        tripsMapInitStarted = false;
    }
    
    if (tripsMapInitStarted) {
        console.log('[TRIPS_MAP] Initialisation déjà en cours');
        return;
    }
    
    tripsMapInitStarted = true;
    console.log('[TRIPS_MAP] Début initialisation carte sur container:', container.id);
    
    ensureMapLibreLoadedForTrips(function() {
        console.log('[TRIPS_MAP] Script chargé, création de la carte...');
        
        if (!document.getElementById(TRIPS_MAP_CONTAINER_ID)) {
            console.warn('[TRIPS_MAP] Container disparu pendant le chargement');
            tripsMapInitStarted = false;
            return;
        }
        
        // Utiliser le même style que la page d'accueil
        let styleUrl = container.getAttribute('data-style-url');
        if (!styleUrl || styleUrl.includes('YOUR_API_KEY')) {
            styleUrl = 'https://demotiles.maplibre.org/style.json';
            console.log('[TRIPS_MAP] Fallback vers demotiles:', styleUrl);
        } else {
            console.log('[TRIPS_MAP] Style du container:', styleUrl);
        }
        
        tripsMapInstance = new maplibregl.Map({
            container: TRIPS_MAP_CONTAINER_ID,
            style: styleUrl,
            center: [2.3522, 48.8566], // Paris par défaut
            zoom: 10,
            preserveDrawingBuffer: true
        });
        
        tripsMapInstance.on('load', function() {
            console.log('[TRIPS_MAP] Carte chargée avec succès');
            setupTripsMapLayersAndEvents(tripsMapInstance);
        });
        
        tripsMapInstance.on('error', function(e) {
            console.error('[TRIPS_MAP] Erreur carte:', e);
            tripsMapInitStarted = false;
        });
        
        // Forcer un resize après initialisation
        setTimeout(function() {
            if (tripsMapInstance && !tripsMapInstance._removed) {
                tripsMapInstance.resize();
                console.log('[TRIPS_MAP] Resize post-initialisation');
            }
        }, 500);
    });
}

// Observer pour détecter l'ajout du container trips - Version renforcée
function watchForTripsContainer() {
    console.log('[TRIPS_MAP] Démarrage watchForTripsContainer');
    
    // Vérification initiale immédiate
    tryInitTripsMap();
    
    const observer = new MutationObserver(function (mutations) {
        // Ne pas arrêter l'observer même si une carte existe déjà
        // car elle peut être supprimée lors des changements de page
        
        let shouldCheck = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.id === TRIPS_MAP_CONTAINER_ID || 
                            (node.querySelector && node.querySelector('#' + TRIPS_MAP_CONTAINER_ID))) {
                            console.log('[TRIPS_MAP] Container détecté via observer');
                            shouldCheck = true;
                        }
                    }
                });
            }
        });
        
        if (shouldCheck) {
            // Essayer plusieurs fois avec des délais différents
            setTimeout(tryInitTripsMap, 50);
            setTimeout(tryInitTripsMap, 200);
            setTimeout(tryInitTripsMap, 500);
        }
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: false
    });
    
    // Vérification périodique plus fréquente et plus longue
    let periodicCheckCount = 0;
    const maxPeriodicChecks = 20; // Augmenté de 10 à 20
    
    const periodicCheck = setInterval(function() {
        periodicCheckCount++;
        
        const container = document.getElementById(TRIPS_MAP_CONTAINER_ID);
        const needsInit = container && (!tripsMapInstance || tripsMapInstance._removed || tripsMapInstance.getContainer() !== container);
        
        if (periodicCheckCount >= maxPeriodicChecks) {
            clearInterval(periodicCheck);
            console.log('[TRIPS_MAP] Vérifications périodiques arrêtées après', periodicCheckCount, 'tentatives');
            return;
        }
        
        if (needsInit) {
            console.log('[TRIPS_MAP] Vérification périodique #' + periodicCheckCount + ' - container trouvé, initialisation');
            tryInitTripsMap();
        } else if (container) {
            console.log('[TRIPS_MAP] Vérification périodique #' + periodicCheckCount + ' - container existe, carte OK');
        } else {
            console.log('[TRIPS_MAP] Vérification périodique #' + periodicCheckCount + ' - pas de container');
        }
    }, 2000); // Réduit de 5s à 2s
    
    // Timeout plus long
    setTimeout(function() {
        clearInterval(periodicCheck);
        console.log('[TRIPS_MAP] Timeout des vérifications périodiques après 120s');
    }, 120000); // Augmenté de 60s à 120s
}

// Configuration des layers et événements pour la carte trips
function setupTripsMapLayersAndEvents(map) {
    function ensureSource() {
        console.log('[TRIPS_MAP_SETUP] Initialisation des sources et layers');
        if (!map.getSource('trips')) {
            console.log('[TRIPS_MAP_SETUP] Ajout de la source trips');
            map.addSource('trips', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
        }
        if (!map.getLayer('trips-line')) {
            console.log('[TRIPS_MAP_SETUP] Ajout du layer trips-line');
            map.addLayer({
                id: 'trips-line',
                type: 'line',
                source: 'trips',
                filter: ['==', ['geometry-type'], 'LineString'],
                paint: {
                    'line-width': 8,
                    'line-color': ['get', 'color']
                }
            });
        }
        if (!map.getLayer('trips-points')) {
            map.addLayer({
                id: 'trips-points',
                type: 'circle',
                source: 'trips',
                filter: ['==', ['geometry-type'], 'Point'],
                paint: {
                    'circle-radius': 8,
                    'circle-color': ['get', 'color'],
                    'circle-stroke-color': '#fff',
                    'circle-stroke-width': 2
                }
            });
        }
    }

    function updateGeoJSON(geojsonText) {
        if (!geojsonText) return;
        try {
            const data = JSON.parse(geojsonText);
            console.log('[TRIPS_MAP_GEOJSON] Données GeoJSON reçues:', data);
            console.log('[TRIPS_MAP_GEOJSON] Nombre de features:', data.features ? data.features.length : 0);
            
            ensureSource();
            const src = map.getSource('trips');
            src.setData(data);
            console.log('[TRIPS_MAP_GEOJSON] Données appliquées à la source trips');
            
            // Fit bounds si il y a des lignes
            const coords = [];
            data.features.forEach(f => {
                if (f.geometry && f.geometry.type === 'LineString') {
                    coords.push(...f.geometry.coordinates);
                }
            });
            if (coords.length) {
                const lons = coords.map(c => c[0]);
                const lats = coords.map(c => c[1]);
                const bounds = [[Math.min(...lons), Math.min(...lats)], [Math.max(...lons), Math.max(...lats)]];
                map.fitBounds(bounds, { padding: 40, maxZoom: 14, duration: 0 });
            }
        } catch (e) {
            console.warn('[TRIPS_MAP] GeoJSON invalide:', e);
        }
    }

    // Écouter les mises à jour du bridge element trips-maplibre
    const bridgeEl = document.getElementById('trips-maplibre');
    if (bridgeEl) {
        console.log('[TRIPS_MAP_SETUP] Bridge element trips-maplibre trouvé');
        // Mise à jour initiale
        updateGeoJSON(bridgeEl.getAttribute('data-geojson'));
        
        const obs = new MutationObserver(muts => {
            muts.forEach(m => {
                if (m.type === 'attributes' && m.attributeName === 'data-geojson') {
                    console.log('[TRIPS_MAP_GEOJSON] Mise à jour GeoJSON pour trips');
                    updateGeoJSON(bridgeEl.getAttribute('data-geojson'));
                }
            });
        });
        obs.observe(bridgeEl, { attributes: true });
    } else {
        console.warn('[TRIPS_MAP_SETUP] Bridge element trips-maplibre non trouvé');
    }

    // Événements de clic et hover (optionnels pour la page trips)
    map.on('click', (e) => {
        console.log('[TRIPS_MAP_DEBUG] Clic sur la carte à:', e.lngLat);
        const features = map.queryRenderedFeatures(e.point);
        const tripFeatures = features.filter(f => f.source === 'trips');
        console.log('[TRIPS_MAP_DEBUG] Features de trajets:', tripFeatures);
    });
}

// Écouter les changements de page Dash - Version améliorée
document.addEventListener('DOMContentLoaded', function() {
    const dashContainer = document.getElementById('_dash-app-content') || document.body;
    
    // Observer plus agressif pour détecter les changements de page
    const pageObserver = new MutationObserver(function(mutations) {
        let shouldCheckTripsContainer = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Détecter spécifiquement le container trips
                        if (node.id === TRIPS_MAP_CONTAINER_ID || 
                            (node.querySelector && node.querySelector('#' + TRIPS_MAP_CONTAINER_ID))) {
                            console.log('[TRIPS_MAP] Container trips détecté dans DOM');
                            shouldCheckTripsContainer = true;
                        }
                        // Détecter les changements de page généraux
                        else if (node.querySelector && (
                            node.querySelector('[data-dash-is-loading]') || 
                            node.id === 'page-content' || 
                            node.className.includes('page-') ||
                            node.querySelector('.page-content') ||
                            node.querySelector('[id*="trips"]')
                        )) {
                            console.log('[TRIPS_MAP] Changement de page détecté');
                            tripsMapInitStarted = false;
                            shouldCheckTripsContainer = true;
                        }
                    }
                });
            }
        });
        
        if (shouldCheckTripsContainer) {
            // Essayer plusieurs fois avec des délais différents
            setTimeout(watchForTripsContainer, 50);
            setTimeout(watchForTripsContainer, 200);
            setTimeout(watchForTripsContainer, 500);
            setTimeout(watchForTripsContainer, 1000);
        }
    });
    
    pageObserver.observe(dashContainer, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'id']
    });
    
    // Observer spécifique pour le container trips
    const tripsObserver = new MutationObserver(function(mutations) {
        const tripsContainer = document.getElementById(TRIPS_MAP_CONTAINER_ID);
        if (tripsContainer && (!tripsMapInstance || tripsMapInstance._removed || tripsMapInstance.getContainer() !== tripsContainer)) {
            console.log('[TRIPS_MAP] Container trips spécifiquement détecté, initialisation...');
            setTimeout(tryInitTripsMap, 100);
        }
    });
    
    tripsObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Initialisation
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', watchForTripsContainer);
} else {
    watchForTripsContainer();
}

console.log('[TRIPS_MAP] Script trips_maplibre.js chargé');
