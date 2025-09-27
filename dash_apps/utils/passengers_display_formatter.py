"""
Formateur pour les données passagers destinées à l'affichage
"""
from typing import Dict, Any, Optional
from dash_apps.utils.settings import load_json_config


class PassengersDisplayFormatter:
    """Formateur configurable pour les données passagers affichage"""
    
    def __init__(self):
        self.config = load_json_config('trip_passengers.json')
        self.display_config = self.config.get('display_formatting', {})
    
    def format_for_display(self, passenger_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données passager pour l'affichage dans les templates
        
        Args:
            passenger_data: Données brutes du passager
            
        Returns:
            Dict avec les données formatées pour l'affichage
        """
        if not passenger_data:
            return {}
        
        # Vérifier si c'est un dict ou un objet Pydantic
        if hasattr(passenger_data, 'model_dump'):
            # C'est un objet Pydantic v2, convertir en dict
            formatted = passenger_data.model_dump()
        elif hasattr(passenger_data, 'dict'):
            # C'est un objet Pydantic v1, convertir en dict
            formatted = passenger_data.dict()
        elif isinstance(passenger_data, dict):
            # C'est déjà un dict, copier
            formatted = passenger_data.copy()
        else:
            # Type inattendu, retourner vide
            return {}
        
        # 1. Nom d'affichage unifié
        formatted['display_name'] = self._get_display_name(formatted)
        
        # 2. Photo sécurisée - remplacer photo_url directement
        safe_url = self._get_safe_photo_url(formatted)
        if safe_url:
            formatted['photo_url'] = safe_url
        
        # 3. Formatage des valeurs
        formatted = self._format_field_values(formatted)
        
        # 4. Statut réservé (booking status) formaté à partir de 'status'
        formatted['status_display'] = self._get_status_display(formatted)
        
        # 5. Liens contextuels
        formatted['profile_link'] = self._get_profile_link(formatted)
        
        return formatted
    
    def _get_display_name(self, data: Dict[str, Any]) -> str:
        """Retourne le nom d'affichage avec fallback configuré"""
        name_config = self.display_config.get('name_fallback', {})
        fields = name_config.get('fields', ['name', 'display_name', 'first_name'])
        default = name_config.get('default', 'Passager')
        
        for field in fields:
            if data.get(field):
                return str(data[field]).strip()
        
        return default
    
    def _get_safe_photo_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Retourne une URL de photo sécurisée ou None"""
        photo_config = self.display_config.get('photo', {})
        fields = photo_config.get('fields', ['photo_url'])
        
        for field in fields:
            url = data.get(field)
            if url and isinstance(url, str) and url.strip():
                # Validation basique de l'URL
                if url.startswith(('http://', 'https://')):
                    return url.strip()
        
        return None
    
    def _format_field_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le formatage configuré aux champs"""
        field_formatting = self.display_config.get('field_formatting', {})
        
        for field, config in field_formatting.items():
            if field in data and data[field] is not None:
                format_type = config.get('type')
                
                if format_type == 'phone':
                    data[field] = self._format_phone(data[field])
                elif format_type == 'email':
                    data[field] = self._format_email(data[field])
                elif format_type == 'text':
                    data[field] = self._format_text(data[field], config)
        
        return data
    
    def _format_phone(self, phone: Any) -> str:
        """Formate un numéro de téléphone"""
        if not phone:
            return 'N/A'
        
        phone_str = str(phone).strip()
        if not phone_str:
            return 'N/A'
        
        # Formatage basique du téléphone
        return phone_str
    
    def _format_email(self, email: Any) -> str:
        """Formate une adresse email"""
        if not email:
            return 'N/A'
        
        email_str = str(email).strip().lower()
        if not email_str or '@' not in email_str:
            return 'N/A'
        
        return email_str
    
    def _format_text(self, text: Any, config: Dict[str, Any]) -> str:
        """Formate un texte selon la configuration"""
        if not text:
            return config.get('default', 'N/A')
        
        text_str = str(text).strip()
        max_length = config.get('max_length')
        
        if max_length and len(text_str) > max_length:
            return text_str[:max_length] + '...'
        
        return text_str
    
    def _get_profile_link(self, data: Dict[str, Any]) -> str:
        """Génère le lien vers le profil utilisateur"""
        uid = data.get('uid') or data.get('user_id')
        if uid:
            return f"/users?uid={uid}"
        return "/users"
    
    def _get_status_display(self, data: Dict[str, Any]) -> str:
        """Retourne le statut (bookings.status) formaté en français"""
        status = data.get('status') or data.get('booking_status')
        if not status:
            return 'N/A'
        mapping = {
            'confirmed': 'Confirmé',
            'pending': 'En attente',
            'cancelled': 'Annulé',
            'canceled': 'Annulé',
            'completed': 'Terminé',
            'trip_closed': 'Clôturé',
            'trip_open': 'Ouvert',
        }
        try:
            key = str(status).lower()
            return mapping.get(key, status)
        except Exception:
            return str(status)
