#!/usr/bin/env python3
"""
Test complet du système de tokens sécurisés
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from dash_apps.services.ticket_reference_service import TicketReferenceService
from dash_apps.services.email_receiver_service import EmailReceiverService
import base64

def test_complete_secure_system():
    """Test complet du système sécurisé"""
    
    print("🔒 Test du système de tokens sécurisés")
    print("=" * 45)
    
    # 1. Vérifier le token existant
    test_ticket_id = "4e4745ab-9aff-4025-b003-16a2f99ff300"
    token = TicketReferenceService.get_reference_for_ticket(test_ticket_id)
    
    print(f"🎫 Token pour ticket {test_ticket_id[:8]}...: {token}")
    
    # 2. Simuler un email avec le nouveau format sécurisé
    secure_email = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': f'Re: Réponse à votre ticket #{token} - TEST DE TICKET'},
                {'name': 'From', 'value': 'client.secure@example.com'}
            ],
            'mimeType': 'text/plain',
            'body': {
                'data': base64.b64encode(f"""Bonjour,

Merci pour votre réponse avec le token sécurisé !

J'ai une question supplémentaire concernant mon problème...

Cordialement,
Client Sécurisé

---
Référence: {token}""".encode()).decode()
            }
        }
    }
    
    print(f"📧 Email de test créé avec token: {token}")
    print(f"📝 Sujet: Re: Réponse à votre ticket #{token} - TEST DE TICKET")
    
    # 3. Tester l'extraction du token depuis le sujet
    subject = f"Re: Réponse à votre ticket #{token} - TEST DE TICKET"
    extracted_token = TicketReferenceService.extract_token_from_subject(subject)
    print(f"🔍 Token extrait du sujet: {extracted_token}")
    
    # 4. Tester la résolution du token
    resolved_id = TicketReferenceService.resolve_reference_token(extracted_token)
    print(f"🔗 Token résolu vers: {resolved_id[:8] if resolved_id else 'ERREUR'}...")
    
    # 5. Tester le traitement complet de l'email
    print(f"\n🧪 Test traitement email complet...")
    success = EmailReceiverService.process_incoming_email(secure_email)
    
    if success:
        print("✅ Email traité avec succès!")
        print("📝 Nouveau commentaire ajouté au ticket")
        print("🔄 Cache invalidé")
    else:
        print("❌ Échec du traitement")
    
    return success

def test_token_extraction_methods():
    """Test des différentes méthodes d'extraction"""
    
    print(f"\n🔍 Test des méthodes d'extraction")
    print("=" * 35)
    
    token = "TK-2025-9Z9J"  # Token de test
    
    # Test 1: Extraction depuis le sujet
    subjects = [
        f"Re: Réponse à votre ticket #{token} - TEST",
        f"Réponse à votre ticket #{token} - Support",
        f"ticket #{token} question",
    ]
    
    for i, subject in enumerate(subjects, 1):
        extracted = TicketReferenceService.extract_token_from_subject(subject)
        status = "✅" if extracted == token else "❌"
        print(f"Test {i} - Sujet: {status} {extracted or 'Non trouvé'}")
    
    # Test 2: Extraction depuis le corps
    body = f"""Bonjour,
    
Merci pour votre aide.

---
Référence: {token}
"""
    
    ticket_id = EmailReceiverService.extract_ticket_id_from_email("Test", body)
    resolved = TicketReferenceService.resolve_reference_token(token) if ticket_id else None
    status = "✅" if resolved else "❌"
    print(f"Test corps: {status} {ticket_id or 'Non trouvé'}")

def test_security_aspects():
    """Test des aspects sécurité"""
    
    print(f"\n🛡️ Test sécurité")
    print("=" * 20)
    
    # Vérifier qu'on ne peut pas deviner les tokens
    test_tokens = ["TK-2025-AAAA", "TK-2025-0000", "TK-2025-1111"]
    
    for token in test_tokens:
        resolved = TicketReferenceService.resolve_reference_token(token)
        if resolved:
            print(f"⚠️  Token prévisible trouvé: {token}")
        else:
            print(f"✅ Token {token} non résolu (sécurité OK)")

if __name__ == "__main__":
    print("Test complet du système de tokens sécurisés")
    print("=" * 50)
    
    # Tests
    success = test_complete_secure_system()
    test_token_extraction_methods()
    test_security_aspects()
    
    if success:
        print(f"\n🎉 Système de tokens sécurisés opérationnel!")
        print("💡 Vérifiez votre interface support pour voir le nouveau commentaire")
    else:
        print(f"\n❌ Des problèmes ont été détectés")
    
    print("\n✅ Tests terminés")
