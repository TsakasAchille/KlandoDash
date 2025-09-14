#!/usr/bin/env python3
"""
Test en 3 étapes pour analyser et valider le schéma de base de données
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash_apps.utils.supabase_client import supabase
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

def etape_1_schema_db():
    """Étape 1: Récupérer la définition des colonnes depuis la DB"""
    print_separator("ÉTAPE 1: DÉFINITION COLONNES DB")
    
    try:
        # supabase est déjà importé directement
        
        # Requête SQL pour obtenir les colonnes de la table users
        print("\n--- COLONNES TABLE USERS ---")
        users_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'users' AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        try:
            users_result = supabase.rpc('execute_sql', {
                'sql_query': users_query,
                'query_params': {}
            }).execute()
            
            if users_result.data:
                print("✅ Colonnes table users récupérées:")
                for col in users_result.data:
                    print(f"  - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
            else:
                print("❌ Aucune colonne trouvée pour users")
                
        except Exception as e:
            print(f"❌ Erreur requête users: {e}")
            # Fallback: essayer avec un SELECT simple
            try:
                users_sample = supabase.table('users').select('*').limit(1).execute()
                if users_sample.data:
                    print("✅ Colonnes users (via sample):")
                    for col in sorted(users_sample.data[0].keys()):
                        print(f"  - {col}")
            except Exception as e2:
                print(f"❌ Fallback users échoué: {e2}")
        
        # Requête SQL pour obtenir les colonnes de la table trips
        print("\n--- COLONNES TABLE TRIPS ---")
        trips_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'trips' AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        try:
            trips_result = supabase.rpc('execute_sql', {
                'sql_query': trips_query,
                'query_params': {}
            }).execute()
            
            if trips_result.data:
                print("✅ Colonnes table trips récupérées:")
                for col in trips_result.data:
                    print(f"  - {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
            else:
                print("❌ Aucune colonne trouvée pour trips")
                
        except Exception as e:
            print(f"❌ Erreur requête trips: {e}")
            # Fallback: essayer avec un SELECT simple
            try:
                trips_sample = supabase.table('trips').select('*').limit(1).execute()
                if trips_sample.data:
                    print("✅ Colonnes trips (via sample):")
                    for col in sorted(trips_sample.data[0].keys()):
                        print(f"  - {col}")
            except Exception as e2:
                print(f"❌ Fallback trips échoué: {e2}")
        
        # Vérifier les foreign keys
        print("\n--- FOREIGN KEYS ---")
        fk_query = """
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND (tc.table_name = 'trips' OR tc.table_name = 'users');
        """
        
        try:
            fk_result = supabase.rpc('execute_sql', {
                'sql_query': fk_query,
                'query_params': {}
            }).execute()
            
            if fk_result.data:
                print("✅ Foreign keys trouvées:")
                for fk in fk_result.data:
                    print(f"  - {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']} ({fk['constraint_name']})")
            else:
                print("❌ Aucune foreign key trouvée")
                
        except Exception as e:
            print(f"❌ Erreur requête foreign keys: {e}")
            
    except Exception as e:
        print(f"❌ Erreur connexion Supabase: {e}")

def etape_2_schema_config():
    """Étape 2: Vérifier correspondance avec les schémas config"""
    print_separator("ÉTAPE 2: VÉRIFICATION SCHÉMAS CONFIG")
    
    try:
        # Charger les schémas depuis config
        print("\n--- SCHÉMA USERS CONFIG ---")
        try:
            users_schema = load_json_config('users_scheme.json')
            if users_schema:
                print("✅ Schéma users chargé:")
                if 'fields' in users_schema:
                    for field_name, field_config in users_schema['fields'].items():
                        print(f"  - {field_name}: {field_config.get('type', 'unknown')}")
                print_json(users_schema, "Schéma users complet")
            else:
                print("❌ Schéma users non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement schéma users: {e}")
        
        print("\n--- SCHÉMA TRIPS CONFIG ---")
        try:
            trips_schema = load_json_config('trips_scheme.json')
            if trips_schema:
                print("✅ Schéma trips chargé:")
                if 'fields' in trips_schema:
                    for field_name, field_config in trips_schema['fields'].items():
                        print(f"  - {field_name}: {field_config.get('type', 'unknown')}")
                print_json(trips_schema, "Schéma trips complet")
            else:
                print("❌ Schéma trips non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement schéma trips: {e}")
            
    except Exception as e:
        print(f"❌ Erreur étape 2: {e}")

def etape_3_query_json():
    """Étape 3: Tester les requêtes JSON et vérifier les données"""
    print_separator("ÉTAPE 3: TEST REQUÊTES JSON")
    
    try:
        # Charger la configuration des requêtes driver
        driver_queries_config = load_json_config('driver_queries.json')
        queries = driver_queries_config.get('queries', {})
        field_mappings = driver_queries_config.get('field_mappings', {})
        
        print("✅ Configuration requêtes driver chargée")
        
        # Initialiser le Query Builder
        query_builder = QueryBuilder(queries, field_mappings)
        
        # Test avec trip_id réel
        trip_id = "TRIP-1757509188099817-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
        
        print(f"\n--- TEST QUERY BUILDER ---")
        sql_query, query_params = query_builder.build_query(
            'driver_by_trip',
            parameters={'trip_id': trip_id},
            dynamic_fields=[]
        )
        
        print(f"SQL généré: {sql_query}")
        print(f"Paramètres: {query_params}")
        
        # Tester la requête directement
        print(f"\n--- TEST REQUÊTE DIRECTE ---")
        try:
            # supabase est déjà importé directement
            
            # Test 1: Requête SQL brute (si execute_sql existe)
            try:
                response = supabase.rpc('execute_sql', {
                    'sql_query': sql_query,
                    'query_params': query_params
                }).execute()
                
                if response.data:
                    print("✅ Requête SQL brute réussie:")
                    print_json(response.data, "Résultat requête SQL")
                else:
                    print("❌ Requête SQL brute: aucune donnée")
                    
            except Exception as e:
                print(f"❌ Requête SQL brute échouée: {e}")
                
                # Test 2: Requête Supabase native
                print(f"\n--- FALLBACK: REQUÊTE NATIVE ---")
                try:
                    # Essayer différentes approches de jointure
                    approaches = [
                        'driver_id, users(uid, name, email, phone_number, role, photo_url)',
                        'driver_id, users!trips_driver_id_fkey(uid, name, email, phone_number, role, photo_url)',
                        'driver_id, users!driver_id(uid, name, email, phone_number, role, photo_url)',
                        '*'
                    ]
                    
                    for i, approach in enumerate(approaches, 1):
                        try:
                            print(f"\nApproche {i}: {approach}")
                            result = supabase.table('trips').select(approach).eq('trip_id', trip_id).limit(1).execute()
                            
                            if result.data:
                                print(f"✅ Approche {i} réussie:")
                                print_json(result.data[0], f"Résultat approche {i}")
                                break
                            else:
                                print(f"❌ Approche {i}: aucune donnée")
                                
                        except Exception as e:
                            print(f"❌ Approche {i} échouée: {e}")
                            
                except Exception as e:
                    print(f"❌ Toutes les approches ont échoué: {e}")
                    
        except Exception as e:
            print(f"❌ Erreur test requête: {e}")
            
    except Exception as e:
        print(f"❌ Erreur étape 3: {e}")

def main():
    """Fonction principale - exécute les 3 étapes"""
    print_separator("ANALYSE COMPLÈTE SCHÉMA DB")
    
    # Étape 1: Analyser le schéma DB
    etape_1_schema_db()
    
    # Étape 2: Vérifier les schémas config
    etape_2_schema_config()
    
    # Étape 3: Tester les requêtes JSON
    etape_3_query_json()
    
    print_separator("ANALYSE TERMINÉE")

if __name__ == "__main__":
    main()
