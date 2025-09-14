"""
Transformateur de données pour optimiser les trajets de la page Map.
Optimise les polylines et prépare les données GeoJSON.
"""

import os
import json
from typing import Dict, Any, Optional, List, Tuple
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.settings import load_json_config


class MapTripsTransformer:
    """Transforme et optimise les données de trajets pour la carte"""
    
    @staticmethod
    def transform_trips_to_geojson(trips_data: List[Dict[str, Any]], selected_ids: List[str] = None) -> str:
        """
        Transforme les données de trajets en GeoJSON optimisé pour MapLibre
        
        Args:
            trips_data: Liste des trajets validés
            selected_ids: IDs des trajets sélectionnés à afficher
            
        Returns:
            String JSON de la FeatureCollection GeoJSON
        """
        debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
        
        try:
            if debug_maps:
                CallbackLogger.log_callback(
                    "transform_trips_to_geojson",
                    {
                        "trips_count": len(trips_data),
                        "selected_count": len(selected_ids) if selected_ids else 0
                    },
                    status="INFO",
                    extra_info="Starting trips to GeoJSON transformation"
                )
            
            # Filtrer les trajets sélectionnés
            selected_set = {str(s) for s in (selected_ids or [])}
            filtered_trips = []
            
            for trip in trips_data:
                trip_id = trip.get('trip_id')
                if trip_id and str(trip_id) in selected_set:
                    filtered_trips.append(trip)
            
            if not filtered_trips:
                # Retourner une collection vide
                empty_collection = {"type": "FeatureCollection", "features": []}
                return json.dumps(empty_collection)
            
            # Palette de couleurs pour différencier les trajets
            palette = [
                "#4281ec", "#e74c3c", "#27ae60", "#f1c40f", 
                "#8e44ad", "#16a085", "#d35400", "#2c3e50"
            ]
            
            features = []
            
            for idx, trip in enumerate(filtered_trips):
                try:
                    # Décoder la polyline
                    coordinates = MapTripsTransformer._decode_polyline(trip.get('polyline'))
                    
                    if not coordinates:
                        continue
                    
                    # Couleur du trajet
                    color = palette[idx % len(palette)]
                    
                    # Propriétés du trajet
                    properties = {
                        "trip_id": trip.get('trip_id'),
                        "color": color,
                        "driver_id": trip.get('driver_id'),
                        "driver_name": trip.get('driver_name', 'Conducteur'),
                        "seats_booked": trip.get('seats_booked', 0),
                        "seats_available": trip.get('seats_available', 1),
                        "passenger_price": trip.get('passenger_price', 0.0),
                        "distance": trip.get('distance', 0.0),
                        "departure_name": trip.get('departure_name', 'Départ'),
                        "destination_name": trip.get('destination_name', 'Arrivée'),
                        "departure_schedule": trip.get('departure_schedule', '')
                    }
                    
                    # Feature LineString pour la polyline
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": coordinates},
                        "properties": properties
                    })
                    
                    # Points de départ et d'arrivée
                    if coordinates:
                        start_point = coordinates[0]
                        end_point = coordinates[-1]
                        
                        # Point de départ
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": start_point},
                            "properties": {
                                "role": "start",
                                "trip_id": properties["trip_id"],
                                "color": color
                            }
                        })
                        
                        # Point d'arrivée
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": end_point},
                            "properties": {
                                "role": "end",
                                "trip_id": properties["trip_id"],
                                "color": color
                            }
                        })
                        
                        # Point milieu pour icône voiture
                        try:
                            mid_point = coordinates[len(coordinates) // 2]
                            features.append({
                                "type": "Feature",
                                "geometry": {"type": "Point", "coordinates": mid_point},
                                "properties": {
                                    "role": "car",
                                    "trip_id": properties["trip_id"],
                                    "color": color
                                }
                            })
                        except Exception:
                            pass
                
                except Exception as e:
                    if debug_maps:
                        CallbackLogger.log_callback(
                            "trip_geojson_error",
                            {
                                "trip_id": trip.get('trip_id', 'Unknown')[:8],
                                "error": str(e)
                            },
                            status="WARNING",
                            extra_info="Skipping trip due to processing error"
                        )
                    continue
            
            # Créer la FeatureCollection
            collection = {"type": "FeatureCollection", "features": features}
            
            if debug_maps:
                CallbackLogger.log_callback(
                    "transform_trips_to_geojson",
                    {
                        "input_trips": len(filtered_trips),
                        "output_features": len(features),
                        "success": True
                    },
                    status="SUCCESS",
                    extra_info="GeoJSON transformation completed"
                )
            
            return json.dumps(collection)
            
        except Exception as e:
            if debug_maps:
                CallbackLogger.log_callback(
                    "transform_trips_to_geojson",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Error transforming trips to GeoJSON"
                )
            
            # Retourner une collection vide en cas d'erreur
            empty_collection = {"type": "FeatureCollection", "features": []}
            return json.dumps(empty_collection)
    
    @staticmethod
    def _decode_polyline(polyline_data: Optional[str]) -> Optional[List[List[float]]]:
        """
        Décode une polyline en coordonnées [longitude, latitude]
        
        Args:
            polyline_data: Polyline encodée
            
        Returns:
            Liste de coordonnées [[lon, lat], ...] ou None
        """
        if not polyline_data:
            return None
        
        try:
            import polyline as polyline_lib
            
            # Gérer le format bytes
            if isinstance(polyline_data, bytes):
                polyline_data = polyline_data.decode('utf-8')
            
            # Décoder : [(lat, lon), ...] -> [[lon, lat], ...]
            coords_latlon = polyline_lib.decode(polyline_data)
            coordinates = [[lon, lat] for (lat, lon) in coords_latlon]
            
            return coordinates if len(coordinates) >= 2 else None
            
        except Exception:
            return None
    
    @staticmethod
    def optimize_trips_data(trips_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimise les données de trajets pour la performance
        
        Args:
            trips_data: Données de trajets brutes
            
        Returns:
            Données optimisées
        """
        debug_maps = os.getenv('DEBUG_MAPS', 'False').lower() == 'true'
        
        try:
            config = load_json_config('map_trips_config.json')
            optimization_config = config.get('map_trips', {}).get('optimization', {})
            
            optimized_trips = []
            
            for trip in trips_data:
                try:
                    optimized_trip = trip.copy()
                    
                    # Optimiser la polyline si nécessaire
                    if optimization_config.get('polyline_simplification', False):
                        polyline = trip.get('polyline')
                        if polyline:
                            # Simplifier la polyline (réduire le nombre de points)
                            simplified = MapTripsTransformer._simplify_polyline(polyline)
                            if simplified:
                                optimized_trip['polyline'] = simplified
                    
                    # Arrondir les coordonnées pour réduire la taille
                    precision = optimization_config.get('coordinate_precision', 6)
                    if 'distance' in optimized_trip and isinstance(optimized_trip['distance'], float):
                        optimized_trip['distance'] = round(optimized_trip['distance'], 2)
                    
                    if 'passenger_price' in optimized_trip and isinstance(optimized_trip['passenger_price'], float):
                        optimized_trip['passenger_price'] = round(optimized_trip['passenger_price'], 2)
                    
                    optimized_trips.append(optimized_trip)
                    
                except Exception as e:
                    if debug_maps:
                        CallbackLogger.log_callback(
                            "trip_optimization_error",
                            {
                                "trip_id": trip.get('trip_id', 'Unknown')[:8],
                                "error": str(e)
                            },
                            status="WARNING",
                            extra_info="Skipping trip optimization"
                        )
                    # Garder le trajet original
                    optimized_trips.append(trip)
            
            if debug_maps:
                CallbackLogger.log_callback(
                    "optimize_trips_data",
                    {
                        "input_count": len(trips_data),
                        "output_count": len(optimized_trips)
                    },
                    status="SUCCESS",
                    extra_info="Trips data optimization completed"
                )
            
            return optimized_trips
            
        except Exception as e:
            if debug_maps:
                CallbackLogger.log_callback(
                    "optimize_trips_data",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Error optimizing trips data, returning original"
                )
            return trips_data
    
    @staticmethod
    def _simplify_polyline(polyline_data: str, tolerance: float = 0.0001) -> Optional[str]:
        """
        Simplifie une polyline en réduisant le nombre de points
        
        Args:
            polyline_data: Polyline encodée
            tolerance: Tolérance pour la simplification
            
        Returns:
            Polyline simplifiée ou None
        """
        try:
            import polyline as polyline_lib
            
            # Décoder
            coords = polyline_lib.decode(polyline_data)
            
            # Simplifier (algorithme Douglas-Peucker basique)
            if len(coords) <= 10:  # Pas besoin de simplifier si peu de points
                return polyline_data
            
            # Garder 1 point sur 2 pour une simplification basique
            simplified_coords = coords[::2]
            
            # S'assurer de garder le dernier point
            if coords[-1] not in simplified_coords:
                simplified_coords.append(coords[-1])
            
            # Réencoder
            return polyline_lib.encode(simplified_coords)
            
        except Exception:
            return polyline_data  # Retourner l'original en cas d'erreur
