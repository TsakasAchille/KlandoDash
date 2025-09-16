"""
Formatter pour les données de détails utilisateur avec configuration JSON.
Transforme les données brutes en format d'affichage selon la configuration.
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, date
from dash_apps.utils.settings import load_json_config


class UserDetailsFormatter:
    """Formatter pour les données de détails utilisateur"""
    
    def __init__(self):
        # Une seule configuration pour toutes les transformations
        self.formatter_config = load_json_config('user_formatter_config.json')
    
    def format_for_display(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données brutes pour l'affichage selon la configuration
        
        Args:
            raw_data: Données brutes de l'utilisateur
            
        Returns:
            dict: Données formatées pour l'affichage
        """
        if not raw_data:
            return {}
        
        # 1. Copier tous les champs directement (pas de mappings nécessaires)
        formatted_data = raw_data.copy()
        
        # 2. Formater les champs selon leur type
        formatted_data = self._apply_field_formatting(formatted_data)
        
        # 3. Ajouter les champs calculés
        formatted_data = self._add_calculated_fields(formatted_data, raw_data)
        
        # 4. Appliquer les transformations spécifiques
        formatted_data = self._apply_transformations(formatted_data)
        
        return formatted_data
    
    def _apply_field_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le formatage spécifique aux champs selon la configuration JSON"""
        formatted = data.copy()
        
        # Transformer les énumérations en strings simples
        transformations = self.formatter_config.get('field_transformations', {})
        
        # Gender: UserGender.man -> "man" + "Homme"
        if 'gender' in transformations:
            gender_config = transformations['gender']
            if 'gender' in formatted and formatted['gender']:
                enum_str = str(formatted['gender'])
                # Convertir enum vers string simple
                formatted['gender'] = gender_config['mappings'].get(enum_str, enum_str)
                # Ajouter version display
                simple_gender = formatted['gender']
                formatted['gender_display'] = gender_config['display_mappings'].get(simple_gender, simple_gender)
        
        # Role: UserRole.passenger -> "passenger" + "Passager"  
        if 'role' in transformations:
            role_config = transformations['role']
            if 'role' in formatted and formatted['role']:
                enum_str = str(formatted['role'])
                # Convertir enum vers string simple
                formatted['role'] = role_config['mappings'].get(enum_str, enum_str)
                # Ajouter version display
                simple_role = formatted['role']
                formatted['role_display'] = role_config['display_mappings'].get(simple_role, simple_role)
        
        # Formatage des dates
        date_config = transformations.get('dates', {})
        date_fields = date_config.get('fields', ['birth', 'created_at', 'updated_at'])
        for field in date_fields:
            if field in formatted and formatted[field]:
                formatted[field] = self._format_date(formatted[field])
        
        # Formatage du téléphone
        if 'phone_number' in formatted and formatted['phone_number']:
            formatted['phone_display'] = self._format_phone(formatted['phone_number'])
        
        # Formatage de la note
        if 'rating' in formatted and formatted['rating']:
            formatted['rating_display'] = self._format_rating(formatted['rating'])
        
        return formatted
    
    def _add_calculated_fields(self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute les champs calculés"""
        result = formatted_data.copy()
        
        # Nom complet
        first_name = str(formatted_data.get('first_name') or '').strip()
        name = str(formatted_data.get('name') or '').strip()
        if first_name and name:
            result['full_name'] = f"{first_name} {name}"
        elif formatted_data.get('display_name'):
            result['full_name'] = str(formatted_data['display_name'] or '').strip()
        else:
            result['full_name'] = "Nom non disponible"
        
        # Âge calculé
        if 'birth' in raw_data and raw_data['birth']:
            result['age'] = self._calculate_age(raw_data['birth'])
        
        # Statut conducteur
        result['is_driver'] = formatted_data.get('role') in ['driver', 'DRIVER']
        
        # Profil complet
        result['profile_completion'] = self._calculate_profile_completion(formatted_data)
        
        # Ancienneté du compte
        if 'created_at' in raw_data and raw_data['created_at']:
            result['account_age_days'] = self._calculate_account_age(raw_data['created_at'])
        
        # Indicateurs booléens pour le template
        result['has_photo'] = bool(formatted_data.get('photo_url'))
        result['has_bio'] = bool(str(formatted_data.get('bio') or '').strip())
        result['has_phone'] = bool(formatted_data.get('phone_number'))
        result['has_documents'] = bool(formatted_data.get('driver_license_url') or formatted_data.get('id_card_url'))
        
        return result
    
    def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les transformations finales"""
        result = data.copy()
        
        # Nettoyer les chaînes vides
        for key, value in result.items():
            if isinstance(value, str) and not str(value or '').strip():
                result[key] = None
        
        # Valeurs par défaut pour l'affichage
        result['bio'] = result.get('bio') or "Aucune biographie"
        result['rating_display'] = result.get('rating_display') or "Pas encore noté"
        
        return result
    
    def _format_date(self, date_value) -> str:
        """Formate une date pour l'affichage"""
        if isinstance(date_value, str):
            try:
                # Essayer différents formats
                for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z']:
                    try:
                        dt = datetime.strptime(date_value, fmt)
                        return dt.strftime('%d/%m/%Y')
                    except ValueError:
                        continue
                return date_value
            except:
                return date_value
        elif isinstance(date_value, (datetime, date)):
            return date_value.strftime('%d/%m/%Y')
        return str(date_value)
    
    def _format_gender(self, gender_value) -> str:
        """Formate le genre pour l'affichage"""
        gender_map = {
            'man': 'Homme',
            'woman': 'Femme',
            'OTHER': 'Autre',
            'NOT_SPECIFIED': 'Non spécifié'
        }
        
        if hasattr(gender_value, 'value'):
            return gender_map.get(gender_value.value, str(gender_value))
        return gender_map.get(str(gender_value), str(gender_value))
    
    def _format_role(self, role_value) -> str:
        """Formate le rôle pour l'affichage"""
        role_map = {
            'passenger': 'Passager',
            'driver': 'Conducteur',
            'DRIVER': 'Conducteur',
            'ADMIN': 'Administrateur',
            'MODERATOR': 'Modérateur'
        }
        
        if hasattr(role_value, 'value'):
            return role_map.get(role_value.value, str(role_value))
        return role_map.get(str(role_value), str(role_value))
    
    def _format_phone(self, phone_value) -> str:
        """Formate le numéro de téléphone"""
        phone_str = str(phone_value)
        if phone_str.startswith('+221'):
            return f"{phone_str[:4]} {phone_str[4:6]} {phone_str[6:9]} {phone_str[9:11]} {phone_str[11:]}"
        return phone_str
    
    def _format_rating(self, rating_value) -> str:
        """Formate la note"""
        if rating_value is None:
            return "Pas encore noté"
        try:
            rating = float(rating_value)
            return f"{rating:.1f}/5 ⭐"
        except:
            return str(rating_value)
    
    def _calculate_age(self, birth_value) -> Optional[int]:
        """Calcule l'âge à partir de la date de naissance"""
        try:
            if isinstance(birth_value, str):
                birth_date = datetime.strptime(birth_value, '%Y-%m-%d').date()
            elif isinstance(birth_value, datetime):
                birth_date = birth_value.date()
            elif isinstance(birth_value, date):
                birth_date = birth_value
            else:
                return None
            
            today = date.today()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        except:
            return None
    
    def _calculate_profile_completion(self, data: Dict[str, Any]) -> int:
        """Calcule le pourcentage de completion du profil"""
        required_fields = ['display_name', 'email', 'phone_number', 'birth', 'bio', 'photo_url']
        completed = 0
        
        for field in required_fields:
            if data.get(field) and str(data[field] or '').strip():
                completed += 1
        
        return int((completed / len(required_fields)) * 100)
    
    def _calculate_account_age(self, created_at_value) -> Optional[int]:
        """Calcule l'ancienneté du compte en jours"""
        try:
            if isinstance(created_at_value, str):
                # Essayer différents formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z']:
                    try:
                        created_date = datetime.strptime(created_at_value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return None
            elif isinstance(created_at_value, datetime):
                created_date = created_at_value.date()
            else:
                return None
            
            today = date.today()
            return (today - created_date).days
        except:
            return None
