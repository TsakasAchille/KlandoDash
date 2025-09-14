#!/usr/bin/env python3
"""
Script de test pour charger la configuration du panel trip details depuis le JSON
Test simple pour valider le chargement et l'affichage de la config
"""

import json
import os
import sys

def load_panel_config():
    """Charge la configuration des panneaux depuis le fichier JSON"""
    config_path = os.path.join('dash_apps', 'config', 'panels_config.json')
    
    print(f"[TEST] Tentative de chargement du fichier: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"[ERROR] Fichier non trouvé: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"[SUCCESS] Configuration chargée avec succès")
        return config
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement: {e}")
        return None

def test_details_panel_config():
    """Test spécifique pour la configuration du panel details"""
    print("=" * 60)
    print("TEST: Configuration du panel 'details'")
    print("=" * 60)
    
    # Charger la config
    config = load_panel_config()
    if not config:
        return False
    
    # Vérifier que le panel details existe
    if 'details' not in config:
        print("[ERROR] Panel 'details' non trouvé dans la configuration")
        return False
    
    details_config = config['details']
    print(f"[INFO] Configuration 'details' trouvée")
    
    # Vérifier les champs requis
    required_fields = [
        'description',
        'cache_ttl', 
        'redis_key_prefix',
        'renderer_function',
        'renderer_module',
        'data_source'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in details_config:
            missing_fields.append(field)
        else:
            print(f"[OK] {field}: {details_config[field]}")
    
    if missing_fields:
        print(f"[ERROR] Champs manquants: {missing_fields}")
        return False
    
    # Vérifier la configuration SQL si data_source = sql
    data_source = details_config.get('data_source')
    print(f"\n[INFO] Source de données: {data_source}")
    
    if data_source == 'sql':
        if 'sql_config' not in details_config:
            print("[ERROR] sql_config manquant pour data_source=sql")
            return False
        
        sql_config = details_config['sql_config']
        print("[INFO] Configuration SQL:")
        
        # Vérifier les champs SQL
        sql_required = ['main_table', 'fields']
        for field in sql_required:
            if field not in sql_config:
                print(f"[ERROR] Champ SQL manquant: {field}")
                return False
            else:
                print(f"  [OK] {field}: {type(sql_config[field])}")
        
        # Afficher les champs configurés
        fields = sql_config.get('fields', {})
        print(f"  [INFO] Nombre de champs configurés: {len(fields)}")
        for field_name, field_config in fields.items():
            table = field_config.get('table', 'N/A')
            column = field_config.get('column', 'N/A')
            print(f"    - {field_name}: {table}.{column}")
    
    elif data_source == 'rest':
        if 'rest_config' not in details_config:
            print("[ERROR] rest_config manquant pour data_source=rest")
            return False
        
        rest_config = details_config['rest_config']
        print("[INFO] Configuration REST:")
        print(f"  [OK] api_module: {rest_config.get('api_module')}")
        print(f"  [OK] api_function: {rest_config.get('api_function')}")
    
    print(f"\n[SUCCESS] Configuration du panel 'details' valide!")
    return True

def test_sql_query_generation():
    """Test de génération de requête SQL pour le panel details"""
    print("\n" + "=" * 60)
    print("TEST: Génération de requête SQL pour 'details'")
    print("=" * 60)
    
    config = load_panel_config()
    if not config:
        return False
    
    details_config = config.get('details', {})
    sql_config = details_config.get('sql_config', {})
    
    if not sql_config:
        print("[SKIP] Pas de configuration SQL pour details")
        return True
    
    # Simuler la génération de requête
    main_table = sql_config.get('main_table')
    joins = sql_config.get('joins', [])
    fields = sql_config.get('fields', {})
    
    print(f"[INFO] Table principale: {main_table}")
    print(f"[INFO] Nombre de jointures: {len(joins)}")
    print(f"[INFO] Nombre de champs: {len(fields)}")
    
    # Construire SELECT
    select_parts = []
    for field_key, field_config in fields.items():
        table = field_config.get('table')
        column = field_config.get('column')
        select_parts.append(f"{table}.{column} as {field_key}")
    
    select_clause = "SELECT " + ", ".join(select_parts)
    
    # Construire FROM
    from_clause = f"FROM {main_table}"
    
    # Construire JOINs
    join_clauses = []
    for join in joins:
        join_type = join.get('type', 'LEFT')
        join_table = join.get('table')
        join_condition = join.get('condition')
        join_clauses.append(f"{join_type} JOIN {join_table} ON {join_condition}")
    
    # Assembler la requête
    query_parts = [select_clause, from_clause] + join_clauses
    query_parts.append("WHERE trips.trip_id = 'TRIP-TEST-123'")
    
    generated_query = "\n".join(query_parts)
    
    print("\n[INFO] Requête SQL générée:")
    print("-" * 40)
    print(generated_query)
    print("-" * 40)
    
    print(f"\n[SUCCESS] Génération de requête SQL réussie!")
    return True

if __name__ == "__main__":
    print("Script de test - Configuration Panel Trip Details")
    print("=" * 60)
    
    # Test 1: Chargement de la configuration
    success1 = test_details_panel_config()
    
    # Test 2: Génération de requête SQL
    success2 = test_sql_query_generation()
    
    # Résultat final
    print("\n" + "=" * 60)
    print("RÉSULTATS DES TESTS")
    print("=" * 60)
    print(f"Test configuration: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test génération SQL: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        sys.exit(0)
    else:
        print("\n💥 CERTAINS TESTS ONT ÉCHOUÉ!")
        sys.exit(1)
