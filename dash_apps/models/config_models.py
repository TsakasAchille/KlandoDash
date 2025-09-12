"""
Modèles Pydantic pour la validation des configurations JSON
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime


class CacheConfig(BaseModel):
    """Configuration du cache"""
    enabled: bool = True
    ttl_seconds: int = Field(ge=1, le=3600, default=300)
    key_prefix: str = Field(min_length=1, default="trip_details")


class DataSourceConfig(BaseModel):
    """Configuration de la source de données"""
    primary: Literal["rest_api", "sql"] = "rest_api"
    fallback: Optional[Literal["rest_api", "sql"]] = "sql"
    timeout_seconds: int = Field(ge=1, le=60, default=30)


class ValidationConfig(BaseModel):
    """Configuration de la validation"""
    enabled: bool = True
    schema_file: str = Field(min_length=1, default="trips_scheme.json")
    strict_mode: bool = False
    auto_fix: bool = True


class FieldConfig(BaseModel):
    """Configuration d'un champ"""
    type: Literal["string", "integer", "float", "boolean", "datetime", "array"] = "string"
    label: str = Field(min_length=1)
    required: bool = False
    format: Optional[str] = None
    default_value: Optional[Any] = None
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v: Optional[str], info) -> Optional[str]:
        if v and info.data.get('type') == 'datetime':
            # Valider les formats datetime
            valid_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', 'iso']
            if v not in valid_formats:
                raise ValueError(f'Format datetime invalide. Formats valides: {valid_formats}')
        return v


class SectionConfig(BaseModel):
    """Configuration d'une section de rendu"""
    title: str = Field(min_length=1)
    fields: Dict[str, FieldConfig]
    collapsible: bool = False
    default_collapsed: bool = False
    
    @field_validator('fields')
    @classmethod
    def validate_fields_not_empty(cls, v: Dict[str, FieldConfig]) -> Dict[str, FieldConfig]:
        if not v:
            raise ValueError('Une section doit contenir au moins un champ')
        return v


class RenderingConfig(BaseModel):
    """Configuration du rendu"""
    sections: Dict[str, SectionConfig]
    
    @field_validator('sections')
    @classmethod
    def validate_sections_not_empty(cls, v: Dict[str, SectionConfig]) -> Dict[str, SectionConfig]:
        if not v:
            raise ValueError('La configuration de rendu doit contenir au moins une section')
        return v


class TripDetailsConfig(BaseModel):
    """Configuration complète pour les détails de trajet"""
    cache: CacheConfig = Field(default_factory=CacheConfig)
    data_source: DataSourceConfig = Field(default_factory=DataSourceConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    rendering: RenderingConfig
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
        "validate_assignment": True
    }
    
    @model_validator(mode='after')
    def validate_config_consistency(self) -> 'TripDetailsConfig':
        """Validation croisée de la configuration"""
        # Vérifier que tous les champs configurés dans le rendu sont cohérents
        all_fields = {}
        for section_name, section in self.rendering.sections.items():
            for field_name, field_config in section.fields.items():
                if field_name in all_fields:
                    # Vérifier la cohérence des types si le champ est dupliqué
                    if all_fields[field_name].type != field_config.type:
                        raise ValueError(
                            f'Champ {field_name} défini avec des types différents: '
                            f'{all_fields[field_name].type} vs {field_config.type}'
                        )
                all_fields[field_name] = field_config
        
        return self


class TripDataModel(BaseModel):
    """Modèle Pydantic pour valider les données de trajet depuis l'API"""
    trip_id: str = Field(min_length=10, pattern=r"^TRIP-.*")
    departure_name: Optional[str] = None
    destination_name: Optional[str] = None
    departure_schedule: Optional[datetime] = None
    driver_id: Optional[str] = None
    seats_published: Optional[int] = Field(ge=0, default=None)
    seats_available: Optional[int] = Field(ge=0, default=None)
    seats_booked: Optional[int] = Field(ge=0, default=None)
    passenger_price: Optional[float] = Field(ge=0, default=None)
    driver_price: Optional[float] = Field(ge=0, default=None)
    distance: Optional[float] = Field(ge=0, default=None)
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {
        "extra": "allow",  # Permet des champs supplémentaires
        "str_strip_whitespace": True
    }


class MainConfig(BaseModel):
    """Configuration principale contenant toutes les configurations"""
    trip_details: TripDetailsConfig
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }
