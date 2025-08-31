#!/usr/bin/env python3
"""
Test simple des performances du cache HTML sans dépendances DB
"""

import time
import statistics
from typing import Dict, List

# Simuler des données utilisateur pour les tests
MOCK_USERS = [
    {"uid": f"user_{i:03d}", "name": f"User {i}", "email": f"user{i}@test.com", 
     "total_trips": i * 2, "total_distance": i * 100.5, "avg_rating": 4.2 + (i % 10) * 0.1}
    for i in range(1, 21)
]

class MockUsersCacheService:
    """Version simplifiée du cache pour les tests de performance"""
    
    _html_cache = {}
    _local_cache = {}
    
    @staticmethod
    def get_cached_panel(user_id: str, panel_type: str):
        """Récupère un panneau depuis le cache"""
        cache_key = f"{user_id}_{panel_type}"
        return MockUsersCacheService._html_cache.get(cache_key)
    
    @staticmethod
    def set_cached_panel(user_id: str, panel_type: str, panel_html):
        """Met en cache un panneau"""
        cache_key = f"{user_id}_{panel_type}"
        MockUsersCacheService._html_cache[cache_key] = panel_html
    
    @staticmethod
    def clear_all_cache():
        """Efface tout le cache"""
        MockUsersCacheService._html_cache.clear()
        MockUsersCacheService._local_cache.clear()
    
    @staticmethod
    def get_user_data(user_id: str):
        """Récupère les données d'un utilisateur"""
        return next((user for user in MOCK_USERS if user["uid"] == user_id), None)

def mock_render_panel(user_data: Dict, panel_type: str) -> str:
    """Simule la génération d'un panneau HTML"""
    # Simuler du travail de rendu (comme Jinja2)
    time.sleep(0.001)  # 1ms de simulation
    
    if panel_type == "profile":
        return f"<div>Profile: {user_data['name']} ({user_data['email']})</div>"
    elif panel_type == "stats":
        return f"<div>Stats: {user_data['total_trips']} trips, {user_data['total_distance']}km</div>"
    elif panel_type == "trips":
        return f"<div>Trips: Rating {user_data['avg_rating']}</div>"
    
    return "<div>Unknown panel</div>"

