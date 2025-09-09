#!/usr/bin/env python3
"""
Script de test de performance pour le système de cache local des trips
Teste L1 (cache local) vs L3 (API REST directe)
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
from dash_apps.repositories.repository_factory import RepositoryFactory

class LocalCachePerformanceTester:
    """
    Testeur de performance pour le système de cache local des trips
    """
    
    def __init__(self):
        self.results = {
            'L1_local_cache': [],
            'L3_api_direct': [],
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
    
    def clear_local_cache(self):
        """Vide le cache local"""
        print("🧹 Nettoyage du cache local...")
        
        try:
            TripsCacheService._html_cache.clear()
            TripsCacheService._local_cache.clear()
            TripsCacheService._cache_timestamps.clear()
            print("✅ Cache local vidé")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
    
    def test_l3_api_direct_performance(self, trip_id: str, iterations: int = 5) -> List[float]:
        """
        Teste les performances de l'API REST directe (L3) - pas de cache
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Liste des temps de réponse en secondes
        """
        times = []
        
        for i in range(iterations):
            # Vider le cache avant chaque test L3
            self.clear_local_cache()
            
            start_time = time.time()
            
            try:
                # Appel direct à l'API REST sans cache
                trip_repository = RepositoryFactory.get_trip_repository()
                trip_data = trip_repository.get_trip(trip_id)
                
                if trip_data:
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  L3 (API directe) - Itération {i+1}: {response_time:.4f}s")
                else:
                    print(f"  L3 (API directe) - Itération {i+1}: Aucune donnée retournée")
                    
            except Exception as e:
                print(f"  L3 (API directe) - Itération {i+1}: Erreur - {e}")
        
        return times
    
    def test_l1_local_cache_performance(self, trip_id: str, iterations: int = 5) -> List[float]:
        """
        Teste les performances du cache local (L1)
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Liste des temps de réponse en secondes
        """
        times = []
        
        # Première requête pour peupler le cache local
        try:
            result = TripsCacheService.get_trips_page_result(1, 10, {})
            print(f"  L1 (Cache local) - Cache peuplé...")
        except Exception as e:
            print(f"  L1 (Cache local) - Erreur lors du peuplement: {e}")
            return times
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # Récupération depuis le cache local (L1)
                cache_key = TripsCacheService._get_cache_key(1, 10, {})
                cached_data = TripsCacheService._get_from_cache(cache_key)
                
                if cached_data:
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  L1 (Cache local) - Itération {i+1}: {response_time:.4f}s")
                else:
                    print(f"  L1 (Cache local) - Itération {i+1}: Cache miss")
                    
            except Exception as e:
                print(f"  L1 (Cache local) - Itération {i+1}: Erreur - {e}")
        
        return times
    
    def test_panel_cache_performance(self, trip_id: str, iterations: int = 5) -> Dict[str, List[float]]:
        """
        Teste les performances des panneaux avec cache vs sans cache
        
        Args:
            trip_id: ID du trip à tester
            iterations: Nombre d'itérations
            
        Returns:
            Dictionnaire avec les temps pour cache et sans cache
        """
        results = {
            'with_cache': [],
            'without_cache': []
        }
        
        print(f"🔄 Test des panneaux pour trip {trip_id[:8]}...")
        
        # Test avec cache
        print("  Test avec cache...")
        for i in range(iterations):
            start_time = time.time()
            
            try:
                panel = TripsCacheService.get_trip_details_panel(trip_id)
                if panel:
                    end_time = time.time()
                    response_time = end_time - start_time
                    results['with_cache'].append(response_time)
                    print(f"    Avec cache - Itération {i+1}: {response_time:.4f}s")
            except Exception as e:
                print(f"    Avec cache - Itération {i+1}: Erreur - {e}")
        
        # Test sans cache (en vidant à chaque fois)
        print("  Test sans cache...")
        for i in range(iterations):
            self.clear_local_cache()
            
            start_time = time.time()
            
            try:
                panel = TripsCacheService.get_trip_details_panel(trip_id)
                if panel:
                    end_time = time.time()
                    response_time = end_time - start_time
                    results['without_cache'].append(response_time)
                    print(f"    Sans cache - Itération {i+1}: {response_time:.4f}s")
            except Exception as e:
                print(f"    Sans cache - Itération {i+1}: Erreur - {e}")
        
        return results
    
    def run_performance_tests(self, iterations: int = 5, num_trips: int = 3):
        """
        Lance tous les tests de performance
        
        Args:
            iterations: Nombre d'itérations par test
            num_trips: Nombre de trips à tester
        """
        print("🚀 Démarrage des tests de performance du cache local")
        print("=" * 60)
        
        # Setup des données de test
        trip_ids = self.setup_test_data(num_trips)
        if not trip_ids:
            print("❌ Impossible de continuer sans données de test")
            return
        
        self.results['test_metadata']['test_iterations'] = iterations
        self.results['test_metadata']['num_trips'] = len(trip_ids)
        
        # Test général cache vs API
        print(f"\n📊 Test général: Cache local vs API directe")
        print("-" * 40)
        
        # Test L3 (API directe)
        print("🔄 Test L3 (API directe)...")
        l3_times = []
        for trip_id in trip_ids[:2]:  # Tester sur 2 trips
            times = self.test_l3_api_direct_performance(trip_id, 3)
            l3_times.extend(times)
        self.results['L3_api_direct'].extend(l3_times)
        
        # Test L1 (Cache local)
        print("🔄 Test L1 (Cache local)...")
        l1_times = self.test_l1_local_cache_performance(trip_ids[0], iterations)
        self.results['L1_local_cache'].extend(l1_times)
        
        # Test des panneaux spécifiques
        print(f"\n📊 Test des panneaux avec/sans cache")
        print("-" * 40)
        
        panel_results = self.test_panel_cache_performance(trip_ids[0], iterations)
        
        # Ajouter les résultats des panneaux
        self.results['panels_with_cache'] = panel_results['with_cache']
        self.results['panels_without_cache'] = panel_results['without_cache']
    
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
        print("📈 RÉSULTATS DES TESTS DE PERFORMANCE - CACHE LOCAL")
        print("=" * 60)
        
        # Statistiques pour chaque niveau
        levels = [
            ('L1 (Cache Local)', self.results['L1_local_cache']),
            ('L3 (API Directe)', self.results['L3_api_direct'])
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
        
        # Test des panneaux si disponible
        if 'panels_with_cache' in self.results and 'panels_without_cache' in self.results:
            print(f"\n🎯 Panneaux avec cache")
            print("-" * 30)
            stats_with = self.calculate_statistics(self.results['panels_with_cache'])
            print(f"  Temps moyen:     {stats_with['mean']:.4f}s")
            
            print(f"\n🎯 Panneaux sans cache")
            print("-" * 30)
            stats_without = self.calculate_statistics(self.results['panels_without_cache'])
            print(f"  Temps moyen:     {stats_without['mean']:.4f}s")
            
            if stats_without['mean'] > 0 and stats_with['mean'] > 0:
                improvement = stats_without['mean'] / stats_with['mean']
                print(f"\n⚡ Amélioration avec cache: {improvement:.1f}x plus rapide")
        
        # Comparaison des performances
        if self.results['L1_local_cache'] and self.results['L3_api_direct']:
            l1_avg = statistics.mean(self.results['L1_local_cache'])
            l3_avg = statistics.mean(self.results['L3_api_direct'])
            
            print(f"\n⚡ COMPARAISON CACHE vs API")
            print("-" * 30)
            if l1_avg > 0:
                improvement = l3_avg / l1_avg
                print(f"  Cache local vs API: {improvement:.1f}x plus rapide")
    
    def save_results_to_file(self, filename: str = None):
        """
        Sauvegarde les résultats dans un fichier JSON
        
        Args:
            filename: Nom du fichier (optionnel)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"local_cache_performance_results_{timestamp}.json"
        
        # Ajouter les statistiques aux résultats
        for level in ['L1_local_cache', 'L3_api_direct']:
            if level in self.results:
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
    print("🎯 Test de Performance du Cache Local - KlandoDash")
    print("=" * 60)
    
    # Paramètres du test
    iterations = 5  # Nombre d'itérations par test
    num_trips = 3   # Nombre de trips à tester
    
    # Créer et lancer le testeur
    tester = LocalCachePerformanceTester()
    
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
