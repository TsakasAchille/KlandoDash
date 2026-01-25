# Plan d'Intégration - Authentification Google

> **Date:** 2025-01-25
> **Branche:** `feature/auth-google`
> **Objectif:** Protéger le dashboard avec authentification Google (comptes individuels)

---

## 1. Analyse de l'Ancien Système (Streamlit)

### Architecture précédente

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Google OAuth  │────▶│    Firebase     │────▶│    Streamlit    │
│   (Login)       │     │   Admin SDK     │     │   Session       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ dash_authorized │
                        │     _users      │
                        └─────────────────┘
```

### Variables d'environnement utilisées

```env
# Google OAuth
GOOGLE_CLIENT_ID=VOTRE_CLIENT_ID
GOOGLE_CLIENT_SECRET=VOTRE_CLIENT_SECRET

# Emails autorisés (hardcodés)
AUTHORIZED_EMAILS=admin@example.com,user@example.com

# Admin credentials (fallback)
ADMIN_USERNAME=admin
APP_PASSWORD=VOTRE_MOT_DE_PASSE

# Session
SECRET_KEY=VOTRE_SECRET_KEY
```

### Table `dash_authorized_users` (existante)

```sql
CREATE TABLE dash_authorized_users (
    email VARCHAR(255) PRIMARY KEY,
    active BOOLEAN DEFAULT true NOT NULL,
    role VARCHAR(50) DEFAULT 'user',        -- 'admin' | 'user'
    added_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    added_by VARCHAR(255),
    notes TEXT
);

-- Index existant
CREATE INDEX idx_dash_authorized_users_email ON dash_authorized_users(email);
```

### Données actuelles

```sql
-- Vérifier les utilisateurs autorisés existants
SELECT * FROM dash_authorized_users;
```

---

## 2. Nouvelle Architecture (Next.js)

### Stack recommandée

| Composant | Choix | Raison |
|-----------|-------|--------|
| Auth Provider | **NextAuth.js v5** | Standard Next.js, support Google natif |
| Session | JWT | Stateless, scalable |
| Base de données | Supabase | Déjà en place |
| Middleware | Next.js Middleware | Protection des routes |

### Flux d'authentification

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Click    │────▶│  Google OAuth   │────▶│   NextAuth.js   │
│   "Se connecter"│     │  Consent Screen │     │   Callback      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Vérifier email  │
                                               │ dash_authorized │
                                               │     _users      │
                                               └─────────────────┘
                                                        │
                                          ┌─────────────┴─────────────┐
                                          ▼                           ▼
                                   ┌─────────────┐             ┌─────────────┐
                                   │   Autorisé  │             │ Non autorisé│
                                   │ → Dashboard │             │ → Erreur    │
                                   └─────────────┘             └─────────────┘
```

---

## 3. Implémentation NextAuth.js

### 3.1 Installation

```bash
cd frontend
npm install next-auth@beta
```

### 3.2 Configuration Google Cloud Console

1. Aller sur https://console.cloud.google.com/apis/credentials
2. Projet existant: `klando-d3cb3` (ou créer nouveau)
3. Créer/Modifier OAuth 2.0 Client ID:
   - Type: Web application
   - Origines autorisées:
     - `http://localhost:3000`
     - `https://dashboard.klando-sn.com` (production)
   - URIs de redirection:
     - `http://localhost:3000/api/auth/callback/google`
     - `https://dashboard.klando-sn.com/api/auth/callback/google`

### 3.3 Variables d'environnement

```env
# frontend/.env.local

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=VOTRE_NEXTAUTH_SECRET

# Google OAuth
GOOGLE_CLIENT_ID=VOTRE_CLIENT_ID
GOOGLE_CLIENT_SECRET=VOTRE_CLIENT_SECRET

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://votre-projet.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=VOTRE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=VOTRE_SERVICE_ROLE_KEY
```

### 3.4 Structure des fichiers

```
frontend/src/
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts          # NextAuth handler
│   ├── login/
│   │   └── page.tsx                  # Page de connexion
│   └── layout.tsx                    # Wrap avec SessionProvider
│
├── lib/
│   ├── auth.ts                       # Configuration NextAuth
│   └── queries/
│       └── auth.ts                   # Queries dash_authorized_users
│
├── components/
│   ├── auth/
│   │   ├── login-button.tsx          # Bouton Google
│   │   ├── logout-button.tsx         # Bouton déconnexion
│   │   └── user-menu.tsx             # Menu utilisateur (header)
│   └── sidebar.tsx                   # Ajouter user info
│
└── middleware.ts                     # Protection des routes
```

---

## 4. Code d'implémentation

### 4.1 Configuration NextAuth (`lib/auth.ts`)

