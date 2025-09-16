"""
Formatter pour les données de détails de trajet avec configuration JSON.
Transforme les données brutes en format d'affichage selon la configuration.
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from dash_apps.utils.settings import load_json_config


class TripDetailsFormatter:
    """Formatter pour les données de détails de trajet"""
    
    def __init__(self):
        self.config = load_json_config('trip_details.json')
    
    def format_for_display(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données brutes pour l'affichage selon la configuration
        
        Args:
            raw_data: Données brutes du trajet
            
        Returns:
            dict: Données formatées pour l'affichage
        """
        if not raw_data:
            return {}
        
        formatted_data = {}
        
        # 1. Appliquer les mappings de champs
        field_mappings = self.config.get('queries', {}).get('field_mappings', {})
        for display_field, db_field in field_mappings.items():
            if db_field in raw_data:
                formatted_data[display_field] = raw_data[db_field]
        
        # Copier tous les champs originaux
        for key, value in raw_data.items():
            if key not in formatted_data:
                formatted_data[key] = value
        
        # 2. Formater les champs selon leur type
        formatted_data = self._apply_field_formatting(formatted_data)
        
        # 3. Ajouter les champs calculés
        formatted_data = self._add_calculated_fields(formatted_data, raw_data)
        
        # 4. Appliquer les transformations spécifiques
        formatted_data = self._apply_transformations(formatted_data)
        
        return formatted_data
    
    def _apply_field_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le formatage selon le type de champ"""
        transformations = self.config.get('transformations', {}).get('field_transformations', {})
        
        # Formater le statut
        if 'status' in data and data['status']:
            status_config = transformations.get('status', {})
            display_mappings = status_config.get('display_mappings', {})
            status_value = data['status'].lower() if isinstance(data['status'], str) else str(data['status'])
            data['status_display'] = display_mappings.get(status_value, data['status'])
            data['status_class'] = f"status-{status_value}"
        
        # Formater les dates
        date_config = transformations.get('dates', {})
        date_fields = date_config.get('fields', ['departure_date', 'departure_schedule', 'created_at', 'updated_at'])
        date_format = date_config.get('format', '%d/%m/%Y %H:%M')
        
        for field in date_fields:
            if field in data and data[field]:
                data[field] = self._format_datetime(data[field], date_format)
        
        # Formater les prix
        price_config = transformations.get('price', {})
        price_fields = price_config.get('fields', ['passenger_price', 'driver_price'])
        currency = price_config.get('currency', 'FCFA')
        
        for field in price_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_price(data[field], currency)
        
        # Formater la distance
        distance_config = transformations.get('distance', {})
        if 'distance' in data and data['distance'] is not None:
            unit = distance_config.get('unit', 'km')
            data['distance'] = self._format_distance(data['distance'], unit)
        
        return data
    
    def _format_datetime(self, value: Any, date_format: str) -> str:
        """Formate une date/heure selon le format spécifié"""
        try:
            if isinstance(value, str):
                # Parser différents formats d'entrée
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)
            
            return dt.strftime(date_format)
        except Exception:
            return str(value) if value else 'N/A'
    
    def _format_price(self, value: Any, currency: str = "FCFA") -> str:
        """Formate un prix selon la devise spécifiée"""
        try:
            price = float(value)
            return f"{price} {currency}"
        except (ValueError, TypeError):
            return "N/A"
    
    def _format_distance(self, value: Any, unit: str = "km") -> str:
        """Formate une distance selon l'unité spécifiée"""
        try:
            distance = float(value)
            return f"{distance:.1f} {unit}"
        except (ValueError, TypeError):
            return "N/A"
    
    def _format_duration(self, value: Any) -> str:
        """Formate une durée en heures et minutes"""
        try:
            minutes = int(value)
            hours = minutes // 60
            remaining_minutes = minutes % 60
            
            if hours > 0:
                return f"{hours}h {remaining_minutes}min"
            else:
                return f"{remaining_minutes}min"
        except (ValueError, TypeError):
            return "N/A"
    
    def _add_calculated_fields(self, data: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute des champs calculés selon la configuration"""
        calculated_fields = self.config.get('transformations', {}).get('calculated_fields', {})
        
        # Ajouter les champs calculés définis dans la configuration
        for field_name, field_config in calculated_fields.items():
            if field_name == 'departure_location':
                priority = field_config.get('priority', ['departure_name'])
                fallback = field_config.get('fallback', 'Lieu non spécifié')
                for source_field in priority:
                    if source_field in raw_data and raw_data[source_field]:
                        data[field_name] = raw_data[source_field]
                        break
                else:
                    data[field_name] = fallback
            
            elif field_name == 'destination_location':
                priority = field_config.get('priority', ['destination_name'])
                fallback = field_config.get('fallback', 'Destination non spécifiée')
                for source_field in priority:
                    if source_field in raw_data and raw_data[source_field]:
                        data[field_name] = raw_data[source_field]
                        break
                else:
                    data[field_name] = fallback
            
            elif field_name == 'seats_info':
                available = raw_data.get('seats_available', 0)
                published = raw_data.get('seats_published', 0)
                format_str = field_config.get('format', '{available}/{published} places')
                data[field_name] = format_str.format(available=available, published=published)
        
        # Ajouter les champs de date séparés
        if 'departure_schedule' in raw_data and raw_data['departure_schedule']:
            try:
                if isinstance(raw_data['departure_schedule'], str):
                    dt = datetime.fromisoformat(raw_data['departure_schedule'].replace('Z', '+00:00'))
                elif isinstance(raw_data['departure_schedule'], datetime):
                    dt = raw_data['departure_schedule']
                else:
                    raise ValueError("Format de date non supporté")
                
                data['departure_date_only'] = dt.strftime('%d/%m/%Y')
                data['departure_time_only'] = dt.strftime('%H:%M')
            except Exception:
                data['departure_date_only'] = 'N/A'
                data['departure_time_only'] = 'N/A'
        else:
            data['departure_date_only'] = 'N/A'
            data['departure_time_only'] = 'N/A'
        
        return data
    
    def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique des transformations spécifiques"""
        # Transformer le statut en français
        status_mapping = {
            'PENDING': 'En attente',
            'pending': 'En attente',
            'CONFIRMED': 'Confirmé',
            'confirmed': 'Confirmé', 
            'CANCELED': 'Annulé',
            'canceled': 'Annulé'
        }
        
        if 'status' in data:
            data['status_display'] = status_mapping.get(data['status'], data['status'])
        
        # Ajouter des classes CSS selon le statut
        if 'status' in data:
            status_classes = {
                'PENDING': 'status-pending',
                'pending': 'status-pending',
                'CONFIRMED': 'status-confirmed',
                'confirmed': 'status-confirmed',
                'CANCELED': 'status-canceled',
                'canceled': 'status-canceled'
            }
            data['status_class'] = status_classes.get(data['status'], 'status-unknown')
        
        return data
