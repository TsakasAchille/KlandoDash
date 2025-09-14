#!/usr/bin/env python3
"""
Script de test de performance pour le système de cache des trips
Teste les niveaux L1 (mémoire), L2 (Redis), et L3 (API REST)
"""

import time
import statistics
import json
import os
import sys
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dash_apps.services.trips_cache_service import TripsCacheService
from dash_apps.services.redis_cache import redis_cache
from dash_apps.repositories.repository_factory import RepositoryFactory

class CachePerformanceTester:
    """
    Testeur de performance pour le système de cache des trips
    """
    
    def __init__(self):
        self.results = {
            'L1_memory': [],
            'L2_redis': [],
            'L3_api': [],
            'test_metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_iterations': 0
            }
        }
        self.trip_ids = []
        
    def setup_test_data(self, num_trips: int = 10) -> List[str]:
        """
        Récupère une liste de trip IDs pour les tests
        
        Args:
            num_trips: Nombre de trips à récupérer pour les tests
            
        Returns:
            Liste des trip IDs
        """
        print(f"🔍 Récupération de {num_trips} trips pour les tests...")
        
        try:
            trip_repository = RepositoryFactory.get_trip_repository()
            trips = trip_repository.get_all(limit=num_trips)
            
            if not trips:
                print("❌ Aucun trip trouvé dans la base de données")
                return []
                
            self.trip_ids = [trip.get('trip_id') for trip in trips if trip.get('trip_id')]
            print(f"✅ {len(self.trip_ids)} trips récupérés pour les tests")
            
            return self.trip_ids
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des trips: {e}")
            return []
    
    def clear_all_caches(self):
        """Vide tous les niveaux de cache"""
        print("🧹 Nettoyage de tous les caches...")
        
        # Vider le cache Redis (L2)
        try:
            redis_cache.clear_pattern("trip_*")
            print("✅ Cache Redis (L2) vidé")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage Redis: {e}")
        
        # Vider le cache mémoire (L1)
        try:
            TripsCacheService._html_cache.clear()
            TripsCacheService._local_cache.clear()
            TripsCacheService._cache_timestamps.clear()
            print("✅ Cache mémoire (L1) vidé")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage L1: {e}")
    
    def test_l3_api_performance(self, trip_id: str, iterations: int = 5) -> List[float]:
        """
        Teste les performances de l'API REST (L3) - pas de cache
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Liste des temps de réponse en secondes
        """
        times = []
        
        for i in range(iterations):
            # Vider tous les caches avant chaque test L3
            self.clear_all_caches()
            
            start_time = time.time()
            
            try:
                # Appel direct à l'API REST sans cache
                trip_repository = RepositoryFactory.get_trip_repository()
                trip_data = trip_repository.get_trip(trip_id)
                
                if trip_data:
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  L3 (API) - Itération {i+1}: {response_time:.4f}s")
                else:
                    print(f"  L3 (API) - Itération {i+1}: Aucune donnée retournée")
                    
            except Exception as e:
                print(f"  L3 (API) - Itération {i+1}: Erreur - {e}")
        
        return times
    
    def test_l2_redis_performance(self, trip_id: str, iterations: int = 5) -> List[float]:
        """
        Teste les performances du cache Redis (L2)
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Liste des temps de réponse en secondes
        """
        times = []
        
        # Première requête pour peupler le cache Redis
        try:
            TripsCacheService.get_trip_details_panel(trip_id)
            print(f"  L2 (Redis) - Cache peuplé pour trip {trip_id[:8]}...")
        except Exception as e:
            print(f"  L2 (Redis) - Erreur lors du peuplement: {e}")
            return times
        
        for i in range(iterations):
            # Vider le cache L1 avant chaque test L2
            TripsCacheService._html_cache.clear()
            
            start_time = time.time()
            
            try:
                # Récupération depuis Redis (cache L2)
                cache_key = f"trip_details_{trip_id}"
                cached_data = redis_cache.get(cache_key)
                
                if cached_data:
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  L2 (Redis) - Itération {i+1}: {response_time:.4f}s")
                else:
                    print(f"  L2 (Redis) - Itération {i+1}: Cache miss")
                    
            except Exception as e:
                print(f"  L2 (Redis) - Itération {i+1}: Erreur - {e}")
        
        return times
    
    def test_l1_memory_performance(self, trip_id: str, iterations: int = 5) -> List[float]:
        """
        Teste les performances du cache mémoire (L1)
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Liste des temps de réponse en secondes
        """
        times = []
        
        # Première requête pour peupler tous les caches
        try:
            TripsCacheService.get_trip_panels_data(trip_id, use_cache=True)
            print(f"  L1 (Mémoire) - Cache peuplé pour trip {trip_id[:8]}...")
        except Exception as e:
            print(f"  L1 (Mémoire) - Erreur lors du peuplement: {e}")
            return times
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Récupération depuis le cache mémoire (L1)
                data = TripsCacheService.get_trip_panels_data(trip_id, use_cache=True)
                
                if data:
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  L1 (Mémoire) - Itération {i+1}: {response_time:.4f}s")
                else:
                    print(f"  L1 (Mémoire) - Itération {i+1}: Aucune donnée")
                    
            except Exception as e:
                print(f"  L1 (Mémoire) - Itération {i+1}: Erreur - {e}")
        
        return times
    
    def run_performance_tests(self, iterations: int = 5, num_trips: int = 3):
        """
        Lance tous les tests de performance
        
        Args:
            iterations: Nombre d'itérations par test
            num_trips: Nombre de trips à tester
        """
        print("🚀 Démarrage des tests de performance du cache des trips")
        print("=" * 60)
        
        # Setup des données de test
        trip_ids = self.setup_test_data(num_trips)
        if not trip_ids:
            print("❌ Impossible de continuer sans données de test")
            return
        
        self.results['test_metadata']['test_iterations'] = iterations
        self.results['test_metadata']['num_trips'] = len(trip_ids)
        
        for idx, trip_id in enumerate(trip_ids):
            print(f"\n📊 Test du trip {idx+1}/{len(trip_ids)}: {trip_id[:8]}...")
            print("-" * 40)
            
            # Test L3 (API REST)
            print("🔄 Test L3 (API REST - pas de cache)...")
            l3_times = self.test_l3_api_performance(trip_id, iterations)
            self.results['L3_api'].extend(l3_times)
            
            # Test L2 (Redis)
            print("🔄 Test L2 (Cache Redis)...")
            l2_times = self.test_l2_redis_performance(trip_id, iterations)
            self.results['L2_redis'].extend(l2_times)
            
            # Test L1 (Mémoire)
            print("🔄 Test L1 (Cache Mémoire)...")
            l1_times = self.test_l1_memory_performance(trip_id, iterations)
            self.results['L1_memory'].extend(l1_times)
    
    def calculate_statistics(self, times: List[float]) -> Dict[str, float]:
        """
        Calcule les statistiques pour une liste de temps
        
        Args:
            times: Liste des temps de réponse
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if not times:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0
            }
        
        return {
            'count': len(times),
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def print_results(self):
        """Affiche les résultats des tests"""
        print("\n" + "=" * 60)
        print("📈 RÉSULTATS DES TESTS DE PERFORMANCE")
        print("=" * 60)
        
        # Statistiques pour chaque niveau de cache
        levels = [
            ('L1 (Mémoire)', self.results['L1_memory']),
            ('L2 (Redis)', self.results['L2_redis']),
            ('L3 (API REST)', self.results['L3_api'])
        ]
        
        for level_name, times in levels:
            stats = self.calculate_statistics(times)
            
            print(f"\n🎯 {level_name}")
            print("-" * 30)
            print(f"  Nombre de tests: {stats['count']}")
            print(f"  Temps moyen:     {stats['mean']:.4f}s")
            print(f"  Temps médian:    {stats['median']:.4f}s")
            print(f"  Temps min:       {stats['min']:.4f}s")
            print(f"  Temps max:       {stats['max']:.4f}s")
            print(f"  Écart-type:      {stats['std_dev']:.4f}s")
        
        # Comparaison des performances
        if all(self.results[key] for key in ['L1_memory', 'L2_redis', 'L3_api']):
            l1_avg = statistics.mean(self.results['L1_memory'])
            l2_avg = statistics.mean(self.results['L2_redis'])
            l3_avg = statistics.mean(self.results['L3_api'])
            
            print(f"\n⚡ COMPARAISON DES PERFORMANCES")
            print("-" * 30)
            print(f"  L2 vs L3: {l3_avg/l2_avg:.1f}x plus rapide")
            print(f"  L1 vs L3: {l3_avg/l1_avg:.1f}x plus rapide")
            print(f"  L1 vs L2: {l2_avg/l1_avg:.1f}x plus rapide")
    
    def save_results_to_file(self, filename: str = None):
        """
        Sauvegarde les résultats dans un fichier JSON
        
        Args:
            filename: Nom du fichier (optionnel)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cache_performance_results_{timestamp}.json"
        
        # Ajouter les statistiques aux résultats
        for level in ['L1_memory', 'L2_redis', 'L3_api']:
            times = self.results[level]
            self.results[f'{level}_stats'] = self.calculate_statistics(times)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Résultats sauvegardés dans: {filename}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")


def main():
    """Fonction principale"""
    print("🎯 Test de Performance du Cache des Trips - KlandoDash")
    print("=" * 60)
    
    # Paramètres du test
    iterations = 5  # Nombre d'itérations par niveau de cache
    num_trips = 3   # Nombre de trips à tester
    
    # Créer et lancer le testeur
    tester = CachePerformanceTester()
    
    try:
        # Lancer les tests
        tester.run_performance_tests(iterations=iterations, num_trips=num_trips)
        
        # Afficher les résultats
        tester.print_results()
        
        # Sauvegarder les résultats
        tester.save_results_to_file()
        
        print(f"\n✅ Tests terminés avec succès!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
