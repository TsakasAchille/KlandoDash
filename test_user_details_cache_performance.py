#!/usr/bin/env python3
"""
Script de test de performance pour UserDetailsCache
Teste la lecture/écriture du cache, le vidage et mesure les temps d'exécution
"""
import sys
import os
import time
import json
from typing import Dict, Any, List

# Ajouter le chemin du projet
sys.path.append('/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

from dash_apps.services.user_details_cache_service import UserDetailsCache
from dash_apps.services.local_cache import local_cache

class UserDetailsCachePerformanceTest:
    """Classe de test de performance pour UserDetailsCache"""
    
    def __init__(self):
        self.test_uids = [
            'eV8D2Emx9yYJFPBzlA9kY1s5QP32',  # Ricardo
            'bk17O0BBAndQR7xxSZxDvAGkSWU2',   # Autre utilisateur
        ]
        self.results = {
            'cache_miss_times': [],
            'cache_hit_times': [],
            'cache_operations': [],
            'errors': []
        }
        
    def print_header(self, title: str):
        """Affiche un en-tête formaté"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str):
        """Affiche une étape"""
        print(f"\n📋 {step}")
        print("-" * 40)
    
    def measure_time(self, func, *args, **kwargs) -> tuple:
        """Mesure le temps d'exécution d'une fonction"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # en ms
            return result, execution_time, None
        except Exception as e:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            return None, execution_time, str(e)
    
    def test_cache_miss(self, uid: str) -> Dict[str, Any]:
        """Test avec cache miss (première requête)"""
        self.print_step(f"Test Cache Miss - User {uid[:8]}")
        
        # Vider le cache pour forcer un miss
        try:
            local_cache.delete('user_details', uid=uid)
            print(f"✅ Cache vidé pour {uid[:8]}")
        except:
            print(f"ℹ️  Pas de cache à vider pour {uid[:8]}")
        
        # Mesurer le temps avec cache miss
        result, exec_time, error = self.measure_time(
            UserDetailsCache.get_user_details_data, uid
        )
        
        if error:
            print(f"❌ Erreur: {error}")
            self.results['errors'].append({
                'type': 'cache_miss',
                'uid': uid[:8],
                'error': error,
                'time_ms': exec_time
            })
            return {}
        
        print(f"⏱️  Temps cache miss: {exec_time:.2f}ms")
        print(f"📊 Données récupérées: {len(result)} champs")
        
        self.results['cache_miss_times'].append({
            'uid': uid[:8],
            'time_ms': exec_time,
            'fields_count': len(result)
        })
        
        return result
    
    def test_cache_hit(self, uid: str) -> Dict[str, Any]:
        """Test avec cache hit (requête suivante)"""
        self.print_step(f"Test Cache Hit - User {uid[:8]}")
        
        # Mesurer le temps avec cache hit
        result, exec_time, error = self.measure_time(
            UserDetailsCache.get_user_details_data, uid
        )
        
        if error:
            print(f"❌ Erreur: {error}")
            self.results['errors'].append({
                'type': 'cache_hit',
                'uid': uid[:8],
                'error': error,
                'time_ms': exec_time
            })
            return {}
        
        print(f"⏱️  Temps cache hit: {exec_time:.2f}ms")
        print(f"📊 Données récupérées: {len(result)} champs")
        
        self.results['cache_hit_times'].append({
            'uid': uid[:8],
            'time_ms': exec_time,
            'fields_count': len(result)
        })
        
        return result
    
    def test_cache_operations(self):
        """Test des opérations de cache"""
        self.print_step("Test Opérations Cache")
        
        # Test écriture cache
        test_data = {'test': 'data', 'timestamp': time.time()}
        start_time = time.time()
        try:
            local_cache.set('user_details', test_data, ttl=300, uid='test_uid')
            write_time = (time.time() - start_time) * 1000
            print(f"✅ Écriture cache: {write_time:.2f}ms")
            
            self.results['cache_operations'].append({
                'operation': 'write',
                'time_ms': write_time,
                'success': True
            })
        except Exception as e:
            write_time = (time.time() - start_time) * 1000
            print(f"❌ Erreur écriture cache: {e}")
            self.results['cache_operations'].append({
                'operation': 'write',
                'time_ms': write_time,
                'success': False,
                'error': str(e)
            })
        
        # Test lecture cache
        start_time = time.time()
        try:
            cached_data = local_cache.get('user_details', uid='test_uid')
            read_time = (time.time() - start_time) * 1000
            if cached_data:
                print(f"✅ Lecture cache: {read_time:.2f}ms - Données trouvées")
            else:
                print(f"⚠️  Lecture cache: {read_time:.2f}ms - Aucune donnée")
            
            self.results['cache_operations'].append({
                'operation': 'read',
                'time_ms': read_time,
                'success': cached_data is not None
            })
        except Exception as e:
            read_time = (time.time() - start_time) * 1000
            print(f"❌ Erreur lecture cache: {e}")
            self.results['cache_operations'].append({
                'operation': 'read',
                'time_ms': read_time,
                'success': False,
                'error': str(e)
            })
        
        # Test suppression cache
        start_time = time.time()
        try:
            local_cache.delete('user_details', uid='test_uid')
            delete_time = (time.time() - start_time) * 1000
            print(f"✅ Suppression cache: {delete_time:.2f}ms")
            
            self.results['cache_operations'].append({
                'operation': 'delete',
                'time_ms': delete_time,
                'success': True
            })
        except Exception as e:
            delete_time = (time.time() - start_time) * 1000
            print(f"❌ Erreur suppression cache: {e}")
            self.results['cache_operations'].append({
                'operation': 'delete',
                'time_ms': delete_time,
                'success': False,
                'error': str(e)
            })
    
    def test_multiple_users(self):
        """Test avec plusieurs utilisateurs"""
        self.print_step("Test Utilisateurs Multiples")
        
        for uid in self.test_uids:
            print(f"\n👤 Test utilisateur {uid[:8]}")
            
            # Cache miss
            self.test_cache_miss(uid)
            
            # Cache hit
            self.test_cache_hit(uid)
    
    def calculate_statistics(self):
        """Calcule les statistiques de performance"""
        self.print_step("Statistiques de Performance")
        
        if self.results['cache_miss_times']:
            miss_times = [r['time_ms'] for r in self.results['cache_miss_times']]
            avg_miss = sum(miss_times) / len(miss_times)
            max_miss = max(miss_times)
            min_miss = min(miss_times)
            print(f"📈 Cache Miss - Moyenne: {avg_miss:.2f}ms, Min: {min_miss:.2f}ms, Max: {max_miss:.2f}ms")
        
        if self.results['cache_hit_times']:
            hit_times = [r['time_ms'] for r in self.results['cache_hit_times']]
            avg_hit = sum(hit_times) / len(hit_times)
            max_hit = max(hit_times)
            min_hit = min(hit_times)
            print(f"⚡ Cache Hit - Moyenne: {avg_hit:.2f}ms, Min: {min_hit:.2f}ms, Max: {max_hit:.2f}ms")
            
            if self.results['cache_miss_times']:
                speedup = avg_miss / avg_hit
                print(f"🚀 Accélération cache: {speedup:.1f}x plus rapide")
        
        if self.results['errors']:
            print(f"⚠️  Erreurs rencontrées: {len(self.results['errors'])}")
            for error in self.results['errors']:
                print(f"   - {error['type']} {error['uid']}: {error['error']}")
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier JSON"""
        timestamp = int(time.time())
        filename = f"user_cache_performance_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"💾 Résultats sauvegardés dans {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def run_all_tests(self):
        """Lance tous les tests"""
        self.print_header("TEST DE PERFORMANCE - USER DETAILS CACHE")
        
        print("🎯 Objectifs:")
        print("   - Mesurer temps cache miss vs cache hit")
        print("   - Tester opérations CRUD du cache")
        print("   - Vérifier la robustesse du système")
        print(f"   - Tester avec {len(self.test_uids)} utilisateurs")
        
        # Activer le debug
        os.environ['DEBUG_USERS'] = 'False'  # Désactiver pour éviter trop de logs
        
        # Tests des opérations de cache
        self.test_cache_operations()
        
        # Tests avec utilisateurs multiples
        self.test_multiple_users()
        
        # Statistiques
        self.calculate_statistics()
        
        # Sauvegarde
        self.save_results()
        
        self.print_header("TESTS TERMINÉS")
        print("✅ Tous les tests ont été exécutés")
        print("📊 Consultez les résultats ci-dessus et le fichier JSON généré")

def main():
    """Fonction principale"""
    tester = UserDetailsCachePerformanceTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
