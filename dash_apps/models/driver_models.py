"""
Modèles Pydantic pour les données conducteur
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any

class TripDriverDataModel(BaseModel):
    """Modèle Pydantic pour les données conducteur d'un trajet"""
    
    # Champs de base
    trip_id: str = Field(..., description="ID du trajet")
    
    # Informations conducteur (correspondant au schéma users réel)
    name: Optional[str] = Field(None, description="Nom du conducteur")
    email: Optional[str] = Field(None, description="Email du conducteur")
    uid: Optional[str] = Field(None, description="ID utilisateur du conducteur")
    role: Optional[str] = Field(None, description="Rôle du conducteur")
    phone: Optional[str] = Field(None, description="Téléphone du conducteur")
    
    # Informations supplémentaires du schéma users
    birth: Optional[str] = Field(None, description="Date de naissance")
    gender: Optional[str] = Field(None, description="Genre")
    bio: Optional[str] = Field(None, description="Biographie")
    photo_url: Optional[str] = Field(None, description="URL de la photo de profil")
    driver_license_url: Optional[str] = Field(None, description="URL du permis de conduire")
    id_card_url: Optional[str] = Field(None, description="URL de la carte d'identité")
    is_driver_doc_validated: Optional[bool] = Field(None, description="Documents conducteur validés")
    
    # Évaluations (colonnes réelles du schéma users)
    driver_rating: Optional[float] = Field(None, description="Note du conducteur")
    rating_count: Optional[int] = Field(None, description="Nombre d'évaluations")
    
    # Timestamps
    created_at: Optional[str] = Field(None, description="Date de création")
    updated_at: Optional[str] = Field(None, description="Date de mise à jour")
    
    # Champs legacy pour compatibilité
    driver_id: Optional[str] = Field(None, description="ID conducteur (legacy)")
    driver_name: Optional[str] = Field(None, description="Nom conducteur (legacy)")
    driver_email: Optional[str] = Field(None, description="Email conducteur (legacy)")
    driver_phone: Optional[str] = Field(None, description="Téléphone conducteur (legacy)")
    driver_license: Optional[str] = Field(None, description="Permis de conduire")
    
    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',  # Permet des champs supplémentaires
        str_strip_whitespace=True
    )
    
    def model_post_init(self, __context: Any) -> None:
        """Post-traitement après initialisation du modèle"""
        # Mapper les champs legacy vers les nouveaux champs si nécessaire
        if self.driver_name and not self.name:
            self.name = self.driver_name
        if self.driver_email and not self.email:
            self.email = self.driver_email
        if self.driver_phone and not self.phone:
            self.phone = self.driver_phone
        if self.driver_id and not self.uid:
            self.uid = self.driver_id
