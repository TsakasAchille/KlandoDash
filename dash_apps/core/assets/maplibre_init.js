// Initializes MapLibre map for the stats page. Loaded automatically by Dash via the assets folder.
(function () {
  const DEMO_STYLE = 'https://demotiles.maplibre.org/globe.json';
  function isProxied(url) {
    try {
      const u = new URL(url, window.location.origin);
      return u.pathname === '/proxy/map' && (u.search || '').includes('u=');
    } catch (e) {
      return typeof url === 'string' && url.indexOf('/proxy/map?u=') !== -1;
    }
  }

  function viaProxy(url) {
    try {
      if (isProxied(url)) return url; // avoid double proxying
      const enc = encodeURIComponent(url);
      return `${window.location.origin}/proxy/map?u=${enc}`;
    } catch (e) {
      if (isProxied(url)) return url;
      return `${window.location.origin}/proxy/map?u=${encodeURIComponent(url)}`;
    }
  }

  function shouldProxy(url) {
    try {
      const u = new URL(url, window.location.origin);
      // proxy if cross-origin to geo.klando-carpool.com or other remote hosts
      const isCrossOrigin = (u.origin !== window.location.origin);
      const isGeo = /(^|\.)geo\.klando-carpool\.com$/i.test(u.hostname);
      return isCrossOrigin && (isGeo);
    } catch (e) {
      return typeof url === 'string' && url.startsWith('http');
    }
  }

  function appendKey(url, apiKey) {
    try {
      if (!apiKey) return url;
      const u = new URL(url, window.location.origin);
      if ((u.protocol === 'http:' || u.protocol === 'https:') && !u.searchParams.has('api_key') && !u.searchParams.has('key')) {
        // Prefer 'api_key' as requested by backend
        u.searchParams.set('api_key', apiKey);
      }
      const out = u.toString();
      if (window && window.console) {
        try {
          console.debug('[MapLibre][appendKey]', { in: url, out });
        } catch (_) {}
      }
      return out;
    } catch (e) {
      return url;
    }
  }

  function initMap(container, attempt = 0) {
    try {
      if (container.dataset.mapInited === '1') {
        console.debug('[MapLibre][initMap] already inited, skip', container.id || container.className);
        return; // guard
      }
      const styleUrl = container.getAttribute('data-style-url') || DEMO_STYLE;
      const apiKey = container.getAttribute('data-api-key');
      const initialStyle = appendKey(styleUrl, apiKey);
      console.debug('[MapLibre][initMap] start', { attempt, container: container.id || container.className, styleUrl, apiKey_present: !!apiKey });
      if (!window.maplibregl) {
        if (attempt < 20) {
          // Retry until external script has loaded
          console.debug('[MapLibre][initMap] maplibregl not yet loaded, retrying...', attempt + 1);
          return setTimeout(() => initMap(container, attempt + 1), 200);
        }
        console.error('[MapLibre] maplibregl is not loaded');
        return;
      }

      const map = new maplibregl.Map({
        container: container,
        // Load the provided style (or demo) with selective proxying
        style: shouldProxy(initialStyle) ? viaProxy(initialStyle) : initialStyle,
        center: [-14.452, 14.497], // default: Senegal
        zoom: 5,
        cooperativeGestures: true,
        transformRequest: (url, resourceType) => {
          let finalUrl = url;
          try {
            if (isProxied(url)) {
              // Decode inner target, append key there, then rebuild proxied URL
              const u = new URL(url, window.location.origin);
              const inner = u.searchParams.get('u');
              if (inner) {
                const decodedInner = decodeURIComponent(inner);
                const innerWithKey = appendKey(decodedInner, apiKey);
                if (innerWithKey !== decodedInner) {
                  u.searchParams.set('u', encodeURIComponent(innerWithKey));
                }
                finalUrl = u.toString();
              }
            } else {
              const withKey = appendKey(url, apiKey);
              finalUrl = (shouldProxy(withKey) ? viaProxy(withKey) : withKey);
            }
          } catch (e) {
            // Fallback: keep original url
            finalUrl = url;
          }
          // Ensure absolute URL (workers may not resolve '/')
          try { finalUrl = new URL(finalUrl, window.location.origin).toString(); } catch (_) {}
          console.debug('[MapLibre][transformRequest]', { resourceType, in: url, out: finalUrl });
          return { url: finalUrl };
        }
      });

      // expose for quick inspection
      try { container.__map = map; } catch (_) {}

      map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
      map.on('load', () => {
        try { map.resize(); } catch (e) {}
        console.debug('[MapLibre][event] load');
        // If a route GeoJSON is already present on the container, render it
        try {
          const dataAttr = container.getAttribute('data-geojson');
          if (dataAttr) {
            const gj = JSON.parse(dataAttr);
            ensureRouteLayer(map, gj);
          }
        } catch (e) { console.debug('[MapLibre] no initial geojson'); }
      });
      map.on('error', (e) => {
        const err = e && e.error ? e.error : e;
        console.error('[MapLibre] Map error', err);
        const msgText = (err && err.message) ? String(err.message) : '';
        const isBenign = /sprite|glyph|tile/i.test(msgText) || /404/.test(msgText || '');
        if (isBenign) return; // ignore common non-fatal fetch errors
        if (!container.querySelector('.maplibre-error')) {
          const msg = document.createElement('div');
          msg.className = 'maplibre-error';
          msg.style.cssText = 'position:absolute;top:8px;left:8px;background:#fff3f3;color:#c00;padding:8px 12px;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.1);z-index:2;font-size:12px;';
          msg.textContent = 'Erreur de chargement du style/couches de la carte.';
          container.appendChild(msg);
        }
      });
      // You can add more controls here if needed
      container.dataset.mapInited = '1';
      console.debug('[MapLibre][initMap] done', container.id || container.className);
    } catch (e) {
      console.error('[MapLibre] Initialization error', e);
    }
  }

  function ensureRouteLayer(map, geojson) {
    try {
      const sourceId = 'route-geojson';
      if (map.getSource(sourceId)) {
        map.getSource(sourceId).setData(geojson);
        try { fitToGeojson(map, geojson); } catch (_) {}
        return;
      }
      map.addSource(sourceId, { type: 'geojson', data: geojson });
      map.addLayer({
        id: 'route-line',
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': '#4281ec',
          'line-width': 4,
          'line-opacity': 0.85
        }
      });
      // Start/End points for visibility if present
      map.addLayer({
        id: 'route-points',
        type: 'circle',
        source: sourceId,
        filter: ['any', ['==', ['geometry-type'], 'Point']],
        paint: {
          'circle-radius': 4,
          'circle-color': ['case', ['==', ['get', 'role'], 'start'], '#2ecc71', '#e67e22'],
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        }
      });
      // Fit bounds if possible
      try { fitToGeojson(map, geojson); } catch (_) {}
    } catch (e) {
      console.error('[MapLibre] ensureRouteLayer error', e);
    }
  }

  function fitToGeojson(map, geojson) {
    const bbox = computeBbox(geojson);
    if (bbox) {
      map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]], { padding: 40, duration: 300 });
    }
  }

  function computeBbox(geojson) {
    try {
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      const update = (x, y) => { if (x < minX) minX = x; if (y < minY) minY = y; if (x > maxX) maxX = x; if (y > maxY) maxY = y; };
      const coordsWalk = (geom) => {
        const type = geom.type;
        const coords = geom.coordinates;
        if (type === 'Point') { update(coords[0], coords[1]); }
        else if (type === 'LineString' || type === 'MultiPoint') { coords.forEach(c => update(c[0], c[1])); }
        else if (type === 'MultiLineString' || type === 'Polygon') { coords.forEach(r => r.forEach(c => update(c[0], c[1]))); }
        else if (type === 'MultiPolygon') { coords.forEach(p => p.forEach(r => r.forEach(c => update(c[0], c[1])))); }
        else if (type === 'GeometryCollection') { (geom.geometries || []).forEach(g => coordsWalk(g)); }
      };
      if (geojson.type === 'Feature') coordsWalk(geojson.geometry);
      else if (geojson.type === 'FeatureCollection') (geojson.features || []).forEach(f => coordsWalk(f.geometry));
      else coordsWalk(geojson);
      if (minX === Infinity) return null;
      return [minX, minY, maxX, maxY];
    } catch (e) { return null; }
  }

  function onReady() {
    // Backward compatibility: init specific ID if present
    const legacy = document.getElementById('maplibre-stats-map');
    if (legacy) initMap(legacy);

    // General: initialize all containers with class
    const initAll = () => {
      const nodes = document.querySelectorAll('.maplibre-container');
      console.debug('[MapLibre][onReady] found containers:', nodes.length);
      nodes.forEach((el) => {
        if (legacy && el === legacy) return; // avoid double init
        initMap(el);
      });
    };

    initAll();

    // Observe future dynamic additions (Dash renders async)
    const observer = new MutationObserver((mutations) => {
      let needsInitAll = false;
      for (const m of mutations) {
        if (m.type === 'childList') needsInitAll = true;
        if (m.type === 'attributes' && m.target && m.target.classList && m.target.classList.contains('maplibre-container')) {
          if (m.attributeName === 'data-geojson' && m.target.__map && m.target.getAttribute('data-geojson')) {
            try {
              const gj = JSON.parse(m.target.getAttribute('data-geojson'));
              ensureRouteLayer(m.target.__map, gj);
            } catch (_) {}
          }
        }
      }
      if (needsInitAll) initAll();
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-geojson'] });
    console.debug('[MapLibre][onReady] observer attached');
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(onReady, 0);
  } else {
    document.addEventListener('DOMContentLoaded', onReady);
  }
})();
