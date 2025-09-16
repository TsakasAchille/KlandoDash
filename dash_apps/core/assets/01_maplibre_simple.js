// Robust MapLibre bootstrap for Dash: dash-renderer mounts layout AFTER DOMContentLoaded.
// We wait for the #maplibre-map element to appear, then ensure MapLibre GL JS is loaded, then init once.

const MAP_CONTAINER_ID = 'maplibre-map';
let mapInitStarted = false;
let mapInstance = null; // shared reference

function ensureMapLibreLoaded(callback) {
    console.log('[MAPLIBRE_DEBUG] Vérification MapLibre, typeof:', typeof maplibregl);
    console.log('[MAPLIBRE_DEBUG] User Agent:', navigator.userAgent);
    console.log('[MAPLIBRE_DEBUG] Location:', window.location.href);
    
    if (typeof maplibregl !== 'undefined') {
        console.log('[MAPLIBRE_DEBUG] MapLibre déjà disponible');
        callback();
        return;
    }
    
    const existing = document.querySelector('script[data-maplibre-gl]');
    if (existing) {
        console.log('[MAPLIBRE_DEBUG] Script MapLibre en cours de chargement');
        existing.addEventListener('load', callback, { once: true });
        return;
    }
    
    console.log('[MAPLIBRE_DEBUG] Chargement de MapLibre depuis CDN...');
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js';
    script.async = true;
    script.defer = true;
    script.setAttribute('data-maplibre-gl', 'true');
    
    script.onload = function() {
        console.log('[MAPLIBRE_DEBUG] MapLibre chargé avec succès depuis CDN');
        callback();
    };
    
    script.onerror = function () {
        console.error('[MAPLIBRE_DEBUG] Échec du chargement de maplibre-gl.js depuis CDN');
        console.error('[MAPLIBRE_DEBUG] Tentative de fallback...');
        
        // Essayer un CDN alternatif
        const fallbackScript = document.createElement('script');
        fallbackScript.src = 'https://cdn.jsdelivr.net/npm/maplibre-gl@4.7.1/dist/maplibre-gl.js';
        fallbackScript.onload = function() {
            console.log('[MAPLIBRE_DEBUG] MapLibre chargé depuis CDN fallback');
            callback();
        };
        fallbackScript.onerror = function() {
            console.error('[MAPLIBRE_DEBUG] Échec total du chargement MapLibre');
        };
        document.head.appendChild(fallbackScript);
    };
    
    document.head.appendChild(script);
}

