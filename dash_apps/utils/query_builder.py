"""
Query Builder pour construire des requêtes SQL dynamiques à partir de QuerySpec JSON
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Constructeur de requêtes SQL à partir de spécifications JSON"""
    
    def __init__(self, query_spec: Dict[str, Any], field_mappings: Dict[str, str]):
        self.query_spec = query_spec
        self.field_mappings = field_mappings
    
    def build_query(self, query_name: str, parameters: Dict[str, Any] = None, 
                   dynamic_fields: List[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Construit une requête SQL à partir du nom de la query et des paramètres
        
        Args:
            query_name: Nom de la requête dans le QuerySpec
            parameters: Paramètres à injecter dans la requête
            dynamic_fields: Liste des champs dynamiques à sélectionner
            
        Returns:
            Tuple (sql_query, query_params)
        """
        if query_name not in self.query_spec:
            raise ValueError(f"Query '{query_name}' not found in spec")
        
        spec = self.query_spec[query_name]
        parameters = parameters or {}
        dynamic_fields = dynamic_fields or []
        
        # Construire la clause SELECT
        select_clause = self._build_select_clause(spec, dynamic_fields)
        
        # Construire la clause FROM
        from_clause = self._build_from_clause(spec)
        
        # Construire les JOINs
        join_clause = self._build_join_clause(spec)
        
        # Construire la clause WHERE
        where_clause, query_params = self._build_where_clause(spec, parameters)
        
        # Construire la clause LIMIT
        limit_clause = self._build_limit_clause(spec)
        
        # Assembler la requête
        query_parts = [
            f"SELECT {select_clause}",
            f"FROM {from_clause}",
            join_clause,
            where_clause,
            limit_clause
        ]
        
        sql_query = " ".join(filter(None, query_parts))
        
        logger.debug(f"Built query for '{query_name}': {sql_query}")
        logger.debug(f"Query params: {query_params}")
        
        return sql_query, query_params
    
    def _build_select_clause(self, spec: Dict[str, Any], dynamic_fields: List[str]) -> str:
        """Construit la clause SELECT"""
        select_config = spec.get('select', {})
        
        # Champs de base obligatoires
        base_fields = select_config.get('base', [])
        
        # Champs dynamiques mappés
        mapped_dynamic_fields = []
        for field in dynamic_fields:
            if field in self.field_mappings:
                db_column = self.field_mappings[field]
                # Ajouter l'alias de table si nécessaire
                if '.' not in db_column and self._has_joins(spec):
                    primary_table = spec.get('tables', {}).get('primary', '')
                    if primary_table:
                        db_column = f"{primary_table}.{db_column}"
                mapped_dynamic_fields.append(db_column)
        
        # Combiner tous les champs
        all_fields = base_fields + mapped_dynamic_fields
        
        # Supprimer les doublons tout en préservant l'ordre
        unique_fields = []
        seen = set()
        for field in all_fields:
            if field not in seen:
                unique_fields.append(field)
                seen.add(field)
        
        return ", ".join(unique_fields) if unique_fields else "*"
    
    def _build_from_clause(self, spec: Dict[str, Any]) -> str:
        """Construit la clause FROM"""
        tables = spec.get('tables', {})
        primary_table = tables.get('primary', '')
        
        if not primary_table:
            raise ValueError("Primary table not specified in query spec")
        
        return primary_table
    
    def _build_join_clause(self, spec: Dict[str, Any]) -> str:
        """Construit les clauses JOIN"""
        joins = spec.get('joins', [])
        if not joins:
            return ""
        
        join_parts = []
        for join in joins:
            join_type = join.get('type', 'inner').upper()
            table = join.get('table', '')
            alias = join.get('alias', '')
            on_condition = join.get('on', '')
            
            if not table or not on_condition:
                continue
            
            table_part = f"{table} {alias}" if alias else table
            join_parts.append(f"{join_type} JOIN {table_part} ON {on_condition}")
        
        return " ".join(join_parts)
    
    def _build_where_clause(self, spec: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Construit la clause WHERE avec paramètres"""
        where_config = spec.get('where', {})
        if not where_config:
            return "", {}
        
        conditions = []
        query_params = {}
        param_counter = 0
        
        for column, value_template in where_config.items():
            # Remplacer les templates par les paramètres
            if isinstance(value_template, str) and value_template.startswith('{{') and value_template.endswith('}}'):
                param_name = value_template[2:-2]  # Enlever {{ et }}
                if param_name in parameters:
                    param_key = f"param_{param_counter}"
                    conditions.append(f"{column} = %({param_key})s")
                    query_params[param_key] = parameters[param_name]
                    param_counter += 1
            else:
                # Valeur littérale
                param_key = f"param_{param_counter}"
                conditions.append(f"{column} = %({param_key})s")
                query_params[param_key] = value_template
                param_counter += 1
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        return where_clause, query_params
    
    def _build_limit_clause(self, spec: Dict[str, Any]) -> str:
        """Construit la clause LIMIT"""
        limit = spec.get('limit')
        if limit:
            return f"LIMIT {limit}"
        return ""
    
    def _has_joins(self, spec: Dict[str, Any]) -> bool:
        """Vérifie si la requête a des JOINs"""
        return bool(spec.get('joins', []))
    
    def get_mapped_fields(self, config_fields: List[str]) -> List[str]:
        """
        Mappe les champs de configuration vers les colonnes de base de données
        
        Args:
            config_fields: Liste des champs de configuration
            
        Returns:
            Liste des colonnes de base de données correspondantes
        """
        mapped_fields = []
        for field in config_fields:
            if field in self.field_mappings:
                mapped_fields.append(self.field_mappings[field])
        return mapped_fields
