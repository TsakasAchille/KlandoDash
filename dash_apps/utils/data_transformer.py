"""
Classe générique de transformation de données basée sur les schémas SQL existants.
Valide les colonnes contre le schéma et applique les transformations configurées.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

from dash_apps.utils.data_schema_rest import load_table_definition, get_type_mapping

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transformateur de données générique avec validation de schéma."""
    
    def __init__(self, table_name: str):
        """Initialise le transformateur pour une table donnée."""
        self.table_name = table_name
        self._schema = self._load_schema()
        self._transformers = self._register_transformers()
    
    def _load_schema(self) -> Dict[str, str]:
        """Charge le schéma de la table depuis les définitions JSON."""
        table_def = load_table_definition(self.table_name)
        return {col["column_name"]: col["data_type"] for col in table_def}
    
    def _register_transformers(self) -> Dict[str, callable]:
        """Enregistre les méthodes de transformation disponibles."""
        return {
            "from_iso": self._transform_from_iso,
            "currency": self._transform_currency,
            "enum_badge": self._transform_enum_badge,
            "truncate": self._transform_truncate,
            "format_number": self._transform_format_number,
        }
    
    def validate_column(self, column_name: str) -> bool:
        """Vérifie qu'une colonne existe dans le schéma de la table."""
        exists = column_name in self._schema
        if not exists:
            logger.warning(f"Colonne '{column_name}' non trouvée dans le schéma de '{self.table_name}'")
            logger.info(f"Colonnes disponibles: {list(self._schema.keys())}")
        return exists
    
    def get_column_type(self, column_name: str) -> Optional[str]:
        """Retourne le type SQL d'une colonne."""
        return self._schema.get(column_name)
    
    def validate_transform(self, transform_config: Dict[str, Any]) -> bool:
        """Vérifie qu'une configuration de transformation est supportée."""
        transform_type = transform_config.get("type")
        if not transform_type:
            return False
        
        supported = transform_type in self._transformers
        if not supported:
            logger.warning(f"Type de transformation '{transform_type}' non supporté")
            logger.info(f"Types supportés: {list(self._transformers.keys())}")
        
        return supported
    
    def transform_value(self, column_name: str, value: Any, transform_config: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
        """
        Transforme une valeur selon la configuration donnée.
        
        Returns:
            Tuple (transformed_value, metadata)
        """
        # Validation de la colonne
        if not self.validate_column(column_name):
            return str(value) if value is not None else "-", {}
        
        # Validation de la transformation
        if not self.validate_transform(transform_config):
            return str(value) if value is not None else "-", {}
        
        # Application de la transformation
        transform_type = transform_config["type"]
        transformer = self._transformers[transform_type]
        
        try:
            return transformer(value, transform_config)
        except Exception as e:
            logger.error(f"Erreur lors de la transformation {transform_type} pour {column_name}: {e}")
            return str(value) if value is not None else "-", {}
    
    def _transform_from_iso(self, value: Any, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Transforme un timestamp ISO en date/time formaté."""
        output = config.get("output", "datetime")  # date | time | datetime
        fmt = config.get("format")  # format strftime optionnel
        
        if not isinstance(value, str) or not value:
            return "-", {}
        
        try:
            # Parser le timestamp ISO
            if "T" in value:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            else:
                # Déjà formaté ou format non-ISO
                return value, {}
            
            # Appliquer le format
            if fmt:
                formatted = dt.strftime(fmt)
            elif output == "date":
                formatted = dt.date().isoformat()
            elif output == "time":
                formatted = dt.strftime("%H:%M")
            else:  # datetime
                formatted = dt.isoformat()
            
            return formatted, {}
        
        except Exception as e:
            logger.debug(f"Erreur parsing ISO '{value}': {e}")
            return str(value), {}
    
    def _transform_currency(self, value: Any, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Transforme une valeur numérique en format monétaire."""
        unit = config.get("unit", "")
        
        if value in (None, ""):
            return "-", {}
        
        try:
            # Convertir en nombre si nécessaire
            if isinstance(value, str):
                value = float(value)
            
            formatted = f"{value} {unit}".strip()
            return formatted, {}
        
        except (ValueError, TypeError):
            return str(value), {}
    
    def _transform_enum_badge(self, value: Any, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Transforme une valeur enum en badge avec couleur."""
        values_map = config.get("values", {})
        color_map = config.get("colors", {
            "PENDING": "warning",
            "CONFIRMED": "success", 
            "CANCELED": "danger",
            "COMPLETED": "secondary"
        })
        
        if not value:
            return "Inconnu", {"as_badge": True, "badge_color": "secondary"}
        
        value_upper = str(value).upper()
        label = values_map.get(value_upper, str(value))
        color = color_map.get(value_upper, "secondary")
        
        return label, {"as_badge": True, "badge_color": color}
    
    def _transform_truncate(self, value: Any, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Tronque une chaîne à la longueur spécifiée."""
        max_length = config.get("max_length", 50)
        
        if not value:
            return "-", {}
        
        text = str(value)
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text, {}
    
    def _transform_format_number(self, value: Any, config: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Formate un nombre selon les spécifications."""
        decimals = config.get("decimals", 0)
        
        if value in (None, ""):
            return "-", {}
        
        try:
            if isinstance(value, str):
                value = float(value)
            
            if decimals > 0:
                formatted = f"{value:.{decimals}f}"
            else:
                formatted = str(int(value))
            
            return formatted, {}
        
        except (ValueError, TypeError):
            return str(value), {}


class TableConfigValidator:
    """Validateur de configuration de tableau basé sur les schémas."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.transformer = DataTransformer(table_name)
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide une configuration de tableau complète.
        
        Returns:
            Tuple (is_valid, error_messages)
        """
        errors = []
        columns_config = config.get("columns", {})
        
        for col_name, col_config in columns_config.items():
            # Vérifier que la colonne existe
            if not self.transformer.validate_column(col_name):
                errors.append(f"Colonne '{col_name}' inexistante dans le schéma")
                continue
            
            # Vérifier les transformations si présentes
            transform_config = col_config.get("transform")
            if transform_config:
                if not self.transformer.validate_transform(transform_config):
                    errors.append(f"Transformation invalide pour '{col_name}': {transform_config}")
        
        return len(errors) == 0, errors
    
    def get_available_columns(self) -> Dict[str, str]:
        """Retourne toutes les colonnes disponibles avec leurs types."""
        return self.transformer._schema.copy()
