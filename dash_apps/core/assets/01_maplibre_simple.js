// Robust MapLibre bootstrap for Dash: dash-renderer mounts layout AFTER DOMContentLoaded.
// We wait for the #maplibre-map element to appear, then ensure MapLibre GL JS is loaded, then init once.

const MAP_CONTAINER_ID = 'maplibre-map';
let mapInitStarted = false;
let mapInstance = null; // shared reference

function ensureMapLibreLoaded(callback) {
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
        console.error('[MAPLIBRE] Échec du chargement de maplibre-gl.js');
    };
    document.head.appendChild(script);
}

function tryInitMap() {
    const container = document.getElementById(MAP_CONTAINER_ID);
    if (!container) {
        console.log('[MAPLIBRE] Container pas encore disponible');
        return;
    }
    
    // Vérifier si le container est visible et a des dimensions
    const rect = container.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
        console.log('[MAPLIBRE] Container pas encore dimensionné, retry dans 200ms');
        setTimeout(tryInitMap, 200);
        return;
    }
    
    // Avoid multiple initializations on same container
    if (mapInstance && mapInstance.getContainer() === container && !mapInstance._removed) {
        console.log('[MAPLIBRE] Carte déjà initialisée sur ce container');
        // Forcer un resize au cas où les dimensions auraient changé
        setTimeout(function() {
            if (mapInstance && !mapInstance._removed) {
                mapInstance.resize();
                console.log('[MAPLIBRE] Resize forcé de la carte existante');
            }
        }, 100);
        return;
    }
    
    // Clean up old instance if container has changed or if instance is removed
    if (mapInstance && (mapInstance.getContainer() !== container || mapInstance._removed)) {
        console.log('[MAPLIBRE] Nettoyage ancienne instance de carte');
        try {
            mapInstance.remove();
        } catch (e) {
            console.warn('[MAPLIBRE] Erreur lors du nettoyage:', e);
        }
        mapInstance = null;
        mapInitStarted = false;
    }
    
    if (mapInitStarted) {
        console.log('[MAPLIBRE] Initialisation déjà en cours');
        return;
    }
    
    mapInitStarted = true;
    console.log('[MAPLIBRE] Début initialisation carte sur container:', container.id);
    
    ensureMapLibreLoaded(function() {
        console.log('[MAPLIBRE] Script chargé, création de la carte...');
        
        // Vérifier une dernière fois que le container existe toujours
        if (!document.getElementById(MAP_CONTAINER_ID)) {
            console.warn('[MAPLIBRE] Container disparu pendant le chargement');
            mapInitStarted = false;
            return;
        }
        
        // Utiliser un style par défaut si pas de data-style-url
        let styleUrl = container.getAttribute('data-style-url');
        if (!styleUrl) {
            styleUrl = 'https://demotiles.maplibre.org/style.json';
            console.log('[MAPLIBRE] Utilisation du style par défaut');
        }
        
        mapInstance = new maplibregl.Map({
            container: MAP_CONTAINER_ID,
            style: styleUrl,
            center: [2.3522, 48.8566], // Paris par défaut
            zoom: 10,
            preserveDrawingBuffer: true
        });
        
        mapInstance.on('load', function() {
            console.log('[MAPLIBRE] Carte chargée avec succès');
            setupTripLayersAndEvents(mapInstance);
        });
        
        mapInstance.on('error', function(e) {
            console.error('[MAPLIBRE] Erreur carte:', e);
            mapInitStarted = false;
        });
        
        // Forcer un resize après initialisation
        setTimeout(function() {
            if (mapInstance && !mapInstance._removed) {
                mapInstance.resize();
                console.log('[MAPLIBRE] Resize post-initialisation');
            }
        }, 500);
        
    });
}

// Observe DOM changes to detect when Dash mounts #maplibre-map
function watchForContainer() {
    // initial quick check
    tryInitMap();
    
    // MutationObserver for robust detection avec surveillance continue
    const observer = new MutationObserver(function (mutations) {
        let shouldCheck = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Vérifier si des noeuds ont été ajoutés qui pourraient contenir notre container
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.id === MAP_CONTAINER_ID || node.querySelector('#' + MAP_CONTAINER_ID)) {
                            shouldCheck = true;
                        }
                    }
                });
            }
        });
        
        if (shouldCheck || document.getElementById(MAP_CONTAINER_ID)) {
            // Petit délai pour laisser Dash finir le rendu
            setTimeout(tryInitMap, 100);
        }
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: false  // Pas besoin de surveiller les attributs
    });
    
    // Vérification périodique pour les cas où MutationObserver rate quelque chose
    const periodicCheck = setInterval(function() {
        const container = document.getElementById(MAP_CONTAINER_ID);
        if (container && (!mapInstance || mapInstance.getContainer() !== container)) {
            tryInitMap();
        }
    }, 2000);
    
    // Nettoyer les vérifications périodiques après 30 secondes
    setTimeout(function() {
        clearInterval(periodicCheck);
    }, 30000);
}

