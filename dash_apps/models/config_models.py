"""
Modèles Pydantic pour la validation des configurations JSON
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, date
from enum import Enum


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


class TripPassengersDataModel(BaseModel):
    """Modèle de validation pour les données passagers d'un trajet"""
    trip_id: Optional[str] = None
    user_id: Optional[str] = None
    uid: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    seats: Optional[int] = 1
    booking_status: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    photo_url: Optional[str] = None
    role: Optional[str] = None
    
    class Config:
        extra = "allow"  # Permet des champs supplémentaires


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


# ===== MODÈLES POUR BOOKINGS ET USERS =====

class BookingStatus(str, Enum):
    """Statuts possibles pour une réservation."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class BookingModel(BaseModel):
    """Modèle pour une réservation individuelle."""
    id: str = Field(..., description="ID unique de la réservation")
    seats: int = Field(..., ge=1, le=8, description="Nombre de places réservées")
    user_id: str = Field(..., description="ID de l'utilisateur qui a fait la réservation")
    trip_id: str = Field(..., description="ID du trajet réservé")
    status: Optional[BookingStatus] = Field(default=BookingStatus.PENDING, description="Statut de la réservation")
    created_at: Optional[datetime] = Field(default=None, description="Date de création")
    updated_at: Optional[datetime] = Field(default=None, description="Date de dernière mise à jour")
    
    @field_validator('user_id', 'trip_id')
    @classmethod
    def validate_ids(cls, v):
        """Valide que les IDs ne sont pas vides."""
        if not v or not v.strip():
            raise ValueError("ID ne peut pas être vide")
        return v.strip()
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """Normalise le statut."""
        if v is None or v == "" or v == "null":
            return BookingStatus.CONFIRMED
        if isinstance(v, str):
            # Mapper les valeurs communes
            status_map = {
                "": BookingStatus.CONFIRMED,
                "pending": BookingStatus.PENDING,
                "confirmed": BookingStatus.CONFIRMED,
                "cancelled": BookingStatus.CANCELLED,
                "completed": BookingStatus.COMPLETED
            }
            return status_map.get(v.lower(), BookingStatus.CONFIRMED)
        return v


class BookingsQueryResult(BaseModel):
    """Résultat d'une requête sur les réservations."""
    bookings: List[BookingModel] = Field(default_factory=list, description="Liste des réservations")
    total_count: int = Field(default=0, description="Nombre total de réservations")
    total_seats: int = Field(default=0, description="Nombre total de places réservées")
    user_ids: List[str] = Field(default_factory=list, description="Liste unique des IDs utilisateurs")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculer les totaux après initialisation
        if self.bookings:
            self.user_ids = list(set(booking.user_id for booking in self.bookings))
            self.total_count = len(self.bookings)
            self.total_seats = sum(booking.seats for booking in self.bookings)


class BookingFilter(BaseModel):
    """Filtres pour les requêtes de réservations."""
    trip_id: Optional[str] = Field(default=None, description="Filtrer par ID de trajet")
    user_id: Optional[str] = Field(default=None, description="Filtrer par ID utilisateur")
    status: Optional[BookingStatus] = Field(default=None, description="Filtrer par statut")
    min_seats: Optional[int] = Field(default=None, ge=1, description="Nombre minimum de places")
    max_seats: Optional[int] = Field(default=None, le=8, description="Nombre maximum de places")
    
    def to_query_dict(self) -> dict:
        """Convertit les filtres en dictionnaire pour les requêtes."""
        query = {}
        if self.trip_id:
            query['trip_id'] = self.trip_id
        if self.user_id:
            query['user_id'] = self.user_id
        if self.status:
            query['status'] = self.status.value
        if self.min_seats is not None:
            query['seats__gte'] = self.min_seats
        if self.max_seats is not None:
            query['seats__lte'] = self.max_seats
        return query


