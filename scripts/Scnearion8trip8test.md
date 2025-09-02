python scripts/test_trips_performance.py 
🕐 [IMPORTS START] Début des imports à 01:39:39
[REDIS] Connexion établie: localhost:6379
🕐 [IMPORT] TripsCacheService chargé en 0.687s
🕐 [IMPORT] TripRepository chargé en 9.425s
🕐 [IMPORT] render_custom_trips_table chargé en 9.437s
🕐 [IMPORT] Config chargé en 9.437s
🕐 [IMPORTS END] Tous les imports terminés en 9.437s
🕐 [SCRIPT START] Lancement du script à 01:39:48
🕐 [INIT] Initialisation terminée après 0.000s
🕐 [T+0.000s] Initialisation du script de test
🚀 Script de test de performance - Page Trajets
Reproduit le fonctionnement de Dash pour identifier les latences
🕐 [T+0.000s] (+0.000s) Connexions et imports terminés
🕐 [T+0.000s] (+0.000s) Démarrage des tests de performance
🧪 DÉMARRAGE DES TESTS DE PERFORMANCE
============================================================
🕐 [T+0.000s] (+0.000s) Début Scénario 1

============================================================
🚀 SCÉNARIO 1: Chargement initial de la page
============================================================
🕐 [T+0.000s] (+0.000s) Début scénario 1 - Chargement initial
[TRIPS][REDIS HIT] page_index=0 trips=5 total=6
⏱️  get_trips_page_result: 0.000s
⏱️  extract_table_data: 0.000s
📊 Résultat: 5 trajets chargés sur 6 total
🎯 Premier trajet sélectionné: TRIP-1756507938116116-bk17O0BBAndQR7xxSZxDvAGkSWU2
⏱️  render_custom_trips_table: 0.001s
🕐 [T+0.002s] (+0.002s) Fin Scénario 1 - SUCCÈS
🕐 [T+0.002s] (+0.000s) Transition vers Scénario 2
🕐 [T+0.002s] (+0.000s) Début Scénario 2

============================================================
📄 SCÉNARIO 2: Changement de page (1 → 2)
============================================================
[REDIS] Cache trajets mis à jour depuis result: trips_page:828007d3 (TTL: 300s)
[TRIPS][FETCH] page_index=1 trips=5 total=11 refresh=False
⏱️  get_trips_page_result_page2: 0.140s
⏱️  extract_table_data_page2: 0.000s
📊 Page 2: 5 trajets chargés
⏱️  render_table_page2: 0.004s
🕐 [T+0.146s] (+0.144s) Fin Scénario 2 - SUCCÈS
🕐 [T+0.146s] (+0.000s) Transition vers Scénario 3
🕐 [T+0.146s] (+0.000s) Début Scénario 3

============================================================
🎯 SCÉNARIO 3: Sélection d'un trajet et chargement des panneaux
============================================================
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
🎯 Trajet sélectionné: TRIP-1756507938116116-bk17O0BBAndQR7xxSZxDvAGkSWU2
[TRIP_DETAILS][DB FETCH] Chargement TRIP-175... depuis la DB
Aucun passager trouvé pour ce trajet
[HTML_CACHE] Panneau details mis en cache pour trajet TRIP-175...
⏱️  get_trip_details_panel: 0.242s
[TRIP_STATS][DB FETCH] Chargement TRIP-175... depuis la DB
[HTML_CACHE] Panneau stats mis en cache pour trajet TRIP-175...
⏱️  get_trip_stats_panel: 0.516s
[TRIP_PASSENGERS][DB FETCH] Chargement TRIP-175... depuis la DB
[HTML_CACHE] Panneau passengers mis en cache pour trajet TRIP-175...
⏱️  get_trip_passengers_panel: 0.029s
🕐 [T+0.933s] (+0.788s) Fin Scénario 3 - SUCCÈS
🕐 [T+0.933s] (+0.000s) Transition vers Scénario 4
🕐 [T+0.933s] (+0.000s) Début Scénario 4

