#!/usr/bin/env python3
"""
Test direct du système de réception d'emails sans passer par l'API
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dash_apps.services.email_receiver_service import EmailReceiverService
import base64

def test_direct_email_processing():
    """Test direct du traitement d'email"""
    
    print("🧪 Test direct du traitement d'email")
    print("=" * 40)
    
    # Simuler un message Gmail API
    test_message = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Re: Réponse à votre ticket de support - TEST DE TICKET'},
                {'name': 'From', 'value': 'client.test@example.com'}
            ],
            'mimeType': 'text/plain',
            'body': {
                'data': base64.b64encode("""Bonjour,

Merci pour votre réponse rapide. J'ai une question supplémentaire concernant mon problème...

Pouvez-vous me donner plus de détails ?

Cordialement,
Client Test

---
Ticket ID: 4e4745ab-9aff-4025-b003-16a2f99ff300""".encode()).decode()
            }
        }
    }
    
    print("📧 Message de test créé")
    print(f"Sujet: Re: Réponse à votre ticket de support - TEST DE TICKET")
    print(f"De: client.test@example.com")
    print(f"Ticket ID: 4e4745ab-9aff-4025-b003-16a2f99ff300")
    
    # Traiter le message
    try:
        success = EmailReceiverService.process_incoming_email(test_message)
        
        if success:
            print("✅ Email traité avec succès!")
            print("📝 Un nouveau commentaire devrait être ajouté au ticket")
            print("🔄 Le cache du ticket a été invalidé")
            print("\n💡 Vérifiez votre interface support pour voir le nouveau commentaire")
        else:
            print("❌ Échec du traitement de l'email")
            
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
        import traceback
        traceback.print_exc()

def test_ticket_id_extraction():
    """Test de l'extraction d'ID de ticket"""
    
    print("\n🔍 Test d'extraction d'ID de ticket")
    print("=" * 35)
    
    # Test 1: ID dans le sujet
    subject1 = "Re: Réponse à votre ticket de support - TEST DE TICKET"
    body1 = "Message sans ID"
    
    ticket_id = EmailReceiverService.extract_ticket_id_from_email(subject1, body1)
    print(f"Test 1 - ID dans sujet: {ticket_id or 'Non trouvé'}")
    
    # Test 2: ID dans le corps
    subject2 = "Re: Réponse à votre ticket"
    body2 = """Bonjour,
    
Merci pour votre aide.

---
Ticket ID: 4e4745ab-9aff-4025-b003-16a2f99ff300
"""
    
    ticket_id = EmailReceiverService.extract_ticket_id_from_email(subject2, body2)
    print(f"Test 2 - ID dans corps: {ticket_id or 'Non trouvé'}")

def check_database_connection():
    """Vérifier la connexion à la base de données"""
    
    print("\n🔌 Test de connexion base de données")
    print("=" * 35)
    
    try:
        from dash_apps.core.database import get_session
        
        with get_session() as session:
            # Test simple
            from sqlalchemy import text
            result = session.execute(text("SELECT 1")).fetchone()
            print("✅ Connexion base de données OK")
            
            # Vérifier le ticket de test
            from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
            ticket = SupportTicketRepository.get_ticket(session, "4e4745ab-9aff-4025-b003-16a2f99ff300")
            
            if ticket:
                print(f"✅ Ticket de test trouvé: {ticket.subject}")
                
                # Vérifier les commentaires
                from dash_apps.repositories.support_comment_repository import SupportCommentRepository
                comments = SupportCommentRepository.get_comments_by_ticket(session, "4e4745ab-9aff-4025-b003-16a2f99ff300")
                print(f"📝 Nombre de commentaires: {len(comments)}")
                
                for comment in comments:
                    print(f"  - Type: {comment.comment_type}, Source: {comment.comment_source}")
                    if comment.comment_received:
                        print(f"    Reçu: {comment.comment_received[:50]}...")
                    if comment.comment_sent:
                        print(f"    Envoyé: {comment.comment_sent[:50]}...")
            else:
                print("❌ Ticket de test non trouvé")
                
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Test du système de réception d'emails")
    print("=" * 50)
    
    # Tests
    check_database_connection()
    test_ticket_id_extraction()
    test_direct_email_processing()
    
    print("\n✅ Tests terminés")
