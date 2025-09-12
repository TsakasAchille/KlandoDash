#!/usr/bin/env python3
"""
Script de test pour valider la configuration trip_details contre le schéma Supabase
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dash_apps'))

from dash_apps.services.trip_details_validator import TripDetailsValidator

def main():
    print("🔍 VALIDATION DE LA CONFIGURATION TRIP_DETAILS")
    print("=" * 60)
    
    # 1. Validation complète
    print("\n1. VALIDATION COMPLÈTE")
    is_valid, errors = TripDetailsValidator.validate_and_report()
    
    # 2. Analyse des champs datetime
    print("\n2. ANALYSE DES CHAMPS DATETIME")
    datetime_fields = TripDetailsValidator.validate_field_mapping()
    
    # 3. Proposition d'auto-fix si nécessaire
    if not is_valid:
        print("\n3. CORRECTION AUTOMATIQUE")
        print("Des erreurs ont été détectées. Voulez-vous tenter une correction automatique ?")
        response = input("Tapez 'y' pour oui, autre chose pour non: ")
        
        if response.lower() == 'y':
            success = TripDetailsValidator.auto_fix_config()
            if success:
                print("✅ Configuration corrigée automatiquement")
                print("Re-validation après correction:")
                TripDetailsValidator.validate_and_report()
            else:
                print("❌ Impossible de corriger automatiquement")
    
    print("\n" + "=" * 60)
    print("VALIDATION TERMINÉE")

if __name__ == "__main__":
    main()
