"""
Service de cache spécialisé pour les informations passagers avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
Suit le pattern de user_details_cache_service.py
"""
import os
from typing import Dict, Any, Optional, List
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.settings import load_json_config
from dash_apps.models.config_models import TripPassengersDataModel
from dash_apps.utils.validation_utils import validate_data

from dash_apps.utils.passengers_display_formatter import PassengersDisplayFormatter

class TripPassengersCache:
    """Service de cache pour les informations passagers avec configuration JSON"""
    
    @staticmethod
    def _execute_passengers_query(trip_id: str) -> Optional[List[Dict[str, Any]]]:
        """Exécute une requête passagers optimisée avec retry automatique"""
        # Récupérer les champs configurés depuis trip_passengers.json
        config = load_json_config('trip_passengers.json')
        query_config = config.get('queries', {}).get('trip_passengers', {})
        json_base_fields = query_config.get('select', {}).get('base', [])
        
        # Utiliser les champs configurés ou tous les champs si pas de config
        base_fields = json_base_fields if json_base_fields else ["*"]
        select_clause = ', '.join(base_fields) if base_fields != ["*"] else "*"
        
        # Exécuter la requête avec retry automatique
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Requête pour récupérer les passagers via la table bookings
                response = supabase.table('bookings').select(select_clause).eq('trip_id', trip_id).execute()
                return response.data if response.data else []
                
            except Exception as retry_error:
                retry_count += 1
                if retry_count >= max_retries:
                    raise retry_error
                
                # Attendre avec backoff progressif
                import time
                time.sleep(0.5 * retry_count)
        
        return []
    
    @staticmethod
    def _flatten_passenger_data(passenger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplatit les données de passager en extrayant les champs users au niveau racine
        
        Args:
            passenger_data: Données brutes du passager avec jointure users
            
        Returns:
            Dict avec les données aplaties pour la validation Pydantic
        """
        if not passenger_data:
            return {}
        
        # Commencer avec les données de base (booking)
        flattened = dict(passenger_data)
        
        # Extraire et aplatir les données utilisateur
        users_data = passenger_data.get('users')
        if users_data:
            # Si c'est une liste, prendre le premier élément
            if isinstance(users_data, list) and users_data:
                users_data = users_data[0]
            
            # Aplatir les champs utilisateur au niveau racine
            # IMPORTANT: Ne pas écraser les champs existants s'ils sont déjà présents
            if isinstance(users_data, dict):
                for key, value in users_data.items():
                    # Seulement ajouter si le champ n'existe pas déjà ou s'il est vide
                    if key not in flattened or not flattened.get(key):
                        flattened[key] = value
        
        return flattened
    
    @staticmethod
    def _set_cache_data_generic(trip_id: str, data_type: str, data, ttl_seconds: int):
        """Fonction cache générique pour stocker les données passagers"""
        from dash_apps.services.local_cache import local_cache as cache
        
        try:
            cache_key = f"trip_passengers:{trip_id}"
            return cache.set('trip_passengers', data, ttl=ttl_seconds, key=cache_key)
        except Exception as e:
            debug_passengers = os.getenv('DEBUG_TRIP_PASSENGERS', 'False').lower() == 'true'
            if debug_passengers:
                CallbackLogger.log_callback(
                    "cache_set_passengers_error",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Cache storage failed"
                )
            return False
    
    @staticmethod
    def _get_cached_data(trip_id: str) -> Optional[List[Dict[str, Any]]]:
        """Récupère les données depuis le cache local"""
        from dash_apps.services.local_cache import local_cache as cache
        
        # Vérifier si le debug des passagers est activé
        debug_passengers = os.getenv('DEBUG_TRIP_PASSENGERS', 'False').lower() == 'true'
        
        try:
            cache_key = f"trip_passengers:{trip_id}"
            cached_data = cache.get('trip_passengers', key=cache_key)
            
            if debug_passengers:
                CallbackLogger.log_callback(
                    "cache_get_passengers",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "cache_key": cache_key,
                        "cache_hit": cached_data is not None,
                        "data_type": type(cached_data).__name__ if cached_data else 'None'
                    },
                    status="SUCCESS" if cached_data else "MISS",
                    extra_info="Cache lookup for trip passengers"
                )
            
            return cached_data
            
        except Exception as e:
            if debug_passengers:
                CallbackLogger.log_callback(
                    "cache_get_passengers",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Cache retrieval failed"
                )
            return None
    
    @staticmethod
    def get_trip_passengers_data(trip_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère les données détaillées des passagers d'un trajet avec cache intelligent
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            List contenant les données passagers ou une liste vide si erreur
        """
        if not trip_id:
            return []
                
        # Vérifier le cache d'abord
        cached_data = TripPassengersCache._get_cached_data(trip_id)
        if cached_data:
            return cached_data
        
        debug_passengers = os.getenv('DEBUG_TRIP_PASSENGERS', 'False').lower() == 'true'
        
        try:
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_fetch_start",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Fetching passengers data from database"
                )
            
            # Exécuter la requête optimisée avec configuration JSON
            passengers_data = TripPassengersCache._execute_passengers_query(trip_id)
            
            if not passengers_data:
                return []
            
            # Afficher les données brutes de la DB avec formatage détaillé
            if debug_passengers:
                if isinstance(passengers_data, list):
                    for i, passenger in enumerate(passengers_data):
                        CallbackLogger.log_data_dict(
                            f"DONNÉES BRUTES DB - PASSENGER {i+1}/{len(passengers_data)} TRIP-{trip_id[:8]}",
                            passenger
                        )
                else:
                    CallbackLogger.log_data_dict(
                        f"DONNÉES BRUTES DB - PASSENGER TRIP-{trip_id[:8]}",
                        passengers_data
                    )
            
            # 2. Aplatissement des données avant validation
            flattened_data = []
            for passenger in passengers_data:
                flattened_passenger = TripPassengersCache._flatten_passenger_data(passenger)
                flattened_data.append(flattened_passenger)
            
            if debug_passengers:
                for i, passenger in enumerate(flattened_data):
                    CallbackLogger.log_data_dict(
                        f"DONNÉES APRÈS APLATISSEMENT - PASSENGER {i+1}/{len(flattened_data)} TRIP-{trip_id[:8]}",
                        passenger
                    )
            
            # 3. Validation avec Pydantic - traiter chaque passager individuellement
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_validation_start",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="INFO",
                    extra_info="Starting Pydantic validation for passengers"
                )
            
            validated_data = []
            
            for i, passenger in enumerate(flattened_data):
                validation_result = validate_data(TripPassengersDataModel, passenger)
                
                if not validation_result.success:
                    if debug_passengers:
                        CallbackLogger.log_callback(
                            "passengers_validation_error_individual",
                            {
                                "trip_id": trip_id[:8] if trip_id else 'None', 
                                "passenger_index": i+1,
                                "errors": validation_result.get_error_summary()
                            },
                            status="WARNING",
                            extra_info="Validation échouée pour un passager individuel"
                        )
                    # Continuer avec les autres passagers
                    continue
                
                # Utiliser directement la sortie du validateur (dict JSON-sérialisable)
                validated_data.append(validation_result.data)
            
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_validation_success",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "validated_count": len(validated_data),
                        "total_count": len(flattened_data)
                    },
                    status="SUCCESS",
                    extra_info="Validation Pydantic réussie"
                )
            
            # 4. Formatage pour l'affichage
            formatter = PassengersDisplayFormatter()
            
            formatted_data = []
            for passenger_data in validated_data:
                formatted_passenger = formatter.format_for_display(passenger_data)
                formatted_data.append(formatted_passenger)
            
            # Afficher les données après transformation avec formatage détaillé
            if debug_passengers:
                for i, passenger in enumerate(formatted_data):
                    CallbackLogger.log_data_dict(
                        f"DONNÉES APRÈS TRANSFORMATION FORMATTER - PASSENGER {i+1}/{len(formatted_data)} TRIP-{trip_id[:8]}",
                        passenger
                    )
            
            # 5. Mise en cache avec TTL configuré
            config = load_json_config('trip_passengers.json')
            cache_config = config.get('cache', {})
            ttl_seconds = cache_config.get('ttl_seconds', 300)
            
            success = TripPassengersCache._set_cache_data_generic(trip_id, 'passengers', formatted_data, ttl_seconds)
            
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_cache_set",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "ttl_seconds": ttl_seconds,
                        "success": success
                    },
                    status="SUCCESS" if success else "WARNING",
                    extra_info="Passengers data cached" if success else "Cache storage failed"
                )
            
            return formatted_data
            
        except Exception as e:
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_fetch_error",
                    {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(e)},
                    status="ERROR",
                    extra_info="Failed to fetch passengers data"
                )
            return []
