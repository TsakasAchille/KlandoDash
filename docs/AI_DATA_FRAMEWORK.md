# Framework de Données IA (Klando AI Data Framework)

Ce document définit les fonctions "dures" (Hard Functions) qui servent de fournisseurs de données à l'IA Gemini et cartographie quel contexte est disponible selon chaque module.

## 1. Les Fonctions Fournisseurs (Data Providers)

Ces fonctions sont les seules sources de vérité pour l'IA. Elles extraient et nettoient les données de Supabase avant l'envoi.

| Fonction | Source Supabase (Table / RPC) | Données fournies |
| :--- | :--- | :--- |
| `getDashboardStats()` | RPC `get_klando_stats_final` (Tables `trips`, `users`, `bookings`, `transactions`, `site_trip_requests`) | Chiffres clés, Revenus, Mix Conducteurs/Passagers, Top Routes. |
| `getSiteTripRequests()` | Table `site_trip_requests` | Intentions de voyage (Ville A -> Ville B, Date, Contact). |
| `getUsersContext()` | Table `users` | Segments d'utilisateurs (Actifs, Inactifs, Top Drivers). |
| `getMarketingMemories()`| Fichier local `MARKETING_MEMORIES.md` | Préférences de style et historique des retours admin. |

---

## 2. Cartographie des Contextes (Localisation)

L'IA n'a pas accès à toute la base de données d'un coup. Son contexte est "localisé" selon l'action demandée et les résultats sont stockés dans des tables spécifiques.

### A. IA Relationnelle (Mailing)
*   **Objectif** : Générer des emails de conversion.
*   **Input Context** :
    *   `prospects` (Top 10 demandes de la table `site_trip_requests`).
    *   `inactive_users` (Top 10 utilisateurs de la table `users`).
    *   `preferences` (Fichier `MARKETING_MEMORIES.md`).
*   **Stockage des résultats** : Table `dash_marketing_emails`.
*   **Source de données** : `mailing.ts` -> `generateMailingSuggestionsAction`.

### B. IA Social Media (Communication)
*   **Objectif** : Créer des posts TikTok/Insta/X.
*   **Input Context** :
    *   `stats` (Données issues de la RPC `get_klando_stats_final`).
    *   `pending_requests` (Données de la table `site_trip_requests`).
*   **Stockage des résultats** : Table `dash_marketing_communications`.
*   **Source de données** : `communication.ts` -> `generateCommIdeasAction`.

### C. IA Stratégique (Intelligence)
*   **Objectif** : Analyse de haut niveau et rapports.
*   **Input Context** :
    *   Objet complet `DashboardStats` (RPC final).
*   **Stockage des résultats** : Table `dash_marketing_insights`.
*   **Source de données** : `intelligence.ts` -> `runMarketingAIScanAction`.

---

## 3. Framework de Prompting (Injection)

Chaque appel à l'IA doit suivre cette structure de prompt pour garantir la cohérence :

```markdown
1. Rôle : "Tu es l'expert Marketing de Klando au Sénégal..."
2. Mémoire : [Injection de MARKETING_MEMORIES.md]
3. Données Locales : [Injection du contexte spécifique provenant des tables Supabase]
4. Contrainte : "Réponds en JSON STRICT avec le champ 'ai_reasoning'..."
```

---

## 4. Boucle d'Apprentissage (Learning Loop)

Lorsqu'un administrateur clique sur "Like" ou laisse un commentaire :
1. L'action `saveMailingFeedbackAction` est appelée.
2. La table `dash_marketing_emails` est mise à jour (colonnes `is_liked`, `admin_feedback`).
3. Le fichier `MARKETING_MEMORIES.md` est automatiquement enrichi avec le feedback.
4. Au prochain appel, le `Data Provider` de mémoire envoie les nouvelles consignes à l'IA.
