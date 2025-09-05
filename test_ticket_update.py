#!/usr/bin/env python3
"""
Test de mise à jour des tickets lors des interactions email
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dash_apps.services.email_receiver_service import EmailReceiverService
from dash_apps.core.database import get_session
from dash_apps.models.support_ticket import SupportTicket
import base64
from datetime import datetime

def test_ticket_timestamp_update():
    """Test que les timestamps des tickets sont bien mis à jour"""
    
    print("🕒 Test mise à jour timestamp tickets")
    print("=" * 40)
    
    test_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
    
    # 1. Vérifier le timestamp actuel
    with get_session() as session:
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == test_ticket_id).first()
        if ticket:
            old_timestamp = ticket.updated_at
            print(f"📅 Timestamp avant: {old_timestamp}")
        else:
            print("❌ Ticket non trouvé")
            return False
    
    # 2. Simuler une réponse client
    secure_email = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Re: Réponse à votre ticket #TK-2025-9Z9J - TEST DE TICKET'},
                {'name': 'From', 'value': 'client.timestamp@example.com'}
            ],
            'mimeType': 'text/plain',
            'body': {
                'data': base64.b64encode("""Bonjour,

Test de mise à jour du timestamp du ticket.

Cordialement,
Client Test

---
Référence: TK-2025-9Z9J""".encode()).decode()
            }
        }
    }
    
    print("📧 Simulation réponse client...")
    
    # 3. Traiter l'email
    success = EmailReceiverService.process_incoming_email(secure_email)
    
    if not success:
        print("❌ Échec traitement email")
        return False
    
    # 4. Vérifier que le timestamp a été mis à jour
    with get_session() as session:
        ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == test_ticket_id).first()
        if ticket:
            new_timestamp = ticket.updated_at
            print(f"📅 Timestamp après: {new_timestamp}")
            
            if new_timestamp > old_timestamp:
                print("✅ Timestamp mis à jour avec succès!")
                print(f"⏱️  Différence: {(new_timestamp - old_timestamp).total_seconds():.2f} secondes")
                return True
            else:
                print("❌ Timestamp non mis à jour")
                return False
        else:
            print("❌ Ticket non trouvé après traitement")
            return False

def check_database_state():
    """Vérifie l'état de la base de données"""
    
    print("\n🔍 Vérification état base de données")
    print("=" * 35)
    
    test_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
    
    try:
        with get_session() as session:
            # Vérifier le ticket
            ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == test_ticket_id).first()
            
            if ticket:
                print(f"🎫 Ticket trouvé: {ticket.subject}")
                print(f"📅 Créé: {ticket.created_at}")
                print(f"🔄 Mis à jour: {ticket.updated_at}")
                print(f"📊 Statut: {ticket.status}")
                
                # Vérifier les commentaires
                from dash_apps.models.support_comment import SupportComment
                comments = session.query(SupportComment).filter(
                    SupportComment.ticket_id == test_ticket_id
                ).order_by(SupportComment.created_at.desc()).limit(5).all()
                
                print(f"💬 Derniers commentaires ({len(comments)}):")
                for i, comment in enumerate(comments, 1):
                    comment_type = comment.comment_type or 'internal'
                    source = comment.comment_source or 'interface'
                    print(f"  {i}. Type: {comment_type}, Source: {source}")
                    if comment.comment_received:
                        print(f"     Reçu: {comment.comment_received[:50]}...")
                    if comment.comment_sent:
                        print(f"     Envoyé: {comment.comment_sent[:50]}...")
                    if comment.comment_text:
                        print(f"     Texte: {comment.comment_text[:50]}...")
                
                return True
            else:
                print("❌ Ticket non trouvé")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("Test de mise à jour des tickets support")
    print("=" * 45)
    
    # Vérifier l'état initial
    check_database_state()
    
    # Tester la mise à jour
    success = test_ticket_timestamp_update()
    
    if success:
        print("\n🎉 Système de mise à jour opérationnel!")
        print("📝 Les tickets sont maintenant mis à jour lors des interactions email")
    else:
        print("\n❌ Problème détecté dans la mise à jour")
    
    print("\n✅ Test terminé")
