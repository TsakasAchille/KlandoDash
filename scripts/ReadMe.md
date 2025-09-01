🧪 BENCHMARK  DU SYSTÈME DE CACHE
==================================================

🧪 Test Cache Miss - 10 itérations
  Itération 1: 3.201ms
  Itération 2: 3.180ms
  Itération 3: 3.175ms
  Itération 4: 3.176ms
  Itération 5: 3.187ms
  Itération 6: 3.176ms
  Itération 7: 3.200ms
  Itération 8: 3.189ms
  Itération 9: 3.189ms
  Itération 10: 3.207ms
📊 Moyenne Cache Miss: 3.188ms

🎯 Test Cache Hit - 10 itérations
  Itération 1: 0.006ms
  Itération 2: 0.002ms
  Itération 3: 0.001ms
  Itération 4: 0.001ms
  Itération 5: 0.001ms
  Itération 6: 0.001ms
  Itération 7: 0.001ms
  Itération 8: 0.001ms
  Itération 9: 0.001ms
  Itération 10: 0.001ms
📊 Moyenne Cache Hit: 0.001ms

💾 Test Utilisation Mémoire
  10 utilisateurs: 30 entrées, remplissage en 31.97ms
  50 utilisateurs: 150 entrées, remplissage en 159.48ms
  100 utilisateurs: 300 entrées, remplissage en 319.67ms
  200 utilisateurs: 600 entrées, remplissage en 638.22ms

============================================================
📋 RAPPORT DE PERFORMANCE DU CACHE SIMPLIFIÉ
============================================================

🚀 AMÉLIORATION GLOBALE: 100.0%
   Cache Miss:  3.188ms
   Cache Hit:   0.001ms
   Gain:        3.187ms
   Facteur:     2202.1x plus rapide

📊 STATISTIQUES DÉTAILLÉES:
   Cache Miss - Min: 3.175ms, Max: 3.207ms
   Cache Hit  - Min: 0.001ms, Max: 0.006ms

============================================================

=== TEST DE PERFORMANCE DU CACHE TRAJETS ===

