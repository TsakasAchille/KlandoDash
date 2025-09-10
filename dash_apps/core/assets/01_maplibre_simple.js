// Robust MapLibre bootstrap for Dash: dash-renderer mounts layout AFTER DOMContentLoaded.
// We wait for the #maplibre-map element to appear, then ensure MapLibre GL JS is loaded, then init once.

const MAP_CONTAINER_ID = 'maplibre-map';
let mapInitStarted = false;

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
            console.log('[MAPLIBRE] Carte initialisée');
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