```typescript
import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import { createServerClient } from "./supabase";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    // Vérifier si l'utilisateur est autorisé
    async signIn({ user }) {
      if (!user.email) return false;

      const supabase = createServerClient();
      const { data, error } = await supabase
        .from("dash_authorized_users")
        .select("email, active, role")
        .eq("email", user.email.toLowerCase())
        .eq("active", true)
        .single();

      if (error || !data) {
        console.log(`Accès refusé pour: ${user.email}`);
        return false; // Bloque la connexion
      }

      return true; // Autorise la connexion
    },

    // Enrichir le token avec le rôle
    async jwt({ token, user }) {
      if (user?.email) {
        const supabase = createServerClient();
        const { data } = await supabase
          .from("dash_authorized_users")
          .select("role")
          .eq("email", user.email.toLowerCase())
          .single();

        token.role = data?.role || "user";
      }
      return token;
    },

    // Exposer le rôle dans la session
    async session({ session, token }) {
      if (session.user) {
        session.user.role = token.role as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login", // Redirect vers login en cas d'erreur
  },
});
```

### 4.2 Route Handler (`app/api/auth/[...nextauth]/route.ts`)

```typescript
import { handlers } from "@/lib/auth";

export const { GET, POST } = handlers;
```

### 4.3 Middleware (`middleware.ts`)

```typescript
import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { nextUrl, auth: session } = req;

  // Routes publiques
  const publicRoutes = ["/login", "/api/auth"];
  const isPublicRoute = publicRoutes.some((route) =>
    nextUrl.pathname.startsWith(route)
  );

  if (isPublicRoute) {
    return NextResponse.next();
  }

  // Pas de session = redirect vers login
  if (!session) {
    return NextResponse.redirect(new URL("/login", nextUrl));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

### 4.4 Page de Login (`app/login/page.tsx`)

```typescript
import { signIn } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-klando-dark">
      <div className="text-center space-y-8">
        {/* Logo */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-klando-gold">KlandoDash</h1>
          <p className="text-muted-foreground">
            Tableau de bord d'administration
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-card border rounded-lg p-8 space-y-6 w-80">
          <h2 className="text-xl font-semibold">Connexion</h2>
          <p className="text-sm text-muted-foreground">
            Connectez-vous avec votre compte Google autorisé
          </p>

          <form
            action={async () => {
              "use server";
              await signIn("google");
            }}
          >
            <Button
              type="submit"
              className="w-full bg-white text-black hover:bg-gray-100"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                {/* Google Icon SVG */}
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continuer avec Google
            </Button>
          </form>

          <p className="text-xs text-muted-foreground">
            Accès réservé aux administrateurs Klando
          </p>
        </div>
      </div>
    </div>
  );
}
```

### 4.5 Layout avec SessionProvider (`app/layout.tsx`)

```typescript
import { SessionProvider } from "next-auth/react";
import { auth } from "@/lib/auth";

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  return (
    <html lang="fr">
      <body>
        <SessionProvider session={session}>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}
```

### 4.6 Menu Utilisateur (`components/auth/user-menu.tsx`)

```typescript
"use client";

import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User, LogOut } from "lucide-react";

