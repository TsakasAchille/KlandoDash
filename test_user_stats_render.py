#!/usr/bin/env python3
"""
Script de test pour le rendu des statistiques utilisateur
Test avec l'utilisateur ID: bk17O0BBAndQR7xxSZxDvAGkSWU2
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Activer le debug pour les logs détaillés
os.environ['DEBUG_USERS'] = 'True'

def test_user_stats_service():
    """Test du service UserStatsCache"""
    print("=" * 60)
    print("TEST 1: Service UserStatsCache")
    print("=" * 60)
    
    try:
        from dash_apps.services.user_stats_cache_service import UserStatsCache
        
        user_id = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        print(f"🔍 Test des statistiques pour l'utilisateur: {user_id}")
        
        # Test du calcul des statistiques
        stats = UserStatsCache.get_user_stats(user_id)
        
        if stats:
            print("✅ Statistiques récupérées avec succès:")
            print(f"   📊 Trajets conducteur: {stats.get('driver_trips', 0)}")
            print(f"   🚗 Trajets passager: {stats.get('passenger_trips', 0)}")
            print(f"   📈 Total trajets: {stats.get('total_trips', 0)}")
            print(f"   📏 Distance totale: {stats.get('total_distance', 0)} km")
            print(f"   🛣️  Distance conducteur: {stats.get('driver_distance', 0)} km")
            print(f"   🚶 Distance passager: {stats.get('passenger_distance', 0)} km")
            
            # Vérifier si les données correspondent aux attentes
            if stats.get('driver_trips', 0) >= 4:
                print("✅ Nombre de trajets conducteur correspond aux attentes (4-5 trajets)")
            else:
                print(f"⚠️  Nombre de trajets conducteur ({stats.get('driver_trips', 0)}) inférieur aux attentes")
                
            return stats
        else:
            print("❌ Aucune statistique trouvée")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors du test du service: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_user_stats_template_render(stats):
    """Test du rendu du template Jinja2"""
    print("\n" + "=" * 60)
    print("TEST 2: Rendu du template Jinja2")
    print("=" * 60)
    
    try:
        from dash_apps.utils.settings import get_jinja_template, load_json_config
        
        # Charger la configuration
        config = load_json_config('user_stats.json')
        template_config = config.get('template_style', {})
        
        print("📄 Configuration du template chargée:")
        print(f"   🎨 Style: {json.dumps(template_config, indent=2)}")
        
        # Charger et rendre le template
        template = get_jinja_template('user_stats_template.jinja2')
        
        html_content = template.render(
            stats=stats,
            config=config.get('user_stats', {}),
            layout={
                'card_height': template_config.get('card_height', '350px'),
                'card_width': template_config.get('card_width', '100%')
            }
        )
        
        print("✅ Template rendu avec succès")
        print(f"   📝 Taille du HTML généré: {len(html_content)} caractères")
        
        # Vérifier que les statistiques sont présentes dans le HTML
        if str(stats.get('driver_trips', 0)) in html_content:
            print("✅ Trajets conducteur présents dans le HTML")
        else:
            print("⚠️  Trajets conducteur non trouvés dans le HTML")
            
        if str(stats.get('total_distance', 0)) in html_content:
            print("✅ Distance totale présente dans le HTML")
        else:
            print("⚠️  Distance totale non trouvée dans le HTML")
        
        # Sauvegarder le HTML pour inspection
        output_file = "test_user_stats_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 HTML sauvegardé dans: {output_file}")
        
        return html_content
        
    except Exception as e:
        print(f"❌ Erreur lors du rendu du template: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_database_queries():
    """Test direct des requêtes de base de données"""
    print("\n" + "=" * 60)
    print("TEST 3: Requêtes directes de base de données")
    print("=" * 60)
    
    try:
        from dash_apps.core.database import SessionLocal
        from dash_apps.models.bookings import Booking
        from dash_apps.models.trip import Trip
        from sqlalchemy import func
        
        user_id = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        
        with SessionLocal() as db:
            # Test requête trajets conducteur
            driver_trips = db.query(func.count(Trip.trip_id)).filter(
                Trip.driver_id == user_id
            ).scalar() or 0
            
            print(f"🚗 Trajets en tant que conducteur: {driver_trips}")
            
            # Test requête trajets passager
            passenger_trips = db.query(func.count(Booking.trip_id)).filter(
                Booking.user_id == user_id
            ).scalar() or 0
            
            print(f"🚶 Trajets en tant que passager: {passenger_trips}")
            
            # Test distance conducteur
            driver_distance = db.query(func.sum(Trip.distance)).filter(
                Trip.driver_id == user_id,
                Trip.distance.isnot(None)
            ).scalar() or 0.0
            
            print(f"🛣️  Distance conducteur: {driver_distance} km")
            
            # Test distance passager
            passenger_distance = db.query(func.sum(Trip.distance)).join(
                Booking, Trip.trip_id == Booking.trip_id
            ).filter(
                Booking.user_id == user_id,
                Trip.distance.isnot(None)
            ).scalar() or 0.0
            
            print(f"🚶 Distance passager: {passenger_distance} km")
            
            # Lister quelques trajets pour vérification
            print("\n📋 Échantillon de trajets conducteur:")
            sample_trips = db.query(Trip).filter(Trip.driver_id == user_id).limit(3).all()
            for trip in sample_trips:
                print(f"   - {trip.trip_id}: {trip.departure_name} → {trip.destination_name} ({trip.distance} km)")
            
            return {
                'driver_trips': driver_trips,
                'passenger_trips': passenger_trips,
                'driver_distance': float(driver_distance),
                'passenger_distance': float(passenger_distance)
            }
            
    except Exception as e:
        print(f"❌ Erreur lors des requêtes de base de données: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_cache_functionality():
    """Test de la fonctionnalité de cache"""
    print("\n" + "=" * 60)
    print("TEST 4: Fonctionnalité de cache")
    print("=" * 60)
    
    try:
        from dash_apps.services.user_stats_cache_service import UserStatsCache
        
        user_id = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        
        # Vider le cache pour ce test
        print("🧹 Nettoyage du cache...")
        UserStatsCache.invalidate_user_stats(user_id)
        
        # Premier appel (devrait calculer depuis la DB)
        print("📊 Premier appel (cache miss attendu)...")
        stats1 = UserStatsCache.get_user_stats(user_id)
        
        # Deuxième appel (devrait utiliser le cache)
        print("📊 Deuxième appel (cache hit attendu)...")
        stats2 = UserStatsCache.get_user_stats(user_id)
        
        # Vérifier que les résultats sont identiques
        if stats1 == stats2:
            print("✅ Cache fonctionne correctement - résultats identiques")
        else:
            print("⚠️  Différence entre les appels cache/non-cache")
            
        return stats1
        
    except Exception as e:
        print(f"❌ Erreur lors du test de cache: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Fonction principale de test"""
    print("🧪 SCRIPT DE TEST - STATISTIQUES UTILISATEUR")
    print(f"👤 Utilisateur testé: bk17O0BBAndQR7xxSZxDvAGkSWU2")
    print(f"🕒 Timestamp: {os.popen('date').read().strip()}")
    
    # Test 1: Service UserStatsCache
    stats = test_user_stats_service()
    
    if stats:
        # Test 2: Rendu template
        html_content = test_user_stats_template_render(stats)
        
        # Test 3: Requêtes directes
        db_stats = test_database_queries()
        
        # Test 4: Cache
        cached_stats = test_cache_functionality()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("RÉSUMÉ FINAL")
        print("=" * 60)
        
        if stats and html_content:
            print("✅ Tous les tests principaux ont réussi")
            print(f"📊 Statistiques finales: {json.dumps(stats, indent=2)}")
        else:
            print("❌ Certains tests ont échoué")
            
    else:
        print("❌ Test du service principal échoué - arrêt des tests")

if __name__ == "__main__":
    main()
