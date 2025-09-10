// Dash clientside bridge to poll map events
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.mapbridge = window.dash_clientside.mapbridge || {};

// Define poll only if not already provided (avoid conflicts with maplibre_bridge.js)
if (!window.dash_clientside.mapbridge.poll) {
  window.dash_clientside.mapbridge.poll = function(n_intervals) {
    try {
      const ev = window.__map_events || {};
      const nu = window.dash_clientside && window.dash_clientside.no_update ? window.dash_clientside.no_update : null;
      // Align with maplibre_bridge.js keys: hover_trip_id, click_trip_id
      const hover = Object.prototype.hasOwnProperty.call(ev, 'hover_trip_id') ? ev.hover_trip_id : nu;
      const click = Object.prototype.hasOwnProperty.call(ev, 'click_trip_id') ? ev.click_trip_id : nu;
      return [hover, click];
    } catch (e) {
      return [null, null];
    }
  };
}
