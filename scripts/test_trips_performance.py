#!/usr/bin/env python3
"""
Script de test de performance pour reproduire le fonctionnement de Dash
Teste les différents scénarios de la page trajets pour identifier les latences
Simule les callbacks multiples et la sérialisation JSON comme dans Dash réel
"""

import sys
import os
import time
import json
import threading
import concurrent.futures
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mesurer le temps des imports critiques
import_start = time.time()
print(f"🕐 [IMPORTS START] Début des imports à {time.strftime('%H:%M:%S')}")

from dash_apps.services.trips_cache_service import TripsCacheService
import_trips_cache = time.time() - import_start
print(f"🕐 [IMPORT] TripsCacheService chargé en {import_trips_cache:.3f}s")

from dash_apps.repositories.trip_repository import TripRepository
import_repo = time.time() - import_start
print(f"🕐 [IMPORT] TripRepository chargé en {import_repo:.3f}s")

from dash_apps.components.trips_table_custom import render_custom_trips_table
import_table = time.time() - import_start
print(f"🕐 [IMPORT] render_custom_trips_table chargé en {import_table:.3f}s")

from dash_apps.config import Config
import_config = time.time() - import_start
print(f"🕐 [IMPORT] Config chargé en {import_config:.3f}s")

total_import_time = time.time() - import_start
print(f"🕐 [IMPORTS END] Tous les imports terminés en {total_import_time:.3f}s")


class DashStateSimulator:
    """Simule les variables de store Dash pour reproduire l'état réel"""
    
    def __init__(self):
        self.trips_current_page = 1
        self.selected_trip_id = None
        self.trips_filter_store = {}
        self.refresh_clicks = 0
    
    def reset(self):
        """Remet à zéro l'état simulé"""
        self.trips_current_page = 1
        self.selected_trip_id = None
        self.trips_filter_store = {}
        self.refresh_clicks = 0
    
    def change_page(self, new_page: int):
        """Simule un changement de page"""
        self.trips_current_page = new_page
    
    def select_trip(self, trip_id: str):
        """Simule la sélection d'un trajet"""
        self.selected_trip_id = trip_id
    
    def set_filters(self, filters: Dict[str, Any]):
        """Simule l'application de filtres"""
        self.trips_filter_store = filters
        self.trips_current_page = 1  # Reset page lors du filtrage


@dataclass
class CallbackResult:
    """Résultat d'un callback simulé"""
    output_name: str
    data: Any
    duration: float
    success: bool