export function UserMenu() {
  const { data: session } = useSession();

  if (!session?.user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center gap-2">
          {session.user.image ? (
            <img
              src={session.user.image}
              alt=""
              className="w-8 h-8 rounded-full"
            />
          ) : (
            <User className="w-5 h-5" />
          )}
          <span className="text-sm">{session.user.name}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem disabled className="text-xs text-muted-foreground">
          {session.user.email}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => signOut()}>
          <LogOut className="w-4 h-4 mr-2" />
          Déconnexion
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

---

## 5. Queries pour `dash_authorized_users`

### 5.1 Fichier queries (`lib/queries/auth.ts`)

```typescript
import { createServerClient } from "../supabase";

export interface AuthorizedUser {
  email: string;
  active: boolean;
  role: "admin" | "user";
  added_at: string;
  updated_at: string;
  added_by: string | null;
  notes: string | null;
}

// Vérifier si un email est autorisé
export async function isEmailAuthorized(email: string): Promise<boolean> {
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("dash_authorized_users")
    .select("email")
    .eq("email", email.toLowerCase())
    .eq("active", true)
    .single();

  return !error && !!data;
}

// Récupérer les infos d'un utilisateur autorisé
export async function getAuthorizedUser(
  email: string
): Promise<AuthorizedUser | null> {
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("dash_authorized_users")
    .select("*")
    .eq("email", email.toLowerCase())
    .single();

  if (error) return null;
  return data;
}

// Liste des utilisateurs autorisés (admin only)
export async function getAuthorizedUsers(): Promise<AuthorizedUser[]> {
  const supabase = createServerClient();
  const { data, error } = await supabase
    .from("dash_authorized_users")
    .select("*")
    .order("added_at", { ascending: false });

  if (error) return [];
  return data;
}

// Ajouter un utilisateur autorisé (admin only)
export async function addAuthorizedUser(
  email: string,
  role: "admin" | "user" = "user",
  addedBy: string,
  notes?: string
): Promise<{ success: boolean; error?: string }> {
  const supabase = createServerClient();
  const { error } = await supabase.from("dash_authorized_users").insert({
    email: email.toLowerCase(),
    role,
    added_by: addedBy,
    notes,
  });

  if (error) return { success: false, error: error.message };
  return { success: true };
}

// Désactiver un utilisateur
export async function deactivateUser(
  email: string
): Promise<{ success: boolean; error?: string }> {
  const supabase = createServerClient();
  const { error } = await supabase
    .from("dash_authorized_users")
    .update({ active: false, updated_at: new Date().toISOString() })
    .eq("email", email.toLowerCase());

  if (error) return { success: false, error: error.message };
  return { success: true };
}
```

---

## 6. Intégration dans la Sidebar

### Modification de `sidebar.tsx`

```typescript
"use client";

import { useSession } from "next-auth/react";
import { UserMenu } from "@/components/auth/user-menu";
// ... autres imports

export function Sidebar() {
  const { data: session } = useSession();
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-klando-dark border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-klando-gold">KlandoDash</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        {/* ... menu items existants ... */}
      </nav>

      {/* User section (footer) */}
      <div className="p-4 border-t border-border">
        <UserMenu />
      </div>
    </aside>
  );
}
```

---

## 7. Gestion des erreurs d'autorisation

### Page d'erreur personnalisée (`app/login/page.tsx`)

```typescript
import { useSearchParams } from "next/navigation";

export default function LoginPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  return (
    <div>
      {/* ... */}

      {error === "AccessDenied" && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-sm text-red-400">
          <p className="font-medium">Accès refusé</p>
          <p>
            Votre compte Google n'est pas autorisé à accéder au dashboard.
            Contactez un administrateur.
          </p>
        </div>
      )}

      {/* ... login button ... */}
    </div>
  );
}
```

---

## 8. Étapes d'implémentation

### Phase 1: Setup NextAuth

1. [ ] Installer `next-auth@beta`
2. [ ] Créer `lib/auth.ts`
3. [ ] Créer `app/api/auth/[...nextauth]/route.ts`
4. [ ] Ajouter variables d'environnement

### Phase 2: Page de Login

1. [ ] Créer `app/login/page.tsx`
2. [ ] Style avec Klando theme
3. [ ] Gestion erreur "AccessDenied"

### Phase 3: Protection des routes

1. [ ] Créer `middleware.ts`
2. [ ] Définir routes publiques vs protégées
3. [ ] Tester redirections

### Phase 4: UI utilisateur

1. [ ] Créer `UserMenu` component
2. [ ] Intégrer dans Sidebar
3. [ ] Afficher nom/photo utilisateur

### Phase 5: Gestion des autorisés (optionnel)

1. [ ] Page admin `/settings/users`
2. [ ] CRUD sur `dash_authorized_users`
3. [ ] Réservé aux rôle `admin`

---

## 9. Sécurité

### Points d'attention

| Aspect | Mesure |
|--------|--------|
| CSRF | NextAuth gère automatiquement |
| Session hijacking | JWT signé avec NEXTAUTH_SECRET |
| Brute force | Google gère le rate limiting |
| Email spoofing | Vérifié par Google OAuth |
| Autorisation | Double check: OAuth + table DB |

### Bonnes pratiques

1. **Ne jamais** stocker le service_role_key côté client
2. **Toujours** vérifier l'email dans `dash_authorized_users`
3. **Logger** les tentatives de connexion refusées
4. **Auditer** régulièrement la table des utilisateurs autorisés

---

## 10. Variables d'environnement finales

```env
# frontend/.env.local

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=VOTRE_NEXTAUTH_SECRET

# Google OAuth
GOOGLE_CLIENT_ID=VOTRE_CLIENT_ID
GOOGLE_CLIENT_SECRET=VOTRE_CLIENT_SECRET

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://votre-projet.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=VOTRE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=VOTRE_SERVICE_ROLE_KEY
```

---

## 11. Checklist finale

### Configuration
- [ ] Google Cloud Console: URIs de redirection configurés
- [ ] Variables d'environnement ajoutées
- [ ] `dash_authorized_users` contient les emails autorisés

### Code
- [ ] `next-auth@beta` installé
- [ ] `lib/auth.ts` configuré
- [ ] API route NextAuth créée
- [ ] Middleware de protection actif
- [ ] Page de login stylée
- [ ] UserMenu dans la sidebar

### Tests
- [ ] Login avec email autorisé → accès OK
- [ ] Login avec email non autorisé → "Accès refusé"
- [ ] Accès direct à `/trips` sans session → redirect `/login`
- [ ] Déconnexion → retour page login
- [ ] Session persiste après refresh

---

*Document de planification pour l'authentification Google sur KlandoDash Next.js.*
