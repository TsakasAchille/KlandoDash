# Architecture de l'Intelligence Artificielle (Klando AI)

Ce document décrit l'implémentation, le flux de données et la stratégie de l'IA au sein du module Marketing de KlandoDash.

## 1. Moteur d'IA : Google Gemini
Klando utilise l'API **Google Gemini** (via le SDK `@google/generative-ai`) pour le traitement du langage naturel et l'analyse stratégique.

### Modèles utilisés (Fallback Strategy)
1.  **gemini-2.0-flash** : Priorité haute (rapidité, coût réduit).
2.  **gemini-1.5-flash** : Stable.
3.  **gemini-1.5-pro** : Analyse complexe (Intelligence).

---

## 2. Spécialisation des Flux IA (Modularité Marketing)

L'IA n'est plus un bloc monolithique mais est divisée en 3 piliers dans le Cockpit Marketing :

### A. IA Opérationnelle (Onglet Stratégie)
*   **Approche Analytique d'abord** : Le scan ne déclenche plus l'IA systématiquement pour économiser les tokens.
*   **Scan SQL (PostGIS)** : Identifie les correspondances géographiques réelles via `find_matching_trips`.
*   **Action Cards** : Génère des cartes d'opportunités basées sur les données SQL. L'IA n'intervient qu'à la demande (Aide IA) pour générer le message final.

### B. IA Stratégique (Onglet Intelligence)
*   **Scan IA Global** : Analyse les statistiques de performance (Revenus, Conversion, Qualité).
*   **Rapports Markdown** : Génère des analyses de haut niveau avec des conseils actionnables.
*   **Mise à jour (Clean Refresh)** : Les nouveaux scans remplacent les anciens pour garantir la fraîcheur.

### C. IA Relationnelle (Onglet Mailing)
*   **Scan Opportunités Mail** : Détecte les prospects à convertir et les utilisateurs inactifs.
*   **Draft Generation** : Prépare des brouillons d'emails (Sujet + Corps) envoyables via Resend.

---

## 3. Sécurité et Visibilité des Données (Klando-Gemini)
L'IA fonctionne selon le principe du **"Besoin d'en connaître"** :
*   **Anonymisation** : Pas de numéros de téléphone ni d'emails réels dans les prompts.
*   **Contexte restreint** : Seules les données pertinentes (distances, horaires, ratings) sont envoyées.
*   **Détails** : Voir [docs/Klando-Gemini.md](./Klando-Gemini.md).

---

## 4. Flux de Travail Unifié (UX)

Le système suit une logique de progression pour l'utilisateur :
1.  **Stratégie (Inbox)** : On identifie l'opportunité (SQL).
2.  **Radar (Execution)** : On affine géographiquement, on utilise l'IA pour le message, on agit.
3.  **Prospects (Library)** : On consulte l'historique et les données brutes.

---

## 5. Intégration Technique
*   **ReactMarkdown** : Utilisé pour le rendu professionnel des rapports IA.
*   **Resend** : Service d'envoi pour le mailing marketing.
*   **SQL RPC** : `find_matching_trips` pour le calcul de proximité à haute performance.