class DashCallbackSimulator:
    """Simule le comportement réel des callbacks Dash avec latences"""
    
    @staticmethod
    def simulate_json_serialization(data: Any) -> float:
        """Simule la sérialisation JSON (coûteuse pour gros objets)"""
        start = time.time()
        try:
            json_str = json.dumps(data, default=str, ensure_ascii=False)
            # Simuler la désérialisation aussi
            json.loads(json_str)
        except:
            pass
        return time.time() - start
    
    @staticmethod
    def simulate_html_rendering(component) -> float:
        """Simule le rendu HTML complet"""
        start = time.time()
        try:
            # Simuler la conversion en HTML string
            str(component)
        except:
            pass
        return time.time() - start
    
    @staticmethod
    def simulate_concurrent_callbacks(callbacks: List[callable]) -> List[CallbackResult]:
        """Simule l'exécution concurrente de plusieurs callbacks"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Soumettre tous les callbacks
            futures = []
            for i, callback in enumerate(callbacks):
                future = executor.submit(callback)
                futures.append((f"callback_{i}", future))
            
            # Attendre les résultats
            for name, future in futures:
                start = time.time()
                try:
                    result = future.result(timeout=10)
                    duration = time.time() - start
                    results.append(CallbackResult(name, result, duration, True))
                except Exception as e:
                    duration = time.time() - start
                    results.append(CallbackResult(name, str(e), duration, False))
        
        return results


class PerformanceTester:
    """Testeur de performance pour les fonctions critiques avec simulation Dash réelle"""
    
    def __init__(self):
        self.state = DashStateSimulator()
        self.results = {}
        self.callback_sim = DashCallbackSimulator()
        self.global_start_time = None
        self.last_checkpoint_time = None
    
    def checkpoint(self, message: str):
        """Marque un point de contrôle temporel"""
        current_time = time.time()
        
        if self.global_start_time is None:
            self.global_start_time = current_time
            self.last_checkpoint_time = current_time
            print(f"🕐 [T+0.000s] {message}")
        else:
            elapsed_total = current_time - self.global_start_time
            elapsed_since_last = current_time - self.last_checkpoint_time
            print(f"🕐 [T+{elapsed_total:.3f}s] (+{elapsed_since_last:.3f}s) {message}")
            self.last_checkpoint_time = current_time
    
    def measure_time(self, func_name: str, func, *args, **kwargs):
        """Mesure le temps d'exécution d'une fonction"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  {func_name}: {duration:.3f}s")
            
            if func_name not in self.results:
                self.results[func_name] = []
            self.results[func_name].append(duration)
            
            return result, duration
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ {func_name}: ERREUR après {duration:.3f}s - {str(e)}")
            return None, duration
    
    def test_scenario_1_initial_load(self):
        """Scénario 1: Chargement initial de la page"""
        print("\n" + "="*60)
        print("🚀 SCÉNARIO 1: Chargement initial de la page")
        print("="*60)
        
        self.checkpoint("Début scénario 1 - Chargement initial")
        self.state.reset()
        
        # 1. Chargement des données de la première page
        page_size = Config.USERS_TABLE_PAGE_SIZE
        page_index = 0
        filter_params = {}
        
        result, duration = self.measure_time(
            "get_trips_page_result",
            TripsCacheService.get_trips_page_result,
            page_index, page_size, filter_params, False
        )
        
        if result:
            # 2. Extraction des données pour le tableau
            trips, total_trips, table_rows_data = self.measure_time(
                "extract_table_data",
                TripsCacheService.extract_table_data,
                result
            )[0]
            
            print(f"📊 Résultat: {len(trips)} trajets chargés sur {total_trips} total")
            
            # 3. Auto-sélection du premier trajet
            if table_rows_data and len(table_rows_data) > 0:
                first_trip = table_rows_data[0]
                if isinstance(first_trip, dict) and first_trip.get("trip_id"):
                    self.state.select_trip(first_trip["trip_id"])
                    print(f"🎯 Premier trajet sélectionné: {first_trip['trip_id']}")
            
            # 4. Rendu du tableau
            table_component, duration = self.measure_time(
                "render_custom_trips_table",
                render_custom_trips_table,
                table_rows_data,
                current_page=1,
                total_trips=total_trips,
                selected_trip_id=self.state.selected_trip_id
            )
            
            return True
        
        return False
    
    def test_scenario_2_page_change(self):
        """Scénario 2: Changement de page"""
        print("\n" + "="*60)
        print("📄 SCÉNARIO 2: Changement de page (1 → 2)")
        print("="*60)
        
        # Simuler le changement vers la page 2
        self.state.change_page(2)
        
        page_size = Config.USERS_TABLE_PAGE_SIZE
        page_index = 1  # Page 2 = index 1
        filter_params = {}
        
        # Chargement de la page 2
        result, duration = self.measure_time(
            "get_trips_page_result_page2",
            TripsCacheService.get_trips_page_result,
            page_index, page_size, filter_params, False
        )
        
        if result:
            trips, total_trips, table_rows_data = self.measure_time(
                "extract_table_data_page2",
                TripsCacheService.extract_table_data,
                result
            )[0]
            
            print(f"📊 Page 2: {len(trips)} trajets chargés")
            
            # Rendu du tableau page 2
            table_component, duration = self.measure_time(
                "render_table_page2",
                render_custom_trips_table,
                table_rows_data,
                current_page=2,
                total_trips=total_trips,
                selected_trip_id=self.state.selected_trip_id
            )
            
            return True
        
        return False
    
    def test_scenario_3_trip_selection(self):
        """Scénario 3: Sélection d'un trajet et chargement des panneaux"""
        print("\n" + "="*60)
        print("🎯 SCÉNARIO 3: Sélection d'un trajet et chargement des panneaux")
        print("="*60)
        
        # Utiliser un ID de trajet existant (on prend le premier de la page 1)
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, False)
        trips, _, table_rows_data = TripsCacheService.extract_table_data(result)
        
        if table_rows_data and len(table_rows_data) > 0:
            trip_id = table_rows_data[0].get("trip_id")
            self.state.select_trip(trip_id)
            print(f"🎯 Trajet sélectionné: {trip_id}")
            
            # Test des 3 panneaux
            details_panel, duration = self.measure_time(
                "get_trip_details_panel",
                TripsCacheService.get_trip_details_panel,
                trip_id
            )
            
            stats_panel, duration = self.measure_time(
                "get_trip_stats_panel",
                TripsCacheService.get_trip_stats_panel,
                trip_id
            )
            
            passengers_panel, duration = self.measure_time(
                "get_trip_passengers_panel",
                TripsCacheService.get_trip_passengers_panel,
                trip_id
            )
            
            return True
        
        print("❌ Aucun trajet disponible pour le test")
        return False
    
    def test_scenario_4_filtering(self):
        """Scénario 4: Application de filtres"""
        print("\n" + "="*60)
        print("🔍 SCÉNARIO 4: Application de filtres")
        print("="*60)
        
        # Test avec filtre de texte
        filters = {
            "text": "Dakar",
            "date_sort": "desc"
        }
        
        self.state.set_filters(filters)
        
        page_size = Config.USERS_TABLE_PAGE_SIZE
        page_index = 0
        
        result, duration = self.measure_time(
            "get_trips_filtered",
            TripsCacheService.get_trips_page_result,
            page_index, page_size, filters, False
        )
        
        if result:
            trips, total_trips, table_rows_data = self.measure_time(
                "extract_filtered_data",
                TripsCacheService.extract_table_data,
                result
            )[0]
            
            print(f"📊 Résultats filtrés: {len(trips)} trajets sur {total_trips} total")
            
            return True
        
        return False
    
    def test_scenario_5_cache_performance(self):
        """Scénario 5: Test de performance du cache"""
        print("\n" + "="*60)
        print("💾 SCÉNARIO 5: Performance du cache (hit vs miss)")
        print("="*60)
        
        page_size = Config.USERS_TABLE_PAGE_SIZE
        page_index = 0
        filter_params = {}
        
        # Premier appel (cache miss)
        TripsCacheService.clear_all_html_cache()  # Vider le cache
        result1, duration1 = self.measure_time(
            "cache_miss_first_call",
            TripsCacheService.get_trips_page_result,
            page_index, page_size, filter_params, True  # Force reload
        )
        
        # Deuxième appel (cache hit)
        result2, duration2 = self.measure_time(
            "cache_hit_second_call",
            TripsCacheService.get_trips_page_result,
            page_index, page_size, filter_params, False
        )
        
        if duration1 > 0 and duration2 > 0:
            speedup = duration1 / duration2
            print(f"🚀 Accélération du cache: {speedup:.2f}x plus rapide")
        
        return True
    
    def test_scenario_6_database_startup(self):
        """Scénario 6: Test de connexion à la base de données au démarrage"""
        print("\n" + "="*60)
        print("🗄️  SCÉNARIO 6: Connexion base de données au démarrage")
        print("="*60)
        
        # Test de connexion PostgreSQL/Supabase
        postgres_duration = self.measure_time(
            "postgres_connection_test",
            self._test_postgres_connection
        )[1]
        
        # Test de connexion Redis
        redis_duration = self.measure_time(
            "redis_connection_test",
            self._test_redis_connection
        )[1]
        
        # Test de fallback SQLite
        sqlite_duration = self.measure_time(
            "sqlite_fallback_test",
            self._test_sqlite_fallback
        )[1]
        
        # Test de chargement initial avec connexions froides
        cold_start_duration = self.measure_time(
            "cold_start_full_load",
            self._simulate_cold_start
        )[1]
        
        print(f"📊 Temps de connexion total: {postgres_duration + redis_duration + sqlite_duration:.3f}s")
        
        return True
    
    def test_scenario_7_concurrent_callbacks(self):
        """Scénario 7: Simulation des callbacks concurrents comme dans Dash réel"""
        print("\n" + "="*60)
        print("🔄 SCÉNARIO 7: Callbacks concurrents (simulation Dash réelle)")
        print("="*60)
        
        # Simuler le changement de page qui déclenche 4 callbacks simultanés
        callbacks = [
            lambda: self._simulate_render_trips_table(),
            lambda: self._simulate_render_trip_details(),
            lambda: self._simulate_render_trip_stats(),
            lambda: self._simulate_render_trip_passengers()
        ]
        
        start_time = time.time()
        results = self.callback_sim.simulate_concurrent_callbacks(callbacks)
        total_duration = time.time() - start_time
        
        print(f"🔄 {len(results)} callbacks exécutés en parallèle")
        print(f"⏱️  Durée totale concurrente: {total_duration:.3f}s")
        
        # Calculer la durée séquentielle pour comparaison
        sequential_duration = sum(r.duration for r in results)
        print(f"⏱️  Durée séquentielle équivalente: {sequential_duration:.3f}s")
        
        if sequential_duration > 0:
            speedup = sequential_duration / total_duration
            print(f"🚀 Gain de la concurrence: {speedup:.2f}x plus rapide")
        
        return True
    
    def _test_postgres_connection(self):
        """Test de connexion PostgreSQL/Supabase"""
        try:
            from dash_apps.core.database import SessionLocal
            from sqlalchemy import text
            with SessionLocal() as db:
                # Test simple de connexion avec text() explicite
                db.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"❌ PostgreSQL indisponible: {str(e)[:100]}...")
            return False
    
    def _test_redis_connection(self):
        """Test de connexion Redis"""
        try:
            from dash_apps.services.redis_cache import redis_cache
            # Utiliser ping() pour tester la connexion Redis
            redis_cache.redis_client.ping()
            return True
        except Exception as e:
            print(f"❌ Redis indisponible: {str(e)[:100]}...")
            return False
    
    def _test_sqlite_fallback(self):
        """Test de fallback SQLite"""
        try:
            import sqlite3
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"❌ SQLite fallback échoué: {str(e)[:100]}...")
            return False
    
    def _simulate_cold_start(self):
        """Simule un démarrage à froid complet"""
        # Vider tous les caches
        TripsCacheService.clear_all_html_cache()
        
        # Simuler le premier chargement de page
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, True)
        
        if result:
            trips, total_trips, table_rows_data = TripsCacheService.extract_table_data(result)
            
            # Simuler la sérialisation JSON (coûteuse)
            json_duration = self.callback_sim.simulate_json_serialization(table_rows_data)
            
            # Simuler le rendu HTML
            table_component = render_custom_trips_table(
                table_rows_data, 1, total_trips, None
            )
            html_duration = self.callback_sim.simulate_html_rendering(table_component)
            
            print(f"📊 Cold start: {len(trips)} trajets, JSON: {json_duration:.3f}s, HTML: {html_duration:.3f}s")
            
        return True
    
    def _simulate_render_trips_table(self):
        """Simule le callback render_trips_table"""
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, False)
        trips, total_trips, table_rows_data = TripsCacheService.extract_table_data(result)
        
        # Sérialisation JSON
        json_duration = self.callback_sim.simulate_json_serialization(table_rows_data)
        
        # Rendu du tableau
        table_component = render_custom_trips_table(table_rows_data, 1, total_trips, None)
        html_duration = self.callback_sim.simulate_html_rendering(table_component)
        
        return {"trips_count": len(trips), "json_time": json_duration, "html_time": html_duration}
    
    def _simulate_render_trip_details(self):
        """Simule le callback render_trip_details_panel"""
        # Utiliser un ID fictif ou le premier disponible
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, False)
        trips, _, table_rows_data = TripsCacheService.extract_table_data(result)
        
        if table_rows_data and len(table_rows_data) > 0:
            trip_id = table_rows_data[0].get("trip_id")
            if trip_id:
                panel = TripsCacheService.get_trip_details_panel(trip_id)
                html_duration = self.callback_sim.simulate_html_rendering(panel)
                return {"trip_id": trip_id, "html_time": html_duration}
        
        return {"trip_id": None, "html_time": 0}
    
    def _simulate_render_trip_stats(self):
        """Simule le callback render_trip_stats_panel"""
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, False)
        trips, _, table_rows_data = TripsCacheService.extract_table_data(result)
        
        if table_rows_data and len(table_rows_data) > 0:
            trip_id = table_rows_data[0].get("trip_id")
            if trip_id:
                panel = TripsCacheService.get_trip_stats_panel(trip_id)
                html_duration = self.callback_sim.simulate_html_rendering(panel)
                return {"trip_id": trip_id, "html_time": html_duration}
        
        return {"trip_id": None, "html_time": 0}
    
    def _simulate_render_trip_passengers(self):
        """Simule le callback render_trip_passengers_panel"""
        page_size = Config.USERS_TABLE_PAGE_SIZE
        result = TripsCacheService.get_trips_page_result(0, page_size, {}, False)
        trips, _, table_rows_data = TripsCacheService.extract_table_data(result)
        
        if table_rows_data and len(table_rows_data) > 0:
            trip_id = table_rows_data[0].get("trip_id")
            if trip_id:
                panel = TripsCacheService.get_trip_passengers_panel(trip_id)
                html_duration = self.callback_sim.simulate_html_rendering(panel)
                return {"trip_id": trip_id, "html_time": html_duration}
        
        return {"trip_id": None, "html_time": 0}
    
    def run_all_tests(self):
        """Lance tous les tests de performance"""
        self.checkpoint("Démarrage des tests de performance")
        print("🧪 DÉMARRAGE DES TESTS DE PERFORMANCE")
        print("="*60)
        
        # Lancer tous les scénarios
        scenarios = [
            ("Scénario 1", self.test_scenario_1_initial_load),
            ("Scénario 2", self.test_scenario_2_page_change),
            ("Scénario 3", self.test_scenario_3_trip_selection),
            ("Scénario 4", self.test_scenario_4_filtering),
            ("Scénario 5", self.test_scenario_5_cache_performance),
            ("Scénario 6", self.test_scenario_6_database_startup),
            ("Scénario 7", self.test_scenario_7_concurrent_callbacks)
        ]
        
        success_count = 0
        for i, (scenario_name, scenario_func) in enumerate(scenarios):
            try:
                if i > 0:  # Ajouter une pause entre les scénarios
                    self.checkpoint(f"Transition vers {scenario_name}")
                self.checkpoint(f"Début {scenario_name}")
                if scenario_func():
                    success_count += 1
                    self.checkpoint(f"Fin {scenario_name} - SUCCÈS")
                else:
                    self.checkpoint(f"Fin {scenario_name} - ÉCHEC")
            except Exception as e:
                print(f"❌ Erreur dans le scénario: {str(e)}")
                self.checkpoint(f"Fin {scenario_name} - ERREUR")
        
        # Résumé des performances
        self.checkpoint("Génération du résumé des performances")
        self.print_performance_summary()
        
        self.checkpoint("Tests terminés")
        print(f"\n✅ Tests terminés: {success_count}/{len(scenarios)} scénarios réussis")
    
    def print_performance_summary(self):
        """Affiche un résumé des performances"""
        print("\n" + "="*60)
        print("📈 RÉSUMÉ DES PERFORMANCES")
        print("="*60)
        
        for func_name, durations in self.results.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                
                print(f"📊 {func_name}:")
                print(f"   Moyenne: {avg_duration:.3f}s")
                print(f"   Min: {min_duration:.3f}s")
                print(f"   Max: {max_duration:.3f}s")
                print(f"   Appels: {len(durations)}")
                
                # Alertes de performance
                if avg_duration > 2.0:
                    print(f"   ⚠️  LENT: Moyenne > 2s")
                elif avg_duration > 1.0:
                    print(f"   ⚡ MOYEN: Moyenne > 1s")
                else:
                    print(f"   ✅ RAPIDE: < 1s")
                print()


def main():
    """Point d'entrée principal"""
    # Mesurer le temps AVANT la création du testeur
    import time
    script_start = time.time()
    print(f"🕐 [SCRIPT START] Lancement du script à {time.strftime('%H:%M:%S')}")
    
    tester = PerformanceTester()
    init_time = time.time() - script_start
    print(f"🕐 [INIT] Initialisation terminée après {init_time:.3f}s")
    
    tester.checkpoint("Initialisation du script de test")
    print("🚀 Script de test de performance - Page Trajets")
    print("Reproduit le fonctionnement de Dash pour identifier les latences")
    
    tester.checkpoint("Connexions et imports terminés")
    tester.run_all_tests()


if __name__ == "__main__":
    main()
