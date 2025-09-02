#!/usr/bin/env python3
"""
Script de test pour vérifier l'affichage des commentaires de support
"""

from dash_apps.core.database import get_session
from dash_apps.models.support_comment import SupportComment
from dash_apps.components.support_tickets import render_ticket_details
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
import json

def test_support_display():
    """
    Test l'affichage des commentaires de support pour vérifier les messages externes
    """
    
    print("🧪 Test de l'affichage des commentaires de support")
    print("=" * 60)
    
    try:
        with get_session() as session:
            # 1. Récupérer un ticket avec des commentaires externes
            # Trouver un ticket avec des commentaires externes
            tickets = SupportTicketRepository.list_tickets(session, skip=0, limit=100)
            
            target_ticket = None
            for ticket in tickets:
                # Convertir le ticket schema en dict
                ticket_dict = ticket.model_dump() if hasattr(ticket, 'model_dump') else dict(ticket)
                comments = SupportCommentRepository.list_comments_for_ticket(session, ticket_dict["ticket_id"])
                for comment in comments:
                    # Convertir le schema en dict
                    comment_dict = comment.model_dump() if hasattr(comment, 'model_dump') else dict(comment)
                    if comment_dict.get("comment_sent") or comment_dict.get("comment_received"):
                        target_ticket = ticket_dict
                        break
                if target_ticket:
                    break
            
            if not target_ticket:
                print("❌ Aucun ticket avec des commentaires externes trouvé")
                return
            
            print(f"✅ Ticket trouvé: {target_ticket['ticket_id']}")
            print(f"   Sujet: {target_ticket.get('subject', 'Sans sujet')}")
            
            # 2. Récupérer les commentaires pour ce ticket
            comments = SupportCommentRepository.list_comments_for_ticket(session, target_ticket["ticket_id"])
            print(f"\n📝 Commentaires trouvés: {len(comments)}")
            
            for i, comment in enumerate(comments, 1):
                # Convertir le schema en dict
                comment_dict = comment.model_dump() if hasattr(comment, 'model_dump') else dict(comment)
                
                print(f"\n{i}. Commentaire ID: {comment_dict.get('comment_id')}")
                print(f"   comment_text: {comment_dict.get('comment_text', 'NULL')}")
                print(f"   comment_sent: {comment_dict.get('comment_sent', 'NULL')}")
                print(f"   comment_received: {comment_dict.get('comment_received', 'NULL')}")
                print(f"   comment_type: {comment_dict.get('comment_type', 'NULL')}")
                
                # Simuler la logique de détermination du contenu
                comment_sent = comment_dict.get("comment_sent")
                comment_received = comment_dict.get("comment_received")
                comment_type = comment_dict.get("comment_type")
                
                if comment_sent and comment_sent.strip():
                    interaction_type = "comment_sent"
                    content = comment_sent
                    print(f"   → Type déterminé: {interaction_type}")
                    print(f"   → Contenu affiché: {content}")
                elif comment_received and comment_received.strip():
                    interaction_type = "comment_received"
                    content = comment_received
                    print(f"   → Type déterminé: {interaction_type}")
                    print(f"   → Contenu affiché: {content}")
                elif comment_type == "external":
                    interaction_type = "external"
                    content = comment_dict.get("comment_text", "")
                    print(f"   → Type déterminé: {interaction_type}")
                    print(f"   → Contenu affiché: {content}")
                else:
                    interaction_type = "internal"
                    content = comment_dict.get("comment_text", "")
                    print(f"   → Type déterminé: {interaction_type}")
                    print(f"   → Contenu affiché: {content}")
            
            # 3. Tester la fonction render_ticket_details
            print(f"\n🔧 Test de la fonction render_ticket_details...")
            
            try:
                # Appeler la fonction de rendu
                result = render_ticket_details(target_ticket, comments)
                print("✅ Fonction render_ticket_details exécutée sans erreur")
                
                # Analyser le résultat pour voir si les contenus sont présents
                result_str = str(result)
                
                # Chercher les contenus des messages externes dans le résultat
                for comment in comments:
                    comment_dict = comment.model_dump() if hasattr(comment, 'model_dump') else dict(comment)
                    comment_sent = comment_dict.get("comment_sent")
                    comment_received = comment_dict.get("comment_received")
                    
                    if comment_sent and comment_sent.strip():
                        if comment_sent in result_str:
                            print(f"✅ Message envoyé trouvé dans le rendu: {comment_sent[:50]}...")
                        else:
                            print(f"❌ Message envoyé MANQUANT dans le rendu: {comment_sent[:50]}...")
                    
                    if comment_received and comment_received.strip():
                        if comment_received in result_str:
                            print(f"✅ Message reçu trouvé dans le rendu: {comment_received[:50]}...")
                        else:
                            print(f"❌ Message reçu MANQUANT dans le rendu: {comment_received[:50]}...")
                
            except Exception as e:
                print(f"❌ Erreur lors du rendu: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_support_display()
