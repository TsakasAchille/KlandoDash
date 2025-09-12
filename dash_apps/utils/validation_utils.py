"""
Utilitaires de validation selon les meilleures pratiques Pydantic
"""
from pydantic import BaseModel, ValidationError
from typing import TypeVar, Type, List, Tuple, Optional, Any, Dict
import json
import os

T = TypeVar('T', bound=BaseModel)


class ValidationResult:
    """Wrapper pour les résultats de validation"""
    
    def __init__(self, success: bool, data: Optional[T] = None, errors: Optional[List[Dict]] = None):
        self.success = success
        self.data = data
        self.errors = errors or []
    
    def __bool__(self) -> bool:
        return self.success
    
    def get_error_summary(self) -> str:
        """Retourne un résumé des erreurs"""
        if not self.errors:
            return "Aucune erreur"
        
        summary = []
        for error in self.errors:
            field = error.get('field', 'unknown')
            message = error.get('message', 'Erreur inconnue')
            summary.append(f"• {field}: {message}")
        
        return "\n".join(summary)


def validate_data(
    model_class: Type[T], 
    data: Any, 
    strict: bool = False
) -> ValidationResult:
    """
    Valide des données avec gestion d'erreurs détaillée
    
    Args:
        model_class: Classe du modèle Pydantic
        data: Données à valider
        strict: Mode strict de validation
        
    Returns:
        ValidationResult avec succès/échec et détails
    """
    try:
        from dash_apps.utils.callback_logger import CallbackLogger
        
        validated = model_class.model_validate(data, strict=strict)
        
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_data",
                {"model": model_class.__name__, "strict": strict},
                status="SUCCESS",
                extra_info="Data validation successful"
            )
        
        return ValidationResult(success=True, data=validated)
    except ValidationError as e:
        errors = [
            {
                'field': '.'.join(str(p) for p in err['loc']),
                'message': err['msg'],
                'type': err['type'],
                'input': err.get('input')
            }
            for err in e.errors()
        ]
        
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_data",
                {"model": model_class.__name__, "error_count": len(errors)},
                status="ERROR",
                extra_info="Pydantic validation failed"
            )
        
        return ValidationResult(success=False, errors=errors)
    except Exception as e:
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_data",
                {"model": model_class.__name__, "error": str(e)},
                status="ERROR",
                extra_info="Unexpected validation error"
            )
        
        return ValidationResult(success=False, errors=[{
            'field': 'global',
            'message': str(e),
            'type': 'unexpected_error'
        }])


def validate_json_file(
    model_class: Type[T], 
    file_path: str, 
    strict: bool = False
) -> ValidationResult:
    """
    Valide un fichier JSON contre un modèle Pydantic
    
    Args:
        model_class: Classe du modèle Pydantic
        file_path: Chemin vers le fichier JSON
        strict: Mode strict de validation
        
    Returns:
        ValidationResult avec succès/échec et détails
    """
    try:
        from dash_apps.utils.callback_logger import CallbackLogger
        
        if not os.path.exists(file_path):
            # Vérifier si le debug des trajets est activé
            import os
            debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
            
            if debug_trips:
                CallbackLogger.log_callback(
                    "validate_json_file",
                    {"file_path": file_path, "model": model_class.__name__},
                    status="ERROR",
                    extra_info="File not found"
                )
            return ValidationResult(success=False, errors=[{
                'field': 'file',
                'message': f'Fichier non trouvé: {file_path}',
                'type': 'file_not_found'
            }])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_json_file",
                {"file_path": os.path.basename(file_path), "model": model_class.__name__},
                status="INFO",
                extra_info="JSON file loaded, validating"
            )
        
        return validate_data(model_class, data, strict)
        
    except json.JSONDecodeError as e:
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_json_file",
                {"file_path": os.path.basename(file_path), "json_error": e.msg},
                status="ERROR",
                extra_info="JSON decode error"
            )
        return ValidationResult(success=False, errors=[{
            'field': 'json',
            'message': f'JSON invalide: {e.msg} (ligne {e.lineno})',
            'type': 'json_decode_error'
        }])
    except Exception as e:
        # Vérifier si le debug des trajets est activé
        import os
        debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
        
        if debug_trips:
            CallbackLogger.log_callback(
                "validate_json_file",
                {"file_path": os.path.basename(file_path), "error": str(e)},
                status="ERROR",
                extra_info="File read error"
            )
        return ValidationResult(success=False, errors=[{
            'field': 'file',
            'message': f'Erreur lecture fichier: {str(e)}',
            'type': 'file_read_error'
        }])


