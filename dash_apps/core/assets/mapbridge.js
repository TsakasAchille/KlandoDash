// Dash clientside bridge to poll map events
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  mapbridge: {
    poll: function(n_intervals) {
      try {
        const ev = window.__map_events || {};
        const nu = window.dash_clientside && window.dash_clientside.no_update ? window.dash_clientside.no_update : null;
        const has = (k) => Object.prototype.hasOwnProperty.call(ev, k);
        const hover = has('hoverTripId') ? ev.hoverTripId : nu;
        const click = has('clickTripId') ? ev.clickTripId : nu;
        const viewDriverId = has('viewDriverId') ? ev.viewDriverId : nu;
        const viewPassengerId = has('viewPassengerId') ? ev.viewPassengerId : nu;
        return [hover, click, viewDriverId, viewPassengerId];
      } catch (e) {
        return [null, null, null, null];
      }
    }
  }
});
