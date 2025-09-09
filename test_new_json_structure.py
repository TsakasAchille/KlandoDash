#!/usr/bin/env python3
"""
Script de test pour valider la nouvelle structure JSON avec méthodes
Test la structure reorganisée avec cache, data_fetcher, renderer
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

def test_new_structure_stats():
    """Test de la nouvelle structure pour le panel stats"""
    print("=" * 60)
    print("TEST: Nouvelle structure pour panel 'stats'")
    print("=" * 60)
    
    config = load_panel_config()
    if not config:
        return False
    
    # Vérifier que le panel stats existe
    if 'stats' not in config:
        print("[ERROR] Panel 'stats' non trouvé")
        return False
    
    stats_config = config['stats']
    
    # Vérifier la structure de base
    required_base = ['panel_name', 'description', 'methods']
    for field in required_base:
        if field not in stats_config:
            print(f"[ERROR] Champ de base manquant: {field}")
            return False
        print(f"[OK] {field}: {stats_config[field] if field != 'methods' else 'présent'}")
    
    # Vérifier la structure des méthodes
    methods = stats_config.get('methods', {})
    required_methods = ['cache', 'data_fetcher', 'renderer']
    
    for method in required_methods:
        if method not in methods:
            print(f"[ERROR] Méthode manquante: {method}")
            return False
        print(f"[OK] Méthode '{method}' présente")
    
    # Test méthode cache
    cache_config = methods['cache']
    cache_required = ['html_cache_enabled', 'redis_cache_enabled', 'redis_key_prefix', 'cache_ttl']
    for field in cache_required:
        if field not in cache_config:
            print(f"[ERROR] Cache config manquant: {field}")
            return False
        print(f"  [OK] cache.{field}: {cache_config[field]}")
    
    # Test méthode data_fetcher
    fetcher_config = methods['data_fetcher']
    fetcher_required = ['type', 'inputs']
    for field in fetcher_required:
        if field not in fetcher_config:
            print(f"[ERROR] Data fetcher config manquant: {field}")
            return False
        print(f"  [OK] data_fetcher.{field}: {fetcher_config[field]}")
    
    # Vérifier les inputs du data_fetcher
    inputs = fetcher_config.get('inputs', {})
    if 'trip_id' not in inputs:
        print("[ERROR] Input 'trip_id' manquant pour data_fetcher")
        return False
    print(f"  [OK] data_fetcher.inputs.trip_id: {inputs['trip_id']}")
    
    # Test méthode renderer
    renderer_config = methods['renderer']
    renderer_required = ['type', 'inputs', 'module', 'function']
    for field in renderer_required:
        if field not in renderer_config:
            print(f"[ERROR] Renderer config manquant: {field}")
            return False
        print(f"  [OK] renderer.{field}: {renderer_config[field]}")
    
    # Vérifier les inputs du renderer
    renderer_inputs = renderer_config.get('inputs', {})
    required_renderer_inputs = ['trip_id', 'data']
    for inp in required_renderer_inputs:
        if inp not in renderer_inputs:
            print(f"[ERROR] Input renderer manquant: {inp}")
            return False
        print(f"  [OK] renderer.inputs.{inp}: {renderer_inputs[inp]}")
    
    print(f"\n[SUCCESS] Structure du panel 'stats' valide!")
    return True

def test_method_extraction(panel_name):
    """Test d'extraction des configurations de méthodes"""
    print(f"\n" + "=" * 60)
    print(f"TEST: Extraction des méthodes pour '{panel_name}'")
    print("=" * 60)
    
    config = load_panel_config()
    if not config:
        return False
    
    panel_config = config.get(panel_name, {})
    if not panel_config:
        print(f"[ERROR] Panel '{panel_name}' non trouvé")
        return False
    
    methods = panel_config.get('methods', {})
    
    # Extraire la config cache
    cache_config = methods.get('cache', {})
    print(f"[INFO] Configuration cache extraite:")
    print(f"  - HTML Cache: {cache_config.get('html_cache_enabled', False)}")
    print(f"  - Redis Cache: {cache_config.get('redis_cache_enabled', False)}")
    print(f"  - Redis Key: {cache_config.get('redis_key_prefix', 'N/A')}")
    print(f"  - TTL: {cache_config.get('cache_ttl', 'N/A')} secondes")
    
    # Extraire la config data_fetcher
    fetcher_config = methods.get('data_fetcher', {})
    print(f"\n[INFO] Configuration data_fetcher extraite:")
    print(f"  - Type: {fetcher_config.get('type', 'N/A')}")
    print(f"  - Inputs requis: {list(fetcher_config.get('inputs', {}).keys())}")
    
    if fetcher_config.get('type') == 'sql':
        sql_config = fetcher_config.get('sql_config', {})
        print(f"  - Table principale: {sql_config.get('main_table', 'N/A')}")
        print(f"  - Nombre de jointures: {len(sql_config.get('joins', []))}")
        print(f"  - Nombre de champs: {len(sql_config.get('fields', {}))}")
    
    # Extraire la config renderer
    renderer_config = methods.get('renderer', {})
    print(f"\n[INFO] Configuration renderer extraite:")
    print(f"  - Type: {renderer_config.get('type', 'N/A')}")
    print(f"  - Module: {renderer_config.get('module', 'N/A')}")
    print(f"  - Fonction: {renderer_config.get('function', 'N/A')}")
    print(f"  - Inputs requis: {list(renderer_config.get('inputs', {}).keys())}")
    
    print(f"\n[SUCCESS] Extraction des méthodes pour '{panel_name}' réussie!")
    return True