1. Premier appel (DB) - Cache vide
[REDIS] Cache trajets mis à jour depuis result: trips_page:3cbc214d (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=10 total=11 refresh=False
   Temps DB: 0.550s
   Trajets récupérés: 10
   Total: 11

2. Deuxième appel (Cache local L1)
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=10 total=11
   Temps Cache L1: 0.000s
   Amélioration: 100.0%

3. Test cache Redis (L2) - Vider cache local
[TRIPS][REDIS HIT] page_index=0 trips=10 total=11
   Temps Cache Redis: 0.000s
   Amélioration vs DB: 99.9%

4. Test avec force_reload (bypass cache)
[REDIS] Cache trajets mis à jour depuis result: trips_page:3cbc214d (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=10 total=11 refresh=True
   Temps force_reload: 0.023s

5. Test pagination différente
[REDIS] Cache trajets mis à jour depuis result: trips_page:2c21585b (TTL: 300s)
[TRIPS][FETCH] page_index=1 trips=0 total=10 refresh=False
   Temps page 2 (DB): 0.020s
[TRIPS][LOCAL CACHE HIT] page_index=1 trips=0 total=10
   Temps page 2 (Cache): 0.000s

=== RÉSUMÉ DES PERFORMANCES ===
Base de données:     0.550s
Cache local (L1):    0.000s (100.0% plus rapide)
Cache Redis (L2):    0.000s (99.9% plus rapide)
Force reload:        0.023s

=== TEST CONVERSION DONNÉES ===

DÉBUT DU TEST COMPLET DU SYSTÈME DE CACHE
================================================================================

============================================================
=== TEST STATISTIQUES BASE DE DONNÉES ===
============================================================

Statistiques générales (temps: 0.144s):
   Utilisateurs totaux: 10
   Trajets totaux: 10

Statistiques avancées (temps: 0.035s):
   Distance moyenne: 96.40 km
   Distance totale: 964.00 km
   Places moyennes: 1.40
============================================================
=== TEST COMPLET DU CACHE TRAJETS ===
============================================================

1. Premier appel (DB) - Cache vide
[HTML_CACHE] Tout le cache HTML effacé
[REDIS] Cache trajets mis à jour depuis result: trips_page:3cbc214d (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=10 total=11 refresh=False
   Temps DB: 0.056s
   Trajets récupérés: 10
   Total: 0

2. Deuxième appel (Cache local L1)
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=10 total=11
   Temps Cache L1: 0.000s
   Amélioration: 99.8%

3. Test cache Redis (L2) - Vider cache local
[TRIPS][REDIS HIT] page_index=0 trips=10 total=11
   Temps Cache Redis: 0.001s
   Amélioration vs DB: 98.8%

4. Test avec force_reload (bypass cache)
[REDIS] Cache trajets mis à jour depuis result: trips_page:3cbc214d (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=10 total=11 refresh=True
   Temps force_reload: 0.024s

5. Test pagination différente
[REDIS] Cache trajets mis à jour depuis result: trips_page:2c21585b (TTL: 300s)
[TRIPS][FETCH] page_index=1 trips=0 total=10 refresh=False
   Temps page 2 (DB): 0.022s
[TRIPS][LOCAL CACHE HIT] page_index=1 trips=0 total=10
   Temps page 2 (Cache): 0.000s

=== RÉSUMÉ DES PERFORMANCES TRAJETS ===
Base de données:     0.056s
Cache local (L1):    0.000s (99.8% plus rapide)
Cache Redis (L2):    0.001s (98.8% plus rapide)
Force reload:        0.024s

============================================================
=== TEST COMPLET DU CACHE UTILISATEURS ===
============================================================

1. Premier appel (DB) - Cache vide
[DEBUG] get_users_page_data called with page_index=0, page_size=10, filters=None, force_reload=False
[LOCAL CACHE MISS] Pas de cache local pour page 0
[REDIS CACHE MISS] Pas de cache Redis pour page 0
[DEBUG] Chargement depuis la base de données...
[DEBUG] UserRepository.get_users_paginated called with page=0, page_size=10, filters=None
[DEBUG] Tentative de connexion à la base de données...
[DEBUG] Connexion à la base de données réussie
[DEBUG] Récupéré 10 utilisateurs, total=10
[DEBUG] Résultat DB: 10 utilisateurs, total=10
[REDIS] Cache mis à jour depuis result: users_page:3cbc214d (TTL: 300s)
   Temps DB: 0.037s
   Utilisateurs récupérés: 10
   Total: 10

2. Deuxième appel (Cache local)
[DEBUG] get_users_page_data called with page_index=0, page_size=10, filters=None, force_reload=False
[LOCAL CACHE HIT] Page 0 récupérée du cache local
   Temps Cache: 0.000s
   Amélioration: 99.9%

=== RÉSUMÉ DES PERFORMANCES UTILISATEURS ===
Base de données:     0.037s
Cache local:         0.000s (99.9% plus rapide)

============================================================
=== TEST GÉNÉRATION PANELS ===
============================================================

Test avec trajet: TRIP-1756507938116116-bk17O0BBAndQR7xxSZxDvAGkSWU2
Test avec utilisateur: Loic 

--- PANELS TRAJETS ---
1. Trip Details Panel
   Temps génération: 0.007s
2. Trip Stats Panel
   Temps génération: 0.006s

--- PANELS UTILISATEURS (avec cache HTML) ---
3. User Profile Panel (première génération)
   Temps génération: 0.000s
4. User Profile Panel (depuis cache HTML)
   Temps cache HTML: 0.001s
   Amélioration: -151.2%
5. User Stats Panel
[STATS] Chargement stats optimisées pour T8ZM7m0t... depuis DB
[STATS] 1.0 trajets conducteur, 0.0 trajets passager (optimisé)
   Temps génération: 0.040s
6. User Trips Panel
[TRIPS] Chargement trajets optimisés pour T8ZM7m0t... depuis DB
[TRIPS] 1 trajets récupérés (optimisé)
   Temps génération: 0.028s

=== RÉSUMÉ GÉNÉRATION PANELS ===
Trip Details:        0.007s
Trip Stats:          0.006s
User Profile (1ère): 0.000s
User Profile (cache):0.001s (-151.2% plus rapide)
User Stats:          0.040s
User Trips:          0.028s

============================================================
=== TEST ÉVICTION CACHE LRU ===
============================================================
[HTML_CACHE] Tout le cache HTML effacé

Taille initiale du cache: 0
Remplissage du cache avec plusieurs pages...
[REDIS] Cache trajets mis à jour depuis result: trips_page:5a3ede66 (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=5 total=6 refresh=False
   Page 0: Cache size = 1
[REDIS] Cache trajets mis à jour depuis result: trips_page:828007d3 (TTL: 300s)
[TRIPS][FETCH] page_index=1 trips=5 total=11 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:c19f0d7c (TTL: 300s)
[TRIPS][FETCH] page_index=2 trips=0 total=10 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:e0925d61 (TTL: 300s)
[TRIPS][FETCH] page_index=3 trips=0 total=15 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:ee956fe2 (TTL: 300s)
[TRIPS][FETCH] page_index=4 trips=0 total=20 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:615d91fe (TTL: 300s)
[TRIPS][FETCH] page_index=5 trips=0 total=25 refresh=False
   Page 5: Cache size = 6
[REDIS] Cache trajets mis à jour depuis result: trips_page:9c16a071 (TTL: 300s)
[TRIPS][FETCH] page_index=6 trips=0 total=30 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:0499efaa (TTL: 300s)
[TRIPS][FETCH] page_index=7 trips=0 total=35 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:ba772c84 (TTL: 300s)
[TRIPS][FETCH] page_index=8 trips=0 total=40 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:d70e41ae (TTL: 300s)
[TRIPS][FETCH] page_index=9 trips=0 total=45 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:e508d4a4 (TTL: 300s)
[TRIPS][FETCH] page_index=10 trips=0 total=50 refresh=False
   Page 10: Cache size = 11
[REDIS] Cache trajets mis à jour depuis result: trips_page:b3ef1614 (TTL: 300s)
[TRIPS][FETCH] page_index=11 trips=0 total=55 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:f67a1c77 (TTL: 300s)
[TRIPS][FETCH] page_index=12 trips=0 total=60 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:fcb6be0d (TTL: 300s)
[TRIPS][FETCH] page_index=13 trips=0 total=65 refresh=False
[REDIS] Cache trajets mis à jour depuis result: trips_page:909524f4 (TTL: 300s)
[TRIPS][FETCH] page_index=14 trips=0 total=70 refresh=False

Taille finale du cache: 15
Éviction LRU NON activée

================================================================================
=== RÉSUMÉ GLOBAL ===
================================================================================
Temps total du test: 0.831s
✅ Test complet terminé avec succès
================================================================================