def auto_fix_config(
    model_class: Type[T], 
    data: Dict, 
    schema_data: Optional[Dict] = None
) -> Tuple[bool, Dict, List[str]]:
    """
    Tente de corriger automatiquement une configuration
    
    Args:
        model_class: Classe du modèle Pydantic
        data: Données de configuration
        schema_data: Données de schéma pour validation (optionnel)
        
    Returns:
        Tuple (succès, données corrigées, messages de correction)
    """
    fixed_data = data.copy()
    fixes_applied = []
    
    try:
        # Tentative de validation initiale
        result = validate_data(model_class, fixed_data)
        if result.success:
            return True, fixed_data, []
        
        # Appliquer des corrections automatiques basées sur les erreurs
        for error in result.errors:
            field = error['field']
            error_type = error['type']
            
            if error_type == 'missing':
                # Ajouter des valeurs par défaut pour les champs manquants
                if _add_default_value(fixed_data, field, model_class):
                    fixes_applied.append(f"Ajouté valeur par défaut pour '{field}'")
            
            elif error_type in ['type_error', 'value_error']:
                # Tenter de corriger les types incompatibles
                if _fix_type_error(fixed_data, field, error):
                    fixes_applied.append(f"Corrigé le type pour '{field}'")
        
        # Validation finale
        final_result = validate_data(model_class, fixed_data)
        return final_result.success, fixed_data, fixes_applied
        
    except Exception as e:
        return False, data, [f"Erreur lors de l'auto-fix: {str(e)}"]


def _add_default_value(data: Dict, field_path: str, model_class: Type[BaseModel]) -> bool:
    """Ajoute une valeur par défaut pour un champ manquant"""
    try:
        # Logique simplifiée pour ajouter des valeurs par défaut
        field_parts = field_path.split('.')
        
        # Valeurs par défaut communes
        defaults = {
            'cache.enabled': True,
            'cache.ttl_seconds': 300,
            'validation.enabled': True,
            'validation.strict_mode': False,
            'data_source.primary': 'rest_api'
        }
        
        if field_path in defaults:
            _set_nested_value(data, field_parts, defaults[field_path])
            return True
            
        return False
    except:
        return False


def _fix_type_error(data: Dict, field_path: str, error: Dict) -> bool:
    """Tente de corriger une erreur de type"""
    try:
        field_parts = field_path.split('.')
        current_value = _get_nested_value(data, field_parts)
        
        if current_value is None:
            return False
        
        # Conversions de type communes
        if 'int' in error['type'] and isinstance(current_value, str):
            if current_value.isdigit():
                _set_nested_value(data, field_parts, int(current_value))
                return True
        
        elif 'bool' in error['type'] and isinstance(current_value, str):
            bool_value = current_value.lower() in ('true', '1', 'yes', 'on')
            _set_nested_value(data, field_parts, bool_value)
            return True
            
        return False
    except:
        return False


def _get_nested_value(data: Dict, field_parts: List[str]) -> Any:
    """Récupère une valeur imbriquée"""
    current = data
    for part in field_parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _set_nested_value(data: Dict, field_parts: List[str], value: Any) -> None:
    """Définit une valeur imbriquée"""
    current = data
    for part in field_parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[field_parts[-1]] = value
