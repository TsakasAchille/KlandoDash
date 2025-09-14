"""
Formateur pour les données conducteur destinées à l'affichage
"""
from typing import Dict, Any, Optional
from dash_apps.utils.settings import load_json_config


class DriverDisplayFormatter:
    """Formateur configurable pour les données conducteur affichage"""
    
    def __init__(self):
        self.config = load_json_config('driver_display_config.json')
        self.display_config = self.config.get('display_formatting', {})
    
    def format_for_display(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données conducteur pour l'affichage dans les templates
        
        Args:
            driver_data: Données brutes du conducteur
            
        Returns:
            Dict avec les données formatées pour l'affichage
        """
        if not driver_data:
            return {}
        
        # Copier les données originales
        formatted = driver_data.copy()
        
        # 1. Nom d'affichage unifié
        formatted['display_name'] = self._get_display_name(driver_data)
        
        # 2. Photo sécurisée
        formatted['safe_photo_url'] = self._get_safe_photo_url(driver_data)
        
        # 3. Formatage des valeurs
        formatted = self._format_field_values(formatted)
        
        # 4. Liens contextuels
        formatted['profile_link'] = self._get_profile_link(driver_data)
        
        return formatted
    
    def _get_display_name(self, data: Dict[str, Any]) -> str:
        """Retourne le nom d'affichage avec fallback configuré"""
        name_config = self.display_config.get('name_fallback', {})
        fields = name_config.get('fields', ['name', 'display_name', 'first_name'])
        default = name_config.get('default', 'Conducteur')
        
        for field in fields:
            value = data.get(field)
            if value and isinstance(value, str) and value.strip():
                return value.strip()
        
        return default
    
    def _get_safe_photo_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Retourne une URL de photo sécurisée ou None"""
        photo_url = data.get('photo_url')
        if not photo_url or not isinstance(photo_url, str):
            return None
        
        # Configuration des préfixes autorisés
        photo_config = self.display_config.get('photo_validation', {})
        allowed_prefixes = photo_config.get('allowed_prefixes', ['http://', 'https://', '/'])
        
        # Vérifier que l'URL semble valide
        url_stripped = photo_url.strip()
        if url_stripped and any(url_stripped.startswith(prefix) for prefix in allowed_prefixes):
            return url_stripped
        
        return None
    
    def _format_field_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les valeurs des champs pour l'affichage selon la configuration"""
        formatted = data.copy()
        
        field_config = self.display_config.get('field_formatting', {})
        required_fields = field_config.get('required_fields', {})
        optional_fields = field_config.get('optional_fields', {})
        
        # Traiter les champs requis
        for field, config in required_fields.items():
            if field in formatted:
                value = formatted[field]
                if not value or (isinstance(value, str) and not value.strip()):
                    formatted[field] = config.get('empty_display', 'N/A')
        
        # Traiter les champs optionnels
        for field, config in optional_fields.items():
            if field in formatted:
                value = formatted[field]
                if not value or (isinstance(value, str) and not value.strip()):
                    formatted[field] = config.get('empty_display', None)
        
        return formatted
    
    def _get_profile_link(self, data: Dict[str, Any]) -> str:
        """Génère le lien vers le profil utilisateur selon la configuration"""
        links_config = self.display_config.get('links', {})
        profile_config = links_config.get('profile', {})
        
        uid = data.get('uid')
        if uid and isinstance(uid, str) and uid.strip():
            template = profile_config.get('with_uid', '/users?uid={uid}')
            return template.format(uid=uid.strip())
        
        return profile_config.get('base_url', '/users')
    
    @staticmethod
    def format_rating(rating: Optional[float], rating_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Formate les données de notation pour l'affichage
        
        Args:
            rating: Note du conducteur
            rating_count: Nombre d'évaluations
            
        Returns:
            Dict avec les données de notation formatées
        """
        if not rating or rating <= 0:
            return {
                'has_rating': False,
                'rating_display': 'Pas encore noté',
                'rating_stars': '',
                'rating_class': 'no-rating'
            }
        
        # Arrondir à 1 décimale
        rating_rounded = round(float(rating), 1)
        
        # Générer les étoiles (★☆)
        full_stars = int(rating_rounded)
        half_star = (rating_rounded - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = '★' * full_stars
        if half_star:
            stars += '☆'
        stars += '☆' * empty_stars
        
        # Texte d'affichage
        count_text = f" ({rating_count})" if rating_count and rating_count > 0 else ""
        rating_display = f"{rating_rounded}/5{count_text}"
        
        # Classe CSS selon la note
        if rating_rounded >= 4.5:
            rating_class = 'excellent-rating'
        elif rating_rounded >= 4.0:
            rating_class = 'good-rating'
        elif rating_rounded >= 3.0:
            rating_class = 'average-rating'
        else:
            rating_class = 'poor-rating'
        
        return {
            'has_rating': True,
            'rating_value': rating_rounded,
            'rating_display': rating_display,
            'rating_stars': stars,
            'rating_class': rating_class,
            'rating_count': rating_count or 0
        }
