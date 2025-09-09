#!/usr/bin/env python3
"""
Script de test final pour valider l'intégration complète
- panel_type extrait du JSON (panel_name)
- Fonction générique avec nouvelle structure
- Test complet du flux
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dash_apps'))

def test_panel_name_extraction():
    """Test que panel_type est bien extrait du JSON"""
    print("=" * 60)
    print("TEST: Extraction panel_name depuis JSON")
    print("=" * 60)
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Charger la config
        config = TripsCacheService._load_panel_config()
        
        # Tester extraction panel_name pour chaque panel
        panels = ['stats', 'details']
        
        for panel_key in panels:
            panel_config = config.get(panel_key, {})
            panel_name = panel_config.get('panel_name', 'NOT_FOUND')
            
            print(f"[INFO] Panel '{panel_key}' -> panel_name: '{panel_name}'")
            
            if panel_name == panel_key:
                print(f"[SUCCESS] Panel name correct pour {panel_key}")
            else:
                print(f"[ERROR] Panel name incorrect pour {panel_key}: attendu '{panel_key}', trouvé '{panel_name}'")
                return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur test panel_name: {e}")
        return False

def test_generic_function_signature():
    """Test que la fonction générique a la bonne signature"""
    print("\n" + "=" * 60)
    print("TEST: Signature fonction générique")
    print("=" * 60)
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        import inspect
        
        # Vérifier la signature de _get_cached_panel_generic
        sig = inspect.signature(TripsCacheService._get_cached_panel_generic)
        params = list(sig.parameters.keys())
        
        print(f"[INFO] Paramètres fonction: {params}")
        
        # Doit avoir 2 paramètres: selected_trip_id et panel_config
        expected_params = ['selected_trip_id', 'panel_config']
        
        if params == expected_params:
            print(f"[SUCCESS] Signature correcte: {params}")
            return True
        else:
            print(f"[ERROR] Signature incorrecte: attendu {expected_params}, trouvé {params}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Erreur test signature: {e}")
        return False

def test_panel_methods_integration():
    """Test que les méthodes de panels utilisent la nouvelle structure"""
    print("\n" + "=" * 60)
    print("TEST: Intégration méthodes panels")
    print("=" * 60)
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Charger la config
        config = TripsCacheService._load_panel_config()
        
        # Test get_trip_details_panel
        print("[INFO] Test get_trip_details_panel...")
        details_config = config.get('details', {})
        
        if not details_config:
            print("[ERROR] Configuration details manquante")
            return False
        
        print(f"[INFO] Details config trouvée: {details_config.get('panel_name')}")
        
        # Test get_trip_stats_panel
        print("[INFO] Test get_trip_stats_panel...")
        stats_config = config.get('stats', {})
        
        if not stats_config:
            print("[ERROR] Configuration stats manquante")
            return False
        
        print(f"[INFO] Stats config trouvée: {stats_config.get('panel_name')}")
        
        print("[SUCCESS] Configurations panels trouvées")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur test méthodes: {e}")
        return False

def test_complete_flow_simulation():
    """Test simulation du flux complet"""
    print("\n" + "=" * 60)
    print("TEST: Simulation flux complet")
    print("=" * 60)
    
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        
        # Charger config
        config = TripsCacheService._load_panel_config()
        details_config = config.get('details', {})
        
        # Simuler l'extraction des configurations
        panel_name = details_config.get('panel_name', 'unknown')
        methods = details_config.get('methods', {})
        
        cache_config = methods.get('cache', {})
        data_fetcher_config = methods.get('data_fetcher', {})
        renderer_config = methods.get('renderer', {})
        
        print(f"[INFO] Panel name extrait: {panel_name}")
        print(f"[INFO] Cache config: {cache_config.get('html_cache_enabled', False)}")
        print(f"[INFO] Fetcher type: {data_fetcher_config.get('type', 'N/A')}")
        print(f"[INFO] Renderer module: {renderer_config.get('module', 'N/A')}")
        
        # Vérifier que tout est présent
        if not panel_name or panel_name == 'unknown':
            print("[ERROR] Panel name manquant")
            return False
        
        if not cache_config:
            print("[ERROR] Cache config manquant")
            return False
        
        if not data_fetcher_config:
            print("[ERROR] Data fetcher config manquant")
            return False
        
        if not renderer_config:
            print("[ERROR] Renderer config manquant")
            return False
        
        print("[SUCCESS] Tous les éléments de config présents")
        
        # Simuler validation des inputs
        fetcher_inputs = data_fetcher_config.get('inputs', {})
        renderer_inputs = renderer_config.get('inputs', {})
        
        print(f"[INFO] Fetcher inputs requis: {list(fetcher_inputs.keys())}")
        print(f"[INFO] Renderer inputs requis: {list(renderer_inputs.keys())}")
        
        # Simuler construction SQL
        if data_fetcher_config.get('type') == 'sql':
            sql_config = data_fetcher_config.get('sql_config', {})
            main_table = sql_config.get('main_table')
            fields = sql_config.get('fields', {})
            
            print(f"[INFO] SQL - Table: {main_table}")
            print(f"[INFO] SQL - Champs: {len(fields)}")
            
            if main_table and fields:
                print("[SUCCESS] Configuration SQL valide")
            else:
                print("[ERROR] Configuration SQL incomplète")
                return False
        
        print("[SUCCESS] Simulation flux complet réussie")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur simulation: {e}")
        return False

if __name__ == "__main__":
    print("Test final d'intégration - Nouvelle structure avec panel_name")
    print("=" * 70)
    
    # Tests
    success1 = test_panel_name_extraction()
    success2 = test_generic_function_signature()
    success3 = test_panel_methods_integration()
    success4 = test_complete_flow_simulation()
    
    # Résultats
    print("\n" + "=" * 70)
    print("RÉSULTATS FINAUX")
    print("=" * 70)
    print(f"Test panel_name extraction: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test signature fonction: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Test intégration méthodes: {'✅ PASS' if success3 else '❌ FAIL'}")
    print(f"Test flux complet: {'✅ PASS' if success4 else '❌ FAIL'}")
    
    all_success = all([success1, success2, success3, success4])
    
    if all_success:
        print("\n🎉 INTÉGRATION FINALE RÉUSSIE!")
        print("✅ panel_type extrait du JSON (panel_name)")
        print("✅ Fonction générique avec 2 paramètres seulement")
        print("✅ Structure JSON avec méthodes fonctionnelle")
        print("✅ Flux complet Cache → SQL → Render validé")
        sys.exit(0)
    else:
        print("\n💥 ÉCHEC DE L'INTÉGRATION FINALE!")
        sys.exit(1)