class BookingsJsonQuery(BaseModel):
    """Configuration pour les requêtes JSON sur les bookings."""
    table: Literal["bookings"] = "bookings"
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtres de requête")
    select: List[str] = Field(
        default=["id", "seats", "user_id", "trip_id", "status", "created_at", "updated_at"],
        description="Colonnes à sélectionner"
    )
    order_by: Optional[List[str]] = Field(default=None, description="Tri des résultats")
    limit: Optional[int] = Field(default=None, ge=1, description="Limite du nombre de résultats")
    
    @classmethod
    def for_trip(cls, trip_id: str) -> 'BookingsJsonQuery':
        """Crée une requête pour récupérer les bookings d'un trajet."""
        return cls(
            filters={"trip_id": trip_id},
            order_by=["created_at"]
        )


class UsersJsonQuery(BaseModel):
    """Configuration pour les requêtes JSON sur les users."""
    table: Literal["users"] = "users"
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtres de requête")
    select: List[str] = Field(
        default=[
            "uid", "display_name", "email", "first_name", "name", 
            "phone_number", "birth", "photo_url", "bio", "gender", 
            "rating", "rating_count", "role", "created_at", "updated_at",
            "is_driver_doc_validated"
        ],
        description="Colonnes à sélectionner"
    )
    order_by: Optional[List[str]] = Field(default=None, description="Tri des résultats")
    limit: Optional[int] = Field(default=None, ge=1, description="Limite du nombre de résultats")
    
    @classmethod
    def for_user_ids(cls, user_ids: List[str]) -> 'UsersJsonQuery':
        """Crée une requête pour récupérer les users par leurs IDs."""
        return cls(
            filters={"uid__in": user_ids},
            order_by=["display_name", "first_name", "name"]
        )


class UserGender(str, Enum):
    """Genres possibles pour un utilisateur - valeurs originales de la base."""
    man = "man"
    woman = "woman"
    OTHER = "OTHER"
    NOT_SPECIFIED = "NOT_SPECIFIED"


class UserRole(str, Enum):
    """Rôles possibles pour un utilisateur - valeurs originales de la base."""
    passenger = "passenger"
    driver = "driver"
    DRIVER = "DRIVER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"


