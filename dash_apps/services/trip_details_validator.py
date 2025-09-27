"""
Validateur spécialisé pour la configuration trip_details utilisant Pydantic et JSON local
"""
import os
from dash_apps.services.pydantic_schema_validator import PydanticSchemaValidator


class TripDetailsValidator:
    """Validateur spécialisé pour la configuration trip_details avec Pydantic"""
    
    @staticmethod
    def validate_and_report():
        """Valide la configuration trip_details et génère un rapport"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'trip_details.json'
        )
        
        # Validation avec Pydantic
        is_valid, errors = PydanticSchemaValidator.validate_config_against_schema(config_path)
        
        # Rapport détaillé
        report = PydanticSchemaValidator.generate_schema_report(config_path)
        print(report)
        
        return is_valid, errors
    
    @staticmethod
    def auto_fix_config():
        """Tente de corriger automatiquement la configuration"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'trip_details.json'
        )
        
        return PydanticSchemaValidator.auto_fix_config(config_path)
    
    @staticmethod
    def validate_field_mapping():
        """Valide spécifiquement les mappings de champs datetime depuis trips_scheme.json"""
        # Récupérer le résumé du schéma
        schema_summary = PydanticSchemaValidator.get_schema_summary()
        
        print("\n" + "="*50)
        print("SCHÉMA TRIPS DEPUIS trips_scheme.json")
        print("="*50)
        
        print(f"📊 Total colonnes: {schema_summary['total_columns']}")
        print(f"🔒 Colonnes obligatoires: {len(schema_summary['required_columns'])}")
        print(f"📅 Colonnes datetime: {len(schema_summary['datetime_columns'])}")
        
        print("\n📅 CHAMPS DATETIME DISPONIBLES:")
        for field in schema_summary['datetime_columns']:
            print(f"  • {field}")
        
        print("\n🔒 CHAMPS OBLIGATOIRES:")
        for field in schema_summary['required_columns']:
            print(f"  • {field}")
        
        print("\n📝 CHAMPS TEXT:")
        for field in schema_summary['text_columns'][:10]:  # Limiter l'affichage
            print(f"  • {field}")
        if len(schema_summary['text_columns']) > 10:
            print(f"  ... et {len(schema_summary['text_columns']) - 10} autres")
        
        return schema_summary
