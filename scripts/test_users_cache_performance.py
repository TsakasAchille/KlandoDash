#!/usr/bin/env python3
"""
Script de test des performances du système de cache optimisé
Mesure les temps de réponse avec et sans cache pour différents scénarios
"""

import time
import sys
import os
import statistics
from typing import List, Dict

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration minimale des variables d'environnement pour les tests
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('SECRET_KEY', 'test-key-for-cache-performance')
os.environ.setdefault('DASH_DEBUG', 'False')

from dash_apps.services.users_cache_service import UsersCacheService
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips


class CachePerformanceTester:
    """Testeur de performance pour le système de cache"""
    
    def __init__(self):
        self.test_user_ids = []
        self.results = {}
    
    def setup_test_data(self, num_users: int = 20):
        """Récupère des UIDs d'utilisateurs réels pour les tests"""
        print(f"🔍 Récupération de {num_users} utilisateurs pour les tests...")
        
        try:
            # Récupérer une page d'utilisateurs via le service de cache
            result = UsersCacheService.get_users_page_result(0, num_users, {}, force_reload=True)
            if result and 'users' in result:
                self.test_user_ids = [user['uid'] for user in result['users'] if 'uid' in user]
                print(f"✅ {len(self.test_user_ids)} utilisateurs récupérés")
                return len(self.test_user_ids) > 0
            else:
                print("❌ Aucune donnée utilisateur trouvée")
                return False
        except Exception as e:
            print(f"❌ Erreur récupération utilisateurs: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def measure_time(self, func, *args, **kwargs):
        """Mesure le temps d'exécution d'une fonction"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, (end_time - start_time) * 1000  # Retour en millisecondes
    
    def test_cache_miss_performance(self, iterations: int = 5):
        """Test des performances sans cache (cache miss)"""
        print(f"\n🧪 Test Cache Miss - {iterations} itérations")
        
        times = []
        for i in range(iterations):
            # Nettoyer le cache avant chaque test
            UsersCacheService.clear_all_html_cache()
            UsersCacheService._local_cache.clear()
            
            user_id = self.test_user_ids[i % len(self.test_user_ids)]
            
            # Mesurer le temps de génération complète
            start_time = time.perf_counter()
            
            # Récupérer données utilisateur
            user_data = UsersCacheService.get_user_data(user_id)
            
            # Générer les 3 panneaux
            if user_data:
                profile_panel = render_user_profile(user_data)
                stats_panel = render_user_stats(user_data)
                trips_panel = render_user_trips(user_data)
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            times.append(execution_time)
            
            print(f"  Itération {i+1}: {execution_time:.2f}ms")
        
        avg_time = statistics.mean(times)
        self.results['cache_miss'] = {
            'times': times,
            'average': avg_time,
            'min': min(times),
            'max': max(times)
        }
        print(f"📊 Moyenne Cache Miss: {avg_time:.2f}ms")
    
    def test_cache_hit_performance(self, iterations: int = 5):
        """Test des performances avec cache (cache hit)"""
        print(f"\n🎯 Test Cache Hit - {iterations} itérations")
        
        # Précharger le cache pour les utilisateurs de test
        print("  Préchargement du cache...")
        UsersCacheService.preload_user_panels(self.test_user_ids[:5], async_mode=False)
        
        times = []
        for i in range(iterations):
            user_id = self.test_user_ids[i % min(5, len(self.test_user_ids))]
            
            # Mesurer le temps de récupération depuis le cache
            start_time = time.perf_counter()
            
            # Récupérer depuis le cache HTML
            profile_panel = UsersCacheService.get_cached_panel(user_id, "profile")
            stats_panel = UsersCacheService.get_cached_panel(user_id, "stats")
            trips_panel = UsersCacheService.get_cached_panel(user_id, "trips")
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            times.append(execution_time)
            
            print(f"  Itération {i+1}: {execution_time:.2f}ms")
        
        avg_time = statistics.mean(times)
        self.results['cache_hit'] = {
            'times': times,
            'average': avg_time,
            'min': min(times),
            'max': max(times)
        }
        print(f"📊 Moyenne Cache Hit: {avg_time:.2f}ms")
    
    def test_preload_performance(self):
        """Test des performances du préchargement"""
        print(f"\n⚡ Test Préchargement Asynchrone")
        
        # Nettoyer le cache
        UsersCacheService.clear_all_html_cache()
        
        test_users = self.test_user_ids[:8]
        
        # Test préchargement synchrone
        start_time = time.perf_counter()
        UsersCacheService.preload_user_panels(test_users, ['profile', 'stats'], async_mode=False)
        sync_time = (time.perf_counter() - start_time) * 1000
        
        # Nettoyer le cache
        UsersCacheService.clear_all_html_cache()
        
        # Test préchargement asynchrone
        start_time = time.perf_counter()
        UsersCacheService.preload_user_panels(test_users, ['profile', 'stats'], async_mode=True)
        async_time = (time.perf_counter() - start_time) * 1000
        
        # Attendre un peu pour que les threads se terminent
        time.sleep(0.5)
        
        self.results['preload'] = {
            'sync_time': sync_time,
            'async_time': async_time,
            'improvement': ((sync_time - async_time) / sync_time) * 100
        }
        
        print(f"  Préchargement synchrone: {sync_time:.2f}ms")
        print(f"  Préchargement asynchrone: {async_time:.2f}ms")
        print(f"  Amélioration: {self.results['preload']['improvement']:.1f}%")
    
    def test_cache_stats(self):
        """Test des statistiques de cache"""
        print(f"\n📈 Statistiques du Cache")
        
        stats = UsersCacheService.get_cache_stats()
        print(f"  Cache local: {stats['local_cache_size']} entrées")
        print(f"  Cache HTML: {stats['html_cache_size']} panneaux")
        print(f"  TTL local: {stats['local_cache_ttl']}s")
        
        self.results['cache_stats'] = stats
    
    def generate_report(self):
        """Génère un rapport de performance"""
        print(f"\n" + "="*60)
        print("📋 RAPPORT DE PERFORMANCE DU CACHE")
        print("="*60)
        
        if 'cache_miss' in self.results and 'cache_hit' in self.results:
            miss_avg = self.results['cache_miss']['average']
            hit_avg = self.results['cache_hit']['average']
            improvement = ((miss_avg - hit_avg) / miss_avg) * 100
            
            print(f"\n🚀 AMÉLIORATION GLOBALE: {improvement:.1f}%")
            print(f"   Cache Miss:  {miss_avg:.2f}ms")
            print(f"   Cache Hit:   {hit_avg:.2f}ms")
            print(f"   Gain:        {miss_avg - hit_avg:.2f}ms")
        
        if 'preload' in self.results:
            preload = self.results['preload']
            print(f"\n⚡ PRÉCHARGEMENT:")
            print(f"   Synchrone:   {preload['sync_time']:.2f}ms")
            print(f"   Asynchrone:  {preload['async_time']:.2f}ms")
            print(f"   Amélioration: {preload['improvement']:.1f}%")
        
        if 'cache_stats' in self.results:
            stats = self.results['cache_stats']
            print(f"\n📊 UTILISATION MÉMOIRE:")
            print(f"   Cache local: {stats['local_cache_size']} entrées")
            print(f"   Cache HTML:  {stats['html_cache_size']} panneaux")
        
        print("\n" + "="*60)


def main():
    """Fonction principale du test"""
    print("🧪 BENCHMARK DU SYSTÈME DE CACHE KLANDODASH")
    print("=" * 50)
    
    tester = CachePerformanceTester()
    
    # Configuration des tests
    if not tester.setup_test_data(20):
        print("❌ Impossible de configurer les données de test")
        return
    
    try:
        # Exécuter les tests
        tester.test_cache_miss_performance(5)
        tester.test_cache_hit_performance(5)
        tester.test_preload_performance()
        tester.test_cache_stats()
        
        # Générer le rapport
        tester.generate_report()
        
    except Exception as e:
        print(f"❌ Erreur durant les tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
