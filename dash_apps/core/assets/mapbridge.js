// Dash clientside bridge to poll map events
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  mapbridge: {
    poll: function(n_intervals) {
      try {
        const ev = window.__map_events || {};
        const hover = ev.hoverTripId || null;
        const click = ev.clickTripId || null;
        const viewDriverId = ev.viewDriverId || null;
        const viewPassengerId = ev.viewPassengerId || null;
        return [hover, click, viewDriverId, viewPassengerId];
      } catch (e) {
        return [null, null, null, null];
      }
    }
  }
});