class SimpleCachePerformanceTester:
    """Testeur de performance simplifié"""
    
    def __init__(self):
        self.results = {}
    
    def test_cache_miss_performance(self, iterations: int = 10):
        """Test sans cache (génération complète)"""
        print(f"\n🧪 Test Cache Miss - {iterations} itérations")
        
        times = []
        for i in range(iterations):
            MockUsersCacheService.clear_all_cache()
            
            user_id = MOCK_USERS[i % len(MOCK_USERS)]["uid"]
            user_data = MockUsersCacheService.get_user_data(user_id)
            
            start_time = time.perf_counter()
            
            # Générer les 3 panneaux
            profile_panel = mock_render_panel(user_data, "profile")
            stats_panel = mock_render_panel(user_data, "stats")
            trips_panel = mock_render_panel(user_data, "trips")
            
            # Mettre en cache
            MockUsersCacheService.set_cached_panel(user_id, "profile", profile_panel)
            MockUsersCacheService.set_cached_panel(user_id, "stats", stats_panel)
            MockUsersCacheService.set_cached_panel(user_id, "trips", trips_panel)
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            times.append(execution_time)
            
            print(f"  Itération {i+1}: {execution_time:.3f}ms")
        
        avg_time = statistics.mean(times)
        self.results['cache_miss'] = {
            'times': times,
            'average': avg_time,
            'min': min(times),
            'max': max(times)
        }
        print(f"📊 Moyenne Cache Miss: {avg_time:.3f}ms")
    
    def test_cache_hit_performance(self, iterations: int = 10):
        """Test avec cache (récupération rapide)"""
        print(f"\n🎯 Test Cache Hit - {iterations} itérations")
        
        # Précharger le cache
        for user in MOCK_USERS[:5]:
            user_id = user["uid"]
            profile_panel = mock_render_panel(user, "profile")
            stats_panel = mock_render_panel(user, "stats")
            trips_panel = mock_render_panel(user, "trips")
            
            MockUsersCacheService.set_cached_panel(user_id, "profile", profile_panel)
            MockUsersCacheService.set_cached_panel(user_id, "stats", stats_panel)
            MockUsersCacheService.set_cached_panel(user_id, "trips", trips_panel)
        
        times = []
        for i in range(iterations):
            user_id = MOCK_USERS[i % 5]["uid"]
            
            start_time = time.perf_counter()
            
            # Récupérer depuis le cache
            profile_panel = MockUsersCacheService.get_cached_panel(user_id, "profile")
            stats_panel = MockUsersCacheService.get_cached_panel(user_id, "stats")
            trips_panel = MockUsersCacheService.get_cached_panel(user_id, "trips")
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            times.append(execution_time)
            
            print(f"  Itération {i+1}: {execution_time:.3f}ms")
        
        avg_time = statistics.mean(times)
        self.results['cache_hit'] = {
            'times': times,
            'average': avg_time,
            'min': min(times),
            'max': max(times)
        }
        print(f"📊 Moyenne Cache Hit: {avg_time:.3f}ms")
    
    def test_memory_usage(self):
        """Test de l'utilisation mémoire du cache"""
        print(f"\n💾 Test Utilisation Mémoire")
        
        # Remplir le cache avec différentes quantités de données
        cache_sizes = [10, 50, 100, 200]
        
        for size in cache_sizes:
            MockUsersCacheService.clear_all_cache()
            
            # Générer des données de test
            test_users = [
                {"uid": f"test_user_{i}", "name": f"Test User {i}", "email": f"test{i}@test.com",
                 "total_trips": i, "total_distance": i * 10, "avg_rating": 4.0}
                for i in range(size)
            ]
            
            start_time = time.perf_counter()
            
            # Remplir le cache
            for user in test_users:
                user_id = user["uid"]
                for panel_type in ["profile", "stats", "trips"]:
                    panel = mock_render_panel(user, panel_type)
                    MockUsersCacheService.set_cached_panel(user_id, panel_type, panel)
            
            fill_time = (time.perf_counter() - start_time) * 1000
            cache_entries = len(MockUsersCacheService._html_cache)
            
            print(f"  {size} utilisateurs: {cache_entries} entrées, remplissage en {fill_time:.2f}ms")
    
    def generate_report(self):
        """Génère un rapport de performance"""
        print(f"\n" + "="*60)
        print("📋 RAPPORT DE PERFORMANCE DU CACHE SIMPLIFIÉ")
        print("="*60)
        
        if 'cache_miss' in self.results and 'cache_hit' in self.results:
            miss_avg = self.results['cache_miss']['average']
            hit_avg = self.results['cache_hit']['average']
            improvement = ((miss_avg - hit_avg) / miss_avg) * 100
            
            print(f"\n🚀 AMÉLIORATION GLOBALE: {improvement:.1f}%")
            print(f"   Cache Miss:  {miss_avg:.3f}ms")
            print(f"   Cache Hit:   {hit_avg:.3f}ms")
            print(f"   Gain:        {miss_avg - hit_avg:.3f}ms")
            print(f"   Facteur:     {miss_avg / hit_avg:.1f}x plus rapide")
        
        print(f"\n📊 STATISTIQUES DÉTAILLÉES:")
        if 'cache_miss' in self.results:
            miss = self.results['cache_miss']
            print(f"   Cache Miss - Min: {miss['min']:.3f}ms, Max: {miss['max']:.3f}ms")
        
        if 'cache_hit' in self.results:
            hit = self.results['cache_hit']
            print(f"   Cache Hit  - Min: {hit['min']:.3f}ms, Max: {hit['max']:.3f}ms")
        
        print("\n" + "="*60)

def main():
    """Fonction principale du test"""
    print("🧪 BENCHMARK SIMPLIFIÉ DU SYSTÈME DE CACHE")
    print("=" * 50)
    
    tester = SimpleCachePerformanceTester()
    
    try:
        # Exécuter les tests
        tester.test_cache_miss_performance(10)
        tester.test_cache_hit_performance(10)
        tester.test_memory_usage()
        
        # Générer le rapport
        tester.generate_report()
        
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
