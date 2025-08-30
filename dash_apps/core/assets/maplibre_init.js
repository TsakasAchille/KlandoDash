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
        // Disable cooperative gestures so users don't need to hold Ctrl to scroll-zoom
        cooperativeGestures: false,
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

      // Explicitly enable scroll zoom (should be on by default, but be explicit)
      try { map.scrollZoom.enable(); } catch (_) {}

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
          // Use per-feature color if provided, else default blue
          'line-color': ['coalesce', ['get', 'color'], '#4281ec'],
          'line-width': 4,
          'line-opacity': 0.85
        }
      });
      // Selected highlight layer (drawn above base), filtered by trip_id
      map.addLayer({
        id: 'route-line-selected',
        type: 'line',
        source: sourceId,
        filter: ['==', ['get', 'trip_id'], '__none__'], // initially none selected
        paint: {
          'line-color': ['coalesce', ['get', 'color'], '#ff7f0e'],
          'line-width': 6,
          'line-opacity': 1.0
        }
      });
      // Wide invisible hit layer to enlarge clickable area along the whole polyline
      map.addLayer({
        id: 'route-line-hit',
        type: 'line',
        source: sourceId,
        filter: ['==', ['geometry-type'], 'LineString'],
        paint: {
          'line-color': '#000000',
          'line-opacity': 0.01, // nearly invisible but hit-testable
          'line-width': 24
        }
      });
      // Start/End points for visibility if present
      map.addLayer({
        id: 'route-points',
        type: 'circle',
        source: sourceId,
        filter: ['any', ['==', ['geometry-type'], 'Point']],
        paint: {
          // Support variable bubble size via per-feature 'radius', fallback to 4
          'circle-radius': ['coalesce', ['to-number', ['get', 'radius']], 4],
          // Points inherit the same color as their parent trip when present
          'circle-color': ['coalesce', ['get', 'color'], ['case', ['==', ['get', 'role'], 'start'], '#2ecc71', '#e67e22']],
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff'
        }
      });
      // Center marker source (no visible icon anymore)
      if (!map.getSource('route-center')) {
        map.addSource('route-center', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
      }
      // Interactions: hover feedback only on route hit layer
      try {
        // Car popup logic removed: no HTML builder or server fetch anymore

        var carPopup; // kept for defensive removal only
        var selectedTripId = null;
        // Center icon and its interactions removed: no more 'route-center-symbol'
        map.on('mouseenter', 'route-line-hit', function () { try { map.getCanvas().style.cursor = 'pointer'; } catch (_) {} });
        map.on('mouseleave', 'route-line-hit', function () { try { map.getCanvas().style.cursor = ''; } catch (_) {} });
        map.on('click', 'route-line-hit', function (e) {
          try {
            // Option A: clicking polyline should close any open popup
            try { carPopup && carPopup.remove && carPopup.remove(); } catch (_) {}
            var f = e && e.features && e.features[0];
            var props = f && f.properties ? f.properties : {};
            var tripId = (props && (props.trip_id || props.id || props.tripID)) ? (props.trip_id || props.id || props.tripID) : '';
            // Toggle selection: if already selected, deselect and close popup
            if (selectedTripId && tripId && String(selectedTripId) === String(tripId)) {
              selectedTripId = null;
              try { map.setFilter('route-line-selected', ['==', ['get', 'trip_id'], '__none__']); } catch (_) {}
              try { map.getSource('route-center') && map.getSource('route-center').setData({ type: 'FeatureCollection', features: [] }); } catch (_) {}
              // Publish deselection to Dash
              try { window.__map_events = window.__map_events || {}; window.__map_events.clickTripId = null; } catch (_) {}
              return;
            }

            // Update selected highlight filter
            selectedTripId = tripId || null;
            try { map.setFilter('route-line-selected', ['==', ['get', 'trip_id'], selectedTripId || '__none__']); } catch (_) {}
            // Publish selection to Dash (used by mapbridge.poll)
            try { window.__map_events = window.__map_events || {}; window.__map_events.clickTripId = selectedTripId; } catch (_) {}

            // Compute line midpoint and update center marker source (no visible symbol)
            var midpoint = (function getMid(geom) {
              try {
                var type = geom && geom.type;
                if (type === 'LineString') {
                  var arr = (geom.coordinates || []); var n = arr.length; if (!n) return null; return arr[Math.floor(n / 2)];
                } else if (type === 'MultiLineString') {
                  var first = (geom.coordinates && geom.coordinates[0]) || []; var m = first.length; if (!m) return null; return first[Math.floor(m / 2)];
                } else if (type === 'Feature') {
                  return getMid(geom.geometry);
                }
              } catch (_) {}
              return null;
            })(f && f.geometry);
            if (midpoint && midpoint.length === 2) {
              try {
                var fc = { type: 'FeatureCollection', features: [ { type: 'Feature', properties: { trip_id: selectedTripId }, geometry: { type: 'Point', coordinates: midpoint } } ] };
                map.getSource('route-center') && map.getSource('route-center').setData(fc);
              } catch (_) {}
            }
          } catch (err) { console.warn('[MapLibre] car popup error', err); }
        });
      } catch (_) {}
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
