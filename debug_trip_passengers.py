#!/usr/bin/env python3
"""
Script de test pour analyser le callback render_trip_passengers_panel
et identifier pourquoi le panneau passagers n'affiche rien.
"""

import sys
import os
sys.path.append('/home/achille.tsakas/Klando/KlandoDash2/KlandoDash')

def test_trip_passengers_callback():
    """Test complet du callback render_trip_passengers_panel"""
    
    # Trip ID à tester
    test_trip_id = "TRIP-1756314030617789-n739xt2Uy0Qb5hP30AJ1G3dnT8G3"
    
    print("=" * 80)
    print(f"TEST DU CALLBACK RENDER_TRIP_PASSENGERS_PANEL")
    print(f"Trip ID: {test_trip_id}")
    print("=" * 80)
    
    # Étape 1: Test de l'importation des modules
    print("\n1. TEST DES IMPORTATIONS")
    print("-" * 40)
    
    try:
        from dash_apps.services.passengers_service import PassengersService
        print("✓ PassengersService importé avec succès")
    except Exception as e:
        print(f"✗ Erreur import PassengersService: {e}")
        return
    
    try:
        from dash_apps.layouts.trip_passengers_layout import TripPassengersLayout
        print("✓ TripPassengersLayout importé avec succès")
    except Exception as e:
        print(f"✗ Erreur import TripPassengersLayout: {e}")
        return
    
    # Étape 2: Test de la vérification du trip_id
    print("\n2. TEST DE LA VÉRIFICATION DU TRIP_ID")
    print("-" * 40)
    
    if not test_trip_id:
        print("✗ Trip ID est vide ou None")
        return
    else:
        print(f"✓ Trip ID valide: {test_trip_id}")
    
    # Étape 3: Test du service PassengersService
    print("\n3. TEST DU SERVICE PASSENGERS")
    print("-" * 40)
    
    try:
        print(f"Appel de PassengersService.get_passengers_summary('{test_trip_id}')")
        summary = PassengersService.get_passengers_summary(test_trip_id)
        
        print(f"✓ Service appelé avec succès")
        print(f"Type du résultat: {type(summary)}")
        print(f"Contenu du summary:")
        
        if isinstance(summary, dict):
            for key, value in summary.items():
                print(f"  - {key}: {value} (type: {type(value)})")
        else:
            print(f"  Summary complet: {summary}")
            
        # Vérifications spécifiques
        total_passengers = summary.get('total_passengers', 0) if isinstance(summary, dict) else 0
        total_seats = summary.get('total_seats', 0) if isinstance(summary, dict) else 0
        
        print(f"\nAnalyse des données:")
        print(f"  - Total passagers: {total_passengers}")
        print(f"  - Total sièges: {total_seats}")
        
        if total_passengers > 0:
            print("✓ Des passagers sont trouvés")
        else:
            print("✗ Aucun passager trouvé")
            
    except Exception as e:
        print(f"✗ Erreur dans PassengersService.get_passengers_summary: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Étape 4: Test du layout
    print("\n4. TEST DU LAYOUT")
    print("-" * 40)
    
    try:
        print("Appel de TripPassengersLayout.render_complete_layout(summary)")
        layout_result = TripPassengersLayout.render_complete_layout(summary)
        
        print(f"✓ Layout généré avec succès")
        print(f"Type du layout: {type(layout_result)}")
        
        # Analyser le contenu du layout
        if hasattr(layout_result, 'children'):
            print(f"Layout a des children: {len(layout_result.children) if layout_result.children else 0}")
            if layout_result.children:
                print("Contenu des children:")
                for i, child in enumerate(layout_result.children):
                    print(f"  Child {i}: {type(child)} - {getattr(child, 'id', 'no id')}")
        
        # Essayer de convertir en string pour voir le contenu
        try:
            layout_str = str(layout_result)
            if len(layout_str) > 200:
                print(f"Layout string (premiers 200 chars): {layout_str[:200]}...")
            else:
                print(f"Layout string: {layout_str}")
        except:
            print("Impossible de convertir le layout en string")
            
    except Exception as e:
        print(f"✗ Erreur dans TripPassengersLayout.render_complete_layout: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Étape 5: Test de l'état vide pour comparaison
    print("\n5. TEST DE L'ÉTAT VIDE (COMPARAISON)")
    print("-" * 40)
    
    try:
        empty_layout = TripPassengersLayout.render_empty_state()
        print(f"✓ Layout vide généré: {type(empty_layout)}")
        
        # Comparer avec le layout complet
        if str(layout_result) == str(empty_layout):
            print("⚠️  ATTENTION: Le layout complet est identique au layout vide!")
        else:
            print("✓ Le layout complet est différent du layout vide")
            
    except Exception as e:
        print(f"✗ Erreur dans render_empty_state: {e}")
    
    # Étape 6: Test direct des méthodes internes
    print("\n6. TEST DES MÉTHODES INTERNES")
    print("-" * 40)
    
    try:
        # Test des méthodes internes de PassengersService si disponibles
        if hasattr(PassengersService, 'get_trip_bookings'):
            print("Test de get_trip_bookings...")
            bookings = PassengersService.get_trip_bookings(test_trip_id)
            print(f"Bookings trouvés: {len(bookings) if bookings else 0}")
            
        if hasattr(PassengersService, 'get_users_for_bookings'):
            print("Test de get_users_for_bookings...")
            # Cette méthode nécessite des bookings en paramètre
            
    except Exception as e:
        print(f"Erreur dans les tests internes: {e}")
    
    print("\n" + "=" * 80)
    print("FIN DU TEST")
    print("=" * 80)

if __name__ == "__main__":
    # Activer le debug
    os.environ['DEBUG_TRIPS'] = 'true'
    
    test_trip_passengers_callback()
