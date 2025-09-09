// Dash clientside bridge to poll map events
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.mapbridge = window.dash_clientside.mapbridge || {};

window.dash_clientside.mapbridge.poll = function(n_intervals) {
  try {
    const ev = window.__map_events || {};
    const nu = window.dash_clientside && window.dash_clientside.no_update ? window.dash_clientside.no_update : null;
    const has = (k) => Object.prototype.hasOwnProperty.call(ev, k);
    const hover = has('hoverTripId') ? ev.hoverTripId : nu;
    const click = has('clickTripId') ? ev.clickTripId : nu;
    // Return only two outputs to match Dash callback outputs
    return [hover, click];
  } catch (e) {
    return [null, null];
  }
};
