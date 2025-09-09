// MapLibre initializer for test page
(function () {
  const DEMO_STYLE = 'https://demotiles.maplibre.org/globe.json';

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

  function initTestMap(container, attempt = 0) {
    try {
      if (!container) return;
      if (!window.maplibregl) {
        if (attempt < 10) return setTimeout(() => initTestMap(container, attempt + 1), 200);
        console.warn('[TestMap] MapLibre GL JS not loaded');
        return;
      }
      
      const styleUrl = container.getAttribute('data-style-url') || DEMO_STYLE;
      const apiKey = container.getAttribute('data-api-key');
      const finalStyle = appendKey(styleUrl, apiKey);
      
      console.log('[TestMap] Initializing with style:', finalStyle);
      
      const map = new maplibregl.Map({
        container: container,
        style: finalStyle,
        center: [2.3522, 48.8566], // Paris
        zoom: 10,
        cooperativeGestures: false
      });
      
      // Add navigation controls
      map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
      
      // Enable scroll zoom
      map.scrollZoom.enable();
      
      // Add load event
      map.on('load', () => {
        console.log('[TestMap] Map loaded successfully');
        container.style.border = '2px solid #28a745'; // Green border when loaded
      });
      
      // Handle errors
      map.on('error', (e) => {
        console.error('[TestMap] Map error:', e);
        container.style.border = '2px solid #dc3545'; // Red border on error
      });
      
      // Store map instance
      window.testMapInstance = map;
      
    } catch (error) {
      console.error('[TestMap] Initialization error:', error);
    }
  }

  function onReady() {
    console.log('[TestMap] DOM ready, looking for test container...');
    // Initialize test map container
    const testContainer = document.getElementById('test-maplibre');
    if (testContainer) {
      console.log('[TestMap] Found test container, initializing...');
      initTestMap(testContainer);
    } else {
      console.warn('[TestMap] Test container not found, retrying in 500ms...');
      setTimeout(onReady, 500);
    }
  }

  // Multiple initialization attempts
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(onReady, 100);
  } else {
    document.addEventListener('DOMContentLoaded', onReady);
  }
  
  // Also try when window loads
  window.addEventListener('load', () => {
    setTimeout(onReady, 200);
  });
})();
