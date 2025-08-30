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
        console.warn('[MapLibre] Carte initialisée avec un style vide (aucun chargement distant pour l\'instant).');
        console.warn('[MapLibre] On réactivera le style distant (via proxy si besoin) quand l\'API sera prête.');
      });
      map.on('error', (e) => {
        console.error('[MapLibre] Map error', e && e.error ? e.error : e);
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
    const observer = new MutationObserver(() => initAll());
    observer.observe(document.body, { childList: true, subtree: true });
    console.debug('[MapLibre][onReady] observer attached');
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(onReady, 0);
  } else {
    document.addEventListener('DOMContentLoaded', onReady);
  }
})();
