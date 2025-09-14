"""Implémentation Supabase du repository trip details avec API native"""
import logging
import os
from typing import Optional, List, Dict, Any
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.settings import load_json_config

logger = logging.getLogger(__name__)


class SupabaseTripRepository:
    """Implémentation Supabase du repository trip details avec API native"""
    
    def __init__(self):
        self.debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        # Charger la configuration des requêtes trip details
        self.trip_queries_config = load_json_config('trip_queries.json')
        self.field_mappings = self.trip_queries_config.get('field_mappings', {})
    
    async def get_by_trip_id(self, trip_id: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Récupère les données de trajet pour un trip_id donné avec l'API native Supabase"""
        try:
            # Récupérer les champs de base depuis la configuration JSON
            query_config = self.trip_queries_config.get('queries', {}).get('trip_details', {})
            json_base_fields = query_config.get('select', {}).get('base', [])
            
            # Utiliser les champs de base ou tous les champs si pas de config
            base_fields = json_base_fields if json_base_fields else ["*"]
            
            # Ajouter les champs dynamiques si fournis
            if fields:
                for field in fields:
                    # Mapper avec field_mappings si disponible
                    mapped_field = self.field_mappings.get(field, field)
                    if mapped_field not in base_fields and base_fields != ["*"]:
                        base_fields.append(mapped_field)
            
            # Construire la clause select pour Supabase REST
            select_clause = ', '.join(base_fields) if base_fields != ["*"] else "*"
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_trip_query_native",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "json_raw_fields": json_base_fields,
                        "cleaned_fields": base_fields,
                        "dynamic_fields": fields or [],
                        "final_select_clause": select_clause
                    },
                    status="INFO",
                    extra_info="Executing trip details query using native Supabase API with JSON config"
                )
            
            # Exécuter la requête native Supabase
            response = supabase.table('trips').select(select_clause).eq('trip_id', trip_id).limit(1).execute()
            
            if not response.data or len(response.data) == 0:
                if self.debug_trips:
                    CallbackLogger.log_callback(
                        "supabase_trip_query_no_data",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="WARNING",
                        extra_info="No data found for trip_id"
                    )
                return None
            
            # Extraire les données du résultat
            trip_data = response.data[0]
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_trip_data_retrieved",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "trip_data_keys": list(trip_data.keys()) if isinstance(trip_data, dict) else [],
                        "data_type": type(trip_data).__name__
                    },
                    status="SUCCESS",
                    extra_info="Trip details data successfully retrieved from Supabase"
                )
            
            return trip_data
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du trajet {trip_id}: {e}")
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "trip_repository_error",
                    {"trip_id": trip_id, "error": str(e)},
                    status="ERROR",
                    extra_info="Erreur dans SupabaseTripRepository.get_by_trip_id"
                )
            return None
    
    async def get_multiple_by_ids(self, trip_ids: List[str], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Récupère plusieurs trajets par leurs IDs"""
        try:
            # Récupérer les champs de base depuis la configuration JSON
            query_config = self.trip_queries_config.get('queries', {}).get('trip_details', {})
            json_base_fields = query_config.get('select', {}).get('base', [])
            
            # Utiliser les champs de base ou tous les champs si pas de config
            base_fields = json_base_fields if json_base_fields else ["*"]
            
            # Ajouter les champs dynamiques si fournis
            if fields:
                for field in fields:
                    mapped_field = self.field_mappings.get(field, field)
                    if mapped_field not in base_fields and base_fields != ["*"]:
                        base_fields.append(mapped_field)
            
            # Construire la clause select
            select_clause = ', '.join(base_fields) if base_fields != ["*"] else "*"
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_multiple_trips_query",
                    {
                        "trip_ids_count": len(trip_ids),
                        "select_clause": select_clause
                    },
                    status="INFO",
                    extra_info="Executing multiple trips query"
                )
            
            # Exécuter la requête pour plusieurs trip_ids
            response = supabase.table('trips').select(select_clause).in_('trip_id', trip_ids).execute()
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_multiple_trips_result",
                    {
                        "trips_found": len(response.data) if response.data else 0,
                        "trips_requested": len(trip_ids)
                    },
                    status="SUCCESS",
                    extra_info="Multiple trips data retrieved"
                )
            
            return response.data or []
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de plusieurs trajets: {e}")
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "multiple_trips_repository_error",
                    {"trip_ids_count": len(trip_ids), "error": str(e)},
                    status="ERROR",
                    extra_info="Erreur dans SupabaseTripRepository.get_multiple_by_ids"
                )
            return []
