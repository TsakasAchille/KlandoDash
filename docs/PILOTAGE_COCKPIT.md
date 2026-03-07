# Cockpit Croissance & Marketing (Klando)

Ce document détaille le fonctionnement du Cockpit de Croissance, le centre névralgique de Klando pour lier l'analyse stratégique à l'acquisition opérationnelle.

## 1. Objectifs
Le Cockpit (situé dans `/admin/pilotage`) centralise les métriques de performance et la gestion des leads (Prospects) pour permettre des actions ciblées.

---

## 2. Indicateurs Clés (KPIs - Performance Stratégique)

### A. Acquisition & Activation
*   **Activation Passager (72h)** : % de nouveaux inscrits (30 derniers jours) ayant exprimé un besoin dans les 72h.
*   **Activation Conducteur (7j)** : % de nouveaux inscrits (30 derniers jours) ayant publié leur premier trajet sous 7 jours.

### B. Rétention (Repeat Rate)
*   **Repeat Passager (W1)** : % de passagers actifs en S-2 ayant réservé en S-1.
*   **Repeat Conducteur (W1)** : % de conducteurs actifs en S-2 ayant republié en S-1.

### C. Liquidité (Match Rate)
*   **Match Rate Demande** : % de demandes (Site + Facebook) ayant trouvé une offre.
*   **Match Rate Offre** : % de trajets publiés ayant reçu au moins une réservation.

### D. Efficacité Opérationnelle
*   **Fill Rate Moyen (Realized)** : % d'occupation des sièges (trajets `COMPLETED`).
*   **Exécution** : % de trajets publiés arrivant à terme sans annulation.

---

## 3. Carte des Flux (Corridors Focus)
La carte intégrée au Cockpit utilise le mode `flowMode`. 
*   **Objectif** : Visualisation macro-économique.
*   **Fonctionnement** : Au lieu d'afficher chaque trajet individuellement, les trajets sont agrégés par axe (ex: Dakar ↔ Mbour).
*   **Rendu** : Plus le volume de trajets est important, plus la ligne tracée sur la carte est épaisse. Le clic sur une route dans le tableau sélectionne et zoome sur ce corridor.

---

## 4. Gestion des Prospects
L'ancien module Marketing est désormais intégré ici.
*   **Sources** : Affiche les demandes provenant de la Landing Page (`SITE`) et celles injectées par l'Agent IA depuis les réseaux sociaux (`FACEBOOK`).
*   **Actions** : Permet de lancer le Radar PostGIS pour trouver un conducteur à moins de 15km pour chaque prospect.

---

## 5. Accès & Rôles
*   `admin` : Accès complet.
*   `marketing` : Accès complet pour analyse et matching.
*   `ia` : Accès **bloqué** (l'IA passe par le `/ia` Data Hub).