// Écouter les changements de page Dash
function handlePageChange() {
    console.log('[MAPLIBRE] Changement de page détecté');
    // Réinitialiser les flags pour permettre une nouvelle initialisation
    mapInitStarted = false;
    // Lancer la surveillance du container
    setTimeout(watchForContainer, 100);
}

// Écouter les événements de navigation Dash
document.addEventListener('DOMContentLoaded', function() {
    // Observer les changements dans le conteneur principal de Dash
    const dashContainer = document.getElementById('_dash-app-content') || document.body;
    const pageObserver = new MutationObserver(function(mutations) {
        let pageChanged = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Détecter si une nouvelle page a été chargée
                        if (node.querySelector && (node.querySelector('[data-dash-is-loading]') || 
                            node.id === 'page-content' || node.className.includes('page-'))) {
                            pageChanged = true;
                        }
                    }
                });
            }
        });
        
        if (pageChanged) {
            handlePageChange();
        }
    });
    
    pageObserver.observe(dashContainer, {
        childList: true,
        subtree: true
    });
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', watchForContainer);
} else {
    watchForContainer();
}

// --- Integration with Dash callbacks ---
function setupTripLayersAndEvents(map) {
    // Add empty source once; layers added on first update
    function ensureSource() {
        console.log('[MAP_SETUP] Initialisation des sources et layers');
        if (!map.getSource('trips')) {
            console.log('[MAP_SETUP] Ajout de la source trips');
            map.addSource('trips', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
        }
        if (!map.getLayer('trips-line')) {
            console.log('[MAP_SETUP] Ajout du layer trips-line');
            map.addLayer({
                id: 'trips-line',
                type: 'line',
                source: 'trips',
                filter: ['==', ['geometry-type'], 'LineString'],
                paint: {
                    'line-width': 8,  // Augmenté de 4 à 8 pixels
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
                    'circle-radius': 8,  // Augmenté de 5 à 8 pixels
                    'circle-color': ['get', 'color'],
                    'circle-stroke-color': '#fff',
                    'circle-stroke-width': 2  // Augmenté de 1 à 2 pixels
                }
            });
        }
    }

    function updateGeoJSON(geojsonText) {
        if (!geojsonText) return;
        try {
            const data = JSON.parse(geojsonText);
            console.log('[MAP_GEOJSON] Données GeoJSON reçues:', data);
            console.log('[MAP_GEOJSON] Nombre de features:', data.features ? data.features.length : 0);
            
            ensureSource();
            const src = map.getSource('trips');
            src.setData(data);
            console.log('[MAP_GEOJSON] Données appliquées à la source trips');
            
            // Vérifier les layers après mise à jour
            console.log('[MAP_GEOJSON] Layer trips-line existe:', !!map.getLayer('trips-line'));
            console.log('[MAP_GEOJSON] Layer trips-points existe:', !!map.getLayer('trips-points'));
            
            // Fit bounds if there are lines
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
            console.warn('[MAPLIBRE] GeoJSON invalide:', e);
        }
    }

    // Listen to DOM attribute updates from Dash on #home-maplibre
    const bridgeEl = document.getElementById('home-maplibre');
    if (bridgeEl) {
        // initial
        updateGeoJSON(bridgeEl.getAttribute('data-geojson'));
        const obs = new MutationObserver(muts => {
            muts.forEach(m => {
                if (m.type === 'attributes' && m.attributeName === 'data-geojson') {
                    updateGeoJSON(bridgeEl.getAttribute('data-geojson'));
                }
            });
        });
        obs.observe(bridgeEl, { attributes: true });
    }

    // Emit hover/click events to Dash via maplibre_bridge.js
    let lastEmittedState = { hover: null, click: null };
    
    function emitHoverClick(hoverId, clickId) {
        // Éviter le spam en vérifiant si l'état a vraiment changé
        if (hoverId === lastEmittedState.hover && clickId === lastEmittedState.click) {
            return; // Pas de changement, ne pas émettre
        }
        
        console.log('[MAP_EMIT] emitHoverClick appelé avec hover:', hoverId, 'click:', clickId);
        lastEmittedState = { hover: hoverId, click: clickId };
        
        if (typeof window.updateMapEvents === 'function') {
            console.log('[MAP_EMIT] Appel de window.updateMapEvents');
            window.updateMapEvents(hoverId, clickId);
        } else {
            console.error('[MAP_EMIT] window.updateMapEvents non disponible!');
        }
    }
    // Ajouter un test de clic général sur la carte
    map.on('click', (e) => {
        console.log('[MAP_DEBUG] Clic général sur la carte à:', e.lngLat);
        const features = map.queryRenderedFeatures(e.point);
        console.log('[MAP_DEBUG] Features trouvées au point de clic:', features);
        const tripFeatures = features.filter(f => f.source === 'trips');
        console.log('[MAP_DEBUG] Features de trajets:', tripFeatures);
        
        // Si on trouve des features de trajets, traiter le clic manuellement
        if (tripFeatures.length > 0) {
            const tripFeature = tripFeatures[0];
            const tripId = tripFeature.properties && tripFeature.properties.trip_id;
            console.log('[MAP_DEBUG] Clic manuel sur trajet détecté, ID:', tripId);
            if (tripId) {
                emitHoverClick(null, tripId);
            }
        }
    });
    
    // Ajouter un test de mousemove général sur la carte avec zone élargie
    let lastHoveredTripId = null;
    let lastEmittedHover = null;
    
    map.on('mousemove', (e) => {
        // Augmenter la zone de sélection en utilisant un buffer de 10 pixels
        const buffer = 10;
        const bbox = [
            [e.point.x - buffer, e.point.y - buffer],
            [e.point.x + buffer, e.point.y + buffer]
        ];
        const features = map.queryRenderedFeatures(bbox);
        const tripFeatures = features.filter(f => f.source === 'trips');
        
        if (tripFeatures.length > 0) {
            const tripFeature = tripFeatures[0];
            const tripId = tripFeature.properties && tripFeature.properties.trip_id;
            map.getCanvas().style.cursor = 'pointer';
            
            // Logs seulement si c'est un nouveau trajet survolé
            if (tripId && tripId !== lastHoveredTripId) {
                console.log('🚗 [HOVER] Survol du trajet:', tripId);
                console.log('📍 [HOVER] Propriétés:', tripFeature.properties);
                lastHoveredTripId = tripId;
            }
            
            // Émettre l'événement hover seulement si changement
            if (tripId && tripId !== lastEmittedHover) {
                emitHoverClick(tripId, null);
                lastEmittedHover = tripId;
            }
        } else {
            if (lastHoveredTripId) {
                console.log('👋 [HOVER] Fin du survol du trajet:', lastHoveredTripId);
                lastHoveredTripId = null;
            }
            map.getCanvas().style.cursor = '';
            
            // Émettre null seulement si on avait un hover avant
            if (lastEmittedHover !== null) {
                emitHoverClick(null, null);
                lastEmittedHover = null;
            }
        }
    });
    
    // Attendre que les layers soient ajoutés avant d'ajouter les événements
    map.on('sourcedata', (e) => {
        if (e.sourceId === 'trips' && e.isSourceLoaded) {
            console.log('[MAP_EVENTS] Source trips chargée, ajout des événements');
            
            // Vérifier les features dans la source
            const source = map.getSource('trips');
            if (source && source._data) {
                console.log('[MAP_DEBUG] Features dans la source trips:', source._data.features);
            }
            
            // Supprimer les anciens événements pour éviter les doublons
            map.off('click', 'trips-line');
            map.off('click', 'trips-points');
            map.off('mousemove', 'trips-line');
            map.off('mousemove', 'trips-points');
            
            // Ajouter les événements de clic
            map.on('click', 'trips-line', e => {
                console.log('[MAP_CLICK] Événement clic détecté sur trips-line');
                console.log('[MAP_CLICK] Features disponibles:', e.features);
                const f = e.features && e.features[0];
                const tripId = f && f.properties && f.properties.trip_id || null;
                console.log('[MAP_CLICK] Feature extraite:', f);
                console.log('[MAP_CLICK] Trip ID extrait:', tripId);
                console.log('[MAP_CLICK] Clic sur trajet ligne:', tripId);
                emitHoverClick(null, tripId);
            });
            
            map.on('click', 'trips-points', e => {
                console.log('[MAP_CLICK] Événement clic détecté sur trips-points');
                console.log('[MAP_CLICK] Features disponibles:', e.features);
                const f = e.features && e.features[0];
                const tripId = f && f.properties && f.properties.trip_id || null;
                console.log('[MAP_CLICK] Feature extraite:', f);
                console.log('[MAP_CLICK] Trip ID extrait:', tripId);
                console.log('[MAP_CLICK] Clic sur trajet point:', tripId);
                emitHoverClick(null, tripId);
            });
            
            // Ajouter les événements de hover avec debug
            map.on('mousemove', 'trips-line', e => {
                console.log('[MAP_HOVER] Événement mousemove sur trips-line détecté');
                console.log('[MAP_HOVER] Features:', e.features);
                const f = e.features && e.features[0];
                const tripId = f && f.properties && f.properties.trip_id || null;
                console.log('[MAP_HOVER] Trip ID extrait:', tripId);
                if (tripId) {
                    console.log('[MAP_HOVER] Hover sur ligne:', tripId);
                    map.getCanvas().style.cursor = 'pointer';
                } else {
                    console.log('[MAP_HOVER] Aucun trip ID trouvé');
                }
                emitHoverClick(tripId, null);
            });
            
            map.on('mousemove', 'trips-points', e => {
                const f = e.features && e.features[0];
                const tripId = f && f.properties && f.properties.trip_id || null;
                if (tripId) {
                    console.log('[MAP_HOVER] Hover sur point:', tripId);
                    map.getCanvas().style.cursor = 'pointer';
                }
                emitHoverClick(tripId, null);
            });
            
            // Réinitialiser le curseur quand on quitte les layers
            map.on('mouseleave', 'trips-line', () => {
                map.getCanvas().style.cursor = '';
                emitHoverClick(null, null);
            });
            
            map.on('mouseleave', 'trips-points', () => {
                map.getCanvas().style.cursor = '';
                emitHoverClick(null, null);
            });
        }
    });
}
