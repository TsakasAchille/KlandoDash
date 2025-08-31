#!/usr/bin/env python3
"""
Script pour créer les index de performance pour optimiser les requêtes KlandoDash
"""
import os
import sys
from sqlalchemy import create_engine, text

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash_apps.core.database import engine

def create_performance_indexes():
    """Crée tous les index nécessaires pour optimiser les performances"""
    
    indexes = [
        # Index pour les requêtes utilisateurs
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at DESC);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);", 
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_validation ON users(is_driver_doc_validated);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_rating ON users(rating) WHERE rating IS NOT NULL;",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_gender ON users(gender);",
        
        # Index composites pour les filtres fréquents
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role_created ON users(role, created_at DESC);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_validation_created ON users(is_driver_doc_validated, created_at DESC);",
        
        # Index pour les recherches textuelles (si pas de full-text search)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_name_gin ON users USING gin(to_tsvector('french', COALESCE(name, '') || ' ' || COALESCE(first_name, '') || ' ' || COALESCE(display_name, '')));",
        
        # Index pour les requêtes de trajets
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_driver_id ON trips(driver_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trips_departure ON trips(departure_schedule);",
        
        # Index pour les réservations
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_trip_id ON bookings(trip_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_trip ON bookings(user_id, trip_id);",
        
        # Index pour les tickets de support
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_support_tickets_created ON support_tickets(created_at DESC);",
    ]
    
    print("🚀 Création des index de performance...")
    
    with engine.connect() as conn:
        for i, index_sql in enumerate(indexes, 1):
            try:
                print(f"[{i}/{len(indexes)}] Création index: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'}")
                conn.execute(text(index_sql))
                conn.commit()
                print(f"✅ Index créé avec succès")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"ℹ️  Index déjà existant")
                else:
                    print(f"❌ Erreur: {e}")
                    
    print("\n🎉 Création des index terminée!")
    print("\n📊 Pour vérifier les index créés:")
    print("SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;")

def analyze_tables():
    """Met à jour les statistiques des tables pour l'optimiseur de requêtes"""
    
    tables = ['users', 'trips', 'bookings', 'support_tickets']
    
    print("\n🔍 Mise à jour des statistiques des tables...")
    
    with engine.connect() as conn:
        for table in tables:
            try:
                print(f"Analyse de la table {table}...")
                conn.execute(text(f"ANALYZE {table};"))
                conn.commit()
                print(f"✅ Table {table} analysée")
            except Exception as e:
                print(f"❌ Erreur lors de l'analyse de {table}: {e}")
    
    print("✅ Analyse des tables terminée!")

def show_query_performance_tips():
    """Affiche des conseils pour optimiser les performances"""
    
    print("\n💡 Conseils d'optimisation supplémentaires:")
    print("1. Utiliser EXPLAIN ANALYZE sur les requêtes lentes")
    print("2. Considérer pg_stat_statements pour monitorer les performances")
    print("3. Ajuster les paramètres PostgreSQL (shared_buffers, work_mem)")
    print("4. Utiliser connection pooling (PgBouncer)")
    print("5. Monitorer les slow queries avec log_min_duration_statement")

if __name__ == "__main__":
    print("🎯 Optimisation des performances KlandoDash")
    print("=" * 50)
    
    try:
        create_performance_indexes()
        analyze_tables()
        show_query_performance_tips()
        
        print("\n🚀 Optimisation terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        sys.exit(1)
