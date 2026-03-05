A) Activation (séparer Passager / Conducteur)
Activation passager : % de nouveaux inscrits qui effectuent une recherche / demande dans les 72h.
Formule : (# nouveaux users ayant au moins 1 event “search” ou “request” dans 72h) / (# nouveaux users)
Formule littérale (opérations posées) :
Activation passager (%) = (Nombre de nouveaux users ayant au moins 1 event “search” OU “request” dans les 72h ÷ Nombre total de nouveaux users) × 100
Activation conducteur : % de nouveaux inscrits qui publient un trajet dans les 7 jours.
Formule : (# nouveaux drivers ayant au moins 1 “trip published” dans 7j) / (# nouveaux drivers)
Formule littérale (opérations posées) :
Activation conducteur (%) = (Nombre de nouveaux drivers ayant au moins 1 event “trip_published” dans les 7 jours ÷ Nombre total de nouveaux drivers) × 100
B) Repeat rate (réflexe / rétention)
Repeat passager (W1/W4) : % de passagers actifs qui refont au moins 1 action (recherche/réservation) la semaine suivante / sur 30 jours.
Formule : (# passagers actifs semaine N et aussi actifs semaine N+1) / (# passagers actifs semaine N)
Formule littérale (opérations posées) :
Repeat passager W1 (%) = (Passagers actifs en semaine N ET actifs en semaine N+1 ÷ Passagers actifs en semaine N) × 100
Repeat conducteur (W1/W4) : % de conducteurs qui republient au moins 1 trajet dans les 7 jours / 30 jours.
Formule : (# drivers ayant publié en semaine N et republient en N+1) / (# drivers ayant publié en semaine N)
Formule littérale (opérations posées) :
Repeat conducteur W1 (%) = (Drivers ayant publié en semaine N ET ayant publié en semaine N+1 ÷ Drivers ayant publié en semaine N) × 100
C) Fill rate (taux de remplissage)
Taux de remplissage par trajet : sièges réservés / sièges proposés.
Formule littérale (opérations posées) :
Fill rate (%) = (Somme des sièges réservés ÷ Somme des sièges proposés) × 100
Bonus à afficher (très actionnable) : % trajets à 0 réservation
Formule littérale (opérations posées) :
% trajets à 0 réservation = (Nombre de trajets publiés avec 0 réservation ÷ Nombre total de trajets publiés) × 100
D) TTFV (Time To First Value)
TTFV passager : délai médian entre inscription et 1ère recherche/demande/réservation.
Formule : median(timestamp_first_search_or_booking − signup_timestamp)
Formule littérale (opérations posées) :
TTFV passager = médiane( timestamp_first_search_or_booking − signup_timestamp )
TTFV conducteur : délai médian entre inscription et 1ère publication.
Formule : median(timestamp_first_trip_published − signup_timestamp)
Formule littérale (opérations posées) :
TTFV conducteur = médiane( timestamp_first_trip_published − signup_timestamp )
À afficher aussi : % qui atteignent la “first value” en 24h / 72h.
Formule littérale (opérations posées) :
% first value en 24h = (Nombre de users avec (first_value_timestamp − signup_timestamp) ≤ 24h ÷ Nombre total de nouveaux users) × 100
% first value en 72h = (Nombre de users avec (first_value_timestamp − signup_timestamp) ≤ 72h ÷ Nombre total de nouveaux users) × 100
E) Match rate (liquidité)
Match rate côté demande : % de demandes/recherches qui trouvent au moins 1 trajet pertinent (ou une réponse conducteur).
Formule : (# demandes avec ≥1 résultat / réponse) / (# demandes totales)
Formule littérale (opérations posées) :
Match rate demande (%) = (Nombre de demandes avec au moins 1 résultat OU au moins 1 réponse conducteur ÷ Nombre total de demandes) × 100
Match rate côté offre : % de trajets publiés qui reçoivent au moins 1 réservation.
Formule : (# trajets avec ≥1 réservation) / (# trajets publiés)
Formule littérale (opérations posées) :
Match rate offre (%) = (Nombre de trajets publiés avec au moins 1 réservation ÷ Nombre total de trajets publiés) × 100
F) Response time conducteur (confiance)
Temps de réponse conducteur : délai médian entre demande/réservation et première réponse/acceptation conducteur.
Formule : median(timestamp_driver_response − timestamp_request)
Formule littérale (opérations posées) :
Temps de réponse conducteur = médiane( timestamp_driver_response − timestamp_request )
Objectif early stage : < 10 minutes sur corridors prioritaires
G) Realized / Published (exécution)
Trajets réalisés / trajets publiés : mesure la conversion “publication → exécution”.
Formule : (# trajets réalisés) / (# trajets publiés)
Formule littérale (opérations posées) :
Realized / Published (%) = (Nombre de trajets réalisés ÷ Nombre de trajets publiés) × 100
H) Cancellation (qualité)
Taux d’annulation (à séparer si possible) :
conducteur : (# annulations conducteur) / (# réservations confirmées)
passager : (# annulations passager) / (# réservations confirmées)
Formules littérales (opérations posées) :
Taux d’annulation conducteur (%) = (Nombre d’annulations conducteur ÷ Nombre de réservations confirmées) × 100
Taux d’annulation passager (%) = (Nombre d’annulations passager ÷ Nombre de réservations confirmées) × 100
Ajouter aussi si possible : no-show (si trackable).
2) Bloc “Pilotage commute par corridor” (vue quotidienne)
Pour chaque corridor commute prioritaire, je veux une table/jauge avec :
Trajets publiés / jour
Réservations / jour
Trajets réalisés / jour
Temps de réponse conducteur (médian)  objectif < 10 min au début
% demandes sans match objectif : baisse semaine après semaine
Formule : (# demandes sans résultat/aucune offre) / (# demandes totales)
Formule littérale (opérations posées) :
% demandes sans match = (Nombre de demandes sans résultat / aucune offre ÷ Nombre total de demandes) × 100
Idéalement : filtre par corridor, jour, plage horaire (matin/soir), et un onglet “commute” vs “interurbain”.
3) Notes d’implémentation 
Pour calculer proprement, il nous faut des events minimum :
signup
search / request
trip_published (avec seats_offered, corridor)
booking_created / booking_confirmed (avec seats_booked)
driver_response / accept
trip_completed (réalisé)
cancellation (qui annule + timestamp)
structure de page “Pilotage” (layout) : Overview => Liquidity =>  Corridors commute =>  Funnel =>  Qualité.




