"""
Optimized polyline renderer for map callbacks using configuration-based approach.
"""
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import polyline as polyline_lib
from dash_apps.utils.callback_logger import CallbackLogger


class MapPolylineRenderer:
    """Configuration-based polyline renderer for map display optimization."""
    
    def __init__(self):
        self.debug_enabled = os.getenv('DEBUG_MAP', 'False').lower() == 'true'
        self.logger = CallbackLogger()
        self.config = self._load_config()
        self.rendering_config = self.config.get('polyline_rendering', {})
        self.data_config = self.config.get('data_extraction', {})
        self.coord_config = self.config.get('coordinate_transformation', {})
        
    def _load_config(self) -> Dict[str, Any]:
        """Load polyline rendering configuration."""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'map_polyline_config.json'
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if self.debug_enabled:
                    self.logger.log_callback("config_loaded", {
                        "config_path": config_path, 
                        "sections_count": len(config)
                    }, status="SUCCESS", extra_info="Map polyline configuration loaded successfully")
                return config
        except Exception as e:
            if self.debug_enabled:
                self.logger.log_callback("config_load_error", {
                    "error": str(e), 
                    "fallback": "default_config"
                }, status="ERROR", extra_info="Failed to load map polyline config, using defaults")
            print(f"[MAP_POLYLINE_RENDERER] Warning: Could not load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback configuration if file loading fails."""
        return {
            "polyline_rendering": {
                "color_palette": ["#4281ec", "#e74c3c", "#27ae60", "#f1c40f"],
                "feature_types": {
                    "route": {"enabled": True, "geometry_type": "LineString"},
                    "start_marker": {"enabled": True, "geometry_type": "Point", "role": "start"},
                    "end_marker": {"enabled": True, "geometry_type": "Point", "role": "end"},
                    "car_marker": {"enabled": True, "geometry_type": "Point", "role": "car"}
                },
                "performance": {"max_trips_per_render": 50}
            }
        }
    
    def get_color_palette(self) -> List[str]:
        """Get configured color palette."""
        return self.rendering_config.get('color_palette', ["#4281ec"])
    
    def extract_trip_data(self, trip: Any) -> Dict[str, Any]:
        """Extract trip data using configured field mappings."""
        if isinstance(trip, dict):
            fields = self.data_config.get('dict_fields', {})
            trip_data = {key: trip.get(field) for key, field in fields.items()}
        else:
            fields = self.data_config.get('object_fields', {})
            trip_data = {key: getattr(trip, field, None) for key, field in fields.items()}
        
        if self.debug_enabled:
            self.logger.log_callback("trip_data_extracted", {
                "trip_id": str(trip_data.get('trip_id', 'unknown'))[:8],
                "fields_count": len([v for v in trip_data.values() if v is not None]),
                "has_polyline": bool(trip_data.get('polyline'))
            }, status="INFO", extra_info="Trip data extracted successfully")
        
        return trip_data
    
    def process_polyline_coordinates(self, polyline_data: Any) -> Optional[List[List[float]]]:
        """Process and transform polyline coordinates."""
        if not polyline_data:
            if self.debug_enabled:
                self.logger.log_callback("polyline_missing", {
                    "polyline_data": str(polyline_data)
                }, status="WARNING", extra_info="No polyline data provided")
            return None
            
        try:
            # Handle bytes encoding
            if isinstance(polyline_data, bytes) and self.coord_config.get('decode_bytes', True):
                polyline_data = polyline_data.decode('utf-8')
                if self.debug_enabled:
                    self.logger.log_callback("polyline_decoded", {
                        "original_type": "bytes",
                        "decoded_length": len(polyline_data)
                    }, status="INFO", extra_info="Polyline bytes decoded to string")
            
            # Decode polyline
            coords_latlon = polyline_lib.decode(polyline_data)
            
            # Transform coordinates based on config
            if self.coord_config.get('output_format') == 'lon_lat':
                coords_lonlat = [[lon, lat] for (lat, lon) in coords_latlon]
            else:
                coords_lonlat = [[lat, lon] for (lat, lon) in coords_latlon]
            
            if self.debug_enabled:
                self.logger.log_callback("coordinates_processed", {
                    "input_points": len(coords_latlon),
                    "output_points": len(coords_lonlat),
                    "output_format": self.coord_config.get('output_format', 'lat_lon')
                }, status="SUCCESS", extra_info="Polyline coordinates processed successfully")
                
            return coords_lonlat
            
        except Exception as e:
            if self.debug_enabled:
                self.logger.log_callback("coordinate_processing_error", {
                    "error": str(e),
                    "polyline_type": type(polyline_data).__name__
                }, status="ERROR", extra_info="Failed to process polyline coordinates")
            if not self.rendering_config.get('fallback', {}).get('silent_errors', True):
                print(f"[MAP_POLYLINE_RENDERER] Coordinate processing error: {e}")
            return None
    
    def create_route_feature(self, trip_data: Dict[str, Any], coordinates: List[List[float]], 
                           color: str) -> Dict[str, Any]:
        """Create route LineString feature."""
        feature_config = self.rendering_config.get('feature_types', {}).get('route', {})
        if not feature_config.get('enabled', True):
            return None
            
        properties = {key: trip_data.get(key) for key in self.rendering_config.get('trip_properties', [])}
        properties['color'] = color
        
        return {
            "type": "Feature",
            "geometry": {
                "type": feature_config.get('geometry_type', 'LineString'),
                "coordinates": coordinates
            },
            "properties": properties
        }
    
    def create_marker_features(self, trip_data: Dict[str, Any], coordinates: List[List[float]], 
                             color: str) -> List[Dict[str, Any]]:
        """Create start, end, and car marker features."""
        features = []
        feature_types = self.rendering_config.get('feature_types', {})
        
        if not coordinates:
            return features
            
        # Start marker
        start_config = feature_types.get('start_marker', {})
        if start_config.get('enabled', True):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": start_config.get('geometry_type', 'Point'),
                    "coordinates": coordinates[0]
                },
                "properties": {
                    "role": start_config.get('role', 'start'),
                    "trip_id": trip_data.get('trip_id'),
                    "color": color
                }
            })
        
        # End marker
        end_config = feature_types.get('end_marker', {})
        if end_config.get('enabled', True):
            features.append({
                "type": "Feature", 
                "geometry": {
                    "type": end_config.get('geometry_type', 'Point'),
                    "coordinates": coordinates[-1]
                },
                "properties": {
                    "role": end_config.get('role', 'end'),
                    "trip_id": trip_data.get('trip_id'),
                    "color": color
                }
            })
        
        # Car marker (midpoint)
        car_config = feature_types.get('car_marker', {})
        if car_config.get('enabled', True) and len(coordinates) > 1:
            try:
                mid_idx = len(coordinates) // 2
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": car_config.get('geometry_type', 'Point'),
                        "coordinates": coordinates[mid_idx]
                    },
                    "properties": {
                        "role": car_config.get('role', 'car'),
                        "trip_id": trip_data.get('trip_id'),
                        "color": color
                    }
                })
            except Exception:
                pass  # Silent fallback for car marker
                
        return features
    
    def render_trip_features(self, trip: Any, trip_index: int, 
                           fetch_missing_polyline_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Render all features for a single trip."""
        features = []
        
        # Extract trip data
        trip_data = self.extract_trip_data(trip)
        polyline_data = trip_data.get('polyline')
        trip_id = trip_data.get('trip_id', 'unknown')
        
        if self.debug_enabled:
            self.logger.log_callback("render_trip_start", {
                "trip_id": str(trip_id)[:8],
                "trip_index": trip_index,
                "has_initial_polyline": bool(polyline_data)
            }, status="INFO", extra_info="Starting trip feature rendering")
        
        # Fetch missing polyline if callback provided
        if not polyline_data and fetch_missing_polyline_callback and trip_data.get('trip_id'):
            try:
                if self.debug_enabled:
                    self.logger.log_callback("fetch_missing_polyline", {
                        "trip_id": str(trip_id)[:8]
                    }, status="INFO", extra_info="Fetching missing polyline data")
                full_trip_data = fetch_missing_polyline_callback(trip_data['trip_id'])
                if full_trip_data:
                    trip_data.update(full_trip_data)
                    polyline_data = trip_data.get('polyline')
                    if self.debug_enabled:
                        self.logger.log_callback("polyline_fetched", {
                            "trip_id": str(trip_id)[:8],
                            "has_polyline": bool(polyline_data)
                        }, status="SUCCESS", extra_info="Missing polyline data fetched successfully")
            except Exception as e:
                if self.debug_enabled:
                    self.logger.log_callback("polyline_fetch_error", {
                        "trip_id": str(trip_id)[:8],
                        "error": str(e)
                    }, status="ERROR", extra_info="Failed to fetch missing polyline")
                pass  # Silent fallback
        
        # Skip if no polyline and configured to skip
        if not polyline_data and self.rendering_config.get('fallback', {}).get('skip_missing_polylines', True):
            if self.debug_enabled:
                self.logger.log_callback("trip_skipped", {
                    "trip_id": str(trip_id)[:8],
                    "skip_configured": True
                }, status="WARNING", extra_info="Trip skipped due to missing polyline")
            return features
        
        # Process coordinates
        coordinates = self.process_polyline_coordinates(polyline_data)
        if not coordinates:
            if self.debug_enabled:
                self.logger.log_callback("coordinates_failed", {
                    "trip_id": str(trip_id)[:8]
                }, status="ERROR", extra_info="Trip skipped due to coordinate processing failure")
            return features
        
        # Get color from palette
        palette = self.get_color_palette()
        color = palette[trip_index % len(palette)]
        
        if self.debug_enabled:
            self.logger.log_callback("trip_color_assigned", {
                "trip_id": str(trip_id)[:8],
                "color": color,
                "palette_index": trip_index % len(palette)
            }, status="INFO", extra_info="Color assigned to trip")
        
        # Create route feature
        route_feature = self.create_route_feature(trip_data, coordinates, color)
        if route_feature:
            features.append(route_feature)
        
        # Create marker features
        marker_features = self.create_marker_features(trip_data, coordinates, color)
        features.extend(marker_features)
        
        if self.debug_enabled:
            self.logger.log_callback("trip_features_created", {
                "trip_id": str(trip_id)[:8],
                "total_features": len(features),
                "route_feature": bool(route_feature),
                "marker_features": len(marker_features)
            }, status="SUCCESS", extra_info="Trip features created successfully")
        
        return features
    
    def render_trips_geojson(self, trips: List[Any], selected_trip_ids: List[str],
                           fetch_missing_polyline_callback: Optional[callable] = None) -> str:
        """Render complete GeoJSON for multiple trips."""
        if self.debug_enabled:
            self.logger.log_callback("render_geojson_start", {
                "total_trips": len(trips),
                "selected_trip_ids": len(selected_trip_ids or [])
            }, status="INFO", extra_info="Starting GeoJSON rendering process")
        
        features = []
        max_trips = self.rendering_config.get('performance', {}).get('max_trips_per_render', 50)
        
        # Filter selected trips
        selected_set = {str(trip_id) for trip_id in (selected_trip_ids or [])}
        filtered_trips = []
        
        for trip in trips[:max_trips]:
            trip_data = self.extract_trip_data(trip)
            trip_id = trip_data.get('trip_id')
            if trip_id and str(trip_id) in selected_set:
                filtered_trips.append(trip)
        
        if self.debug_enabled:
            self.logger.log_callback("trips_filtered", {
                "available_trips": len(trips),
                "max_trips": max_trips,
                "selected_trips": len(selected_set),
                "filtered_trips": len(filtered_trips)
            }, status="INFO", extra_info="Trips filtered for rendering")
        
        # Render features for each trip
        for idx, trip in enumerate(filtered_trips):
            trip_features = self.render_trip_features(trip, idx, fetch_missing_polyline_callback)
            features.extend(trip_features)
        
        # Return result
        if not features and self.rendering_config.get('fallback', {}).get('empty_collection_on_no_features', True):
            if self.debug_enabled:
                self.logger.log_callback("empty_geojson_returned", {
                    "reason": "no_features_generated"
                }, status="WARNING", extra_info="Returning empty GeoJSON collection")
            return json.dumps({"type": "FeatureCollection", "features": []})
        
        collection = {"type": "FeatureCollection", "features": features}
        
        if self.debug_enabled:
            self.logger.log_callback("geojson_generated", {
                "total_features": len(features),
                "collection_size": len(json.dumps(collection))
            }, status="SUCCESS", extra_info="GeoJSON generation completed successfully")
        
        return json.dumps(collection)


# Global instance for reuse
map_polyline_renderer = MapPolylineRenderer()
