# Cockpit Marketing & Croissance

Ce module est le centre névralgique de la stratégie de croissance de Klando. Il combine analyse géographique, intelligence artificielle (Gemini) et outils de communication (Resend). 

Depuis la v1.6, le module est divisé en deux domaines distincts pour respecter les principes SOLID : la **Stratégie** (/marketing) et la **Production Éditoriale** (/editorial).

---

## 🧭 1. Stratégie Marketing (/marketing)

Ce sous-module se concentre sur l'analyse et la détection d'opportunités.

1.  **Radar** : Interface cartographique pour le matching manuel assisté par IA.
2.  **Intelligence** : Rapports d'analyse approfondis (Gemini) sur les revenus, la conversion et la qualité.
3.  **Observatoire** : Visualisation des flux de demande et zones de chaleur (Heatmaps).
4.  **Stratégie** : Recommandations IA immédiates basées sur le matching prospects/trajets.
5.  **Prospects** : Gestion des intentions de voyage collectées sur le site.

---

## ✍️ 2. Centre Éditorial (/editorial)

Ce sous-module gère la création de contenu, la planification et la collaboration interne.

1.  **Calendrier** : Interface interactive pour planifier les publications sociales et les mailings.
2.  **Social Media** : Générateur de contenu (TikTok, Instagram, X) avec aperçu et édition.
3.  **Mailing** : Système de rédaction de mailings avec capture de carte intégrée.
4.  **Collaboration** : Système de commentaires internes permettant aux utilisateurs du dashboard de discuter sur chaque contenu.
5.  **Médiathèque** : Gestion des visuels et assets associés aux campagnes.

---

## 🛠 Spécifications Techniques

### 1. Observatoire de la Demande
*   **Données** : Agrégation via la fonction SQL RPC `get_marketing_flow_stats`.
*   **Visualisation** : 
    *   **Flux** : Polylines Burgundy semi-transparentes avec épaisseur proportionnelle au volume.
    *   **Heatmap** : `CircleMarker` dorés dont le rayon varie selon la densité des points de départ.

### 2. Moteur de Mailing & Capture de Carte
*   **Workflow** : Scan IA -> Suggestion -> Brouillon -> Envoi.
*   **Capture Visuelle** : Utilisation de `html2canvas` pour prendre une photo du trajet dans le Radar.
*   **Stockage** : Bucket Supabase `marketing/screenshots/`.

### 3. Planification & Discussion
*   **Base de données** : 
    *   `dash_marketing_communications` : Posts et idées.
    *   `dash_marketing_emails` : Brouillons et historique mails.
    *   `dash_marketing_comments` : Discussion interne liée aux contenus.
*   **Status Workflow** : `NEW` (IA) -> `DRAFT` (Édité/Enregistré) -> `PUBLISHED`/`SENT` (Finalisé).

---

## 🏛 Architecture SOLID

Le module suit une structure modulaire stricte :

*   **Actions** : 
    *   `/app/marketing/actions/` : Intelligence, Mailing, Communication.
    *   `/app/editorial/actions.ts` : Commentaires et visuels.
*   **Composants** :
    *   `/app/marketing/components/tabs/` : Un fichier par onglet stratégique.
    *   `/app/editorial/components/` : Calendrier et modales de détails.
*   **Types** (`/app/marketing/types.ts`) : Contrat de données unique pour tout le domaine Marketing/Editorial.

## 🔒 Sécurité & Accès
*   Accès réservé aux rôles `admin` et `marketing`.
*   RLS activé sur toutes les tables `dash_marketing_*`.
*   Collaboration basée sur les profils de la table `dash_authorized_users`.
