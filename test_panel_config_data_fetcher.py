#!/usr/bin/env python3
"""
Script de test pour valider les configurations de panneaux et récupérer les données
Utilise les configurations JSON pour faire des requêtes et afficher les résultats
"""

import sys
import os
import json
import pandas as pd
from typing import Dict, Any, Optional

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

def test_sql_fetcher(panel_name: str, panel_config: dict, trip_id: str):
    """Test du fetcher SQL pour un panneau donné"""
    print(f"\n=== Test SQL Fetcher pour {panel_name} ===")
    
    try:
        data_fetcher = panel_config.get('methods', {}).get('data_fetcher', {})
        sql_config = data_fetcher.get('sql_config', {})
        
        if not sql_config:
            print(f"✗ Pas de configuration SQL pour {panel_name}")
            return None
        
        # Construire la requête SQL
        main_table = sql_config.get('main_table')
        joins = sql_config.get('joins', [])
        fields = sql_config.get('fields', {})  # Utiliser 'fields' au lieu de 'columns'
        where_conditions = sql_config.get('where_conditions', [])
        filters = sql_config.get('filters', {})
        
        print(f"✓ Table principale: {main_table}")
        print(f"✓ Jointures: {len(joins)} tables")
        print(f"✓ Champs: {len(fields)} champs")
        print(f"✓ Conditions WHERE: {len(where_conditions)} conditions")
        print(f"✓ Filtres: {len(filters)} filtres")
        
        # Construire SELECT
        select_parts = []
        for field_key, field_config in fields.items():
            table = field_config.get('table', main_table)
            column = field_config.get('column')
            alias = f"{field_key}"
            select_parts.append(f"{table}.{column} as {alias}")
        
        if not select_parts:
            print("⚠️  Aucun champ défini, utilisation de SELECT *")
            select_clause = "SELECT *"
        else:
            select_clause = "SELECT " + ", ".join(select_parts)
        
        # Construire FROM avec JOINs
        from_clause = f"FROM {main_table}"
        for join in joins:
            join_table = join.get('table')
            join_condition = join.get('condition')  # Utiliser 'condition' au lieu de 'on'
            join_type = join.get('type', 'LEFT')
            from_clause += f"\n{join_type} JOIN {join_table} ON {join_condition}"
        
        # Construire WHERE à partir des where_conditions
        where_parts = []
        for condition in where_conditions:
            # Remplacer :trip_id par la valeur réelle
            condition_with_value = condition.replace(':trip_id', f"'{trip_id}'")
            where_parts.append(condition_with_value)
        
        # Ajouter les filtres si définis
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
        
        print(f"\n📋 Requête SQL générée:")
        print(f"{full_query}")
        
        # Tester l'exécution avec le repository
        from dash_apps.repositories.repository_factory import RepositoryFactory
        from sqlalchemy import text
        
        trip_repository = RepositoryFactory.get_trip_repository()
        repo_type = type(trip_repository).__name__
        
        print(f"\n🔧 Repository utilisé: {repo_type}")
        
        if hasattr(trip_repository, 'session'):
            print("✓ Repository SQL avec session - Exécution de la requête...")
            try:
                result = trip_repository.session.execute(text(full_query))
                rows = result.fetchall()
                
                if rows:
                    print(f"✓ {len(rows)} résultat(s) trouvé(s)")
                    
                    # Afficher les données
                    for i, row in enumerate(rows):
                        print(f"\n📊 Résultat {i+1}:")
                        row_dict = dict(row._mapping)
                        for key, value in row_dict.items():
                            field_config = fields.get(key, {})
                            label = field_config.get('label', key)
                            print(f"  {label}: {value}")
                    
                    return rows[0] if rows else None
                else:
                    print("⚠️  Aucun résultat trouvé")
                    return None
                    
            except Exception as e:
                print(f"✗ Erreur exécution SQL: {e}")
                return None
        else:
            print("⚠️  Repository REST - Requêtes SQL non supportées")
            return None
            
    except Exception as e:
        print(f"✗ Erreur dans test_sql_fetcher: {e}")
        return None

