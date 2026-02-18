# Stratégie d'Accès aux Données - Klando Gemini

Ce document définit les données de la base de données (Supabase) auxquelles l'IA Gemini devrait avoir accès pour fournir des recommandations marketing et opérationnelles de haute précision.

## 1. Principes Fondamentaux
*   **Sécurité** : Aucune donnée sensible (mot de passe, pièce d'identité brute, numéro de téléphone complet) n'est envoyée à l'IA.
*   **Contexte** : L'IA ne reçoit que les données pertinentes au "bloc d'action" en cours de traitement.
*   **Anonymisation** : Utilisation d'UID techniques au lieu de noms réels si nécessaire.

## 2. Données Actuellement Accessibles
*   **Prospects (site_trip_requests)** : Villes de départ/arrivée, date souhaitée, coordonnées GPS calculées.
*   **Trajets (trips)** : Horaires, places disponibles, itinéraire (polyline), distances par rapport au client.

## 3. Données "Cibles" pour une IA Augmentée (Futur)

Pour améliorer les recommandations, Gemini devrait pouvoir analyser les tables suivantes :

### A. Fiabilité & Qualité (Table `users`)
*   **Rating & Rating Count** : Pour prioriser les chauffeurs les mieux notés dans les recommandations "Traction".
*   **Statut de Validation** : Proposer en priorité des chauffeurs dont les documents sont `is_driver_doc_validated`.
*   **Ancienneté** : "Ce chauffeur est sur Klando depuis 2 ans avec 50 trajets sans accroc."

### B. Historique de Succès (Table `bookings`)
*   **Taux de Conversion** : Savoir quels types de trajets (ex: Dakar -> Thiès le vendredi soir) sont les plus souvent réservés.
*   **Annulations** : Identifier les chauffeurs ou passagers qui annulent souvent pour ajuster le score de confiance.

### C. Contexte Financier (Table `transactions`)
*   **Pouvoir d'achat** : Analyser le montant moyen des transactions pour suggérer des prix "passagers" optimaux.
*   **Récurrence** : Identifier les clients fidèles qui méritent un message marketing personnalisé ("Client VIP").

### D. Support & Satisfaction (Table `support_tickets`)
*   **Problématiques récurrentes** : Si un prospect a ouvert 3 tickets pour des problèmes de retard, l'IA peut adapter son message : "Nous avons sélectionné pour vous notre chauffeur le plus ponctuel."

## 4. Exemple de Prompt "Augmenté" (Vision)

> "Analyse ce prospect pour un trajet Dakar -> Saint-Louis. 
> Le chauffeur TRIP-123 est à 2km. 
> **Contexte additionnel :** Ce chauffeur a un rating de 4.9/5 sur 20 trajets. Il n'a jamais annulé. Le prospect est un client fidèle (10 transactions réussies).
> **Mission :** Rédige un message qui met en avant la fiabilité exceptionnelle du chauffeur pour rassurer ce client fidèle."

## 5. Matrice de Visibilité IA

| Table | Colonnes Visibles par l'IA | Raison |
| :--- | :--- | :--- |
| `users` | rating, rating_count, gender, role | Qualité du matching |
| `trips` | departure_schedule, seats_available, price | Disponibilité réelle |
| `bookings` | status, created_at | Analyse des tendances |
| `transactions` | amount, status | Profilage marketing (VIP) |
| `site_requests` | origin_city, destination_city, notes | Besoins clients |

---
*Dernière mise à jour : 18 Février 2026*
