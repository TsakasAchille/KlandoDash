"""
Validateur de configuration moderne utilisant Pydantic selon les meilleures pratiques
"""
import os
from typing import Optional, Dict, Any
from dash_apps.models.config_models import MainConfig, TripDetailsConfig
from dash_apps.models.trips_schema import TripsTableSchema, TripsColumnSchema
from dash_apps.utils.validation_utils import ValidationResult, validate_json_file, auto_fix_config
import json


class ConfigValidator:
    """Validateur de configuration moderne basé sur les meilleures pratiques Pydantic"""
    
    _trips_schema_cache: Optional[TripsTableSchema] = None
    
    @classmethod
    def validate_config_file(cls, config_path: str, strict: bool = False) -> ValidationResult:
        """
        Valide un fichier de configuration avec Pydantic
        
        Args:
            config_path: Chemin vers le fichier de configuration
            strict: Mode strict de validation
            
        Returns:
            ValidationResult avec succès/échec et détails
        """
        # Validation Pydantic de base
        result = validate_json_file(MainConfig, config_path, strict)
        
        if not result.success:
            return result
        
        # Validation supplémentaire contre le schéma de base de données
        schema_validation = cls._validate_against_db_schema(result.data)
        
        if not schema_validation.success:
            # Combiner les erreurs
            result.errors.extend(schema_validation.errors)
            result.success = False
        
        return result
    
    @classmethod
    def _validate_against_db_schema(cls, config: MainConfig) -> ValidationResult:
        """
        Valide la configuration contre le schéma de base de données
        
        Args:
            config: Configuration validée par Pydantic
            
        Returns:
            ValidationResult avec validation du schéma DB
        """
        trips_schema = cls._get_trips_schema()
        
        if not trips_schema or not trips_schema.columns:
            return ValidationResult(success=False, errors=[{
                'field': 'schema',
                'message': 'Impossible de charger le schéma trips',
                'type': 'schema_load_error'
            }])
        
        errors = []
        
        # Valider tous les champs configurés
        for section_name, section in config.trip_details.rendering.sections.items():
            for field_name, field_config in section.fields.items():
                column = trips_schema.get_column(field_name)
                
                if not column:
                    errors.append({
                        'field': f'rendering.sections.{section_name}.fields.{field_name}',
                        'message': f"Champ '{field_name}' absent du schéma trips",
                        'type': 'field_not_found'
                    })
                    continue
                
                # Valider la compatibilité des types
                type_error = cls._validate_field_type(field_name, field_config.type, column)
                if type_error:
                    errors.append(type_error)
        
        return ValidationResult(success=len(errors) == 0, errors=errors)
    
    @classmethod
    def _validate_field_type(cls, field_name: str, config_type: str, column: TripsColumnSchema) -> Optional[Dict]:
        """
        Valide la compatibilité entre le type configuré et le type DB
        
        Args:
            field_name: Nom du champ
            config_type: Type configuré
            column: Schéma de la colonne DB
            
        Returns:
            Dictionnaire d'erreur ou None si valide
        """
        # Mapping des types compatibles
        type_mapping = {
            'string': ['text', 'varchar', 'char', 'uuid'],
            'integer': ['integer', 'bigint', 'smallint'],
            'float': ['real', 'double precision', 'numeric', 'decimal'],
            'boolean': ['boolean'],
            'datetime': ['timestamp', 'timestamptz', 'date', 'time'],
            'array': ['array', 'json', 'jsonb']
        }
        
        compatible_types = type_mapping.get(config_type, [])
        postgres_type = column.postgres_type.lower()
        
        # Vérifier la compatibilité
        is_compatible = any(pg_type in postgres_type for pg_type in compatible_types)
        
        if not is_compatible:
            return {
                'field': f'field.{field_name}.type',
                'message': f"Type '{config_type}' incompatible avec PostgreSQL '{postgres_type}'",
                'type': 'type_incompatible'
            }
        
        return None
    
    @classmethod
    def _get_trips_schema(cls) -> Optional[TripsTableSchema]:
        """Charge le schéma trips avec cache"""
        if cls._trips_schema_cache is None:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'scheme',
                'trips_scheme.json'
            )
            
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                
                columns = [TripsColumnSchema(**col) for col in schema_data]
                cls._trips_schema_cache = TripsTableSchema(columns=columns)
                
            except Exception as e:
                print(f"[CONFIG_VALIDATOR] Erreur chargement schéma: {e}")
                cls._trips_schema_cache = None
        
        return cls._trips_schema_cache
    
    @classmethod
    def auto_fix_config_file(cls, config_path: str) -> ValidationResult:
        """
        Tente de corriger automatiquement un fichier de configuration
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            ValidationResult avec les corrections appliquées
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tentative d'auto-fix
            success, fixed_data, fixes = auto_fix_config(MainConfig, data)
            
            if success and fixes:
                # Sauvegarder la configuration corrigée
                backup_path = f"{config_path}.backup"
                os.rename(config_path, backup_path)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                
                return ValidationResult(success=True, data=fixed_data, errors=[])
            
            return ValidationResult(success=success, errors=[
                {'field': 'auto_fix', 'message': 'Aucune correction automatique possible', 'type': 'no_fix'}
            ])
            
        except Exception as e:
            return ValidationResult(success=False, errors=[
                {'field': 'file', 'message': f'Erreur auto-fix: {str(e)}', 'type': 'auto_fix_error'}
            ])
    
    @classmethod
    def get_validation_report(cls, config_path: str) -> str:
        """
        Génère un rapport de validation détaillé
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Rapport de validation formaté
        """
        result = cls.validate_config_file(config_path)
        
        report = []
        report.append("=" * 60)
        report.append("📋 RAPPORT DE VALIDATION DE CONFIGURATION")
        report.append("=" * 60)
        report.append(f"Fichier: {config_path}")
        report.append(f"Statut: {'✅ VALIDE' if result.success else '❌ INVALIDE'}")
        report.append("")
        
        if result.success:
            report.append("🎉 Configuration valide selon les modèles Pydantic")
            report.append("🎉 Tous les champs sont compatibles avec le schéma de base de données")
        else:
            report.append(f"❌ {len(result.errors)} erreur(s) détectée(s):")
            report.append("")
            
            for i, error in enumerate(result.errors, 1):
                field = error.get('field', 'unknown')
                message = error.get('message', 'Erreur inconnue')
                error_type = error.get('type', 'unknown')
                
                report.append(f"{i}. Champ: {field}")
                report.append(f"   Erreur: {message}")
                report.append(f"   Type: {error_type}")
                report.append("")
        
        # Informations sur le schéma
        trips_schema = cls._get_trips_schema()
        if trips_schema and trips_schema.columns:
            report.append("📊 INFORMATIONS SCHÉMA")
            report.append(f"• Colonnes disponibles: {len(trips_schema.columns)}")
            report.append(f"• Colonnes obligatoires: {len(trips_schema.get_required_columns())}")
            report.append(f"• Colonnes datetime: {len(trips_schema.get_datetime_columns())}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    @classmethod
    def get_schema_summary(cls) -> Dict[str, Any]:
        """Retourne un résumé du schéma trips"""
        trips_schema = cls._get_trips_schema()
        
        if not trips_schema:
            return {'error': 'Impossible de charger le schéma'}
        
        return {
            'total_columns': len(trips_schema.columns),
            'required_columns': [col.column_name for col in trips_schema.get_required_columns()],
            'datetime_columns': [col.column_name for col in trips_schema.get_datetime_columns()],
            'text_columns': [col.column_name for col in trips_schema.get_columns_by_type('text')],
            'bigint_columns': [col.column_name for col in trips_schema.get_columns_by_type('bigint')],
            'double_precision_columns': [col.column_name for col in trips_schema.get_columns_by_type('double precision')]
        }
