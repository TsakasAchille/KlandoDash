"""Implémentation Supabase du repository conducteur avec API native"""
import logging
import os
from typing import Optional, List, Dict, Any
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.settings import load_json_config

logger = logging.getLogger(__name__)


class SupabaseDriverRepository:
    """Implémentation Supabase du repository conducteur avec API native"""
    
    def __init__(self):
        self.debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        # Charger seulement les field mappings (plus besoin du Query Builder)
        self.driver_queries_config = load_json_config('driver_queries.json')
        self.field_mappings = self.driver_queries_config.get('field_mappings', {})
    
    async def get_by_trip_id(self, trip_id: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Récupère les données conducteur pour un trajet donné avec l'API native Supabase"""
        try:
            # Récupérer les champs de base depuis la configuration JSON
            query_config = self.driver_queries_config.get('queries', {}).get('driver_by_trip', {})
            json_base_fields = query_config.get('select', {}).get('base', [])
            
            # Nettoyer les champs (enlever le préfixe u.)
            base_fields = [field.replace('u.', '') for field in json_base_fields]
            
            # Ajouter les champs dynamiques si fournis
            if fields:
                for field in fields:
                    # Mapper avec field_mappings si disponible
                    mapped_field = self.field_mappings.get(field, field)
                    if mapped_field not in base_fields:
                        base_fields.append(mapped_field)
            
            # Construire la clause select pour Supabase REST
            select_clause = ', '.join(base_fields)
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_driver_query_native",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "json_raw_fields": json_base_fields,
                        "cleaned_fields": base_fields,
                        "dynamic_fields": fields or [],
                        "final_select_clause": select_clause
                    },
                    status="INFO",
                    extra_info="Executing driver query using native Supabase API with JSON config"
                )
            
            # Exécuter la requête native Supabase avec join automatique
            response = supabase.table('trips').select(
                f'driver_id, users({select_clause})'
            ).eq('trip_id', trip_id).limit(1).execute()
            
            if not response.data or len(response.data) == 0:
                if self.debug_trips:
                    CallbackLogger.log_callback(
                        "supabase_driver_query_no_data",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="WARNING",
                        extra_info="No data found for trip_id"
                    )
                return None
            
            # Extraire les données utilisateur du résultat
            trip_data = response.data[0]
            user_data = trip_data.get('users')
            
            if not user_data:
                if self.debug_trips:
                    CallbackLogger.log_callback(
                        "supabase_driver_no_user_data",
                        {"trip_id": trip_id[:8] if trip_id else 'None'},
                        status="WARNING",
                        extra_info="No user data in response for trip_id"
                    )
                return None
            
            # Si users est une liste, prendre le premier élément
            if isinstance(user_data, list) and len(user_data) > 0:
                user_data = user_data[0]
            
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "supabase_driver_data_retrieved",
                    {
                        "trip_id": trip_id[:8] if trip_id else 'None',
                        "user_data_keys": list(user_data.keys()) if isinstance(user_data, dict) else [],
                        "data_type": type(user_data).__name__
                    },
                    status="SUCCESS",
                    extra_info="Driver data successfully retrieved from Supabase"
                )
            
            return user_data
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du conducteur pour {trip_id}: {e}")
            if self.debug_trips:
                CallbackLogger.log_callback(
                    "driver_repository_error",
                    {"trip_id": trip_id, "error": str(e)},
                    status="ERROR",
                    extra_info="Erreur dans SupabaseDriverRepository.get_by_trip_id"
                )
            return None
    
    async def get_by_driver_id(self, driver_id: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Récupère les données conducteur par son ID avec l'API native Supabase"""
        try:
            # Récupérer les champs de base depuis la configuration JSON
            query_config = self.driver_queries_config.get('queries', {}).get('driver_by_id', {})
            base_fields = query_config.get('select', {}).get('base', [])
            
            # Ajouter les champs dynamiques si fournis
            if fields:
                for field in fields:
                    # Mapper avec field_mappings si disponible
                    mapped_field = self.field_mappings.get(field, field)
                    if mapped_field not in base_fields:
                        base_fields.append(mapped_field)
            
            # Construire la clause select pour Supabase REST
            select_clause = ', '.join(base_fields)
            
            if self.debug_trips:
                print(f"\n=== DRIVER QUERY DEBUG (Native Supabase) ===")
                print(f"Driver ID: {driver_id}")
                print(f"Champs sélectionnés: {base_fields}")
                print(f"Clause SELECT: users({select_clause})")
                print("=" * 50)
                
                CallbackLogger.log_callback(
                    "supabase_driver_query",
                    {
                        "driver_id": driver_id[:8] if driver_id else 'None',
                        "query": sql_query[:100] + "..." if len(sql_query) > 100 else sql_query,
                        "fields_requested": len(fields) if fields else 0
                    },
                    status="INFO",
                    extra_info="Executing driver by ID query with QuerySpec"
                )
            
            # Exécuter la requête
            response = supabase.rpc('execute_sql', {
                'sql_query': sql_query,
                'query_params': query_params
            })
            
            if not response.data or len(response.data) == 0:
                return None
            
            user_data = response.data[0]
            
            # Retourner directement les données
            return user_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du conducteur {driver_id}: {e}")
            return None
