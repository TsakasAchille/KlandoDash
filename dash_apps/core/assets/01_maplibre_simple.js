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
    if (mapInitStarted) return; // guard against multiple calls
    const container = document.getElementById(MAP_CONTAINER_ID);
    if (!container) return; // not yet mounted by Dash
    const styleUrl = container.getAttribute('data-style-url');
    if (!styleUrl) {
        console.warn('[MAPLIBRE] data-style-url manquant sur #', MAP_CONTAINER_ID);
        return;
    }
    mapInitStarted = true;
    ensureMapLibreLoaded(function () {
        try {
            const map = new maplibregl.Map({
                container: MAP_CONTAINER_ID,
                style: styleUrl,
                center: [-17.4441, 14.6928],
                zoom: 12
            });
            map.addControl(new maplibregl.NavigationControl());
            // expose for debugging
            window.mapLibreInstance = map;
            mapInstance = map;
            setupTripLayersAndEvents(map);
        } catch (e) {
            mapInitStarted = false; // allow retry on failure
            console.error('[MAPLIBRE] Erreur initialisation carte:', e);
        }
    });
}

// Observe DOM changes to detect when Dash mounts #maplibre-map
function watchForContainer() {
    // initial quick check
    tryInitMap();
    // MutationObserver for robust detection
    const observer = new MutationObserver(function () {
        if (document.getElementById(MAP_CONTAINER_ID)) {
            tryInitMap();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    // safety timeout to disconnect observer after init
    const stopWhenInited = setInterval(function () {
        if (mapInitStarted) {
            observer.disconnect();
            clearInterval(stopWhenInited);
        }
    }, 500);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', watchForContainer);
} else {
    watchForContainer();
}

// --- Integration with Dash callbacks ---
function setupTripLayersAndEvents(map) {
    // Add empty source once; layers added on first update
    function ensureSource() {
        if (!map.getSource('trips')) {
            map.addSource('trips', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
        }
        if (!map.getLayer('trips-line')) {
            map.addLayer({
                id: 'trips-line',
                type: 'line',
                source: 'trips',
                filter: ['==', ['geometry-type'], 'LineString'],
                paint: {
                    'line-width': 4,
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
                    'circle-radius': 5,
                    'circle-color': ['get', 'color'],
                    'circle-stroke-color': '#fff',
                    'circle-stroke-width': 1
                }
            });
        }
    }

    function updateGeoJSON(geojsonText) {
        if (!geojsonText) return;
        try {
            const data = JSON.parse(geojsonText);
            ensureSource();
            const src = map.getSource('trips');
            src.setData(data);
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
    function emitHoverClick(hoverId, clickId) {
        if (typeof window.updateMapEvents === 'function') {
            window.updateMapEvents(hoverId, clickId);
        }
    }
    map.on('mousemove', 'trips-line', e => {
        const f = e.features && e.features[0];
        emitHoverClick(f && f.properties && f.properties.trip_id || null, null);
    });
    map.on('click', 'trips-line', e => {
        const f = e.features && e.features[0];
        emitHoverClick(null, f && f.properties && f.properties.trip_id || null);
    });
    map.on('mousemove', 'trips-points', e => {
        const f = e.features && e.features[0];
        emitHoverClick(f && f.properties && f.properties.trip_id || null, null);
    });
    map.on('click', 'trips-points', e => {
        const f = e.features && e.features[0];
        emitHoverClick(null, f && f.properties && f.properties.trip_id || null);
    });
}
