// Legacy-only MapLibre initializer (neutralized to avoid duplicate init). Loaded by Dash via assets.
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

  function appendKey(url, apiKey) {
    try {
      if (!apiKey) return url;
      const u = new URL(url, window.location.origin);
      if ((u.protocol === 'http:' || u.protocol === 'https:') && !u.searchParams.has('api_key') && !u.searchParams.has('key')) {
        u.searchParams.set('api_key', apiKey);
      }
      return u.toString();
    } catch (e) {
      return url;
    }
  }

  function viaProxy(url) {
    try {
      if (isProxied(url)) return url;
      return `${window.location.origin}/proxy/map?u=${encodeURIComponent(url)}`;
    } catch (e) {
      return `${window.location.origin}/proxy/map?u=${encodeURIComponent(url || '')}`;
    }
  }

  function shouldProxy(url) {
    try {
      const u = new URL(url, window.location.origin);
      const isCrossOrigin = (u.origin !== window.location.origin);
      const isGeo = /(^|\.)geo\.klando-carpool\.com$/i.test(u.hostname);
      return isCrossOrigin && isGeo;
    } catch (e) {
      return typeof url === 'string' && url.startsWith('http');
    }
  }

  function initLegacy(container, attempt = 0) {
    try {
      if (!container) return;
      if (!window.maplibregl) {
        if (attempt < 10) return setTimeout(() => initLegacy(container, attempt + 1), 200);
        return;
      }
      const styleUrl = container.getAttribute('data-style-url') || DEMO_STYLE;
      const apiKey = container.getAttribute('data-api-key');
      const initialStyle = appendKey(styleUrl, apiKey);
      const map = new maplibregl.Map({
        container,
        style: shouldProxy(initialStyle) ? viaProxy(initialStyle) : initialStyle,
        center: [-14.452, 14.497],
        zoom: 5,
        cooperativeGestures: true,
        transformRequest: (url) => {
          let finalUrl = url;
          try {
            if (isProxied(url)) {
              const u = new URL(url, window.location.origin);
              const inner = u.searchParams.get('u');
              if (inner) {
                const decodedInner = decodeURIComponent(inner);
                const innerWithKey = appendKey(decodedInner, apiKey);
                if (innerWithKey !== decodedInner) u.searchParams.set('u', encodeURIComponent(innerWithKey));
                finalUrl = u.toString();
              }
            } else {
              const withKey = appendKey(url, apiKey);
              finalUrl = shouldProxy(withKey) ? viaProxy(withKey) : withKey;
            }
          } catch (_) {}
          try { finalUrl = new URL(finalUrl, window.location.origin).toString(); } catch (_) {}
          return { url: finalUrl };
        }
      });
      map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
      map.on('error', (e) => {
        const err = e && e.error ? e.error : e;
        const msg = (err && err.message) ? String(err.message) : '';
        if (/sprite|glyph|tile/i.test(msg) || /404/.test(msg)) return;
        // Do not show intrusive banners here; core initializer will handle UX.
        console.warn('[MapLibre][legacy] error:', err);
      });
    } catch (_) {}
  }

  function onReady() {
    // Only initialize legacy element if present. Do NOT scan all containers.
    const legacy = document.getElementById('maplibre-stats-map');
    if (legacy) initLegacy(legacy);
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(onReady, 0);
  } else {
    document.addEventListener('DOMContentLoaded', onReady);
  }
})();