function tryInitMap() {
    console.log('[MAPLIBRE_DEBUG] tryInitMap() appelé');
    
    const container = document.getElementById(MAP_CONTAINER_ID);
    if (!container) {
        console.log('[MAPLIBRE_DEBUG] Container pas encore disponible');
        return;
    }
    
    console.log('[MAPLIBRE_DEBUG] Container trouvé:', container.id);
    
    // Vérifier si le container est visible et a des dimensions
    const rect = container.getBoundingClientRect();
    console.log('[MAPLIBRE_DEBUG] Dimensions container:', {
        width: rect.width,
        height: rect.height,
        top: rect.top,
        left: rect.left
    });
    
    // Vérifier les styles CSS
    const computedStyle = window.getComputedStyle(container);
    console.log('[MAPLIBRE_DEBUG] Styles container:', {
        display: computedStyle.display,
        visibility: computedStyle.visibility,
        position: computedStyle.position,
        width: computedStyle.width,
        height: computedStyle.height
    });
    
    if (rect.width === 0 || rect.height === 0) {
        // Éviter les retries infinis - limiter à 5 tentatives max
        if (!tryInitMap.retryCount) tryInitMap.retryCount = 0;
        tryInitMap.retryCount++;
        
        if (tryInitMap.retryCount <= 5) {
            console.log('[MAPLIBRE_DEBUG] Container pas encore dimensionné, retry', tryInitMap.retryCount, '/5 dans 500ms');
            setTimeout(tryInitMap, 500); // Augmenté de 200ms à 500ms
        } else {
            console.warn('[MAPLIBRE_DEBUG] Abandon après 5 tentatives - container toujours pas dimensionné');
            mapInitStarted = false;
        }
        return;
    }
    
    // Réinitialiser le compteur de retry si on arrive ici
    tryInitMap.retryCount = 0;
    console.log('[MAPLIBRE_DEBUG] Container prêt, dimensions OK');
    
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
        console.log('[MAPLIBRE_DEBUG] Script chargé, création de la carte...');
        
        // Vérifier WebGL avant d'initialiser
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        console.log('[MAPLIBRE_DEBUG] WebGL disponible:', !!gl);
        if (!gl) {
            console.error('[MAPLIBRE_DEBUG] WebGL non disponible - la carte ne peut pas fonctionner');
            mapInitStarted = false;
            return;
        }
        
        // Vérifier une dernière fois que le container existe toujours
        if (!document.getElementById(MAP_CONTAINER_ID)) {
            console.warn('[MAPLIBRE_DEBUG] Container disparu pendant le chargement');
            mapInitStarted = false;
            return;
        }
        
        // Utiliser un style par défaut si pas de data-style-url
        let styleUrl = container.getAttribute('data-style-url');
        if (!styleUrl) {
            styleUrl = 'https://demotiles.maplibre.org/style.json';
            console.log('[MAPLIBRE_DEBUG] Utilisation du style par défaut:', styleUrl);
        } else {
            styleUrl = container.getAttribute('data-style-url');
            const apiKey = container.getAttribute('data-api-key');
            
            // Vérifier si l'URL contient déjà une clé API
            if (styleUrl.includes('api_key=')) {
                console.log('[MAPLIBRE_DEBUG] Style URL contient déjà une clé API:', styleUrl.replace(/api_key=[^&]+/, 'api_key=HIDDEN'));
            } else if (apiKey) {
                styleUrl = styleUrl + '?api_key=' + apiKey;
                console.log('[MAPLIBRE_DEBUG] Style du container avec API key depuis env:', styleUrl.replace(apiKey, 'HIDDEN'));
            } else {
                console.log('[MAPLIBRE_DEBUG] Style du container sans API key:', styleUrl);
            }
        }
        
        console.log('[MAPLIBRE_DEBUG] Création de l\'instance MapLibre...');
        
        try {
            mapInstance = new maplibregl.Map({
                container: MAP_CONTAINER_ID,
                style: styleUrl,
                center: [2.3522, 48.8566], // Paris par défaut
                zoom: 10,
                preserveDrawingBuffer: true,
                failIfMajorPerformanceCaveat: false // Accepter même avec performance dégradée
            });
            
            console.log('[MAPLIBRE_DEBUG] Instance MapLibre créée avec succès');
            
            mapInstance.on('load', function() {
                console.log('[MAPLIBRE_DEBUG] Carte chargée avec succès - événement load déclenché');
                setupTripLayersAndEvents(mapInstance);
            });
            
            mapInstance.on('error', function(e) {
                console.error('[MAPLIBRE_DEBUG] Erreur carte:', e);
                console.error('[MAPLIBRE_DEBUG] Détails erreur:', e.error);
                console.log('[MAPLIBRE_DEBUG] Style URL actuel:', styleUrl);
                
                // Vérifier si c'est une erreur CORS avec le style Klando
                const errorMessage = e.error ? e.error.message || e.error.toString() : '';
                const isCorsError = errorMessage.includes('Failed to fetch') ||
                    errorMessage.includes('CORS') ||
                    errorMessage.includes('Access-Control-Allow-Origin') ||
                    (e.error && e.error.name === 'TypeError' && errorMessage.includes('fetch'));
                
                console.log('[MAPLIBRE_DEBUG] Est une erreur CORS:', isCorsError);
                console.log('[MAPLIBRE_DEBUG] Style Klando:', styleUrl.includes('geo.klando-carpool.com'));
                
                if (isCorsError && styleUrl.includes('geo.klando-carpool.com')) {
                    console.log('[MAPLIBRE_DEBUG] ✅ CORS détecté avec Klando - basculement vers style par défaut');
                    mapInitStarted = false;
                    
                    // Détruire l'instance actuelle
                    if (mapInstance && !mapInstance._removed) {
                        mapInstance.remove();
                        mapInstance = null;
                    }
                    
                    // Réessayer avec le style par défaut
                    setTimeout(function() {
                        initMapWithDefaultStyle();
                    }, 500);
                } else {
                    console.log('[MAPLIBRE_DEBUG] Erreur non-CORS ou style différent - fallback minimal');
                    mapInitStarted = false;
                    // Tentative de fallback avec style minimal pour autres erreurs
                    if (styleUrl !== 'data:application/json,{"version":8,"sources":{},"layers":[]}') {
                        console.log('[MAPLIBRE_DEBUG] Tentative avec style minimal...');
                        setTimeout(function() {
                            initMapWithFallback();
                        }, 1000);
                    }
                }
            });
            
            mapInstance.on('styledata', function() {
                console.log('[MAPLIBRE_DEBUG] Style chargé');
            });
            
            mapInstance.on('sourcedata', function(e) {
                console.log('[MAPLIBRE_DEBUG] Source data:', e.sourceId, e.isSourceLoaded);
            });
            
            // Forcer un resize après initialisation
            setTimeout(function() {
                if (mapInstance && !mapInstance._removed) {
                    mapInstance.resize();
                    console.log('[MAPLIBRE_DEBUG] Resize post-initialisation');
                }
            }, 500);
            
        } catch (error) {
            console.error('[MAPLIBRE_DEBUG] Erreur lors de la création de l\'instance:', error);
            mapInitStarted = false;
            
            // Fallback avec style minimal
            setTimeout(function() {
                initMapWithFallback();
            }, 1000);
        }
        
    });
}

