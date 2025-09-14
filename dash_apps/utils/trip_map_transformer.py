"""
Transformateur de données pour la carte des trajets.
Convertit les données de trajet validées en données de carte.
"""

import os
from typing import Dict, Any, Optional, List
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.models.config_models import TripMapDataModel
from dash_apps.utils.validation_utils import validate_data


class TripMapTransformer:
    """Transforme les données de trajet en données de carte"""
    
    @staticmethod
    def transform_trip_data_to_map_data(trip_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transforme les données de trajet validées en données de carte
        
        Args:
            trip_data: Données de trajet validées depuis TripDetailsCache
            
        Returns:
            Données de carte formatées ou None si erreur
        """
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        try:
            if debug_trips:
                print("====== TRANSFORMER DEBUG ======")
                print(f"Input data type: {type(trip_data)}")
                print(f"Input data: {trip_data}")
                print("===============================")
                CallbackLogger.log_callback(
                    "transform_trip_to_map",
                    {"trip_id": trip_data.get('trip_id', 'Unknown')[:8] if isinstance(trip_data, dict) else 'Not dict'},
                    status="INFO",
                    extra_info="Starting trip data transformation for map"
                )
            
            # Vérifier que trip_data est un dictionnaire
            if not isinstance(trip_data, dict):
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_trip_to_map",
                        {"error": f"Expected dict, got {type(trip_data)}"},
                        status="ERROR",
                        extra_info="Trip data is not a dictionary"
                    )
                return None
            
            # Extraire l'ID du trajet
            trip_id = trip_data.get('trip_id')
            if not trip_id:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_trip_to_map",
                        {"error": "No trip_id found", "available_keys": list(trip_data.keys())},
                        status="ERROR",
                        extra_info="Trip ID missing from data"
                    )
                return None
            
            # Extraire les coordonnées de départ et destination
            departure_coords = TripMapTransformer._extract_coordinates(
                trip_data, 'departure', debug_trips
            )
            destination_coords = TripMapTransformer._extract_coordinates(
                trip_data, 'destination', debug_trips
            )
            
            # Fallback vers des coordonnées par défaut si non disponibles
            if not departure_coords:
                departure_coords = [14.6937, -17.4441]  # Dakar par défaut
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_coordinates",
                        {"type": "departure", "fallback": True},
                        status="WARNING",
                        extra_info="Using fallback coordinates for departure"
                    )
            
            if not destination_coords:
                destination_coords = [14.7167, -17.4667]  # Pikine par défaut
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_coordinates",
                        {"type": "destination", "fallback": True},
                        status="WARNING",
                        extra_info="Using fallback coordinates for destination"
                    )
            
            # Extraire et décoder la polyline
            polyline_data = trip_data.get('polyline')
            route_points = TripMapTransformer._decode_polyline(
                polyline_data, departure_coords, destination_coords, debug_trips
            )
            
            # Extraire et nettoyer la distance
            distance_value = TripMapTransformer._extract_distance(trip_data, debug_trips)
            
            # Construire les données de carte
            map_data = {
                "trip_id": trip_id,
                "polyline": polyline_data,
                "departure_coords": departure_coords,
                "destination_coords": destination_coords,
                "distance_km": distance_value,
                "estimated_duration": trip_data.get('estimated_duration', "00:25:00"),
                "route_points": route_points
            }
            
            # Validation Pydantic directe
            try:
                validated_model = TripMapDataModel(**map_data)
                validated_data = validated_model.model_dump()
            except Exception as validation_error:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "pydantic_validation_error",
                        {"trip_id": trip_id[:8], "error": str(validation_error)},
                        status="ERROR",
                        extra_info="Pydantic validation failed"
                    )
                validated_data = None
            
            if validated_data:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_trip_to_map",
                        {
                            "trip_id": trip_id[:8],
                            "has_polyline": bool(polyline_data),
                            "points_count": len(route_points) if route_points else 0
                        },
                        status="SUCCESS",
                        extra_info="Trip data transformed successfully for map"
                    )
                return validated_data
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "transform_trip_to_map",
                        {"trip_id": trip_id[:8]},
                        status="ERROR",
                        extra_info="Validation failed for transformed map data"
                    )
                return None
                
        except Exception as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "transform_trip_to_map",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Error transforming trip data for map"
                )
            return None
    
    @staticmethod
    def _extract_coordinates(trip_data: Dict[str, Any], coord_type: str, debug_trips: bool) -> Optional[List[float]]:
        """
        Extrait les coordonnées de départ ou destination
        
        Args:
            trip_data: Données du trajet
            coord_type: 'departure' ou 'destination'
            debug_trips: Flag de debug
            
        Returns:
            Coordonnées [longitude, latitude] ou None
        """
        try:
            lat_key = f'{coord_type}_latitude'
            lon_key = f'{coord_type}_longitude'
            
            lat = trip_data.get(lat_key)
            lon = trip_data.get(lon_key)
            
            if lat is not None and lon is not None:
                coords = [float(lon), float(lat)]
                
                # Validation des coordonnées
                if -180 <= coords[0] <= 180 and -90 <= coords[1] <= 90:
                    if debug_trips:
                        CallbackLogger.log_callback(
                            "extract_coordinates",
                            {
                                "type": coord_type,
                                "coordinates": coords,
                                "valid": True
                            },
                            status="SUCCESS",
                            extra_info=f"Valid {coord_type} coordinates extracted"
                        )
                    return coords
                else:
                    if debug_trips:
                        CallbackLogger.log_callback(
                            "extract_coordinates",
                            {
                                "type": coord_type,
                                "coordinates": coords,
                                "valid": False
                            },
                            status="WARNING",
                            extra_info=f"Invalid {coord_type} coordinates range"
                        )
            
            return None
            
        except (ValueError, TypeError) as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "extract_coordinates",
                    {"type": coord_type, "error": str(e)},
                    status="ERROR",
                    extra_info=f"Error extracting {coord_type} coordinates"
                )
            return None
    
    @staticmethod
    def _decode_polyline(polyline_data: Optional[str], departure_coords: List[float], 
                        destination_coords: List[float], debug_trips: bool) -> List[List[float]]:
        """
        Décode la polyline ou retourne une ligne droite
        
        Args:
            polyline_data: Données de polyline encodées
            departure_coords: Coordonnées de départ
            destination_coords: Coordonnées de destination
            debug_trips: Flag de debug
            
        Returns:
            Liste de points [[longitude, latitude], ...]
        """
        # Fallback par défaut : ligne droite
        fallback_points = [departure_coords, destination_coords]
        
        if not polyline_data:
            if debug_trips:
                CallbackLogger.log_callback(
                    "decode_polyline",
                    {"has_polyline": False},
                    status="INFO",
                    extra_info="No polyline data, using direct line"
                )
            return fallback_points
        
        try:
            import polyline as polyline_lib
            
            # Gérer le format bytes si nécessaire
            if isinstance(polyline_data, bytes):
                polyline_data = polyline_data.decode('utf-8')
            
            # Décoder la polyline : [(lat, lon), ...] -> [[lon, lat], ...]
            coords_latlon = polyline_lib.decode(polyline_data)
            route_points = [[lon, lat] for (lat, lon) in coords_latlon]
            
            if len(route_points) >= 2:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "decode_polyline",
                        {
                            "has_polyline": True,
                            "points_count": len(route_points)
                        },
                        status="SUCCESS",
                        extra_info="Polyline decoded successfully"
                    )
                return route_points
            else:
                if debug_trips:
                    CallbackLogger.log_callback(
                        "decode_polyline",
                        {"points_count": len(route_points)},
                        status="WARNING",
                        extra_info="Not enough points in polyline, using fallback"
                    )
                return fallback_points
                
        except Exception as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "decode_polyline",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Failed to decode polyline, using fallback"
                )
            return fallback_points
    
    @staticmethod
    def _extract_distance(trip_data: Dict[str, Any], debug_trips: bool) -> float:
        """
        Extrait et nettoie la valeur de distance
        
        Args:
            trip_data: Données du trajet
            debug_trips: Flag de debug
            
        Returns:
            Distance en km (float)
        """
        try:
            distance = trip_data.get('distance', 15.0)
            
            # Si c'est déjà un nombre, le retourner
            if isinstance(distance, (int, float)):
                return float(distance)
            
            # Si c'est une chaîne, extraire le nombre
            if isinstance(distance, str):
                # Extraire les chiffres de la chaîne (ex: "807 m" -> 807)
                import re
                numbers = re.findall(r'\d+\.?\d*', distance)
                if numbers:
                    distance_value = float(numbers[0])
                    
                    # Convertir en km si nécessaire
                    if 'm' in distance.lower() and 'km' not in distance.lower():
                        distance_value = distance_value / 1000  # Convertir m en km
                    
                    if debug_trips:
                        CallbackLogger.log_callback(
                            "extract_distance",
                            {
                                "original": distance,
                                "extracted": distance_value,
                                "converted_to_km": 'm' in distance.lower() and 'km' not in distance.lower()
                            },
                            status="SUCCESS",
                            extra_info="Distance extracted and converted"
                        )
                    
                    return distance_value
            
            # Fallback
            if debug_trips:
                CallbackLogger.log_callback(
                    "extract_distance",
                    {"original": distance, "fallback": True},
                    status="WARNING",
                    extra_info="Using fallback distance value"
                )
            return 15.0
            
        except Exception as e:
            if debug_trips:
                CallbackLogger.log_callback(
                    "extract_distance",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Error extracting distance, using fallback"
                )
            return 15.0
