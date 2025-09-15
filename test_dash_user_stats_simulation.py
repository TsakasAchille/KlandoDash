#!/usr/bin/env python3
"""
Script de simulation Dash pour tester les statistiques utilisateur avec vraies données
Simule l'appel du callback update_user_stats comme dans l'application Dash réelle
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

def setup_environment():
    """Configure l'environnement pour simuler Dash"""
    print("🔧 Configuration de l'environnement de simulation Dash...")
    
    # Vérifier les variables d'environnement nécessaires
    env_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variables d'environnement manquantes: {missing_vars}")
        print("   L'application utilisera la base de données locale (SQLite)")
    else:
        print("✅ Variables d'environnement Supabase configurées")
    
    return len(missing_vars) == 0

def simulate_dash_callback():
    """Simule l'appel du callback update_user_stats comme dans Dash"""
    print("\n" + "=" * 70)
    print("🎯 SIMULATION DU CALLBACK DASH - update_user_stats")
    print("=" * 70)
    
    try:
        # Importer le callback comme le ferait Dash
        from dash_apps.callbacks.users_callbacks import update_user_stats
        
        # ID utilisateur à tester
        user_id = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        
        print(f"👤 Test avec utilisateur: {user_id}")
        print("📞 Appel du callback update_user_stats...")
        
        # Simuler l'appel du callback avec différents formats d'entrée
        test_cases = [
            {"name": "String ID", "input": user_id},
            {"name": "Dict format", "input": {"uid": user_id}},
        ]
        
        results = {}
        
        for test_case in test_cases:
            print(f"\n🧪 Test: {test_case['name']}")
            print(f"   📥 Input: {test_case['input']}")
            
            try:
                # Appeler le callback comme le ferait Dash
                result = update_user_stats(test_case['input'])
                
                if result:
                    print(f"   ✅ Callback réussi")
                    print(f"   📊 Type de résultat: {type(result)}")
                    
                    # Analyser le résultat Dash
                    if hasattr(result, 'children'):
                        print(f"   🏗️  Composant Dash avec {len(result.children)} enfants")
                        
                        # Chercher l'iframe avec le HTML
                        for child in result.children:
                            if hasattr(child, 'srcDoc'):
                                html_content = child.srcDoc
                                print(f"   📄 HTML généré: {len(html_content)} caractères")
                                
                                # Sauvegarder le HTML
                                filename = f"dash_simulation_{test_case['name'].lower().replace(' ', '_')}.html"
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                print(f"   💾 HTML sauvegardé: {filename}")
                                
                                # Analyser le contenu HTML
                                analyze_html_content(html_content, test_case['name'])
                                break
                    
                    results[test_case['name']] = "SUCCESS"
                else:
                    print(f"   ❌ Callback retourné None")
                    results[test_case['name']] = "NULL_RESULT"
                    
            except Exception as e:
                print(f"   ❌ Erreur callback: {str(e)}")
                results[test_case['name']] = f"ERROR: {str(e)}"
                import traceback
                traceback.print_exc()
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import du callback: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_html_content(html_content, test_name):
    """Analyse le contenu HTML généré"""
    print(f"   🔍 Analyse du HTML pour {test_name}:")
    
    # Chercher les statistiques dans le HTML
    stats_indicators = [
        ("trajets effectués", "total_trips"),
        ("conducteur", "driver_trips"),
        ("passager", "passenger_trips"),
        ("distance totale", "total_distance"),
        ("km", "distance_unit")
    ]
    
    found_stats = []
    for indicator, stat_type in stats_indicators:
        if indicator.lower() in html_content.lower():
            found_stats.append(stat_type)
    
    print(f"     📈 Éléments statistiques trouvés: {found_stats}")
    
    # Extraire les valeurs numériques
    import re
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', html_content)
    if numbers:
        print(f"     🔢 Valeurs numériques dans le HTML: {numbers[:10]}...")  # Première 10 valeurs
    
    # Vérifier la structure HTML
    if '<div class="stat-item">' in html_content:
        stat_items = html_content.count('<div class="stat-item">')
        print(f"     📊 Nombre d'éléments statistiques: {stat_items}")
    
    if 'svg' in html_content:
        svg_count = html_content.count('<svg')
        print(f"     🎨 Icônes SVG: {svg_count}")

