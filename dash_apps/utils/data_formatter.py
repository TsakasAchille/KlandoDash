"""
Utilitaire pour formater les données selon la configuration JSON
Homogénéise les formats entre Supabase, validation et template Jinja2
"""
from datetime import datetime
from typing import Dict, Any, Optional
import re
from dash_apps.utils.settings import load_json_config


class DataFormatter:
    """Formateur de données basé sur la configuration JSON"""
    
    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse un timestamp Supabase en objet datetime"""
        if not timestamp_str:
            return None
            
        try:
            # Format Supabase: "2025-10-09T16:00:00+00:00"
            if '+' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif 'T' in timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            else:
                return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            from dash_apps.utils.callback_logger import CallbackLogger
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "parse_timestamp",
                    {"timestamp": timestamp_str, "error": str(e)},
                    status="ERROR",
                    extra_info="Timestamp parsing failed"
                )
            return None
    
    @staticmethod
    def _format_datetime(dt: datetime, output_format: str) -> str:
        """Formate un datetime selon le format spécifié"""
        if not dt:
            return "-"
            
        format_map = {
            "HH:mm": "%H:%M",
            "DD/MM/YYYY": "%d/%m/%Y", 
            "DD/MM/YYYY HH:mm": "%d/%m/%Y %H:%M",
            "YYYY-MM-DD": "%Y-%m-%d",
            "YYYY-MM-DD HH:mm:ss": "%Y-%m-%d %H:%M:%S"
        }
        
        python_format = format_map.get(output_format, "%Y-%m-%d %H:%M:%S")
        return dt.strftime(python_format)
    
    @staticmethod
    def format_trip_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données de trajet selon la configuration JSON
        Transforme les timestamps Supabase vers les formats attendus par le template
        """
        from dash_apps.utils.callback_logger import CallbackLogger
        
        if not raw_data:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "format_trip_data",
                    {"data_empty": True},
                    status="WARNING",
                    extra_info="No data to format"
                )
            return raw_data
            
        try:
            # Charger la configuration de formatage
            config = load_json_config('trip_details.json')
            formatting_config = config.get('trip_details', {}).get('data_formatting', {})
            datetime_fields = formatting_config.get('datetime_fields', {})
            
            formatted_data = raw_data.copy()
            formatted_fields = []
            
            # Formater chaque champ datetime configuré
            for field_name, field_config in datetime_fields.items():
                if field_name in raw_data and raw_data[field_name]:
                    
                    # Parser le timestamp Supabase
                    dt = DataFormatter._parse_timestamp(raw_data[field_name])
                    
                    if dt:
                        # Formater selon la configuration
                        output_format = field_config.get('output_format', 'DD/MM/YYYY HH:mm')
                        formatted_value = DataFormatter._format_datetime(dt, output_format)
                        formatted_data[field_name] = formatted_value
                        formatted_fields.append(field_name)
                        
                        # Créer aussi un champ séparé pour departure_date si nécessaire
                        if field_name == 'departure_schedule':
                            date_format = datetime_fields.get('departure_date', {}).get('output_format', 'DD/MM/YYYY')
                            formatted_data['departure_date'] = DataFormatter._format_datetime(dt, date_format)
                            formatted_fields.append('departure_date')
                        
                        # Vérifier si le debug des trajets est activé
                        import os
                        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
                        
                        if debug_trips:
                            CallbackLogger.log_callback(
                                "format_datetime_field",
                                {
                                    "field": field_name,
                                    "original": raw_data[field_name],
                                    "formatted": formatted_value,
                                    "format": output_format
                                },
                                status="SUCCESS",
                                extra_info="Datetime field formatted"
                            )
            
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "format_trip_data",
                    {
                        "fields_formatted": len(formatted_fields),
                        "formatted_fields": formatted_fields
                    },
                    status="SUCCESS",
                    extra_info="Trip data formatting completed"
                )
            
            return formatted_data
            
        except Exception as e:
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "format_trip_data",
                    {"error": str(e)},
                    status="ERROR",
                    extra_info="Data formatting failed"
                )
            return raw_data  # Retourner les données brutes en cas d'erreur
