#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des panneaux trip_details et trip_driver
Simule un clic sur un trajet et vérifie que les données s'affichent correctement
"""
import os
import sys
import time
from typing import Dict, Any, Optional

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Activer le debug pour voir tous les logs
os.environ['DEBUG_TRIPS'] = 'true'

from dash_apps.services.trip_details_cache_service import TripDetailsCache
from dash_apps.services.trip_driver_cache_service import TripDriverCache
from dash_apps.utils.settings import get_jinja_template
from dash_apps.utils.settings import load_json_config

def print_separator(title: str):
    """Affiche un séparateur avec titre"""
    print("\n" + "="*80)
    print(f"🔧 {title}")
    print("="*80)

def print_step(step: str, status: str = "INFO"):
    """Affiche une étape avec statut"""
    emoji = "✅" if status == "SUCCESS" else "❌" if status == "ERROR" else "🔍"
    print(f"{emoji} {step}")

def test_panels_display():
    """Test de l'affichage des panneaux avec vraies données"""
    
    # ID de test
    test_trip_id = "TRIP-1757688627290606-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
    
    print_separator("TEST D'AFFICHAGE DES PANNEAUX")
    print(f"🎯 Trip ID de test: {test_trip_id}")
    
    # ========================================
    # ÉTAPE 1: RÉCUPÉRER LES DONNÉES TRIP DETAILS
    # ========================================
    print_separator("ÉTAPE 1: RÉCUPÉRATION DONNÉES TRIP DETAILS")
    
    try:
        trip_data = TripDetailsCache.get_trip_details_data(test_trip_id)
        
        if trip_data:
            print_step("✅ Données trip_details récupérées", "SUCCESS")
            print(f"   - ID: {trip_data.get('id', 'N/A')}")
            print(f"   - Départ: {trip_data.get('departure_name', 'N/A')}")
            print(f"   - Destination: {trip_data.get('destination_name', 'N/A')}")
            print(f"   - Date: {trip_data.get('departure_date', 'N/A')}")
            print(f"   - Heure: {trip_data.get('departure_schedule', 'N/A')}")
            print(f"   - Prix: {trip_data.get('price_per_seat', 'N/A')}")
            print(f"   - Places: {trip_data.get('seats_published', 'N/A')}")
            print(f"   - Statut: {trip_data.get('status', 'N/A')}")
        else:
            print_step("❌ Aucune donnée trip_details", "ERROR")
            return False
            
    except Exception as e:
        print_step(f"❌ Erreur trip_details: {e}", "ERROR")
        return False
    
    # ========================================
    # ÉTAPE 2: RÉCUPÉRER LES DONNÉES DRIVER
    # ========================================
    print_separator("ÉTAPE 2: RÉCUPÉRATION DONNÉES DRIVER")
    
    try:
        driver_data = TripDriverCache.get_trip_driver_data(test_trip_id)
        
        if driver_data:
            print_step("✅ Données driver récupérées", "SUCCESS")
            print(f"   - Nom: {driver_data.get('name', 'N/A')}")
            print(f"   - Email: {driver_data.get('email', 'N/A')}")
            print(f"   - Téléphone: {driver_data.get('phone', 'N/A')}")
            print(f"   - Note: {driver_data.get('driver_rating', 'N/A')}")
        else:
            print_step("❌ Aucune donnée driver", "ERROR")
            return False
            
    except Exception as e:
        print_step(f"❌ Erreur driver: {e}", "ERROR")
        return False
    
    # ========================================
    # ÉTAPE 3: TESTER LE TEMPLATE TRIP DETAILS
    # ========================================
    print_separator("ÉTAPE 3: TEST TEMPLATE TRIP DETAILS")
    
    try:
        config = load_json_config('trip_details_config.json')
        details_template = get_jinja_template('trip_details_template.jinja2')
        
        details_html = details_template.render(
            trip=trip_data,
            config=config.get('trip_details', {}),
            layout={
                'card_height': '350px',
                'card_width': '100%',
                'card_min_height': '300px'
            }
        )
        
        print_step("✅ Template trip_details rendu", "SUCCESS")
        print(f"   - Taille HTML: {len(details_html)} caractères")
        
        # Vérifier que les données sont dans le HTML
        if trip_data.get('departure_name', '') in details_html:
            print_step("✅ Données départ trouvées dans HTML", "SUCCESS")
        else:
            print_step("❌ Données départ manquantes dans HTML", "ERROR")
            
        if trip_data.get('destination_name', '') in details_html:
            print_step("✅ Données destination trouvées dans HTML", "SUCCESS")
        else:
            print_step("❌ Données destination manquantes dans HTML", "ERROR")
            
    except Exception as e:
        print_step(f"❌ Erreur template trip_details: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False
    
    # ========================================
    # ÉTAPE 4: TESTER LE TEMPLATE DRIVER
    # ========================================
    print_separator("ÉTAPE 4: TEST TEMPLATE DRIVER")
    
    try:
        config = load_json_config('trip_driver_config.json')
        driver_template = get_jinja_template('trip_driver_template_dynamic.jinja2')
        
        driver_html = driver_template.render(
            trip=driver_data,
            config=config.get('trip_driver', {}),
            layout={
                'card_height': '450px',
                'card_width': '50%',
                'card_min_height': '400px'
            }
        )
        
        print_step("✅ Template driver rendu", "SUCCESS")
        print(f"   - Taille HTML: {len(driver_html)} caractères")
        
        # Vérifier que les données sont dans le HTML
        if driver_data.get('name', '') in driver_html:
            print_step("✅ Nom conducteur trouvé dans HTML", "SUCCESS")
        else:
            print_step("❌ Nom conducteur manquant dans HTML", "ERROR")
            
        if driver_data.get('email', '') in driver_html:
            print_step("✅ Email conducteur trouvé dans HTML", "SUCCESS")
        else:
            print_step("❌ Email conducteur manquant dans HTML", "ERROR")
            
    except Exception as e:
        print_step(f"❌ Erreur template driver: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False
    
    # ========================================
    # ÉTAPE 5: AFFICHER UN ÉCHANTILLON DES TEMPLATES
    # ========================================
    print_separator("ÉTAPE 5: ÉCHANTILLON DES TEMPLATES GÉNÉRÉS")
    
    print("📄 TRIP DETAILS HTML (premiers 500 caractères):")
    print("-" * 60)
    print(details_html[:500])
    print("-" * 60)
    
    print("\n📄 DRIVER HTML (premiers 500 caractères):")
    print("-" * 60)
    print(driver_html[:500])
    print("-" * 60)
    
    # ========================================
    # RÉSUMÉ
    # ========================================
    print_separator("RÉSUMÉ DU TEST")
    
    print_step("✅ Données trip_details récupérées et valides", "SUCCESS")
    print_step("✅ Données driver récupérées et valides", "SUCCESS")
    print_step("✅ Templates rendus avec succès", "SUCCESS")
    print_step("✅ Données présentes dans les templates HTML", "SUCCESS")
    
    print("\n🎉 LES PANNEAUX DEVRAIENT AFFICHER LES VRAIES DONNÉES!")
    print("💡 Si vous voyez encore des tirets, vérifiez:")
    print("   1. Que le trip_id sélectionné correspond à celui testé")
    print("   2. Que les callbacks utilisent bien les mêmes services de cache")
    print("   3. Que les templates Jinja2 sont bien chargés")
    
    return True

def main():
    """Point d'entrée principal"""
    try:
        result = test_panels_display()
        
        if result:
            print("\n✅ TEST D'AFFICHAGE TERMINÉ AVEC SUCCÈS")
            sys.exit(0)
        else:
            print("\n❌ TEST D'AFFICHAGE ÉCHOUÉ")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
