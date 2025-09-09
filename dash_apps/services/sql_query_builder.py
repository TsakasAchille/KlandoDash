"""
Query Builder générique basé sur la configuration JSON des panneaux
Construit des requêtes SQL dynamiquement à partir de panels_config.json
"""
import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from dash_apps.repositories.repository_factory import RepositoryFactory


class SQLQueryBuilder:
    """Constructeur de requêtes SQL générique basé sur la configuration JSON"""
    
    @staticmethod
    def _load_panel_config():
        """Charge la configuration des panneaux depuis le fichier JSON"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'panels_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[SQL_BUILDER] Erreur chargement panels_config.json: {e}")
            return {}
    
    @staticmethod
    def build_select_query(panel_type: str, trip_id: str) -> Optional[str]:
        """
        Construit une requête SELECT basée sur la configuration du panel
        
        Args:
            panel_type: Type de panel (stats, details, passengers)
            trip_id: ID du trajet pour filtrer
            
        Returns:
            Requête SQL construite ou None si erreur
        """
        config = SQLQueryBuilder._load_panel_config()
        panel_config = config.get(panel_type, {})
        
        if not panel_config or 'sql_config' not in panel_config:
            print(f"[SQL_BUILDER] Configuration SQL manquante pour {panel_type}")
            return None
        
        sql_config = panel_config['sql_config']
        main_table = sql_config.get('main_table')
        joins = sql_config.get('joins', [])
        fields = sql_config.get('fields', {})
        where_conditions = sql_config.get('where_conditions', [])
        
        if not main_table or not fields:
            print(f"[SQL_BUILDER] Configuration incomplète pour {panel_type}")
            return None
        
        # Construire la clause SELECT
        select_parts = []
        group_by_needed = False
        
        for field_key, field_config in fields.items():
            table = field_config.get('table')
            column = field_config.get('column')
            field_type = field_config.get('type')
            
            if field_type == 'count':
                select_parts.append(f"{table}.{column} as {field_key}")
                group_by_needed = field_config.get('group_by', False)
            else:
                select_parts.append(f"{table}.{column} as {field_key}")
        
        select_clause = "SELECT " + ", ".join(select_parts)
        
        # Construire la clause FROM
        from_clause = f"FROM {main_table}"
        
        # Construire les JOINs
        join_clauses = []
        for join in joins:
            join_type = join.get('type', 'LEFT')
            join_table = join.get('table')
            join_condition = join.get('condition')
            join_clauses.append(f"{join_type} JOIN {join_table} ON {join_condition}")
        
        # Construire la clause WHERE
        where_clauses = []
        
        # Ajouter les conditions de base de la config
        for condition in where_conditions:
            where_clauses.append(condition.replace(':trip_id', f"'{trip_id}'"))
        
        # Ajouter la condition trip_id si pas déjà présente
        if main_table == 'trips' and not any(':trip_id' in cond for cond in where_conditions):
            where_clauses.append(f"{main_table}.trip_id = '{trip_id}'")
        elif main_table != 'trips' and not any(':trip_id' in cond for cond in where_conditions):
            # Pour les autres tables, chercher une colonne trip_id
            where_clauses.append(f"{main_table}.trip_id = '{trip_id}'")
        
        # Assembler la requête
        query_parts = [select_clause, from_clause]
        query_parts.extend(join_clauses)
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        if group_by_needed:
            # Grouper par les colonnes non-agrégées
            non_aggregate_fields = []
            for field_key, field_config in fields.items():
                if field_config.get('type') != 'count':
                    table = field_config.get('table')
                    column = field_config.get('column')
                    non_aggregate_fields.append(f"{table}.{column}")
            
            if non_aggregate_fields:
                query_parts.append("GROUP BY " + ", ".join(non_aggregate_fields))
        
        return "\n".join(query_parts)
    
    @staticmethod
    def execute_panel_query(panel_type: str, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Exécute la requête pour un panel et retourne les données formatées
        
        Args:
            panel_type: Type de panel
            trip_id: ID du trajet
            
        Returns:
            Dictionnaire avec les données ou None si erreur
        """
        query = SQLQueryBuilder.build_select_query(panel_type, trip_id)
        if not query:
            return None
        
        try:
            # Utiliser directement une session SQLAlchemy
            from dash_apps.core.database import SessionLocal
            
            with SessionLocal() as session:
                result = session.execute(text(query))
                row = result.fetchone()
                
                if not row:
                    print(f"[SQL_BUILDER] Aucun résultat pour {panel_type} trip_id={trip_id}")
                    return None
                
                # Convertir en dictionnaire
                data = dict(row._mapping)
            
            # Appliquer le formatage basé sur la config
            config = SQLQueryBuilder._load_panel_config()
            panel_config = config.get(panel_type, {})
            fields_config = panel_config.get('sql_config', {}).get('fields', {})
            
            formatted_data = {}
            for field_key, value in data.items():
                field_config = fields_config.get(field_key, {})
                field_type = field_config.get('type')
                unit = field_config.get('unit')
                values_mapping = field_config.get('values', {})
                
                # Appliquer le formatage selon le type
                if field_type == 'currency' and unit:
                    formatted_data[field_key] = f"{value} {unit}"
                elif field_type == 'enum' and values_mapping:
                    formatted_data[field_key] = values_mapping.get(str(value), value)
                else:
                    formatted_data[field_key] = value
                
                # Ajouter aussi le label
                label = field_config.get('label', field_key)
                formatted_data[f"{field_key}_label"] = label
            
            return formatted_data
            
        except Exception as e:
            print(f"[SQL_BUILDER] Erreur exécution requête {panel_type}: {e}")
            return None
    
    @staticmethod
    def execute_raw_query(query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Exécute une requête SQL brute et retourne les résultats
        
        Args:
            query: Requête SQL à exécuter
            
        Returns:
            Liste de dictionnaires représentant les résultats ou None en cas d'erreur
        """
        try:
            trip_repository = RepositoryFactory.get_trip_repository()
            
            # Vérifier si c'est un repository REST
            if hasattr(trip_repository, 'table_name'):
                print("[SQL_BUILDER] Repository REST détecté - requêtes SQL non supportées")
                return None
            
            # Repository SQL - utiliser la session
            if hasattr(trip_repository, 'session'):
                result = trip_repository.session.execute(text(query))
                rows = result.fetchall()
                
                if not rows:
                    return []
                
                return [dict(row._mapping) for row in rows]
            else:
                # Fallback: utiliser directement une session SQLAlchemy
                from dash_apps.core.database import SessionLocal
                
                with SessionLocal() as session:
                    result = session.execute(text(query))
                    rows = result.fetchall()
                    
                    if not rows:
                        return []
                    
                    return [dict(row._mapping) for row in rows]
                
        except Exception as e:
            print(f"[SQL_BUILDER] Erreur exécution requête brute: {e}")
            return None
    
    @staticmethod
    def get_panel_data_via_sql(panel_type: str, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Point d'entrée principal pour récupérer les données d'un panel via SQL
        
        Args:
            panel_type: Type de panel (stats, details, passengers)
            trip_id: ID du trajet
            
        Returns:
            Données formatées du panel ou None si erreur
        """
        print(f"[SQL_BUILDER] Récupération données {panel_type} pour trip {trip_id[:8]}...")
        return SQLQueryBuilder.execute_panel_query(panel_type, trip_id)
