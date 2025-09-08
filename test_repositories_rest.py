#!/usr/bin/env python3
"""
Script pour tester les repositories REST avec Supabase
Ceci vérifie que les repositories REST fonctionnent correctement
avant de les intégrer à l'ensemble de l'application.

Usage:
    python3 test_repositories_rest.py
"""
import os
import sys
from dash_apps.repositories.repository_factory import RepositoryFactory

# Forcer l'utilisation de l'API REST pour les tests
os.environ['FORCE_REST_API'] = 'True'
os.environ['CONNECTION_MODE'] = 'rest'

# Importer directement les repositories REST au lieu d'utiliser la factory
from dash_apps.repositories.user_repository_rest import UserRepositoryRest
from dash_apps.repositories.trip_repository_rest import TripRepositoryRest
from dash_apps.repositories.support_ticket_repository_rest import SupportTicketRepositoryRest
from dash_apps.repositories.support_comment_repository_rest import SupportCommentRepositoryRest
from dash_apps.repositories.booking_repository_rest import BookingRepositoryRest

def test_user_repository():
    """Test du UserRepositoryRest"""
    print("\n=== Test UserRepository ===")
    # Utiliser directement la classe REST au lieu de passer par la factory
    user_repo = UserRepositoryRest()
    
    # Test get_all_users
    print("Test get_all_users...")
    users = user_repo.get_all_users()
    print(f"Nombre d'utilisateurs: {len(users)}")
    
    # Si des utilisateurs sont trouvés, tester get_user_by_id
    if users:
        user_id = users[0].get('uid')
        print(f"\nTest get_user_by_id pour {user_id}...")
        user = user_repo.get_user_by_id(user_id)
        if user:
            print(f"Utilisateur trouvé: {user.get('display_name')} - {user.get('email')}")
        else:
            print("❌ Erreur: Utilisateur non trouvé")
    
    # Test pagination
    print("\nTest get_users_paginated...")
    result = user_repo.get_users_paginated(page=0, page_size=5)
    print(f"Utilisateurs paginés: {len(result.get('users', []))} sur {result.get('total_count', 0)} total")
    
    return len(users) > 0

def test_trip_repository():
    """Test du TripRepositoryRest"""
    print("\n=== Test TripRepository ===")
    # Utiliser directement la classe REST au lieu de passer par la factory
    trip_repo = TripRepositoryRest()
    
    # Test list_trips
    print("Test list_trips...")
    # Vérifier si c'est un objet REST ou SQL
    if hasattr(trip_repo, '__class__') and 'Rest' in trip_repo.__class__.__name__:
        # Version REST - pas de paramètre session
        trips = trip_repo.list_trips(limit=10)
    else:
        # Version SQL - nécessite une session None pour les tests
        from dash_apps.core.database import SessionLocal
        with SessionLocal() as session:
            trips = trip_repo.list_trips(session, limit=10)
            
    print(f"Nombre de trajets: {len(trips) if trips else 0}")
    
    # Si des trajets sont trouvés, tester get_trip_by_id
    if trips:
        trip_id = trips[0].get('trip_id')
        print(f"\nTest get_trip_by_id pour {trip_id}...")
        # Vérifier si c'est un objet REST ou SQL
        if hasattr(trip_repo, '__class__') and 'Rest' in trip_repo.__class__.__name__:
            trip = trip_repo.get_trip_by_id(trip_id)
        else:
            # Version SQL
            trip = trip_repo.get_trip_by_id(trip_id)
            
        if trip:
            print(f"Trajet trouvé: {trip.get('departure_name')} → {trip.get('destination_name')}")
        else:
            print("❌ Erreur: Trajet non trouvé")
    
    # Test pagination
    print("\nTest get_trips_paginated_minimal...")
    result = trip_repo.get_trips_paginated_minimal(page=0, page_size=5)
    print(f"Trajets paginés: {len(result.get('trips', []))} sur {result.get('total_count', 0)} total")
    
    return len(trips) > 0 if trips else False

def test_support_ticket_repository():
    """Test du SupportTicketRepositoryRest"""
    print("\n=== Test SupportTicketRepository ===")
    # Utiliser directement la classe REST au lieu de passer par la factory
    ticket_repo = SupportTicketRepositoryRest()
    
    # Test get_tickets_by_page
    print("Test get_tickets_by_page...")
    # Vérifier si c'est un objet REST ou SQL
    if hasattr(ticket_repo, '__class__') and 'Rest' in ticket_repo.__class__.__name__:
        # Version REST - pas de paramètre session
        result = ticket_repo.get_tickets_by_page(page=1, page_size=5)
    else:
        # Version SQL - nécessite une session
        from dash_apps.core.database import SessionLocal
        with SessionLocal() as session:
            result = ticket_repo.get_tickets_by_page(session, page=1, page_size=5)
            
    print(f"Tickets trouvés: {len(result.get('tickets', []))} sur {result.get('pagination', {}).get('total_count', 0)} total")
    
    # Si des tickets sont trouvés, tester get_ticket
    tickets = result.get('tickets', [])
    if tickets:
        ticket_id = tickets[0].get('ticket_id')
        print(f"\nTest get_ticket pour {ticket_id}...")
        # Vérifier si c'est un objet REST ou SQL
        if hasattr(ticket_repo, '__class__') and 'Rest' in ticket_repo.__class__.__name__:
            ticket = ticket_repo.get_ticket(ticket_id)
        else:
            from dash_apps.core.database import SessionLocal
            with SessionLocal() as session:
                ticket = ticket_repo.get_ticket(session, ticket_id)
                
        if ticket:
            print(f"Ticket trouvé: {ticket.get('subject')}")
        else:
            print("❌ Erreur: Ticket non trouvé")
    
    return len(tickets) > 0

