"""
Modèle Pydantic pour le schéma de la table trips basé sur trips_scheme.json
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class PostgreSQLType(str, Enum):
    """Types PostgreSQL supportés"""
    TEXT = "text"
    BIGINT = "bigint"
    DOUBLE_PRECISION = "double precision"
    TIMESTAMP_WITH_TZ = "timestamp with time zone"
    BOOLEAN = "boolean"


class ConfigFieldType(str, Enum):
    """Types de configuration supportés"""
    STRING = "string"
    INTEGER = "integer"
    CURRENCY = "currency"
    DATETIME = "datetime"
    DISTANCE = "distance"
    PHONE = "phone"
    BOOLEAN = "boolean"
    ENUM = "enum"


class TripsColumnSchema(BaseModel):
    """Schéma d'une colonne de la table trips"""
    column_name: str
    data_type: str
    is_nullable: str  # "YES" ou "NO"
    column_default: Optional[str] = None
    character_maximum_length: Optional[int] = None
    
    @property
    def is_required(self) -> bool:
        """Retourne True si la colonne est obligatoire"""
        return self.is_nullable == "NO"
    
    @property
    def postgres_type(self) -> str:
        """Retourne le type PostgreSQL normalisé"""
        return self.data_type.lower()


class TripsTableSchema(BaseModel):
    """Schéma complet de la table trips"""
    columns: List[TripsColumnSchema]
    
    def get_column(self, column_name: str) -> Optional[TripsColumnSchema]:
        """Récupère une colonne par son nom"""
        for col in self.columns:
            if col.column_name == column_name:
                return col
        return None
    
    def get_columns_by_type(self, data_type: str) -> List[TripsColumnSchema]:
        """Récupère toutes les colonnes d'un type donné"""
        return [col for col in self.columns if col.data_type.lower() == data_type.lower()]
    
    def get_datetime_columns(self) -> List[TripsColumnSchema]:
        """Récupère toutes les colonnes datetime/timestamp"""
        return [col for col in self.columns if 'timestamp' in col.data_type.lower() or 'date' in col.data_type.lower()]
    
    def get_required_columns(self) -> List[TripsColumnSchema]:
        """Récupère toutes les colonnes obligatoires"""
        return [col for col in self.columns if col.is_required]


class TypeCompatibilityMap(BaseModel):
    """Mapping de compatibilité entre types config et PostgreSQL"""
    config_type: ConfigFieldType
    compatible_postgres_types: List[str]
    
    @staticmethod
    def get_compatibility_rules() -> List['TypeCompatibilityMap']:
        """Retourne les règles de compatibilité"""
        return [
            TypeCompatibilityMap(
                config_type=ConfigFieldType.STRING,
                compatible_postgres_types=["text", "varchar", "character varying", "uuid"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.INTEGER,
                compatible_postgres_types=["integer", "bigint", "smallint"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.CURRENCY,
                compatible_postgres_types=["integer", "bigint", "numeric", "double precision"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.DATETIME,
                compatible_postgres_types=["timestamp with time zone", "timestamp without time zone", "date"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.ENUM,
                compatible_postgres_types=["text", "varchar", "character varying"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.DISTANCE,
                compatible_postgres_types=["numeric", "double precision", "real"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.PHONE,
                compatible_postgres_types=["text", "varchar", "character varying"]
            ),
            TypeCompatibilityMap(
                config_type=ConfigFieldType.BOOLEAN,
                compatible_postgres_types=["boolean"]
            )
        ]
    
    @staticmethod
    def is_compatible(config_type: str, postgres_type: str) -> bool:
        """Vérifie si un type config est compatible avec un type PostgreSQL"""
        rules = TypeCompatibilityMap.get_compatibility_rules()
        
        for rule in rules:
            if rule.config_type.value == config_type:
                return any(
                    postgres_type.lower().startswith(compat.lower()) 
                    for compat in rule.compatible_postgres_types
                )
        
        return False
    
    @staticmethod
    def suggest_config_type(postgres_type: str) -> str:
        """Suggère le type de configuration approprié pour un type PostgreSQL"""
        postgres_type_lower = postgres_type.lower()
        
        if 'timestamp' in postgres_type_lower or 'date' in postgres_type_lower:
            return ConfigFieldType.DATETIME.value
        elif 'bigint' in postgres_type_lower or 'integer' in postgres_type_lower:
            return ConfigFieldType.INTEGER.value
        elif 'numeric' in postgres_type_lower or 'double' in postgres_type_lower:
            return ConfigFieldType.CURRENCY.value
        elif 'boolean' in postgres_type_lower:
            return ConfigFieldType.BOOLEAN.value
        else:
            return ConfigFieldType.STRING.value
