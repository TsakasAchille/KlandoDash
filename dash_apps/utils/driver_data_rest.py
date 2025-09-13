"""
Utilitaires pour récupérer les données conducteur via l'API REST avec validation Pydantic
"""
import logging
import os
from typing import Optional, Dict, Any
from dash_apps.utils.supabase_client import supabase
from dash_apps.utils.settings import load_json_config
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.validation_utils import validate_data
from dash_apps.models.driver_models import TripDriverDataModel
from pydantic import ValidationError

# Logger
logger = logging.getLogger(__name__)

def get_trip_driver_configured(trip_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les données conducteur d'un trajet selon la configuration JSON avec validation Pydantic
    """
    try:
        # Vérifier si le debug des trajets est activé
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        # 1. Charger la configuration via settings.py
        config = load_json_config('trip_driver_config.json')
        driver_config = config.get('trip_driver', {})
        fields_config = driver_config.get('fields', {})
        
        # 2. Extraire tous les champs configurés
        configured_fields = []
        for section_name, section_fields in fields_config.items():
            configured_fields.extend(section_fields.keys())
        
        # Utiliser CallbackLogger pour tracer les colonnes configurées
        if debug_trips:
            CallbackLogger.log_callback(
                "get_driver_configured_fields",
                {"configured_fields": configured_fields, "fields_count": len(configured_fields)},
                status="SUCCESS",
                extra_info="Champs conducteur extraits de la configuration"
            )
        
        # 3. Récupérer les données du trajet pour obtenir le driver_id
        trip_response = supabase.table("trips").select("driver_id").eq("trip_id", trip_id).execute()
        
        if not trip_response.data:
            if debug_trips:
                CallbackLogger.log_callback(
                    "trip_not_found_driver",
                    {"trip_id": trip_id},
                    status="WARNING",
                    extra_info="Trajet non trouvé dans Supabase pour données conducteur"
                )
            return None
        
        trip_data = trip_response.data[0]
        driver_id = trip_data.get('driver_id')
        
        if not driver_id:
            if debug_trips:
                CallbackLogger.log_callback(
                    "no_driver_id",
                    {"trip_id": trip_id},
                    status="WARNING",
                    extra_info="Aucun driver_id trouvé pour ce trajet"
                )
            return None
        
        # 4. Récupérer les informations du conducteur depuis la table users
        user_response = supabase.table("users").select("*").eq("uid", driver_id).execute()
        
        user_data = {}
        if user_response.data:
            user_data = user_response.data[0]
            if debug_trips:
                CallbackLogger.log_callback(
                    "supabase_user_query",
                    {"driver_id": driver_id[:8] if driver_id else 'None', "user_found": True},
                    status="SUCCESS",
                    extra_info="Données utilisateur récupérées de la table users"
                )
        else:
            if debug_trips:
                CallbackLogger.log_callback(
                    "user_not_found",
                    {"driver_id": driver_id[:8] if driver_id else 'None'},
                    status="WARNING",
                    extra_info="Utilisateur conducteur non trouvé dans la table users"
                )
        
        # 5. Mapper les données selon la configuration JSON
        driver_data = {'trip_id': trip_id}
        
        # Mapping des colonnes de base de données vers les champs de configuration
        field_mapping = {
            'name': lambda: user_data.get('name') or user_data.get('display_name') or user_data.get('first_name'),
            'email': lambda: user_data.get('email'),
            'uid': lambda: driver_id,
            'role': lambda: user_data.get('role'),
            'phone': lambda: user_data.get('phone_number'),  # Colonne réelle: phone_number
            'birth': lambda: user_data.get('birth'),
            'gender': lambda: user_data.get('gender'),
            'bio': lambda: user_data.get('bio'),
            'photo_url': lambda: user_data.get('photo_url'),
            'driver_license_url': lambda: user_data.get('driver_license_url'),
            'id_card_url': lambda: user_data.get('id_card_url'),
            'is_driver_doc_validated': lambda: user_data.get('is_driver_doc_validated'),
            'driver_rating': lambda: user_data.get('rating'),  # Colonne réelle: rating
            'rating_count': lambda: user_data.get('rating_count'),
            'created_at': lambda: user_data.get('created_at'),
            'updated_at': lambda: user_data.get('updated_at'),
            # Champs legacy pour compatibilité
            'driver_id': lambda: driver_id,
            'driver_name': lambda: user_data.get('name') or user_data.get('display_name'),
            'driver_email': lambda: user_data.get('email'),
            'driver_phone': lambda: user_data.get('phone_number'),
            'driver_license': lambda: user_data.get('driver_license_url'),
        }
        
        # Appliquer le mapping selon les champs configurés
        for field in configured_fields:
            if field in field_mapping:
                value = field_mapping[field]()
                if value is not None:
                    driver_data[field] = value
            elif debug_trips and field in ['name', 'email', 'uid']:  # Champs importants manquants
                    CallbackLogger.log_callback(
                        "driver_field_missing",
                        {"field": field, "trip_id": trip_id},
                        status="WARNING",
                        extra_info="Champ conducteur configuré mais absent des données"
                    )
        
        # 6. Validation avec Pydantic
        
        # Valider les données avec le modèle Pydantic
        validation_result = validate_data(TripDriverDataModel, driver_data)
        
        if not validation_result.success:
            if debug_trips:
                CallbackLogger.log_callback(
                    "driver_validation_error",
                    {"trip_id": trip_id, "errors": validation_result.get_error_summary()},
                    status="ERROR",
                    extra_info="Échec de la validation Pydantic pour conducteur"
                )
                logger.error(f"[DRIVER_CONFIGURED] Données conducteur invalides pour {trip_id}")
            return None
        
        # 7. Formater les données selon la configuration (si formatter disponible)
        try:
            from dash_apps.utils.data_formatter import DataFormatter
            formatted_data = DataFormatter.format_driver_data(filtered_data)
        except (ImportError, AttributeError):
            # Si pas de formatter spécifique, utiliser les données validées
            formatted_data = validation_result.data.model_dump()
        
        if debug_trips:
            CallbackLogger.log_callback(
                "driver_data_success",
                {
                    "trip_id": trip_id, 
                    "fields_returned": len(formatted_data),
                    "has_name": bool(formatted_data.get('name')),
                    "has_email": bool(formatted_data.get('email'))
                },
                status="SUCCESS",
                extra_info="Données conducteur validées, filtrées et formatées"
            )
            logger.info(f"[DRIVER_CONFIGURED] Données conducteur validées pour {trip_id}")
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération configurée du conducteur pour {trip_id}: {e}")
        if debug_trips:
            CallbackLogger.log_callback(
                "driver_config_error",
                {"trip_id": trip_id, "error": str(e)},
                status="ERROR",
                extra_info="Erreur dans get_trip_driver_configured"
            )
        return None
