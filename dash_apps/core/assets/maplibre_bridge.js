/**
 * MapLibre Bridge - Interface entre Dash et MapLibre GL JS
 * Gère les événements de la carte et la communication avec les callbacks Dash
 */

// Namespace global pour les événements de carte
window.__map_events = {
    hover_trip_id: null,
    click_trip_id: null,
    last_update: Date.now()
};

// Fonction de polling pour les callbacks Dash clientside
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.mapbridge = window.dash_clientside.mapbridge || {};

if (!window.dash_clientside.mapbridge.poll) {
    window.dash_clientside.mapbridge.poll = function(n_intervals) {
        const events = window.__map_events;
        const now = Date.now();
        
        // Retourner les événements actuels
        return [
            events.hover_trip_id,
            events.click_trip_id
        ];
    };
}

// Fonction utilitaire pour mettre à jour les événements
window.updateMapEvents = function(hoverTripId, clickTripId) {
    window.__map_events.hover_trip_id = hoverTripId;
    window.__map_events.click_trip_id = clickTripId;
    window.__map_events.last_update = Date.now();
};

console.log('[MAP_BRIDGE] MapLibre bridge initialisé');