def test_sql_query_generation_new_structure(panel_name):
    """Test génération SQL avec la nouvelle structure"""
    print(f"\n" + "=" * 60)
    print(f"TEST: Génération SQL nouvelle structure - '{panel_name}'")
    print("=" * 60)
    
    config = load_panel_config()
    if not config:
        return False
    
    panel_config = config.get(panel_name, {})
    methods = panel_config.get('methods', {})
    fetcher_config = methods.get('data_fetcher', {})
    
    if fetcher_config.get('type') != 'sql':
        print(f"[SKIP] Panel '{panel_name}' n'utilise pas SQL")
        return True
    
    sql_config = fetcher_config.get('sql_config', {})
    
    # Construire la requête
    main_table = sql_config.get('main_table')
    joins = sql_config.get('joins', [])
    fields = sql_config.get('fields', {})
    where_conditions = sql_config.get('where_conditions', [])
    
    # SELECT
    select_parts = []
    for field_key, field_config in fields.items():
        table = field_config.get('table')
        column = field_config.get('column')
        select_parts.append(f"{table}.{column} as {field_key}")
    
    select_clause = "SELECT " + ", ".join(select_parts)
    
    # FROM
    from_clause = f"FROM {main_table}"
    
    # JOINs
    join_clauses = []
    for join in joins:
        join_type = join.get('type', 'LEFT')
        join_table = join.get('table')
        join_condition = join.get('condition')
        join_clauses.append(f"{join_type} JOIN {join_table} ON {join_condition}")
    
    # WHERE
    where_clauses = []
    for condition in where_conditions:
        # Remplacer :trip_id par une valeur de test
        condition_resolved = condition.replace(':trip_id', "'TRIP-TEST-123'")
        where_clauses.append(condition_resolved)
    
    # Assembler
    query_parts = [select_clause, from_clause] + join_clauses
    if where_clauses:
        query_parts.append("WHERE " + " AND ".join(where_clauses))
    
    generated_query = "\n".join(query_parts)
    
    print(f"[INFO] Requête SQL générée pour '{panel_name}':")
    print("-" * 50)
    print(generated_query)
    print("-" * 50)
    
    print(f"\n[SUCCESS] Génération SQL nouvelle structure réussie!")
    return True

if __name__ == "__main__":
    print("Script de test - Nouvelle structure JSON avec méthodes")
    print("=" * 60)
    
    # Test 1: Structure du panel stats
    success1 = test_new_structure_stats()
    
    # Test 2: Extraction des méthodes pour stats
    success2 = test_method_extraction('stats')
    
    # Test 3: Extraction des méthodes pour details
    success3 = test_method_extraction('details')
    
    # Test 4: Génération SQL nouvelle structure
    success4 = test_sql_query_generation_new_structure('stats')
    success5 = test_sql_query_generation_new_structure('details')
    
    # Résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DES TESTS")
    print("=" * 60)
    print(f"Test structure stats: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test extraction stats: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Test extraction details: {'✅ PASS' if success3 else '❌ FAIL'}")
    print(f"Test SQL stats: {'✅ PASS' if success4 else '❌ FAIL'}")
    print(f"Test SQL details: {'✅ PASS' if success5 else '❌ FAIL'}")
    
    all_success = all([success1, success2, success3, success4, success5])
    
    if all_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("La nouvelle structure JSON avec méthodes est valide!")
        sys.exit(0)
    else:
        print("\n💥 CERTAINS TESTS ONT ÉCHOUÉ!")
        sys.exit(1)