def test_rest_fetcher(panel_name: str, panel_config: dict, trip_id: str):
    """Test du fetcher REST pour un panneau donné"""
    print(f"\n=== Test REST Fetcher pour {panel_name} ===")
    
    try:
        data_fetcher = panel_config.get('methods', {}).get('data_fetcher', {})
        rest_config = data_fetcher.get('rest_config', {})
        
        if not rest_config:
            print(f"✗ Pas de configuration REST pour {panel_name}")
            return None
        
        api_module = rest_config.get('api_module')
        api_function = rest_config.get('api_function')
        
        print(f"✓ Module API: {api_module}")
        print(f"✓ Fonction API: {api_function}")
        
        # Tester l'import et l'exécution
        try:
            module = __import__(api_module, fromlist=[api_function])
            api_func = getattr(module, api_function)
            
            print(f"✓ Fonction importée avec succès")
            
            # Exécuter la fonction
            print(f"🔄 Exécution: {api_function}('{trip_id}')")
            result = api_func(trip_id)
            
            if result is not None:
                print(f"✓ Résultat obtenu: {type(result)}")
                
                # Afficher les données selon le type
                if isinstance(result, pd.DataFrame):
                    print(f"📊 DataFrame: {len(result)} lignes, {len(result.columns)} colonnes")
                    if not result.empty:
                        print("Colonnes:", list(result.columns))
                        print("Premier enregistrement:")
                        for col in result.columns:
                            print(f"  {col}: {result.iloc[0][col]}")
                elif isinstance(result, dict):
                    print(f"📊 Dictionnaire: {len(result)} clés")
                    for key, value in result.items():
                        print(f"  {key}: {value}")
                elif isinstance(result, list):
                    print(f"📊 Liste: {len(result)} éléments")
                    if result:
                        print(f"Premier élément: {result[0]}")
                else:
                    print(f"📊 Données: {result}")
                
                return result
            else:
                print("⚠️  Aucun résultat retourné")
                return None
                
        except ImportError as e:
            print(f"✗ Erreur import module {api_module}: {e}")
            return None
        except AttributeError as e:
            print(f"✗ Fonction {api_function} non trouvée: {e}")
            return None
        except Exception as e:
            print(f"✗ Erreur exécution API: {e}")
            return None
            
    except Exception as e:
        print(f"✗ Erreur dans test_rest_fetcher: {e}")
        return None

def test_panel_configuration(panel_name: str, panel_config: dict, trip_id: str):
    """Test complet d'un panneau avec sa configuration"""
    print(f"\n{'='*60}")
    print(f"TEST PANNEAU: {panel_name.upper()}")
    print(f"{'='*60}")
    
    # Informations générales
    description = panel_config.get('description', 'Aucune description')
    print(f"📝 Description: {description}")
    
    methods = panel_config.get('methods', {})
    if not methods:
        print("✗ Aucune méthode configurée")
        return False
    
    # Configuration cache
    cache_config = methods.get('cache', {})
    if cache_config:
        print(f"💾 Cache HTML: {'✓' if cache_config.get('html_cache_enabled') else '✗'}")
        print(f"💾 Cache Redis: {'✓' if cache_config.get('redis_cache_enabled') else '✗'}")
        print(f"💾 TTL: {cache_config.get('cache_ttl', 'Non défini')}s")
    
    # Configuration data fetcher
    data_fetcher = methods.get('data_fetcher', {})
    if not data_fetcher:
        print("✗ Aucun data fetcher configuré")
        return False
    
    fetcher_type = data_fetcher.get('type')
    print(f"🔧 Type de fetcher: {fetcher_type}")
    
    # Tester selon le type
    result = None
    if fetcher_type == 'sql':
        result = test_sql_fetcher(panel_name, panel_config, trip_id)
    elif fetcher_type == 'rest':
        result = test_rest_fetcher(panel_name, panel_config, trip_id)
    else:
        print(f"✗ Type de fetcher non supporté: {fetcher_type}")
        return False
    
    # Configuration renderer
    renderer_config = methods.get('renderer', {})
    if renderer_config:
        print(f"\n🎨 Renderer configuré:")
        print(f"  Module: {renderer_config.get('module')}")
        print(f"  Fonction: {renderer_config.get('function')}")
        print(f"  Inputs requis: {renderer_config.get('required_inputs', [])}")
    
    success = result is not None
    print(f"\n{'✓ SUCCÈS' if success else '✗ ÉCHEC'} - Panneau {panel_name}")
    
    return success

def main():
    """Fonction principale de test"""
    print("Script de Test des Configurations de Panneaux")
    print("=" * 60)
    
    # Charger la configuration
    config = load_panel_config()
    if not config:
        print("✗ Impossible de charger la configuration")
        return False
    
    print(f"✓ Configuration chargée: {len(config)} panneaux")
    
    # ID de trajet de test
    test_trip_id = "TRIP-1756910377933763-bk17O0BBAndQR7xxSZxDvAGkSWU2"
    print(f"🎯 Trajet de test: {test_trip_id}")
    
    # Tester chaque panneau
    results = {}
    for panel_name, panel_config in config.items():
        try:
            success = test_panel_configuration(panel_name, panel_config, test_trip_id)
            results[panel_name] = success
        except Exception as e:
            print(f"✗ Erreur critique pour {panel_name}: {e}")
            results[panel_name] = False
    
    # Résumé final
    print(f"\n{'='*60}")
    print("RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    total_panels = len(results)
    successful_panels = sum(results.values())
    
    for panel_name, success in results.items():
        status = "✓ RÉUSSI" if success else "✗ ÉCHOUÉ"
        print(f"{panel_name:.<30} {status}")
    
    print(f"\nRésultat global: {successful_panels}/{total_panels} panneaux fonctionnels")
    
    if successful_panels == total_panels:
        print("🎉 Tous les panneaux sont correctement configurés!")
    elif successful_panels > 0:
        print("⚠️  Certains panneaux nécessitent des corrections")
    else:
        print("❌ Aucun panneau ne fonctionne correctement")
    
    return successful_panels == total_panels

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
