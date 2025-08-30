// Ensure clientside namespace exists early to avoid race errors before other assets load
(function(){
  if (!window.dash_clientside) {
    window.dash_clientside = {};
  }
  if (!window.dash_clientside.mapbridge) {
    window.dash_clientside.mapbridge = {};
  }
  if (typeof window.dash_clientside.mapbridge.poll !== 'function') {
    // No-op fallback, returns two values to match Dash Outputs
    window.dash_clientside.mapbridge.poll = function(){ return [null, null]; };
  }
})();