// Fonction de fallback avec style par défaut MapLibre
function initMapWithDefaultStyle() {
    console.log('[MAPLIBRE_DEBUG] Initialisation avec style par défaut MapLibre (fallback CORS)');
    
    const container = document.getElementById(MAP_CONTAINER_ID);
    if (!container) {
        console.error('[MAPLIBRE_DEBUG] Container introuvable pour fallback style par défaut');
        return;
    }
    
    mapInitStarted = true;
    
    try {
        mapInstance = new maplibregl.Map({
            container: MAP_CONTAINER_ID,
            style: 'https://demotiles.maplibre.org/style.json', // Style par défaut sans CORS
            center: [2.3522, 48.8566],
            zoom: 10,
            preserveDrawingBuffer: true,
            failIfMajorPerformanceCaveat: false
        });
        
        console.log('[MAPLIBRE_DEBUG] Carte avec style par défaut créée avec succès');
        
        mapInstance.on('load', function() {
            console.log('[MAPLIBRE_DEBUG] Carte par défaut chargée avec succès');
            setupTripLayersAndEvents(mapInstance);
            
            // Afficher un message à l'utilisateur
            const messageDiv = document.createElement('div');
            messageDiv.style.cssText = `
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(33, 150, 243, 0.9);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                z-index: 1000;
                max-width: 300px;
            `;
            messageDiv.innerHTML = 'Carte avec style par défaut - Style personnalisé indisponible (CORS)';
            container.appendChild(messageDiv);
            
            // Masquer le message après 5 secondes
            setTimeout(function() {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 5000);
        });
        
        mapInstance.on('error', function(e) {
            console.error('[MAPLIBRE_DEBUG] Erreur même avec style par défaut:', e);
            // En dernier recours, utiliser le style minimal
            setTimeout(function() {
                initMapWithFallback();
            }, 1000);
        });
        
    } catch (error) {
        console.error('[MAPLIBRE_DEBUG] Erreur lors de la création avec style par défaut:', error);
        setTimeout(function() {
            initMapWithFallback();
        }, 1000);
    }
}

// Fonction de fallback avec style minimal
function initMapWithFallback() {
    console.log('[MAPLIBRE_DEBUG] Initialisation fallback avec style minimal');
    
    const container = document.getElementById(MAP_CONTAINER_ID);
    if (!container) {
        console.error('[MAPLIBRE_DEBUG] Container introuvable pour fallback');
        return;
    }
    
    mapInitStarted = true;
    
    try {
        // Style minimal sans sources externes
        const minimalStyle = {
            "version": 8,
            "sources": {},
            "layers": [{
                "id": "background",
                "type": "background",
                "paint": {
                    "background-color": "#f0f0f0"
                }
            }]
        };
        
        mapInstance = new maplibregl.Map({
            container: MAP_CONTAINER_ID,
            style: minimalStyle,
            center: [2.3522, 48.8566],
            zoom: 10,
            preserveDrawingBuffer: true,
            failIfMajorPerformanceCaveat: false
        });
        
        console.log('[MAPLIBRE_DEBUG] Carte fallback créée avec style minimal');
        
        mapInstance.on('load', function() {
            console.log('[MAPLIBRE_DEBUG] Carte fallback chargée avec succès');
            // Afficher un message à l'utilisateur
            const messageDiv = document.createElement('div');
            messageDiv.style.cssText = `
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(255, 255, 255, 0.9);
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                z-index: 1000;
                max-width: 300px;
            `;
            messageDiv.innerHTML = 'Carte en mode dégradé - Certaines fonctionnalités peuvent être limitées';
            container.appendChild(messageDiv);
        });
        
        mapInstance.on('error', function(e) {
            console.error('[MAPLIBRE_DEBUG] Erreur même en mode fallback:', e);
            showMapError(container);
        });
        
    } catch (error) {
        console.error('[MAPLIBRE_DEBUG] Erreur critique même en fallback:', error);
        showMapError(container);
    }
}

// Afficher un message d'erreur dans le container
function showMapError(container) {
    console.log('[MAPLIBRE_DEBUG] Affichage du message d\'erreur');
    container.innerHTML = `
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            color: #6c757d;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
        ">
            <div>
                <h4>Carte non disponible</h4>
                <p>Impossible de charger la carte MapLibre.<br>
                Vérifiez votre connexion internet et rechargez la page.</p>
                <button onclick="location.reload()" style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                ">Recharger</button>
            </div>
        </div>
    `;
}

// Diagnostic complet de l'environnement
function runEnvironmentDiagnostics() {
    console.log('[MAPLIBRE_DEBUG] === DIAGNOSTIC ENVIRONNEMENT ===');
    console.log('[MAPLIBRE_DEBUG] User Agent:', navigator.userAgent);
    console.log('[MAPLIBRE_DEBUG] URL actuelle:', window.location.href);
    console.log('[MAPLIBRE_DEBUG] Protocole:', window.location.protocol);
    console.log('[MAPLIBRE_DEBUG] Host:', window.location.host);
    
    // Test WebGL
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    console.log('[MAPLIBRE_DEBUG] WebGL supporté:', !!gl);
    if (gl) {
        console.log('[MAPLIBRE_DEBUG] WebGL Vendor:', gl.getParameter(gl.VENDOR));
        console.log('[MAPLIBRE_DEBUG] WebGL Renderer:', gl.getParameter(gl.RENDERER));
        console.log('[MAPLIBRE_DEBUG] WebGL Version:', gl.getParameter(gl.VERSION));
    }
    
    // Test des ressources réseau
    console.log('[MAPLIBRE_DEBUG] Test de connectivité...');
    fetch('https://demotiles.maplibre.org/style.json', { method: 'HEAD' })
        .then(response => {
            console.log('[MAPLIBRE_DEBUG] Connectivité MapLibre demo:', response.status);
        })
        .catch(error => {
            console.error('[MAPLIBRE_DEBUG] Erreur connectivité MapLibre demo:', error);
        });
    
    // Vérifier les variables globales
    console.log('[MAPLIBRE_DEBUG] maplibregl disponible:', typeof maplibregl !== 'undefined');
    if (typeof maplibregl !== 'undefined') {
        console.log('[MAPLIBRE_DEBUG] Version MapLibre:', maplibregl.version);
        console.log('[MAPLIBRE_DEBUG] Supported:', maplibregl.supported());
    }
    
    console.log('[MAPLIBRE_DEBUG] === FIN DIAGNOSTIC ===');
}

// Observe DOM changes to detect when Dash mounts #maplibre-map
function watchForContainer() {
    // initial quick check
    tryInitMap();
    
    // MutationObserver optimisé pour détecter l'ajout du container de carte
    const observer = new MutationObserver(function (mutations) {
        // Si la carte est déjà initialisée, arrêter l'observation
        if (mapInstance && !mapInstance._removed) {
            observer.disconnect();
            console.log('[MAPLIBRE] Observer déconnecté - carte déjà initialisée');
            return;
        }
        
        let shouldCheck = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Vérifier si des noeuds ont été ajoutés qui pourraient contenir notre container
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.id === MAP_CONTAINER_ID || 
                            (node.querySelector && node.querySelector('#' + MAP_CONTAINER_ID))) {
                            shouldCheck = true;
                        }
                    }
                });
            }
        });
        
        if (shouldCheck) {
            // Petit délai pour laisser Dash finir le rendu
            setTimeout(tryInitMap, 100);
        }
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: false  // Pas besoin de surveiller les attributs
    });
    
    // Vérification périodique réduite pour les cas où MutationObserver rate quelque chose
    let periodicCheckCount = 0;
    const maxPeriodicChecks = 10; // Limiter à 10 vérifications max
    
    const periodicCheck = setInterval(function() {
        periodicCheckCount++;
        
        // Arrêter après le nombre max de vérifications ou si la carte est initialisée
        if (periodicCheckCount >= maxPeriodicChecks || (mapInstance && !mapInstance._removed)) {
            clearInterval(periodicCheck);
            console.log('[MAPLIBRE] Vérifications périodiques arrêtées après', periodicCheckCount, 'tentatives');
            return;
        }
        
        const container = document.getElementById(MAP_CONTAINER_ID);
        if (container && (!mapInstance || mapInstance.getContainer() !== container || mapInstance._removed)) {
            console.log('[MAPLIBRE] Vérification périodique #' + periodicCheckCount + ' - tentative d\'initialisation');
            tryInitMap();
        }
    }, 5000); // Réduit de 2s à 5s pour moins de fréquence
    
    // Nettoyer les vérifications périodiques après 60 secondes (augmenté de 30s)
    setTimeout(function() {
        clearInterval(periodicCheck);
        console.log('[MAPLIBRE] Timeout des vérifications périodiques après 60s');
    }, 60000);
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
    console.log('[MAPLIBRE_DEBUG] DOM Content Loaded - lancement du diagnostic');
    
    // Lancer le diagnostic complet de l'environnement
    runEnvironmentDiagnostics();
    
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
