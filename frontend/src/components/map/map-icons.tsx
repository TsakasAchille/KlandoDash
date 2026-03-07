import L from "leaflet";

export const popupStyles = `
  .leaflet-popup-content-wrapper {
    background-color: rgba(8, 28, 54, 0.95) !important;
    backdrop-filter: blur(8px);
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid rgba(235, 195, 63, 0.2) !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3) !important;
  }
  .leaflet-popup-content {
    color: white !important;
    margin: 12px !important;
    font-family: system-ui, -apple-system, sans-serif !important;
  }
  .leaflet-container { background: #f8fafc !important; }
  @keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
  }
`;

export const POLYLINE_COLORS = [
  "#EBC33F", "#3B82F6", "#22C55E", "#EF4444", "#A855F7", "#F97316", 
  "#06B6D4", "#EC4899", "#84CC16", "#6366F1", "#14B8A6", "#F59E0B",
];

export const createTripIcon = (color: string, isSelected: boolean) =>
  L.divIcon({
    className: "custom-trip-marker",
    html: `<div style="background-color: ${color}; width: ${isSelected ? '16px' : '12px'}; height: ${isSelected ? '16px' : '12px'}; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3); ${isSelected ? 'transform: scale(1.2); box-shadow: 0 0 0 4px rgba(235, 195, 63, 0.3);' : ''}"></div>`,
    iconSize: isSelected ? [16, 16] : [12, 12],
    iconAnchor: isSelected ? [8, 8] : [6, 6],
  });

export const createRequestStartIcon = (isSelected: boolean) =>
  L.divIcon({
    className: "custom-request-start",
    html: `<div style="background-color: #22C55E; width: ${isSelected ? '18px' : '14px'}; height: ${isSelected ? '18px' : '14px'}; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 15px rgba(34, 197, 94, 0.6); display: flex; align-items: center; justify-content: center; ${isSelected ? 'animation: pulse 2s infinite;' : ''}"><div style="width: 4px; height: 4px; background: white; border-radius: 50%;"></div></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

export const createRequestEndIcon = (isSelected: boolean) =>
  L.divIcon({
    className: "custom-request-end",
    html: `<div style="background-color: #EF4444; width: ${isSelected ? '18px' : '14px'}; height: ${isSelected ? '18px' : '14px'}; border-radius: 3px; border: 3px solid white; box-shadow: 0 0 15px rgba(239, 68, 68, 0.6); transform: rotate(45deg); display: flex; align-items: center; justify-content: center; ${isSelected ? 'animation: pulse 2s infinite;' : ''}"><div style="width: 4px; height: 4px; background: white; transform: rotate(-45deg);"></div></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
