# KlandoDash

Tableau de bord administrateur pour [Klando](https://klando-sn.com), service de covoiturage au Senegal.

## Stack technique

- **Frontend**: Next.js 14 + Shadcn/ui + TailwindCSS
- **Base de donnees**: Supabase (PostgreSQL)
- **Authentification**: NextAuth.js v5 + Google OAuth

## Installation

```bash
cd frontend
npm install
```

## Configuration

Creer un fichier `.env.local` a la racine avec :

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_role_key>
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>

# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<openssl rand -base64 32>
AUTH_SECRET=<meme valeur>

# Google OAuth
GOOGLE_CLIENT_ID=<depuis Google Cloud Console>
GOOGLE_CLIENT_SECRET=<depuis Google Cloud Console>
```

Creer un symlink dans `frontend/` :
```bash
ln -sf ../.env.local frontend/.env.local
```

## Lancement

```bash
cd frontend
npm run dev
```

Ouvrir http://localhost:3000

## Authentification

Seuls les utilisateurs presents dans la table `dash_authorized_users` (Supabase) avec `active=true` peuvent acceder au dashboard. Les profils sont automatiquement enrichis lors de la premiere connexion Google.

| Colonne | Description |
|---------|-------------|
| `email` | Email Google (PK) |
| `active` | Autorisation active |
| `role` | `admin`, `support` ou `user` |
| `display_name` | Nom complet recupere de Google |
| `avatar_url` | Photo de profil recuperee de Google |

## Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (App Router)
│   ├── src/components/
│   ├── src/lib/      # Supabase + Auth + Queries
│   └── src/types/
├── database/          # SQL schemas, migrations
└── CLAUDE.md          # Documentation technique
```

## Pages

- `/` - Accueil (KPI globaux)
- `/trips` - Gestion des trajets (Filtres, Recherche, Détails)
- `/users` - Gestion des utilisateurs (Recherche, Bio, Profil vérifié)
- `/map` - Carte des trajets (Temps réel, Filtres conducteurs)
- `/transactions` - Flux financier & revenus (Marge Klando, Cash Flow)
- `/stats` - Statistiques & KPI financiers
- `/support` - Tickets support & système de mentions @user
- `/site-requests` - Gestion des intentions de voyage issues du site vitrine
- `/login` - Connexion Google OAuth

## Fonctionnalités Clés

- **Filtres Avancés** : Recherche par nom, email, ville ou ID sur les tableaux principaux.
- **Expérience Fluide** : Transition entre les pages avec **Skeleton Loading**.
- **Responsive Design** : Interface optimisée pour mobile et tablettes.
- **Sécurité** : Accès restreint par liste blanche et rôles (Admin / Support).
