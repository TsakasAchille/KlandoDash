# Cockpit de Pilotage Growth (Klando)

Ce document détaille le fonctionnement du Cockpit de Pilotage, l'outil stratégique de Klando pour mesurer la croissance et l'efficacité opérationnelle selon les indicateurs du cahier des charges.

## 1. Objectifs
Le Cockpit centralise les métriques de performance pour permettre aux administrateurs de prendre des décisions basées sur la donnée (Data-Driven Decisions). Contrairement aux statistiques classiques, le Pilotage se concentre sur les **ratios de conversion** et la **liquidité**.

---

## 2. Indicateurs Clés (KPIs)

### A. Acquisition & Activation
*   **Activation Passager (72h)** : % de nouveaux inscrits (30 derniers jours) ayant effectué au moins une recherche ou demande dans les 72h suivant leur inscription.
    *   *Tables :* `users`, `site_trip_requests`.
*   **Activation Conducteur (7j)** : % de nouveaux inscrits (30 derniers jours) ayant publié leur premier trajet dans les 7 jours suivant leur inscription.
    *   *Tables :* `users`, `trips`.

### B. Rétention (Repeat Rate)
*   **Repeat Passager (W1)** : % de passagers actifs en semaine N-2 ayant effectué au moins une réservation en semaine N-1.
    *   *Tables :* `bookings`.
*   **Repeat Conducteur (W1)** : % de conducteurs actifs en semaine N-2 ayant publié au moins un trajet en semaine N-1.
    *   *Tables :* `trips`.

### C. Liquidité (Match Rate)
*   **Match Rate Demande** : % de demandes provenant du site vitrine (`site_trip_requests`) ayant trouvé au moins une offre correspondante.
    *   *Tables :* `site_trip_requests`, `site_trip_request_matches`.
*   **Match Rate Offre** : % de trajets publiés ayant reçu au moins une réservation.
    *   *Tables :* `trips`.

### D. Efficacité Opérationnelle
*   **Fill Rate Moyen (Realized)** : % moyen d'occupation des sièges uniquement pour les trajets terminés (`COMPLETED`).
    *   *Formule :* `AVG(seats_booked / total_seats)`.
*   **Exécution (Realized / Published)** : % de trajets publiés qui arrivent à terme sans être annulés.
    *   *Tables :* `trips`.

---

## 3. Analyse par Corridor Focus
Le Cockpit affiche les 10 corridors les plus actifs des 30 derniers jours avec :
*   Volume de trajets.
*   Total des réservations.
*   Taux de remplissage moyen (Fill Rate).
*   **Statut de performance** : "Optimal" (> 50% de remplissage) ou "À booster" (≤ 50%).

---

## 4. Implémentation Technique

### Backend (SQL RPC)
La fonction `get_pilotage_metrics()` calcule l'ensemble des indicateurs en une seule passe :
```sql
-- Migration 056_create_pilotage_metrics.sql
SELECT public.get_pilotage_metrics();
```

### Frontend (Next.js)
*   **Route** : `/admin/pilotage`.
*   **Composant** : `PilotagePage` utilisant le composant `KPICard`.
*   **Interactivité** : Chaque carte possède un bouton **Info** (Popover) expliquant la formule exacte et les tables SQL utilisées.

---

## 5. Accès & Rôles
L'accès est restreint aux rôles suivants :
*   `admin` : Accès complet.
*   `marketing` : Accès complet pour analyse de croissance.
*   `ia` : Accès **bloqué** (le Cockpit est réservé aux humains pour le moment).
