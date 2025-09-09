#!/usr/bin/env python3
"""
Script de test pour récupérer les données de trajets depuis PostgreSQL
en utilisant les configurations des panneaux
"""

import sys
import os
import json
import pandas as pd
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_panel_config():
    """Charge la configuration des panneaux depuis le fichier JSON"""
    config_path = os.path.join('dash_apps', 'config', 'panels_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur chargement panels_config.json: {e}")
        return {}

def get_postgres_connection():
    """Établit une connexion PostgreSQL avec les paramètres d'environnement"""
    try:
        # Paramètres de connexion depuis les variables d'environnement
        connection_params = {
            'host': os.getenv('SUPABASE_DB_HOST', 'aws-0-eu-west-3.pooler.supabase.com'),
            'port': os.getenv('SUPABASE_DB_PORT', '5432'),
            'database': os.getenv('SUPABASE_DB_NAME', 'postgres'),
            'user': os.getenv('SUPABASE_DB_USER', 'postgres.qvvlwqkrqnmqgkqvlnlq'),
            'password': os.getenv('SUPABASE_DB_PASSWORD', ''),
            'connect_timeout': 10,
            'application_name': 'KlandoDash_Test'
        }
        
        print(f"🔌 Tentative de connexion à PostgreSQL...")
        print(f"   Host: {connection_params['host']}")
        print(f"   Port: {connection_params['port']}")
        print(f"   Database: {connection_params['database']}")
        print(f"   User: {connection_params['user']}")
        
        conn = psycopg2.connect(**connection_params)
        conn.set_session(autocommit=True)
        
        print("✅ Connexion PostgreSQL établie avec succès")
        return conn
        
    except Exception as e:
        print(f"❌ Erreur de connexion PostgreSQL: {e}")
        return None

def build_sql_query_from_config(panel_name: str, panel_config: dict, trip_id: str) -> Optional[str]:
    """Construit une requête SQL à partir de la configuration du panneau"""
    try:
        sql_config = panel_config.get('methods', {}).get('data_fetcher', {}).get('sql_config', {})
        
        if not sql_config:
            print(f"⚠️  Pas de configuration SQL pour {panel_name}")
            return None
        
        # Éléments de la requête
        main_table = sql_config.get('main_table')
        joins = sql_config.get('joins', [])
        fields = sql_config.get('fields', {})
        where_conditions = sql_config.get('where_conditions', [])
        filters = sql_config.get('filters', {})
        
        # Construire SELECT
        select_parts = []
        for field_key, field_config in fields.items():
            table = field_config.get('table', main_table)
            column = field_config.get('column')
            
            # Gérer les fonctions d'agrégation
            if column == 'COUNT(*)':
                select_parts.append(f"COUNT(*) as {field_key}")
            else:
                select_parts.append(f"{table}.{column} as {field_key}")
        
        if not select_parts:
            select_clause = "SELECT *"
        else:
            select_clause = "SELECT " + ", ".join(select_parts)
        
        # Construire FROM avec JOINs
        from_clause = f"FROM {main_table}"
        for join in joins:
            join_table = join.get('table')
            join_condition = join.get('condition')
            join_type = join.get('type', 'LEFT')
            from_clause += f"\n{join_type} JOIN {join_table} ON {join_condition}"
        
        # Construire WHERE
        where_parts = []
        for condition in where_conditions:
            condition_with_value = condition.replace(':trip_id', f"'{trip_id}'")
            where_parts.append(condition_with_value)
        
        # Ajouter les filtres
        for filter_key, filter_config in filters.items():
            if filter_key == 'trip_id':
                column = filter_config.get('column')
                operator = filter_config.get('operator', '=')
                where_parts.append(f"{column} {operator} '{trip_id}'")
        
        where_clause = ""
        if where_parts:
            where_clause = "WHERE " + " AND ".join(where_parts)
        
        # Requête complète
        full_query = f"{select_clause}\n{from_clause}"
        if where_clause:
            full_query += f"\n{where_clause}"
        
        # Ajouter GROUP BY si nécessaire (pour les COUNT)
        group_by_fields = []
        for field_key, field_config in fields.items():
            if field_config.get('group_by'):
                continue  # Skip les champs d'agrégation
            if field_config.get('column') != 'COUNT(*)':
                table = field_config.get('table', main_table)
                column = field_config.get('column')
                group_by_fields.append(f"{table}.{column}")
        
        # Ajouter GROUP BY seulement s'il y a des fonctions d'agrégation
        has_aggregation = any(field.get('column') == 'COUNT(*)' for field in fields.values())
        if has_aggregation and group_by_fields:
            full_query += f"\nGROUP BY " + ", ".join(group_by_fields)
        
        return full_query
        
    except Exception as e:
        print(f"❌ Erreur construction requête pour {panel_name}: {e}")
        return None

def execute_sql_query(conn, query: str, panel_name: str) -> Optional[List[Dict]]:
    """Exécute une requête SQL et retourne les résultats"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            print(f"\n🔍 Exécution requête {panel_name}:")
            print(f"📋 {query}")
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convertir en liste de dictionnaires
            data = [dict(row) for row in results]
            
            print(f"✅ {len(data)} résultat(s) trouvé(s)")
            return data
            
    except Exception as e:
        print(f"❌ Erreur exécution requête {panel_name}: {e}")
        return None

def format_panel_data(data: List[Dict], panel_config: dict, panel_name: str) -> List[Dict]:
    """Formate les données selon la configuration du panneau"""
    try:
        sql_config = panel_config.get('methods', {}).get('data_fetcher', {}).get('sql_config', {})
        fields_config = sql_config.get('fields', {})
        
        formatted_results = []
        
        for row in data:
            formatted_row = {}
            
            for field_key, value in row.items():
                field_config = fields_config.get(field_key, {})
                field_type = field_config.get('type')
                unit = field_config.get('unit')
                values_mapping = field_config.get('values', {})
                label = field_config.get('label', field_key)
                
                # Appliquer le formatage selon le type
                formatted_value = value
                if field_type == 'currency' and unit and value is not None:
                    formatted_value = f"{value} {unit}"
                elif field_type == 'enum' and values_mapping and value is not None:
                    formatted_value = values_mapping.get(str(value), value)
                elif field_type == 'datetime' and value is not None:
                    if isinstance(value, str):
                        try:
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            formatted_value = dt.strftime('%d/%m/%Y %H:%M')
                        except:
                            formatted_value = value
                
                formatted_row[field_key] = {
                    'label': label,
                    'value': formatted_value,
                    'raw_value': value,
                    'type': field_type
                }
            
            formatted_results.append(formatted_row)
        
        return formatted_results
        
    except Exception as e:
        print(f"❌ Erreur formatage données {panel_name}: {e}")
        return data

def test_panel_data_retrieval(panel_name: str, panel_config: dict, trip_id: str, conn) -> bool:
    """Test complet de récupération des données pour un panneau"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST PANNEAU: {panel_name.upper()}")
    print(f"{'='*60}")
    
    # Informations du panneau
    description = panel_config.get('description', 'Aucune description')
    print(f"📝 Description: {description}")
    
    # Construire la requête SQL
    query = build_sql_query_from_config(panel_name, panel_config, trip_id)
    if not query:
        print(f"❌ Impossible de construire la requête pour {panel_name}")
        return False
    
    # Exécuter la requête
    raw_data = execute_sql_query(conn, query, panel_name)
    if raw_data is None:
        print(f"❌ Échec de l'exécution de la requête pour {panel_name}")
        return False
    
    if not raw_data:
        print(f"⚠️  Aucune donnée trouvée pour {panel_name}")
        return True  # Pas d'erreur, juste pas de données
    
    # Formater les données
    formatted_data = format_panel_data(raw_data, panel_config, panel_name)
    
    # Afficher les résultats
    print(f"\n📊 DONNÉES RÉCUPÉRÉES ({len(formatted_data)} enregistrement(s)):")
    for i, row in enumerate(formatted_data):
        print(f"\n📋 Enregistrement {i+1}:")
        for field_key, field_data in row.items():
            label = field_data.get('label', field_key)
            value = field_data.get('value')
            field_type = field_data.get('type', 'string')
            print(f"  {label}: {value} ({field_type})")
    
    print(f"\n✅ SUCCÈS - Panneau {panel_name} traité avec succès")
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Script de Test PostgreSQL - Données Trajets")
    print("=" * 60)
    
    # Charger la configuration
    config = load_panel_config()
    if not config:
        print("❌ Impossible de charger la configuration des panneaux")
        return False
    
    print(f"✅ Configuration chargée: {len(config)} panneaux")
    
    # Établir la connexion PostgreSQL
    conn = get_postgres_connection()
    if not conn:
        print("❌ Impossible de se connecter à PostgreSQL")
        return False
    
    # ID de trajet de test (vous pouvez le changer)
    test_trip_ids = [
        "TRIP-1756910377933763-bk17O0BBAndQR7xxSZxDvAGkSWU2",
        "TRIP-1756507938116116-bk17O0BBAndQR7xxSZxDvAGkSWU2",
        "TRIP-1756361288826038-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
    ]
    
    # Tester avec le premier ID disponible
    test_trip_id = test_trip_ids[0]
    print(f"🎯 Trajet de test: {test_trip_id}")
    
    # Tester chaque panneau
    results = {}
    for panel_name, panel_config in config.items():
        try:
            success = test_panel_data_retrieval(panel_name, panel_config, test_trip_id, conn)
            results[panel_name] = success
        except Exception as e:
            print(f"❌ Erreur critique pour {panel_name}: {e}")
            results[panel_name] = False
    
    # Fermer la connexion
    conn.close()
    print(f"\n🔌 Connexion PostgreSQL fermée")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    total_panels = len(results)
    successful_panels = sum(results.values())
    
    for panel_name, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{panel_name:.<30} {status}")
    
    print(f"\nRésultat global: {successful_panels}/{total_panels} panneaux fonctionnels")
    
    if successful_panels == total_panels:
        print("🎉 Tous les panneaux fonctionnent avec PostgreSQL!")
    elif successful_panels > 0:
        print("⚠️  Certains panneaux nécessitent des corrections")
    else:
        print("❌ Aucun panneau ne fonctionne correctement")
    
    return successful_panels == total_panels

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
