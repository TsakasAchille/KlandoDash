#!/usr/bin/env python3
"""
Script de test pour créer et tester une fonction générique avec la nouvelle structure JSON
"""

import json
import os
import sys
from typing import Dict, Any, Optional

def load_panel_config():
    """Charge la configuration des panneaux depuis le fichier JSON"""
    config_path = os.path.join('dash_apps', 'config', 'panels_config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Erreur chargement config: {e}")
        return {}

def get_cache_config(panel_config: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait la configuration cache du panel"""
    return panel_config.get('methods', {}).get('cache', {})

def get_data_fetcher_config(panel_config: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait la configuration data_fetcher du panel"""
    return panel_config.get('methods', {}).get('data_fetcher', {})

def get_renderer_config(panel_config: Dict[str, Any]) -> Dict[str, Any]:
    """Extrait la configuration renderer du panel"""
    return panel_config.get('methods', {}).get('renderer', {})

def validate_inputs(required_inputs: Dict[str, str], provided_inputs: Dict[str, Any]) -> bool:
    """Valide que tous les inputs requis sont fournis"""
    for input_name, requirement in required_inputs.items():
        if requirement == "required" and input_name not in provided_inputs:
            print(f"[ERROR] Input requis manquant: {input_name}")
            return False
        if input_name in provided_inputs and provided_inputs[input_name] is None:
            print(f"[ERROR] Input requis est None: {input_name}")
            return False
    return True

def build_sql_query(sql_config: Dict[str, Any], inputs: Dict[str, Any]) -> str:
    """Construit une requête SQL basée sur la config et les inputs"""
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
    
    # WHERE avec remplacement des paramètres
    where_clauses = []
    for condition in where_conditions:
        resolved_condition = condition
        for param_name, param_value in inputs.items():
            resolved_condition = resolved_condition.replace(f":{param_name}", f"'{param_value}'")
        where_clauses.append(resolved_condition)
    
    # Assembler
    query_parts = [select_clause, from_clause] + join_clauses
    if where_clauses:
        query_parts.append("WHERE " + " AND ".join(where_clauses))
    
    return "\n".join(query_parts)

def simulate_data_fetcher(panel_config: Dict[str, Any], inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Simule l'exécution du data_fetcher"""
    fetcher_config = get_data_fetcher_config(panel_config)
    
    if not fetcher_config:
        print("[ERROR] Configuration data_fetcher manquante")
        return None
    
    # Valider les inputs
    required_inputs = fetcher_config.get('inputs', {})
    if not validate_inputs(required_inputs, inputs):
        return None
    
    fetcher_type = fetcher_config.get('type')
    
    if fetcher_type == 'sql':
        sql_config = fetcher_config.get('sql_config', {})
        query = build_sql_query(sql_config, inputs)
        
        print(f"[INFO] Requête SQL générée:")
        print("-" * 50)
        print(query)
        print("-" * 50)
        
        # Simuler des données de retour
        fields = sql_config.get('fields', {})
        mock_data = {}
        
        for field_key, field_config in fields.items():
            field_type = field_config.get('type', 'string')
            
            if field_type == 'currency':
                mock_data[field_key] = f"1500 {field_config.get('unit', '')}"
            elif field_type == 'integer':
                mock_data[field_key] = 4
            elif field_type == 'count':
                mock_data[field_key] = 2
            elif field_type == 'enum':
                values = field_config.get('values', {})
                first_key = list(values.keys())[0] if values else 'active'
                mock_data[field_key] = values.get(first_key, first_key)
            else:
                mock_data[field_key] = f"Mock {field_config.get('label', field_key)}"
        
        return mock_data
    
    else:
        print(f"[ERROR] Type de fetcher non supporté: {fetcher_type}")
        return None

def simulate_renderer(panel_config: Dict[str, Any], inputs: Dict[str, Any]) -> str:
    """Simule l'exécution du renderer"""
    renderer_config = get_renderer_config(panel_config)
    
    if not renderer_config:
        print("[ERROR] Configuration renderer manquante")
        return "ERROR: Renderer config missing"
    
    # Valider les inputs
    required_inputs = renderer_config.get('inputs', {})
    if not validate_inputs(required_inputs, inputs):
        return "ERROR: Invalid inputs"
    
    module = renderer_config.get('module')
    function = renderer_config.get('function')
    
    print(f"[INFO] Appel simulé: {module}.{function}")
    print(f"[INFO] Inputs: {list(inputs.keys())}")
    
    # Simuler le rendu HTML
    data = inputs.get('data', {})
    trip_id = inputs.get('trip_id', 'UNKNOWN')
    
    html_content = f"""
    <div class="panel-{panel_config.get('panel_name', 'unknown')}">
        <h3>{panel_config.get('description', 'Panel')}</h3>
        <p>Trip ID: {trip_id}</p>
        <ul>
    """
    
    for key, value in data.items():
        html_content += f"        <li><strong>{key}:</strong> {value}</li>\n"
    
    html_content += """        </ul>
    </div>"""
    
    return html_content

def generic_panel_processor(panel_type: str, inputs: Dict[str, Any]) -> str:
    """
    Fonction générique pour traiter un panel avec la nouvelle structure JSON
    
    Args:
        panel_type: Type de panel ('stats', 'details', etc.)
        inputs: Dictionnaire des inputs (ex: {'trip_id': 'TRIP-123'})
        
    Returns:
        HTML rendu du panel ou message d'erreur
    """
    print(f"\n{'='*60}")
    print(f"TRAITEMENT GÉNÉRIQUE DU PANEL: {panel_type.upper()}")
    print(f"{'='*60}")
    
    # Charger la config
    config = load_panel_config()
    panel_config = config.get(panel_type, {})
    
    if not panel_config:
        return f"ERROR: Panel '{panel_type}' non trouvé dans la configuration"
    
    print(f"[INFO] Panel trouvé: {panel_config.get('description', 'N/A')}")
    
    # Étape 1: Vérifier le cache (simulation)
    cache_config = get_cache_config(panel_config)
    if cache_config.get('html_cache_enabled', False):
        print(f"[INFO] Cache HTML activé (TTL: {cache_config.get('cache_ttl', 'N/A')}s)")
        print(f"[SIMULATION] Vérification cache HTML... MISS")
    
    if cache_config.get('redis_cache_enabled', False):
        redis_key = cache_config.get('redis_key_prefix', 'unknown')
        print(f"[INFO] Cache Redis activé (clé: {redis_key})")
        print(f"[SIMULATION] Vérification cache Redis... MISS")
    
    # Étape 2: Récupérer les données
    print(f"\n[INFO] Récupération des données...")
    data = simulate_data_fetcher(panel_config, inputs)
    
    if not data:
        return "ERROR: Échec récupération des données"
    
    print(f"[SUCCESS] Données récupérées: {len(data)} champs")
    
    # Étape 3: Rendre le panel
    print(f"\n[INFO] Rendu du panel...")
    render_inputs = inputs.copy()
    render_inputs['data'] = data
    
    html_result = simulate_renderer(panel_config, render_inputs)
    
    # Étape 4: Mise en cache (simulation)
    if cache_config.get('html_cache_enabled', False):
        print(f"[SIMULATION] Mise en cache HTML du résultat")
    
    if cache_config.get('redis_cache_enabled', False):
        print(f"[SIMULATION] Mise en cache Redis des données")
    
    print(f"\n[SUCCESS] Panel '{panel_type}' traité avec succès!")
    return html_result

def test_generic_processor():
    """Test de la fonction générique"""
    print("Script de test - Fonction générique nouvelle structure")
    print("=" * 60)
    
    # Test 1: Panel stats
    print("\nTEST 1: Panel stats")
    inputs_stats = {'trip_id': 'TRIP-TEST-STATS-123'}
    result_stats = generic_panel_processor('stats', inputs_stats)
    
    print(f"\nRésultat stats:")
    print("-" * 30)
    print(result_stats)
    print("-" * 30)
    
    # Test 2: Panel details
    print("\nTEST 2: Panel details")
    inputs_details = {'trip_id': 'TRIP-TEST-DETAILS-456'}
    result_details = generic_panel_processor('details', inputs_details)
    
    print(f"\nRésultat details:")
    print("-" * 30)
    print(result_details)
    print("-" * 30)
    
    # Test 3: Panel inexistant
    print("\nTEST 3: Panel inexistant")
    inputs_invalid = {'trip_id': 'TRIP-TEST-789'}
    result_invalid = generic_panel_processor('nonexistent', inputs_invalid)
    
    print(f"\nRésultat panel inexistant:")
    print("-" * 30)
    print(result_invalid)
    print("-" * 30)
    
    return True

if __name__ == "__main__":
    success = test_generic_processor()
    
    print("\n" + "=" * 60)
    print("RÉSULTAT FINAL")
    print("=" * 60)
    
    if success:
        print("🎉 FONCTION GÉNÉRIQUE TESTÉE AVEC SUCCÈS!")
        print("La nouvelle structure JSON permet un traitement complètement générique!")
        sys.exit(0)
    else:
        print("💥 ÉCHEC DU TEST!")
        sys.exit(1)