def test_support_comment_repository():
    """Test du SupportCommentRepositoryRest"""
    print("\n=== Test SupportCommentRepository ===")
    # Utiliser directement les classes REST au lieu de passer par la factory
    ticket_repo = SupportTicketRepositoryRest()
    comment_repo = SupportCommentRepositoryRest()
    
    # Trouver un ticket pour tester les commentaires
    # Vérifier si c'est un objet REST ou SQL
    if hasattr(ticket_repo, '__class__') and 'Rest' in ticket_repo.__class__.__name__:
        # Version REST - pas de paramètre session
        result = ticket_repo.get_tickets_by_page(page=1, page_size=1)
    else:
        # Version SQL - nécessite une session
        from dash_apps.core.database import SessionLocal
        with SessionLocal() as session:
            result = ticket_repo.get_tickets_by_page(session, page=1, page_size=1)
            
    tickets = result.get('tickets', [])
    
    if tickets:
        ticket_id = tickets[0].get('ticket_id')
        print(f"Test list_comments_for_ticket pour {ticket_id}...")
        
        # Vérifier si c'est un objet REST ou SQL
        if hasattr(comment_repo, '__class__') and 'Rest' in comment_repo.__class__.__name__:
            # Version REST
            comments = comment_repo.list_comments_for_ticket(ticket_id)
        else:
            # Version SQL
            from dash_apps.core.database import SessionLocal
            with SessionLocal() as session:
                comments = comment_repo.list_comments_for_ticket(session, ticket_id)
                
        print(f"Commentaires trouvés: {len(comments) if comments else 0}")
        
        return len(comments) >= 0 if comments else False
    else:
        print("⚠️ Pas de tickets disponibles pour tester les commentaires")
        return False

def test_booking_repository():
    """Test du BookingRepositoryRest"""
    print("\n=== Test BookingRepository ===")
    # Utiliser directement les classes REST au lieu de passer par la factory
    booking_repo = BookingRepositoryRest()
    trip_repo = TripRepositoryRest()
    
    # Trouver un trajet pour tester les réservations
    # Vérifier si c'est un objet REST ou SQL
    if hasattr(trip_repo, '__class__') and 'Rest' in trip_repo.__class__.__name__:
        # Version REST - pas de paramètre session
        trips = trip_repo.list_trips(limit=1)
    else:
        # Version SQL - nécessite une session
        from dash_apps.core.database import SessionLocal
        with SessionLocal() as session:
            trips = trip_repo.list_trips(session, limit=1)
    
    if trips:
        trip_id = trips[0].get('trip_id')
        print(f"Test get_trip_bookings pour {trip_id}...")
        
        # Vérifier si c'est un objet REST ou SQL
        if hasattr(booking_repo, '__class__') and 'Rest' in booking_repo.__class__.__name__:
            # Version REST
            bookings = booking_repo.get_trip_bookings(trip_id)
        else:
            # Version SQL
            bookings = booking_repo.get_trip_bookings(trip_id)
            
        print(f"Réservations trouvées: {len(bookings) if bookings else 0}")
        
        return len(bookings) >= 0 if bookings else False
    else:
        print("⚠️ Pas de trajets disponibles pour tester les réservations")
        return False

def run_all_tests():
    """Exécute tous les tests et retourne un statut global"""
    results = {}
    
    print("\n🔍 TESTS DES REPOSITORIES REST")
    print("================================")
    
    try:
        results["user"] = test_user_repository()
    except Exception as e:
        print(f"❌ Erreur lors du test UserRepository: {str(e)}")
        results["user"] = False
    
    try:
        results["trip"] = test_trip_repository()
    except Exception as e:
        print(f"❌ Erreur lors du test TripRepository: {str(e)}")
        results["trip"] = False
    
    try:
        results["ticket"] = test_support_ticket_repository()
    except Exception as e:
        print(f"❌ Erreur lors du test SupportTicketRepository: {str(e)}")
        results["ticket"] = False
    
    try:
        results["comment"] = test_support_comment_repository()
    except Exception as e:
        print(f"❌ Erreur lors du test SupportCommentRepository: {str(e)}")
        results["comment"] = False
    
    try:
        results["booking"] = test_booking_repository()
    except Exception as e:
        print(f"❌ Erreur lors du test BookingRepository: {str(e)}")
        results["booking"] = False
    
    print("\n================================")
    print("📊 RÉSULTATS DES TESTS:")
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    
    for name, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{name}: {status}")
    
    print(f"\nBilan: {success_count}/{total_count} tests réussis")
    
    return success_count == total_count

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
