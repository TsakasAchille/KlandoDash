#!/usr/bin/env python3
"""
Script de test pour vérifier les performances du SupportCacheService
"""

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash_apps.services.support_cache_service import SupportCacheService
from dash_apps.core.database import get_session

def test_support_cache_performance():
    """Test des performances du cache support"""
    print("=== Test Performance SupportCacheService ===")
    
    # Configuration de test
    page_size = 10
    filter_params = {'category': None, 'subtype': None}
    
    # Test 1: Premier chargement (DB)
    print("\n1. Premier chargement depuis la DB...")
    start_time = time.time()
    result1 = SupportCacheService.get_tickets_page_result(
        page_index=1,
        page_size=page_size,
        status="OPEN",
        filter_params=filter_params,
        force_reload=True
    )
    db_time = time.time() - start_time
    print(f"   Temps DB: {db_time:.3f}s")
    print(f"   Tickets trouvés: {len(result1.get('tickets', []))}")
    print(f"   Total: {result1.get('total_count', 0)}")
    
    # Test 2: Deuxième chargement (Cache local)
    print("\n2. Deuxième chargement (cache local)...")
    start_time = time.time()
    result2 = SupportCacheService.get_tickets_page_result(
        page_index=1,
        page_size=page_size,
        status="OPEN",
        filter_params=filter_params,
        force_reload=False
    )
    cache_time = time.time() - start_time
    print(f"   Temps Cache: {cache_time:.3f}s")
    print(f"   Tickets trouvés: {len(result2.get('tickets', []))}")
    
    # Test 3: Performance avec filtres
    print("\n3. Test avec filtres...")
    filter_params_with_category = {'category': 'signalement_trajet', 'subtype': None}
    start_time = time.time()
    result3 = SupportCacheService.get_tickets_page_result(
        page_index=1,
        page_size=page_size,
        status="OPEN",
        filter_params=filter_params_with_category,
        force_reload=True
    )
    filter_time = time.time() - start_time
    print(f"   Temps avec filtres: {filter_time:.3f}s")
    print(f"   Tickets filtrés: {len(result3.get('tickets', []))}")
    
    # Test 4: Statistiques du cache
    print("\n4. Statistiques du cache...")
    stats = SupportCacheService.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Calcul de l'amélioration
    if db_time > 0:
        improvement = ((db_time - cache_time) / db_time) * 100
        print(f"\n✅ Amélioration performance: {improvement:.1f}%")
    
    print("\n=== Test terminé ===")

def test_support_cache_invalidation():
    """Test de l'invalidation du cache"""
    print("\n=== Test Invalidation Cache ===")
    
    # Test de l'invalidation pour un ticket spécifique
    test_ticket_id = "test_ticket_123"
    
    # Simuler la mise en cache d'un panneau
    from dash import html
    test_panel = html.Div("Test panel")
    SupportCacheService.set_cached_panel(test_ticket_id, 'details', test_panel)
    
    print(f"Panneau mis en cache pour {test_ticket_id}")
    
    # Vérifier que le panneau est en cache
    cached_panel = SupportCacheService.get_cached_panel(test_ticket_id, 'details')
    if cached_panel:
        print("✅ Panneau trouvé dans le cache")
    else:
        print("❌ Panneau non trouvé dans le cache")
    
    # Effacer le cache pour ce ticket
    SupportCacheService.clear_ticket_cache(test_ticket_id)
    print(f"Cache effacé pour {test_ticket_id}")
    
    # Vérifier que le panneau n'est plus en cache
    cached_panel_after = SupportCacheService.get_cached_panel(test_ticket_id, 'details')
    if not cached_panel_after:
        print("✅ Cache correctement effacé")
    else:
        print("❌ Cache non effacé")
    
    print("=== Test invalidation terminé ===")

if __name__ == "__main__":
    try:
        test_support_cache_performance()
        test_support_cache_invalidation()
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
