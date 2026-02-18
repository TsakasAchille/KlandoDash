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
| `role` | `admin`, `marketing` ou `support` |
| `display_name` | Nom complet recupere de Google |
| `avatar_url` | Photo de profil recuperee de Google |

## Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (App Router)
│   ├── src/marketing # Module de croissance (IA + Prospects + Radar)
│   ├── src/components/
│   ├── src/lib/      # Supabase + Auth + Queries
│   └── src/types/
├── database/          # SQL schemas, migrations
└── docs/              # Documentation technique
```

## Pages

- `/` - Accueil (KPI globaux)
- `/marketing` - **Cockpit Marketing** (Stratégie IA, Intelligence, Prospects, Radar, Mailing)
- `/trips` - Gestion des trajets (Liste des passagers, Détails détaillés, Filtres)
- `/users` - Gestion des utilisateurs (Recherche, Bio, Profil vérifié)
- `/map` - Carte Live "Voyager" (Trajets & Demandes clients, Filtres avancés)
- `/transactions` - Flux financier & revenus (Marge Klando, Cash Flow)
- `/stats` - Statistiques & KPI financiers (Admins uniquement)
- `/support` - Tickets support & système de mentions @user
- `/login` - Connexion Google OAuth

## Fonctionnalités Clés

- **Cockpit Marketing Unifié** : Un espace unique pour transformer les intentions du site en réservations réelles via l'IA et le Radar géographique.
- **Intelligence Artificielle (Gemini)** : Analyses stratégiques par thématique (Revenus, Conversion, Qualité) et aide à la rédaction de messages WhatsApp/Email.
- **Mailing IA** : Détection automatique des opportunités de relance et envoi via Resend.
- **Carte Live Premium** : Visualisation en temps réel des trajets et des demandes clients avec filtrage avancé et style "Voyager".
- **Matching Analytique** : Algorithme de correspondance géographique SQL (PostGIS) pour un filtrage ultra-précis.
- **Sécurité** : Accès restreint par liste blanche et rôles (Admin / Marketing / Support).
