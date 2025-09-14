"""
Formatter pour les données de statistiques de trajet avec configuration JSON.
Transforme les données brutes en format d'affichage selon la configuration.
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from dash_apps.utils.settings import load_json_config


class TripStatsFormatter:
    """Formatter pour les données de statistiques de trajet"""
    
    def __init__(self):
        self.config = load_json_config('trip_details_config.json')
        self.display_config = load_json_config('trip_stats_display_config.json')
    
    def format_for_display(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate les données brutes pour l'affichage selon la configuration
        
        Args:
            raw_data: Données brutes des statistiques de trajet
            
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
        
        # 3. Ajouter les métriques calculées
        formatted_data = self._add_calculated_metrics(formatted_data, raw_data)
        
        # 4. Appliquer les transformations spécifiques
        formatted_data = self._apply_transformations(formatted_data)
        
        return formatted_data
    
    def _apply_field_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique le formatage selon le type de champ"""
        formatting_config = self.display_config.get('display_formatting', {})
        
        # Formater les prix et revenus
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
        
        # Formater les pourcentages
        percentage_fields = formatting_config.get('percentage_fields', [])
        for field in percentage_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_percentage(data[field])
        
        # Formater les ratings
        rating_fields = formatting_config.get('rating_fields', ['driver_rating'])
        for field in rating_fields:
            if field in data and data[field] is not None:
                data[field] = self._format_rating(data[field])
        
        return data
    
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
    
    def _format_percentage(self, value: Any) -> str:
        """Formate un pourcentage"""
        try:
            percentage = float(value)
            return f"{percentage:.1f}%"
        except (ValueError, TypeError):
            return "N/A"
    
    def _format_rating(self, value: Any) -> str:
        """Formate un rating avec étoiles"""
        try:
            rating = float(value)
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            return f"{rating:.1f}/5 {stars}"
        except (ValueError, TypeError):
            return "N/A"
    
    def _add_calculated_metrics(self, data: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute des métriques calculées"""
        
        # Calculer le taux de confirmation
        if 'total_bookings' in raw_data and 'confirmed_bookings' in raw_data:
            try:
                total = int(raw_data.get('total_bookings', 0))
                confirmed = int(raw_data.get('confirmed_bookings', 0))
                if total > 0:
                    confirmation_rate = (confirmed / total) * 100
                    data['confirmation_rate'] = f"{confirmation_rate:.1f}%"
                else:
                    data['confirmation_rate'] = "N/A"
            except (ValueError, TypeError):
                data['confirmation_rate'] = "N/A"
        
        # Calculer le taux d'annulation
        if 'total_bookings' in raw_data and 'cancelled_bookings' in raw_data:
            try:
                total = int(raw_data.get('total_bookings', 0))
                cancelled = int(raw_data.get('cancelled_bookings', 0))
                if total > 0:
                    cancellation_rate = (cancelled / total) * 100
                    data['cancellation_rate'] = f"{cancellation_rate:.1f}%"
                else:
                    data['cancellation_rate'] = "N/A"
            except (ValueError, TypeError):
                data['cancellation_rate'] = "N/A"
        
        # Calculer le revenu par passager
        if 'total_revenue' in raw_data and 'confirmed_bookings' in raw_data:
            try:
                revenue = float(raw_data.get('total_revenue', 0))
                passengers = int(raw_data.get('confirmed_bookings', 0))
                if passengers > 0:
                    revenue_per_passenger = revenue / passengers
                    data['revenue_per_passenger'] = f"{revenue_per_passenger:.2f} €"
                else:
                    data['revenue_per_passenger'] = "N/A"
            except (ValueError, TypeError):
                data['revenue_per_passenger'] = "N/A"
        
        # Calculer l'efficacité (revenus/distance)
        if 'total_revenue' in raw_data and 'distance' in raw_data:
            try:
                revenue = float(raw_data.get('total_revenue', 0))
                distance = float(raw_data.get('distance', 0))
                if distance > 0:
                    efficiency = revenue / (distance / 1000)  # €/km
                    data['efficiency'] = f"{efficiency:.2f} €/km"
                else:
                    data['efficiency'] = "N/A"
            except (ValueError, TypeError):
                data['efficiency'] = "N/A"
        
        return data
    
    def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Applique des transformations spécifiques"""
        
        # Ajouter des classes CSS selon les métriques
        if 'confirmation_rate' in data:
            try:
                rate = float(data['confirmation_rate'].replace('%', ''))
                if rate >= 80:
                    data['confirmation_rate_class'] = 'metric-excellent'
                elif rate >= 60:
                    data['confirmation_rate_class'] = 'metric-good'
                elif rate >= 40:
                    data['confirmation_rate_class'] = 'metric-average'
                else:
                    data['confirmation_rate_class'] = 'metric-poor'
            except (ValueError, TypeError):
                data['confirmation_rate_class'] = 'metric-unknown'
        
        # Ajouter des indicateurs de performance
        if 'driver_rating' in data:
            try:
                rating = float(str(data['driver_rating']).split('/')[0])
                if rating >= 4.5:
                    data['driver_performance'] = 'Excellent'
                    data['driver_performance_class'] = 'performance-excellent'
                elif rating >= 4.0:
                    data['driver_performance'] = 'Bon'
                    data['driver_performance_class'] = 'performance-good'
                elif rating >= 3.0:
                    data['driver_performance'] = 'Moyen'
                    data['driver_performance_class'] = 'performance-average'
                else:
                    data['driver_performance'] = 'Faible'
                    data['driver_performance_class'] = 'performance-poor'
            except (ValueError, TypeError):
                data['driver_performance'] = 'N/A'
                data['driver_performance_class'] = 'performance-unknown'
        
        return data
