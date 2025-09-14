#!/usr/bin/env python3
"""
Test script pour diagnostiquer les problèmes de cache et récupération API
pour les données conducteur avec le système de requêtes JSON
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Activer le debug
os.environ['DEBUG_TRIPS'] = 'true'

from dash_apps.services.trip_driver_cache_service import TripDriverCache
from dash_apps.infrastructure.repositories.supabase_driver_repository import SupabaseDriverRepository
from dash_apps.utils.query_builder import QueryBuilder
from dash_apps.utils.settings import load_json_config
from dash_apps.utils.driver_display_formatter import DriverDisplayFormatter

def print_separator(title: str):
    """Affiche un séparateur avec titre"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_json(data: Any, title: str = "Data"):
    """Affiche des données JSON formatées"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

async def test_query_builder():
    """Test du Query Builder avec les requêtes JSON"""
    print_separator("TEST QUERY BUILDER")
    
    try:
        # Charger la configuration
        driver_queries_config = load_json_config('driver_queries.json')
        queries = driver_queries_config.get('queries', {})
        field_mappings = driver_queries_config.get('field_mappings', {})
        
        print("Configuration chargée:")
        print_json(queries, "Queries")
        print_json(field_mappings, "Field Mappings")
        
        # Initialiser le Query Builder
        query_builder = QueryBuilder(queries, field_mappings)
        
        # Test avec trip_id
        trip_id = "TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
        
        print(f"\nTest avec trip_id: {trip_id}")
        
        # Construire la requête
        sql_query, query_params = query_builder.build_query(
            'driver_by_trip',
            parameters={'trip_id': trip_id},
            dynamic_fields=[]
        )
        
        print(f"\nRequête SQL générée:")
        print(sql_query)
        print(f"\nParamètres:")
        print_json(query_params)
        
        return sql_query, query_params
        
    except Exception as e:
        print(f"ERREUR Query Builder: {e}")
        import traceback
        traceback.print_exc()
        return None, None

async def test_repository():
    """Test du Repository Supabase"""
    print_separator("TEST REPOSITORY SUPABASE")
    
    try:
        repository = SupabaseDriverRepository()
        trip_id = "TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
        
        print(f"Test repository avec trip_id: {trip_id}")
        
        # Appeler get_by_trip_id
        result = await repository.get_by_trip_id(trip_id)
        
        print(f"\nRésultat repository:")
        if result:
            print_json(result, "Driver Data")
        else:
            print("Aucune donnée retournée")
            
        return result
        
    except Exception as e:
        print(f"ERREUR Repository: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_formatter(driver_data: Optional[Dict[str, Any]]):
    """Test du Formatter"""
    print_separator("TEST FORMATTER")
    
    if not driver_data:
        print("Pas de données à formater")
        return None
        
    try:
        formatter = DriverDisplayFormatter()
        formatted_data = formatter.format_for_display(driver_data)
        
        print("Données formatées:")
        print_json(formatted_data, "Formatted Driver Data")
        
        return formatted_data
        
    except Exception as e:
        print(f"ERREUR Formatter: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_cache_service():
    """Test du service de cache complet"""
    print_separator("TEST CACHE SERVICE")
    
    try:
        trip_id = "TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
        
        print(f"Test cache service avec trip_id: {trip_id}")
        
        # Test get_trip_driver_data
        result = await TripDriverCache.get_trip_driver_data(trip_id)
        
        print(f"\nRésultat cache service:")
        if result:
            print_json(result, "Cache Service Result")
        else:
            print("Aucune donnée retournée par le cache service")
            
        return result
        
    except Exception as e:
        print(f"ERREUR Cache Service: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Fonction principale de test"""
    print_separator("DÉBUT DES TESTS DRIVER CACHE")
    
    # Test 1: Query Builder
    sql_query, query_params = await test_query_builder()
    
    # Test 2: Repository
    driver_data = await test_repository()
    
    # Test 3: Formatter
    formatted_data = await test_formatter(driver_data)
    
    # Test 4: Cache Service complet
    cache_result = await test_cache_service()
    
    print_separator("RÉSUMÉ DES TESTS")
    print(f"Query Builder: {'✅ OK' if sql_query else '❌ ERREUR'}")
    print(f"Repository: {'✅ OK' if driver_data else '❌ ERREUR'}")
    print(f"Formatter: {'✅ OK' if formatted_data else '❌ ERREUR'}")
    print(f"Cache Service: {'✅ OK' if cache_result else '❌ ERREUR'}")
    
    if cache_result:
        print("\n🎉 SUCCÈS: Le système fonctionne correctement!")
    else:
        print("\n❌ ÉCHEC: Des problèmes ont été détectés")

if __name__ == "__main__":
    asyncio.run(main())