def test_cache_behavior():
    """Test du comportement du cache avec vraies données"""
    print("\n" + "=" * 70)
    print("💾 TEST DU CACHE AVEC VRAIES DONNÉES")
    print("=" * 70)
    
    try:
        from dash_apps.services.user_stats_cache_service import UserStatsCache
        
        user_id = "bk17O0BBAndQR7xxSZxDvAGkSWU2"
        
        # Vider le cache pour commencer proprement
        print("🧹 Nettoyage du cache...")
        UserStatsCache.invalidate_user_stats(user_id)
        
        # Premier appel - devrait aller chercher en base
        print("📊 Premier appel (cache miss attendu)...")
        stats1 = UserStatsCache.get_user_stats(user_id)
        
        if stats1:
            print("✅ Statistiques récupérées:")
            for key, value in stats1.items():
                print(f"   {key}: {value}")
        
        # Deuxième appel - devrait utiliser le cache
        print("\n📊 Deuxième appel (cache hit attendu)...")
        stats2 = UserStatsCache.get_user_stats(user_id)
        
        # Vérifier la cohérence
        if stats1 == stats2:
            print("✅ Cache cohérent - résultats identiques")
        else:
            print("⚠️  Incohérence cache détectée")
        
        return stats1
        
    except Exception as e:
        print(f"❌ Erreur test cache: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_database_connection():
    """Test de la connexion à la base de données"""
    print("\n" + "=" * 70)
    print("🗄️  TEST DE CONNEXION BASE DE DONNÉES")
    print("=" * 70)
    
    try:
        from dash_apps.core.database import SessionLocal
        
        with SessionLocal() as db:
            # Test de connexion basique
            result = db.execute("SELECT 1 as test").fetchone()
            if result:
                print("✅ Connexion base de données OK")
                
                # Lister les tables disponibles
                try:
                    # Pour SQLite
                    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                    table_names = [table[0] for table in tables]
                    print(f"📋 Tables disponibles: {table_names}")
                    
                    # Vérifier les tables nécessaires
                    required_tables = ['trips', 'bookings', 'users']
                    missing_tables = [t for t in required_tables if t not in table_names]
                    
                    if missing_tables:
                        print(f"⚠️  Tables manquantes: {missing_tables}")
                        return False
                    else:
                        print("✅ Toutes les tables nécessaires sont présentes")
                        return True
                        
                except Exception as e:
                    print(f"⚠️  Impossible de lister les tables: {str(e)}")
                    # Essayer avec une approche différente pour d'autres DB
                    return True
            else:
                print("❌ Test de connexion échoué")
                return False
                
    except Exception as e:
        print(f"❌ Erreur connexion DB: {str(e)}")
        return False

def generate_summary_report(callback_results, cache_stats, db_connected):
    """Génère un rapport de synthèse"""
    print("\n" + "=" * 70)
    print("📋 RAPPORT DE SYNTHÈSE - SIMULATION DASH")
    print("=" * 70)
    
    print(f"🕒 Timestamp: {os.popen('date').read().strip()}")
    print(f"👤 Utilisateur testé: bk17O0BBAndQR7xxSZxDvAGkSWU2")
    
    # Statut de la base de données
    db_status = "✅ Connectée" if db_connected else "❌ Problème"
    print(f"🗄️  Base de données: {db_status}")
    
    # Résultats des callbacks
    print(f"\n📞 Résultats des callbacks:")
    if callback_results:
        for test_name, result in callback_results.items():
            status = "✅" if result == "SUCCESS" else "❌"
            print(f"   {status} {test_name}: {result}")
    else:
        print("   ❌ Aucun callback testé")
    
    # Statistiques du cache
    print(f"\n💾 Cache:")
    if cache_stats:
        print(f"   ✅ Fonctionnel")
        print(f"   📊 Statistiques récupérées: {len(cache_stats)} champs")
        if cache_stats.get('total_trips', 0) > 0:
            print(f"   🎯 Données réelles détectées")
        else:
            print(f"   ⚠️  Données vides (tables manquantes?)")
    else:
        print("   ❌ Problème cache")
    
    # Recommandations
    print(f"\n💡 Recommandations:")
    if not db_connected:
        print("   🔧 Vérifier la configuration de la base de données")
    if callback_results and all(r == "SUCCESS" for r in callback_results.values()):
        print("   ✅ Système prêt pour la production")
    else:
        print("   🔧 Corriger les erreurs de callback avant déploiement")

def main():
    """Fonction principale de simulation"""
    print("🎭 SIMULATION DASH - STATISTIQUES UTILISATEUR")
    print("=" * 70)
    
    # Configuration de l'environnement
    has_supabase = setup_environment()
    
    # Test de connexion DB
    db_connected = test_database_connection()
    
    # Test du cache
    cache_stats = test_cache_behavior()
    
    # Simulation des callbacks Dash
    callback_results = simulate_dash_callback()
    
    # Rapport final
    generate_summary_report(callback_results, cache_stats, db_connected)
    
    print(f"\n🏁 Simulation terminée")

if __name__ == "__main__":
    main()
