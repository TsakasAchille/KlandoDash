#!/usr/bin/env python3
"""
Script pour créer la table ticket_references dans la base de données
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dash_apps.core.database import get_engine, Base
from dash_apps.models.ticket_reference import TicketReference

def create_ticket_references_table():
    """Crée la table ticket_references"""
    
    print("🔧 Création de la table ticket_references")
    print("=" * 45)
    
    try:
        # Récupérer l'engine de base de données
        engine = get_engine()
        
        # Créer la table
        TicketReference.__table__.create(engine, checkfirst=True)
        
        print("✅ Table ticket_references créée avec succès")
        print("📋 Colonnes:")
        print("  - reference_token (VARCHAR(20), PRIMARY KEY)")
        print("  - ticket_id (VARCHAR(36), UNIQUE)")
        print("  - created_at (DATETIME)")
        print("  - expires_at (DATETIME, NULLABLE)")
        print("📊 Index:")
        print("  - idx_ticket_references_ticket_id")
        print("  - idx_ticket_references_token")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

def test_token_generation():
    """Test de génération de tokens"""
    
    print("\n🧪 Test de génération de tokens")
    print("=" * 30)
    
    try:
        from dash_apps.services.ticket_reference_service import TicketReferenceService
        
        # Test avec le ticket existant
        test_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
        
        print(f"📝 Création token pour ticket: {test_ticket_id[:8]}...")
        token = TicketReferenceService.create_reference_mapping(test_ticket_id)
        
        if token:
            print(f"✅ Token créé: {token}")
            
            # Test de résolution
            resolved_id = TicketReferenceService.resolve_reference_token(token)
            if resolved_id == test_ticket_id:
                print(f"✅ Résolution OK: {token} -> {resolved_id[:8]}...")
            else:
                print(f"❌ Erreur résolution: {resolved_id}")
        else:
            print("❌ Échec création token")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Migration: Table ticket_references")
    print("=" * 40)
    
    # Créer la table
    success = create_ticket_references_table()
    
    if success:
        # Tester le système
        test_token_generation()
    
    print("\n✅ Migration terminée")
