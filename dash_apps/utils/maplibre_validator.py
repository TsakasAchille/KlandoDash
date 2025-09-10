"""Validation Pydantic V2 pour les URLs MapLibre - Approche moderne recommandée"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)

class MapLibreStyleConfig(BaseModel):
    """
    Modèle Pydantic V2 pour valider la configuration MapLibre
    
    Utilise les nouvelles APIs Pydantic V2 pour:
    - Performance optimisée (Rust backend)
    - Type safety améliorée
    - Validation plus flexible
    """
    
    style_url: str = Field(..., description="URL du style MapLibre")
    api_key: Optional[str] = Field(None, description="Clé API MapLibre (optionnelle si intégrée dans l'URL)")
    
    @field_validator('style_url')
    @classmethod
    def validate_style_url(cls, v: str) -> str:
        """Valide que l'URL du style est correctement formée"""
        if not v:
            raise ValueError("L'URL du style ne peut pas être vide")
        
        try:
            parsed = urlparse(v)
        except Exception as e:
            raise ValueError(f"URL malformée: {e}")
        
        # Vérifier le schéma
        if parsed.scheme not in ('http', 'https'):
            raise ValueError("L'URL doit utiliser le protocole HTTP ou HTTPS")
        
        # Vérifier que l'URL pointe vers un fichier JSON de style
        if not (parsed.path.endswith('.json') or 'style' in parsed.path.lower()):
            logger.warning(f"L'URL ne semble pas pointer vers un style JSON: {v}")
        
        return v
    
    @model_validator(mode='after')
    def validate_api_key_consistency(self) -> 'MapLibreStyleConfig':
        """Valide la cohérence de la clé API avec l'URL du style"""
        # Vérifier si l'API key est dans l'URL
        has_api_key_in_url = 'api_key=' in self.style_url or 'key=' in self.style_url
        
        if not has_api_key_in_url and not self.api_key:
            logger.warning("Aucune clé API trouvée ni dans l'URL ni comme paramètre séparé")
        
        if has_api_key_in_url and self.api_key:
            logger.warning("Clé API trouvée à la fois dans l'URL et comme paramètre - l'URL sera prioritaire")
        
        return self
    
    def get_api_key_from_url(self) -> Optional[str]:
        """Extrait la clé API de l'URL si elle y est présente"""
        try:
            parsed = urlparse(self.style_url)
            query_params = parse_qs(parsed.query)
            
            # Chercher 'api_key' ou 'key'
            api_key = query_params.get('api_key', [None])[0]
            if not api_key:
                api_key = query_params.get('key', [None])[0]
            
            return api_key
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de l'API key: {e}")
            return None
    
    def has_api_key_in_url(self) -> bool:
        """Vérifie si l'URL contient déjà une clé API"""
        return self.get_api_key_from_url() is not None
    
    def get_effective_api_key(self) -> Optional[str]:
        """Retourne la clé API effective (URL prioritaire sur paramètre)"""
        url_api_key = self.get_api_key_from_url()
        return url_api_key if url_api_key else self.api_key
    
    def to_container_attrs(self) -> Dict[str, Any]:
        """Convertit la configuration en attributs pour le conteneur HTML"""
        attrs = {
            "data-style-url": self.style_url,
            "data-selected-trip-id": ""
        }
        
        # Ajouter l'API key seulement si elle n'est pas dans l'URL
        if not self.has_api_key_in_url() and self.api_key:
            attrs["data-api-key"] = self.api_key
        
        return attrs

def validate_maplibre_config(style_url: str, api_key: Optional[str] = None) -> MapLibreStyleConfig:
    """
    Valide et normalise la configuration MapLibre
    
    Args:
        style_url: URL du style MapLibre
        api_key: Clé API optionnelle
    
    Returns:
        Configuration validée
    
    Raises:
        ValueError: Si la configuration est invalide
    """
    try:
        config = MapLibreStyleConfig(
            style_url=style_url,
            api_key=api_key
        )
        
        logger.info(f"Configuration MapLibre validée: {style_url}")
        if config.has_api_key_in_url():
            logger.info("Clé API détectée dans l'URL")
        elif config.api_key:
            logger.info("Clé API fournie comme paramètre séparé")
        else:
            logger.info("Aucune clé API configurée")
        
        return config
        
    except Exception as e:
        logger.error(f"Validation échouée pour {style_url}: {e}")
        raise
