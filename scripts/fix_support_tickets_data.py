#!/usr/bin/env python3
"""
Script pour corriger et compléter les données dans la table support_tickets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dash_apps.core.database import get_session
from dash_apps.models.support_ticket import SupportTicket
from datetime import datetime

def analyze_ticket_data():
    """Analyse les données actuelles des tickets"""
    
    print("🔍 Analyse des données support_tickets")
    print("=" * 40)
    
    try:
        with get_session() as session:
            tickets = session.query(SupportTicket).all()
            
            print(f"📊 Nombre total de tickets: {len(tickets)}")
            
            # Analyser chaque ticket
            missing_fields = {}
            for ticket in tickets:
                ticket_dict = ticket.to_dict()
                
                print(f"\n🎫 Ticket: {ticket_dict['ticket_id'][:8]}...")
                print(f"   Sujet: {ticket_dict['subject'][:50]}...")
                
                # Vérifier chaque champ
                for field, value in ticket_dict.items():
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        if field not in missing_fields:
                            missing_fields[field] = 0
                        missing_fields[field] += 1
                        print(f"   ⚠️  {field}: VIDE")
                    else:
                        print(f"   ✅ {field}: {str(value)[:30]}...")
            
            if missing_fields:
                print(f"\n📋 Résumé des champs manquants:")
                for field, count in missing_fields.items():
                    print(f"   {field}: {count} tickets")
            else:
                print(f"\n✅ Tous les champs sont remplis")
                
            return tickets
            
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        return []

def fix_missing_data():
    """Corrige les données manquantes"""
    
    print(f"\n🔧 Correction des données manquantes")
    print("=" * 35)
    
    try:
        with get_session() as session:
            tickets = session.query(SupportTicket).all()
            
            for ticket in tickets:
                updated = False
                
                # Corriger les champs manquants avec des valeurs par défaut
                if not ticket.status:
                    ticket.status = "OPEN"
                    updated = True
                    print(f"🔄 {ticket.ticket_id}: status -> OPEN")
                
                if not ticket.created_at:
                    ticket.created_at = datetime.now()
                    updated = True
                    print(f"🔄 {ticket.ticket_id}: created_at -> {ticket.created_at}")
                
                if not ticket.updated_at:
                    ticket.updated_at = ticket.created_at or datetime.now()
                    updated = True
                    print(f"🔄 {ticket.ticket_id}: updated_at -> {ticket.updated_at}")
                
                if not ticket.contact_preference:
                    # Deviner la préférence basée sur les données disponibles
                    if ticket.mail and "@" in ticket.mail:
                        ticket.contact_preference = "mail"
                    elif ticket.phone:
                        ticket.contact_preference = "phone"
                    else:
                        ticket.contact_preference = "mail"
                    updated = True
                    print(f"🔄 {ticket.ticket_id}: contact_preference -> {ticket.contact_preference}")
                
                if updated:
                    session.commit()
                    print(f"✅ Ticket {ticket.ticket_id[:8]}... mis à jour")
            
            print(f"\n✅ Correction terminée")
            
    except Exception as e:
        print(f"❌ Erreur correction: {e}")

def validate_specific_ticket():
    """Valide le ticket spécifique mentionné par l'utilisateur"""
    
    print(f"\n🎯 Validation ticket spécifique")
    print("=" * 30)
    
    target_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
    expected_data = {
        "user_id": "bk17O0BBAndQR7xxSZxDvAGkSWU2",
        "subject": "TEST DE TICKET",
        "message": "J'ai un soucis avec mon application",
        "status": "OPEN",
        "contact_preference": "mail",
        "phone": "+33623518730",
        "mail": "achilletsakde512de51de51de1de51@gmail.com"
    }
    
    try:
        with get_session() as session:
            ticket = session.query(SupportTicket).filter(
                SupportTicket.ticket_id == target_ticket_id
            ).first()
            
            if not ticket:
                print(f"❌ Ticket {target_ticket_id} non trouvé")
                return False
            
            print(f"🎫 Validation ticket: {target_ticket_id[:8]}...")
            
            # Vérifier chaque champ
            ticket_dict = ticket.to_dict()
            all_correct = True
            
            for field, expected_value in expected_data.items():
                actual_value = ticket_dict.get(field)
                
                if actual_value == expected_value:
                    print(f"   ✅ {field}: {actual_value}")
                else:
                    print(f"   ❌ {field}: '{actual_value}' != '{expected_value}'")
                    all_correct = False
                    
                    # Corriger la valeur
                    setattr(ticket, field, expected_value)
                    print(f"   🔄 Correction: {field} -> {expected_value}")
            
            # Vérifier les timestamps
            if ticket.created_at:
                print(f"   ✅ created_at: {ticket.created_at}")
            else:
                print(f"   ❌ created_at: manquant")
                all_correct = False
            
            if ticket.updated_at:
                print(f"   ✅ updated_at: {ticket.updated_at}")
            else:
                print(f"   ❌ updated_at: manquant")
                all_correct = False
            
            if not all_correct:
                session.commit()
                print(f"   🔄 Ticket corrigé et sauvegardé")
            
            return all_correct
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

def export_ticket_data():
    """Exporte les données des tickets au format JSON"""
    
    print(f"\n📤 Export des données tickets")
    print("=" * 30)
    
    try:
        with get_session() as session:
            tickets = session.query(SupportTicket).all()
            
            tickets_data = []
            for i, ticket in enumerate(tickets):
                ticket_dict = ticket.to_dict()
                # Convertir les dates en string pour JSON
                if ticket_dict['created_at']:
                    ticket_dict['created_at'] = ticket_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S.%f')
                if ticket_dict['updated_at']:
                    ticket_dict['updated_at'] = ticket_dict['updated_at'].strftime('%Y-%m-%d %H:%M:%S.%f')
                
                ticket_dict['idx'] = i
                tickets_data.append(ticket_dict)
            
            print(f"📊 {len(tickets_data)} tickets exportés")
            
            # Afficher le premier ticket comme exemple
            if tickets_data:
                import json
                print(f"\n📋 Exemple (premier ticket):")
                print(json.dumps(tickets_data[0], indent=2, ensure_ascii=False))
            
            return tickets_data
            
    except Exception as e:
        print(f"❌ Erreur export: {e}")
        return []

if __name__ == "__main__":
    print("Correction des données support_tickets")
    print("=" * 45)
    
    # 1. Analyser les données actuelles
    tickets = analyze_ticket_data()
    
    # 2. Corriger les données manquantes
    if tickets:
        fix_missing_data()
    
    # 3. Valider le ticket spécifique
    validate_specific_ticket()
    
    # 4. Exporter les données
    export_ticket_data()
    
    print(f"\n✅ Script terminé")