class UserModel(BaseModel):
    """Modèle pour un utilisateur."""
    uid: str = Field(..., description="ID unique de l'utilisateur")
    display_name: Optional[str] = Field(default=None, description="Nom d'affichage")
    email: Optional[str] = Field(default=None, description="Adresse email")
    first_name: Optional[str] = Field(default=None, description="Prénom")
    name: Optional[str] = Field(default=None, description="Nom de famille")
    phone_number: Optional[str] = Field(default=None, description="Numéro de téléphone")
    birth: Optional[date] = Field(default=None, description="Date de naissance")
    photo_url: Optional[str] = Field(default=None, description="URL de la photo de profil")
    bio: Optional[str] = Field(default=None, description="Biographie")
    driver_license_url: Optional[str] = Field(default=None, description="URL du permis de conduire")
    gender: Optional[UserGender] = Field(default=UserGender.NOT_SPECIFIED, description="Genre")
    id_card_url: Optional[str] = Field(default=None, description="URL de la carte d'identité")
    rating: Optional[float] = Field(default=None, description="Note moyenne")
    rating_count: Optional[int] = Field(default=0, description="Nombre d'évaluations")
    role: Optional[UserRole] = Field(default=UserRole.passenger, description="Rôle de l'utilisateur")
    updated_at: Optional[datetime] = Field(default=None, description="Date de dernière mise à jour")
    created_at: Optional[datetime] = Field(default=None, description="Date de création")
    is_driver_doc_validated: Optional[bool] = Field(default=False, description="Documents conducteur validés")
    
    @field_validator('uid')
    @classmethod
    def validate_uid(cls, v):
        """Valide que l'UID n'est pas vide."""
        if v is None:
            raise ValueError("UID ne peut pas être None")
        if not v or not str(v).strip():
            raise ValueError("UID ne peut pas être vide")
        return str(v).strip()
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Valide le format de l'email."""
        if v is None:
            return None
        if v and str(v).strip():
            # Validation basique d'email
            v_str = str(v).strip()
            if '@' not in v_str or '.' not in v_str.split('@')[-1]:
                raise ValueError("Format d'email invalide")
            return v_str.lower()
        return None
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        """Normalise le numéro de téléphone."""
        if v is None:
            return None
        if v and str(v).strip():
            # Supprime les espaces et caractères spéciaux
            v_str = str(v).strip()
            cleaned = ''.join(c for c in v_str if c.isdigit() or c in '+')
            return cleaned if cleaned else None
        return None
    
    @field_validator('gender', mode='before')
    @classmethod
    def validate_gender(cls, v):
        """Normalise le genre."""
        if v is None or v == '':
            return UserGender.NOT_SPECIFIED
        
        # Convertir string vers énumération
        if isinstance(v, str):
            gender_map = {
                'man': UserGender.man,
                'woman': UserGender.woman,
                'OTHER': UserGender.OTHER,
                'NOT_SPECIFIED': UserGender.NOT_SPECIFIED
            }
            return gender_map.get(v, UserGender.NOT_SPECIFIED)
        
        return v
    
    @field_validator('role', mode='before')
    @classmethod
    def validate_role(cls, v):
        """Normalise le rôle."""
        if v is None or v == '':
            return UserRole.passenger
        
        # Convertir string vers énumération
        if isinstance(v, str):
            role_map = {
                'passenger': UserRole.passenger,
                'driver': UserRole.driver,
                'DRIVER': UserRole.driver,
                'ADMIN': UserRole.ADMIN,
                'MODERATOR': UserRole.MODERATOR
            }
            return role_map.get(v, UserRole.passenger)
        
        return v
    
    @property
    def full_name(self) -> str:
        """Retourne le nom complet de l'utilisateur."""
        if self.first_name and self.name:
            return f"{self.first_name} {self.name}"
        elif self.display_name:
            return self.display_name
        elif self.first_name:
            return self.first_name
        elif self.name:
            return self.name
        else:
            return "Utilisateur anonyme"
    
    @property
    def is_driver(self) -> bool:
        """Vérifie si l'utilisateur est un conducteur."""
        return self.role in [UserRole.DRIVER, UserRole.ADMIN]
    
    @property
    def rating_display(self) -> str:
        """Retourne l'affichage de la note."""
        if self.rating is not None and self.rating_count is not None and self.rating_count > 0:
            return f"{self.rating:.1f}/5 ({self.rating_count} avis)"
        return "Pas encore noté"
    
    model_config = {
        "extra": "allow",  # Permet des champs supplémentaires
        "str_strip_whitespace": True,
        "validate_assignment": True
    }


class PassengerInfo(BaseModel):
    """Informations d'un passager avec ses réservations."""
    user: UserModel = Field(..., description="Informations utilisateur")
    seats_booked: int = Field(..., ge=1, description="Nombre de places réservées")
    booking_status: str = Field(..., description="Statut de la réservation")
    booking_id: str = Field(..., description="ID de la réservation")
    booking_created_at: Optional[datetime] = Field(default=None, description="Date de réservation")
    
    @property
    def passenger_display_name(self) -> str:
        """Nom d'affichage du passager."""
        return self.user.full_name
    
    @property
    def seats_text(self) -> str:
        """Texte pour les places."""
        return f"{self.seats_booked} place{'s' if self.seats_booked > 1 else ''}"


class PassengersQueryResult(BaseModel):
    """Résultat d'une requête sur les passagers."""
    passengers: List[PassengerInfo] = Field(default_factory=list, description="Liste des passagers")
    total_passengers: int = Field(default=0, description="Nombre total de passagers")
    total_seats: int = Field(default=0, description="Nombre total de places réservées")
    trip_id: Optional[str] = Field(default=None, description="ID du trajet")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculer les totaux après initialisation
        if self.passengers:
            self.total_passengers = len(self.passengers)
            self.total_seats = sum(p.seats_booked for p in self.passengers)
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
