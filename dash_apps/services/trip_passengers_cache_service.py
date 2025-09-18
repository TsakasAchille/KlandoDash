"""
Service de cache spécialisé pour les informations passagers avec configuration JSON dynamique.
Implémente le pattern: Cache → JSON Config → DB/API → Cache → Panel HTML
Suit le pattern de user_details_cache_service.py
"""
import json
import os
from typing import Dict, Any, Optional, List
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.settings import load_json_config
from dash_apps.models.config_models import TripPassengersDataModel


class TripPassengersCache:
    """Service de cache pour les informations passagers avec configuration JSON"""
    
    _config_cache = None
    
    @staticmethod
    def _execute_passengers_query(trip_id: str) -> Optional[List[Dict[str, Any]]]:
        """Exécute une requête passagers optimisée avec retry automatique"""
        # Récupérer les champs configurés depuis trip_passengers.json
        config = TripPassengersCache._load_config()
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
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON consolidé"""
        if TripPassengersCache._config_cache is None:
            TripPassengersCache._config_cache = load_json_config('trip_passengers.json')
        
        return TripPassengersCache._config_cache
    
    @staticmethod
    def _get_cache_key(trip_id: str) -> str:
        """Génère la clé de cache - utilise directement le trip_id avec préfixe fixe"""
        return f"trip_passengers:{trip_id}"
    
    @staticmethod
    def _transform_passenger_data(passenger_data: Dict[str, Any], field_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Transforme les données de passager avec jointure users selon les mappings configurés
        
        Args:
            passenger_data: Données brutes du passager avec jointure
            field_mappings: Mappings de champs depuis la configuration
            
        Returns:
            Dict avec les données transformées et aplaties
        """
        if not passenger_data:
            return {}
        
        transformed = {}
        
        # Copier les champs directs de booking
        direct_fields = ['trip_id', 'user_id', 'seats', 'status', 'created_at']
        for field in direct_fields:
            if field in passenger_data:
                transformed[field] = passenger_data[field]
        
        # Traiter les données utilisateur de la jointure
        users_data = passenger_data.get('users')
        if users_data:
            # Si c'est une liste (ne devrait pas arriver avec inner join), prendre le premier
            if isinstance(users_data, list) and users_data:
                users_data = users_data[0]
            
            # Mapper les champs utilisateur selon la configuration
            user_field_mappings = {
                'uid': 'uid',
                'name': 'name', 
                'display_name': 'display_name',
                'first_name': 'first_name',
                'email': 'email',
                'phone_number': 'phone_number',
                'photo_url': 'photo_url'
            }
            
            for target_field, source_field in user_field_mappings.items():
                if source_field in users_data:
                    transformed[target_field] = users_data[source_field]
        
        # Nettoyer les champs non nécessaires pour les passagers (conserver 'status' de bookings)
        fields_to_remove = ['role', 'booking_status']
        for field in fields_to_remove:
            transformed.pop(field, None)
        
        return transformed
    
    @staticmethod
    def _set_cache_data_generic(trip_id: str, data_type: str, data, ttl_seconds: int):
        """Fonction cache générique pour stocker les données passagers"""
        from dash_apps.services.local_cache import local_cache as cache
        method_name = f"set_trip_{data_type}"
        if hasattr(cache, method_name):
            return getattr(cache, method_name)(trip_id, data, ttl_seconds=ttl_seconds)
        return False
    
    @staticmethod
    def _get_cached_data(trip_id: str) -> Optional[List[Dict[str, Any]]]:
        """Récupère les données depuis le cache local"""
        try:
            from dash_apps.services.local_cache import local_cache as cache
            cached_data = cache.get_trip_passengers(trip_id)
            
            debug_passengers = os.getenv('DEBUG_TRIP_PASSENGERS', 'False').lower() == 'true'
            
            if debug_passengers:
                CallbackLogger.log_callback(
                    "cache_get_passengers",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "cache_hit": cached_data is not None,
                        "data_type": type(cached_data).__name__ if cached_data else 'None'
                    },
                    status="SUCCESS" if cached_data else "MISS",
                    extra_info="Cache lookup for trip passengers"
                )
            
            return cached_data
            
        except Exception as e:
            debug_passengers = os.getenv('DEBUG_TRIP_PASSENGERS', 'False').lower() == 'true'
            
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
            
            # 2. Transformation des données avec jointure users
            config = TripPassengersCache._load_config()
            field_mappings = config.get('field_mappings', {})
            
            transformed_data = []
            
            if isinstance(passengers_data, list):
                for passenger in passengers_data:
                    transformed_passenger = TripPassengersCache._transform_passenger_data(passenger, field_mappings)
                    if transformed_passenger:
                        transformed_data.append(transformed_passenger)
            else:
                transformed_passenger = TripPassengersCache._transform_passenger_data(passengers_data, field_mappings)
                if transformed_passenger:
                    transformed_data = [transformed_passenger]
            
            if debug_passengers:
                for i, passenger in enumerate(transformed_data):
                    CallbackLogger.log_data_dict(
                        f"DONNÉES APRÈS TRANSFORMATION MAPPINGS - PASSENGER {i+1}/{len(transformed_data)} TRIP-{trip_id[:8]}",
                        passenger
                    )
            
            # 3. Validation avec Pydantic - traiter chaque passager individuellement
            validated_data = []
            
            for passenger in transformed_data:
                try:
                    validated_passenger = TripPassengersDataModel.model_validate(passenger, strict=False)
                    validated_data.append(validated_passenger)
                except Exception as validation_error:
                    if debug_passengers:
                        CallbackLogger.log_callback(
                            "passengers_validation_error_individual",
                            {"trip_id": trip_id[:8] if trip_id else 'None', "error": str(validation_error)},
                            status="WARNING",
                            extra_info="Validation échouée pour un passager individuel"
                        )
                    # Continuer avec les autres passagers
                    continue
            
            if debug_passengers:
                CallbackLogger.log_callback(
                    "passengers_validation_success",
                    {"trip_id": trip_id[:8] if trip_id else 'None'},
                    status="SUCCESS",
                    extra_info="Validation Pydantic réussie"
                )
            
            # 4. Formatage pour l'affichage
            from dash_apps.utils.passengers_display_formatter import PassengersDisplayFormatter
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
            config = TripPassengersCache._load_config()
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
