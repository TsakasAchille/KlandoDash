#!/usr/bin/env python3
"""
Script de test des performances de chargement SQL pour KlandoDash
Compare différentes méthodes d'insertion de données
"""
import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Boolean, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timedelta
import random

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_apps.core.database import engine

class SQLLoadingBenchmark:
    def __init__(self, num_records=10000):
        self.num_records = num_records
        self.test_table = "users_performance_test"
        self.engine = engine
        
    def generate_test_data(self):
        """Génère des données de test réalistes"""
        print(f"🔄 Génération de {self.num_records} enregistrements de test...")
        
        data = []
        for i in range(self.num_records):
            data.append({
                'uid': str(uuid.uuid4()),
                'display_name': f'User_{i}',
                'email': f'user{i}@test.com',
                'first_name': f'First{i}',
                'name': f'Last{i}',
                'phone_number': f'+221{random.randint(700000000, 799999999)}',
                'gender': random.choice(['M', 'F']),
                'role': random.choice(['user', 'driver', 'admin']),
                'rating': round(random.uniform(1.0, 5.0), 1) if random.random() > 0.3 else None,
                'rating_count': random.randint(0, 100),
                'is_driver_doc_validated': random.choice([True, False]),
                'created_at': datetime.now() - timedelta(days=random.randint(0, 365)),
                'updated_at': datetime.now()
            })
        
        return data
    
    def create_test_table(self):
        """Crée la table de test"""
        print("📋 Création de la table de test...")
        
        with self.engine.connect() as conn:
            # Supprimer la table si elle existe
            conn.execute(text(f"DROP TABLE IF EXISTS {self.test_table}"))
            
            # Créer la nouvelle table
            create_sql = f"""
            CREATE TABLE {self.test_table} (
                uid VARCHAR PRIMARY KEY,
                display_name VARCHAR,
                email VARCHAR,
                first_name VARCHAR,
                name VARCHAR,
                phone_number VARCHAR,
                gender VARCHAR,
                role VARCHAR,
                rating NUMERIC,
                rating_count INTEGER,
                is_driver_doc_validated BOOLEAN,
                created_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE
            )
            """
            conn.execute(text(create_sql))
            conn.commit()
    
    def cleanup_test_table(self):
        """Nettoie la table de test"""
        with self.engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {self.test_table}"))
            conn.commit()
    
    def method_1_single_inserts(self, data):
        """Méthode 1: INSERT classiques un par un (LENT)"""
        print("🐌 Test Méthode 1: INSERT classiques...")
        
        start_time = time.time()
        
        with self.engine.connect() as conn:
            for record in data:
                conn.execute(text(f"""
                    INSERT INTO {self.test_table} 
                    (uid, display_name, email, first_name, name, phone_number, gender, role, 
                     rating, rating_count, is_driver_doc_validated, created_at, updated_at)
                    VALUES (:uid, :display_name, :email, :first_name, :name, :phone_number, 
                            :gender, :role, :rating, :rating_count, :is_driver_doc_validated, 
                            :created_at, :updated_at)
                """), record)
            conn.commit()
        
        elapsed = time.time() - start_time
        rate = len(data) / elapsed
        print(f"   ⏱️  Temps: {elapsed:.2f}s | Vitesse: {rate:.0f} records/sec")
        return elapsed, rate
    
    def method_2_batch_inserts(self, data, batch_size=1000):
        """Méthode 2: INSERT par batch avec transactions"""
        print(f"🚀 Test Méthode 2: Batch INSERT (taille: {batch_size})...")
        
        start_time = time.time()
        
        with self.engine.begin() as conn:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                conn.execute(text(f"""
                    INSERT INTO {self.test_table} 
                    (uid, display_name, email, first_name, name, phone_number, gender, role, 
                     rating, rating_count, is_driver_doc_validated, created_at, updated_at)
                    VALUES (:uid, :display_name, :email, :first_name, :name, :phone_number, 
                            :gender, :role, :rating, :rating_count, :is_driver_doc_validated, 
                            :created_at, :updated_at)
                """), batch)
        
        elapsed = time.time() - start_time
        rate = len(data) / elapsed
        print(f"   ⏱️  Temps: {elapsed:.2f}s | Vitesse: {rate:.0f} records/sec")
        return elapsed, rate
    
    def method_3_pandas_to_sql(self, data):
        """Méthode 3: Pandas to_sql avec method='multi'"""
        print("🐼 Test Méthode 3: Pandas to_sql...")
        
        df = pd.DataFrame(data)
        
        start_time = time.time()
        
        df.to_sql(
            self.test_table, 
            self.engine, 
            if_exists='append', 
            index=False, 
            method='multi',
            chunksize=1000
        )
        
        elapsed = time.time() - start_time
        rate = len(data) / elapsed
        print(f"   ⏱️  Temps: {elapsed:.2f}s | Vitesse: {rate:.0f} records/sec")
        return elapsed, rate
    
    def method_4_copy_from_csv(self, data):
        """Méthode 4: PostgreSQL COPY (le plus rapide)"""
        print("⚡ Test Méthode 4: PostgreSQL COPY...")
        
        # Créer un fichier CSV temporaire
        df = pd.DataFrame(data)
        csv_file = '/tmp/test_data.csv'
        df.to_csv(csv_file, index=False)
        
        start_time = time.time()
        
        with self.engine.connect() as conn:
            # Utiliser COPY pour charger le CSV
            conn.execute(text(f"""
                COPY {self.test_table} FROM '{csv_file}' 
                WITH (FORMAT csv, HEADER true)
            """))
            conn.commit()
        
        # Nettoyer le fichier temporaire
        os.remove(csv_file)
        
        elapsed = time.time() - start_time
        rate = len(data) / elapsed
        print(f"   ⏱️  Temps: {elapsed:.2f}s | Vitesse: {rate:.0f} records/sec")
        return elapsed, rate
    
    def run_benchmark(self):
        """Lance tous les tests de performance"""
        print("🎯 Benchmark des performances de chargement SQL")
        print("=" * 60)
        print(f"📊 Nombre d'enregistrements: {self.num_records:,}")
        print()
        
        # Générer les données de test
        test_data = self.generate_test_data()
        
        results = {}
        
        # Test de chaque méthode
        methods = [
            ("Single INSERTs", self.method_1_single_inserts),
            ("Batch INSERTs", self.method_2_batch_inserts),
            ("Pandas to_sql", self.method_3_pandas_to_sql),
            ("PostgreSQL COPY", self.method_4_copy_from_csv)
        ]
        
        for method_name, method_func in methods:
            try:
                # Créer une table propre pour chaque test
                self.create_test_table()
                
                # Exécuter le test
                elapsed, rate = method_func(test_data)
                results[method_name] = {'time': elapsed, 'rate': rate}
                
                # Vérifier que les données ont été insérées
                with self.engine.connect() as conn:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {self.test_table}")).scalar()
                    print(f"   ✅ {count:,} enregistrements insérés")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                results[method_name] = {'time': float('inf'), 'rate': 0}
                print()
        
        # Afficher le résumé
        self.display_results(results)
        
        # Nettoyer
        self.cleanup_test_table()
    
    def display_results(self, results):
        """Affiche un résumé des résultats"""
        print("🏆 RÉSULTATS DU BENCHMARK")
        print("=" * 60)
        
        # Trier par vitesse (records/sec)
        sorted_results = sorted(results.items(), key=lambda x: x[1]['rate'], reverse=True)
        
        print(f"{'Méthode':<20} {'Temps (s)':<12} {'Vitesse (rec/s)':<15} {'Ratio':<10}")
        print("-" * 60)
        
        fastest_rate = sorted_results[0][1]['rate'] if sorted_results else 1
        
        for method, data in sorted_results:
            time_str = f"{data['time']:.2f}" if data['time'] != float('inf') else "ERREUR"
            rate_str = f"{data['rate']:.0f}" if data['rate'] > 0 else "0"
            ratio = data['rate'] / fastest_rate if fastest_rate > 0 else 0
            ratio_str = f"{ratio:.1f}x" if ratio > 0 else "-"
            
            print(f"{method:<20} {time_str:<12} {rate_str:<15} {ratio_str:<10}")
        
        print()
        print("💡 Recommandations:")
        if sorted_results:
            winner = sorted_results[0]
            print(f"   🥇 Méthode la plus rapide: {winner[0]}")
            print(f"   📈 Vitesse: {winner[1]['rate']:.0f} records/seconde")
        
        print("   🔧 Pour optimiser davantage:")
        print("      - Désactiver les index pendant l'import")
        print("      - Augmenter maintenance_work_mem")
        print("      - Utiliser des transactions plus grosses")

def main():
    """Fonction principale"""
    print("🚀 Test des performances de chargement SQL pour KlandoDash")
    print()
    
    # Demander le nombre d'enregistrements à tester
    try:
        num_records = int(input("Nombre d'enregistrements à tester (défaut: 10000): ") or "10000")
    except ValueError:
        num_records = 10000
    
    # Lancer le benchmark
    benchmark = SQLLoadingBenchmark(num_records)
    benchmark.run_benchmark()

if __name__ == "__main__":
    main()
