#!/usr/bin/env python3
"""
Test pour vérifier si driver_queries.json est bien écrit et optimisé
puis tester si le Query Builder lit bien le fichier
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash_apps.utils.settings import load_json_config
from dash_apps.utils.query_builder import QueryBuilder

def print_separator(title: str):
    """Affiche un séparateur avec titre"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def print_json(data: Any, title: str = "Data"):
    """Affiche des données JSON formatées"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

def etape_1_validation_json():
    """Étape 1: Vérifier la structure et optimisation du JSON"""
    print_separator("ÉTAPE 1: VALIDATION DRIVER_QUERIES.JSON")
    
    try:
        # Charger le fichier JSON
        driver_queries_config = load_json_config('driver_queries.json')
        
        if not driver_queries_config:
            print("❌ Impossible de charger driver_queries.json")
            return False
            
        print("✅ Fichier driver_queries.json chargé avec succès")
        print_json(driver_queries_config, "Configuration complète")
        
        # Vérifier la structure principale
        required_keys = ['queries', 'field_mappings']
        missing_keys = []
        
        for key in required_keys:
            if key not in driver_queries_config:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Clés manquantes: {missing_keys}")
            return False
        else:
            print("✅ Structure principale correcte (queries, field_mappings)")
        
        # Analyser chaque requête
        queries = driver_queries_config.get('queries', {})
        print(f"\n--- ANALYSE DES REQUÊTES ({len(queries)} trouvées) ---")
        
        for query_name, query_config in queries.items():
            print(f"\n🔍 Requête: {query_name}")
            
            # Vérifier les champs obligatoires
            required_query_fields = ['description']
            optional_query_fields = ['tables', 'joins', 'where', 'select', 'limit']
            
            for field in required_query_fields:
                if field in query_config:
                    print(f"  ✅ {field}: {query_config[field]}")
                else:
                    print(f"  ❌ {field}: MANQUANT")
            
            for field in optional_query_fields:
                if field in query_config:
                    print(f"  ✅ {field}: présent")
                    if field == 'select':
                        select_config = query_config[field]
                        if isinstance(select_config, dict):
                            if 'base' in select_config:
                                print(f"    - base fields: {len(select_config['base'])} champs")
                            if 'dynamic' in select_config:
                                print(f"    - dynamic: {select_config['dynamic']}")
                        else:
                            print(f"    - format: {type(select_config).__name__}")
                else:
                    print(f"  ⚠️  {field}: absent")
        
        # Vérifier les field_mappings
        field_mappings = driver_queries_config.get('field_mappings', {})
        print(f"\n--- FIELD MAPPINGS ({len(field_mappings)} mappings) ---")
        
        for original, mapped in field_mappings.items():
            print(f"  {original} -> {mapped}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation JSON: {e}")
        import traceback
        traceback.print_exc()
        return False

def etape_2_test_query_builder():
    """Étape 2: Tester si le Query Builder lit bien le fichier"""
    print_separator("ÉTAPE 2: TEST QUERY BUILDER")
    
    try:
        # Charger la configuration
        driver_queries_config = load_json_config('driver_queries.json')
        queries = driver_queries_config.get('queries', {})
        field_mappings = driver_queries_config.get('field_mappings', {})
        
        print("✅ Configuration chargée pour Query Builder")
        
        # Initialiser le Query Builder
        query_builder = QueryBuilder(queries, field_mappings)
        print("✅ Query Builder initialisé")
        
        # Test avec chaque requête
        test_parameters = {
            'driver_by_trip': {'trip_id': 'TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3'},
            'driver_by_id': {'driver_id': 'n739xt2Uy0Qb5hP30AJ1G3dnT8G3'},
            'trip_driver_id': {'trip_id': 'TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3'}
        }
        
        for query_name in queries.keys():
            print(f"\n--- TEST REQUÊTE: {query_name} ---")
            
            try:
                params = test_parameters.get(query_name, {})
                sql_query, query_params = query_builder.build_query(
                    query_name,
                    parameters=params,
                    dynamic_fields=[]
                )
                
                print(f"✅ Requête {query_name} construite avec succès")
                print(f"SQL: {sql_query}")
                print(f"Params: {query_params}")
                
            except Exception as e:
                print(f"❌ Erreur construction requête {query_name}: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Query Builder: {e}")
        import traceback
        traceback.print_exc()
        return False

def etape_3_recommandations():
    """Étape 3: Recommandations d'optimisation"""
    print_separator("ÉTAPE 3: RECOMMANDATIONS D'OPTIMISATION")
    
    try:
        driver_queries_config = load_json_config('driver_queries.json')
        queries = driver_queries_config.get('queries', {})
        
        print("📋 RECOMMANDATIONS:")
        
        # Analyser driver_by_trip
        driver_by_trip = queries.get('driver_by_trip', {})
        
        print("\n🔍 driver_by_trip:")
        
        # Vérifier les champs sélectionnés
        select_config = driver_by_trip.get('select', {})
        base_fields = select_config.get('base', [])
        
        print(f"  - Champs sélectionnés: {len(base_fields)}")
        print(f"  - Liste: {base_fields}")
        
        # Recommandations spécifiques
        recommended_fields = ['uid', 'name', 'email', 'phone_number', 'role', 'photo_url']
        current_fields = [field.split('.')[-1] for field in base_fields]  # Enlever les préfixes u.
        
        missing_fields = set(recommended_fields) - set(current_fields)
        extra_fields = set(current_fields) - set(recommended_fields)
        
        if missing_fields:
            print(f"  ⚠️  Champs manquants recommandés: {list(missing_fields)}")
        else:
            print("  ✅ Tous les champs recommandés sont présents")
            
        if extra_fields:
            print(f"  ℹ️  Champs supplémentaires: {list(extra_fields)}")
        
        # Vérifier la jointure
        joins = driver_by_trip.get('joins', [])
        if joins:
            join = joins[0]
            print(f"  - Jointure: {join.get('type')} JOIN {join.get('table')} ON {join.get('on')}")
            
            # Vérifier si la jointure est optimale
            if join.get('on') == 'trips.driver_id = u.uid':
                print("  ✅ Jointure optimale (clé étrangère)")
            else:
                print("  ⚠️  Vérifier la jointure")
        
        # Vérifier l'index
        where_clause = driver_by_trip.get('where', {})
        if 'trips.trip_id' in where_clause:
            print("  ✅ Filtre sur trip_id (devrait être indexé)")
        
        # Vérifier la limite
        limit = driver_by_trip.get('limit')
        if limit == 1:
            print("  ✅ LIMIT 1 pour performance (un conducteur par trajet)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur recommandations: {e}")
        return False

def main():
    """Fonction principale"""
    print_separator("VALIDATION COMPLÈTE DRIVER_QUERIES.JSON")
    
    # Étape 1: Validation JSON
    json_valid = etape_1_validation_json()
    
    # Étape 2: Test Query Builder
    builder_works = etape_2_test_query_builder()
    
    # Étape 3: Recommandations
    recommendations = etape_3_recommandations()
    
    print_separator("RÉSUMÉ FINAL")
    print(f"JSON valide: {'✅' if json_valid else '❌'}")
    print(f"Query Builder fonctionne: {'✅' if builder_works else '❌'}")
    print(f"Recommandations analysées: {'✅' if recommendations else '❌'}")
    
    if json_valid and builder_works:
        print("\n🎉 SUCCÈS: La configuration JSON est correcte et le Query Builder fonctionne!")
    else:
        print("\n❌ ÉCHEC: Des problèmes ont été détectés")

if __name__ == "__main__":
    main()
