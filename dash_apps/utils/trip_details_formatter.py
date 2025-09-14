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
        self.config = load_json_config('trip_details_config.json')
        self.display_config = load_json_config('trip_details_display_config.json')
    
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
        field_mappings = self.display_config.get('field_mappings', {})
        for display_field, db_field in field_mappings.items():
            if db_field in raw_data:
                formatted_data[display_field] = raw_data[db_field]
        
        # 2. Formater les champs selon leur type
        formatted_data = self._apply_field_formatting(formatted_data)
        
        # 3. Ajouter les champs calculés
        formatted_data = self._add_calculated_fields(formatted_data, raw_data)
        
        # 4. Appliquer les transformations spécifiques
        formatted_data = self._apply_transformations(formatted_data)
        
        return formatted_data
    
    def _apply_field_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le formatage selon le type de champ"""
        formatting_config = self.display_config.get('display_formatting', {})
        
        # Formater les dates
        datetime_fields = formatting_config.get('datetime_fields', {})
        for field, format_config in datetime_fields.items():
            if field in data and data[field]:
                data[field] = self._format_datetime(data[field], format_config)
        
        # Formater les prix
        price_fields = formatting_config.get('price_fields', ['price', 'total_revenue'])
        for field in price_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_price(data[field])
        
        # Formater les distances
        distance_fields = formatting_config.get('distance_fields', ['distance'])
        for field in distance_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_distance(data[field])
        
        # Formater les durées
        duration_fields = formatting_config.get('duration_fields', ['duration'])
        for field in duration_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_duration(data[field])
        
        return data
    
    def _format_datetime(self, value: Any, format_config: Dict[str, str]) -> str:
        """Formate une date/heure selon la configuration"""
        try:
            if isinstance(value, str):
                # Parser différents formats d'entrée
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)
            
            output_format = format_config.get('display_format', '%d/%m/%Y %H:%M')
            return dt.strftime(output_format)
        except Exception:
            return str(value) if value else 'N/A'
    
    def _format_price(self, value: Any) -> str:
        """Formate un prix en euros"""
        try:
            price = float(value)
            return f"{price:.2f} €"
        except (ValueError, TypeError):
            return "N/A"
    
    def _format_distance(self, value: Any) -> str:
        """Formate une distance en km"""
        try:
            distance = float(value)
            if distance >= 1000:
                return f"{distance/1000:.1f} km"
            else:
                return f"{distance:.0f} m"
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
        """Ajoute des champs calculés"""
        # Calculer le prix par km
        if 'price' in data and 'distance' in data:
            try:
                price = float(raw_data.get('price', 0))
                distance = float(raw_data.get('distance', 0))
                if distance > 0:
                    data['price_per_km'] = f"{(price / (distance/1000)):.2f} €/km"
                else:
                    data['price_per_km'] = "N/A"
            except (ValueError, TypeError):
                data['price_per_km'] = "N/A"
        
        # Calculer la vitesse moyenne
        if 'distance' in data and 'duration' in data:
            try:
                distance = float(raw_data.get('distance', 0)) / 1000  # en km
                duration = float(raw_data.get('duration', 0)) / 60    # en heures
                if duration > 0:
                    data['average_speed'] = f"{(distance / duration):.1f} km/h"
                else:
                    data['average_speed'] = "N/A"
            except (ValueError, TypeError):
                data['average_speed'] = "N/A"
        
        return data
    
    def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique des transformations spécifiques"""
        # Transformer le statut en français
        status_mapping = {
            'pending': 'En attente',
            'confirmed': 'Confirmé', 
            'in_progress': 'En cours',
            'completed': 'Terminé',
            'cancelled': 'Annulé'
        }
        
        if 'status' in data:
            data['status_display'] = status_mapping.get(data['status'], data['status'])
        
        # Ajouter des classes CSS selon le statut
        if 'status' in data:
            status_classes = {
                'pending': 'status-pending',
                'confirmed': 'status-confirmed',
                'in_progress': 'status-progress', 
                'completed': 'status-completed',
                'cancelled': 'status-cancelled'
            }
            data['status_class'] = status_classes.get(data['status'], 'status-unknown')
        
        return data
