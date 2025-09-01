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