============================================================
🔍 SCÉNARIO 4: Application de filtres
============================================================
[REDIS] Cache trajets mis à jour depuis result: trips_page:3a26c82f (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=3 total=3 refresh=False
⏱️  get_trips_filtered: 0.170s
⏱️  extract_filtered_data: 0.000s
📊 Résultats filtrés: 3 trajets sur 3 total
🕐 [T+1.103s] (+0.170s) Fin Scénario 4 - SUCCÈS
🕐 [T+1.103s] (+0.000s) Transition vers Scénario 5
🕐 [T+1.103s] (+0.000s) Début Scénario 5

============================================================
💾 SCÉNARIO 5: Performance du cache (hit vs miss)
============================================================
[HTML_CACHE] Tout le cache HTML effacé
[REDIS] Cache trajets mis à jour depuis result: trips_page:5a3ede66 (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=5 total=6 refresh=True
⏱️  cache_miss_first_call: 0.024s
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
⏱️  cache_hit_second_call: 0.000s
🚀 Accélération du cache: 470.32x plus rapide
🕐 [T+1.128s] (+0.025s) Fin Scénario 5 - SUCCÈS
🕐 [T+1.128s] (+0.000s) Transition vers Scénario 6
🕐 [T+1.128s] (+0.000s) Début Scénario 6

============================================================
🗄️  SCÉNARIO 6: Connexion base de données au démarrage
============================================================
⏱️  postgres_connection_test: 0.021s
⏱️  redis_connection_test: 0.000s
⏱️  sqlite_fallback_test: 0.000s
[HTML_CACHE] Tout le cache HTML effacé
[REDIS] Cache trajets mis à jour depuis result: trips_page:5a3ede66 (TTL: 300s)
[TRIPS][FETCH] page_index=0 trips=5 total=6 refresh=True
📊 Cold start: 5 trajets, JSON: 0.000s, HTML: 0.003s
⏱️  cold_start_full_load: 0.033s
📊 Temps de connexion total: 0.022s
🕐 [T+1.183s] (+0.055s) Fin Scénario 6 - SUCCÈS
🕐 [T+1.183s] (+0.000s) Transition vers Scénario 7
🕐 [T+1.183s] (+0.000s) Début Scénario 7

============================================================
🔄 SCÉNARIO 7: Callbacks concurrents (simulation Dash réelle)
============================================================
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
[TRIPS][LOCAL CACHE HIT] page_index=0 trips=5 total=6
[TRIP_DETAILS][REDIS HIT] Détails récupérés pour TRIP-175...
[TRIP_PASSENGERS][DB FETCH] Chargement TRIP-175... depuis la DB
[TRIP_STATS][REDIS HIT] Stats récupérées pour TRIP-175...
[HTML_CACHE] Panneau stats mis en cache pour trajet TRIP-175...
Aucun passager trouvé pour ce trajet
[HTML_CACHE] Panneau passengers mis en cache pour trajet TRIP-175...
[HTML_CACHE] Panneau details mis en cache pour trajet TRIP-175...
🔄 4 callbacks exécutés en parallèle
⏱️  Durée totale concurrente: 0.509s
⏱️  Durée séquentielle équivalente: 0.504s
🚀 Gain de la concurrence: 0.99x plus rapide
🕐 [T+1.692s] (+0.509s) Fin Scénario 7 - SUCCÈS
🕐 [T+1.692s] (+0.000s) Génération du résumé des performances

============================================================
📈 RÉSUMÉ DES PERFORMANCES
============================================================
📊 get_trips_page_result:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 extract_table_data:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 render_custom_trips_table:
   Moyenne: 0.001s
   Min: 0.001s
   Max: 0.001s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 get_trips_page_result_page2:
   Moyenne: 0.140s
   Min: 0.140s
   Max: 0.140s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 extract_table_data_page2:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 render_table_page2:
   Moyenne: 0.004s
   Min: 0.004s
   Max: 0.004s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 get_trip_details_panel:
   Moyenne: 0.242s
   Min: 0.242s
   Max: 0.242s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 get_trip_stats_panel:
   Moyenne: 0.516s
   Min: 0.516s
   Max: 0.516s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 get_trip_passengers_panel:
   Moyenne: 0.029s
   Min: 0.029s
   Max: 0.029s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 get_trips_filtered:
   Moyenne: 0.170s
   Min: 0.170s
   Max: 0.170s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 extract_filtered_data:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 cache_miss_first_call:
   Moyenne: 0.024s
   Min: 0.024s
   Max: 0.024s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 cache_hit_second_call:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 postgres_connection_test:
   Moyenne: 0.021s
   Min: 0.021s
   Max: 0.021s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 redis_connection_test:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 sqlite_fallback_test:
   Moyenne: 0.000s
   Min: 0.000s
   Max: 0.000s
   Appels: 1
   ✅ RAPIDE: < 1s

📊 cold_start_full_load:
   Moyenne: 0.033s
   Min: 0.033s
   Max: 0.033s
   Appels: 1
   ✅ RAPIDE: < 1s

🕐 [T+1.693s] (+0.000s) Tests terminés

✅ Tests terminés: 7/7 scénarios réussis
