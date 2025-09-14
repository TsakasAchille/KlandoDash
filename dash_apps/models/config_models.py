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


class TripMapDataModel(BaseModel):
    """Modèle pour les données de carte d'un trajet"""
    trip_id: str = Field(..., description="ID du trajet")
    polyline: Optional[str] = Field(None, description="Données de polyline encodées")
    departure_coords: List[float] = Field(..., description="Coordonnées de départ [lng, lat]")
    destination_coords: List[float] = Field(..., description="Coordonnées de destination [lng, lat]")
    distance_km: Optional[float] = Field(None, description="Distance en kilomètres")
    estimated_duration: Optional[str] = Field(None, description="Durée estimée au format HH:mm:ss")
    route_points: Optional[List[List[float]]] = Field(None, description="Points de la route [[lng, lat], ...]")
    
    @field_validator('departure_coords', 'destination_coords')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError('Les coordonnées doivent contenir exactement 2 valeurs [longitude, latitude]')
        if not (-180 <= v[0] <= 180):
            raise ValueError('La longitude doit être entre -180 et 180')
        if not (-90 <= v[1] <= 90):
            raise ValueError('La latitude doit être entre -90 et 90')
        return v
    
    @field_validator('route_points')
    @classmethod
    def validate_route_points(cls, v):
        if v is not None:
            for point in v:
                if len(point) != 2:
                    raise ValueError('Chaque point de route doit contenir exactement 2 valeurs [longitude, latitude]')
        return v


class TripDriverDataModel(BaseModel):
    """Modèle Pydantic pour valider les données conducteur depuis l'API"""
    trip_id: str = Field(min_length=10, pattern=r"^TRIP-.*")
    
    # Informations conducteur (correspondant au schéma users réel)
    name: Optional[str] = None
    email: Optional[str] = None
    uid: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    
    # Informations supplémentaires du schéma users
    birth: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    driver_license_url: Optional[str] = None
    id_card_url: Optional[str] = None
    is_driver_doc_validated: Optional[bool] = None
    
    # Évaluations (colonnes réelles du schéma users)
    driver_rating: Optional[float] = Field(ge=0, le=5, default=None)
    rating_count: Optional[int] = Field(ge=0, default=None)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Champs legacy pour compatibilité
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    driver_email: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_license: Optional[str] = None
    
    model_config = {
        "extra": "allow",  # Permet des champs supplémentaires
        "str_strip_whitespace": True
    }


class MapTripDataModel(BaseModel):
    """Modèle pour les données de trajet optimisées pour la carte"""
    trip_id: str = Field(min_length=1)
    departure_name: str = Field(min_length=1)
    destination_name: str = Field(min_length=1)
    polyline: Optional[str] = None
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    seats_booked: Optional[int] = Field(ge=0, default=0)
    seats_available: Optional[int] = Field(ge=0, default=1)
    passenger_price: Optional[float] = Field(ge=0, default=0.0)
    distance: Optional[float] = Field(ge=0, default=0.0)
    departure_schedule: Optional[str] = None
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }


class MapDataCollectionModel(BaseModel):
    """Collection de trajets pour la carte"""
    trips: List[MapTripDataModel]
    total_count: int = Field(ge=0)
    cached_at: Optional[datetime] = None
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }


class MainConfig(BaseModel):
    """Configuration principale contenant toutes les configurations"""
    trip_details: TripDetailsConfig
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }
