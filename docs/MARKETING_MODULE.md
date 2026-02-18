# Cockpit Marketing & Croissance

Ce module est le centre névralgique de la stratégie de croissance de Klando. Il combine analyse géographique, intelligence artificielle (Gemini) et outils de communication (Resend).

## 🧭 Structure du Cockpit

Le module est divisé en 6 piliers stratégiques :

1.  **Stratégie** : Recommandations IA immédiates basées sur le matching prospects/trajets.
2.  **Communication** : Générateur de contenu social (TikTok, Instagram, X) et angles d'attaque marketing.
3.  **Intelligence** : Rapports d'analyse approfondis sur les revenus, la conversion et la qualité de service.
4.  **Prospects** : Gestion des intentions de voyage avec filtrage intelligent (Uniquement à venir).
5.  **Radar** : Interface cartographique pour le matching manuel assisté par IA.
6.  **Observatoire** : Visualisation des flux de demande et zones de chaleur (Heatmaps).

---

## 🛠 Spécifications Techniques

### 1. Observatoire de la Demande
*   **Données** : Agrégation via la fonction SQL RPC `get_marketing_flow_stats`.
*   **Visualisation** : 
    *   **Flux** : Polylines Burgundy semi-transparentes avec épaisseur proportionnelle au volume.
    *   **Heatmap** : `CircleMarker` dorés dont le rayon varie selon la densité des points de départ.
    *   **Carte** : Utilisation du layer `Voyager` (CartoDB) pour un contraste optimal en mode clair.

### 2. Moteur de Mailing & Capture de Carte
*   **Workflow** : Scan IA -> Suggestion -> Brouillon -> Envoi.
*   **Capture Visuelle** : Utilisation de `html2canvas` pour prendre une photo du trajet dans le Radar.
*   **Stockage** : Les captures sont stockées dans le bucket Supabase `marketing/screenshots/`.
*   **Insertion** : Lien public inséré dynamiquement via la colonne `image_url` de la table `dash_marketing_emails`.

### 3. Agence de Communication IA
*   **Plateformes** : TikTok (Punchy), Instagram (Esthétique), X (Informatif).
*   **Logic** : Adapte le ton et les emojis selon la cible.
*   **Base de données** : Table `dash_marketing_communications`.

---

## 🏛 Architecture SOLID

Le module suit une structure modulaire stricte :

*   **Actions** (`/app/marketing/actions/`) : Séparées par domaine (`communication.ts`, `intelligence.ts`, `mailing.ts`).
*   **Composants** (`/app/marketing/components/`) :
    *   `tabs/` : Un fichier par onglet fonctionnel.
    *   `shared/` : Composants transverses (Carte de flux, Modales).
*   **Types** (`/app/marketing/types.ts`) : Contrat de données unique pour tout le module.

## 🔒 Sécurité & Accès
*   Accès réservé aux rôles `admin` et `marketing`.
*   RLS activé sur toutes les tables `dash_marketing_*`.
*   Anonymisation des données envoyées à Gemini (uniquement les noms de villes et les volumes, pas de données personnelles sensibles).
