import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import { createClient, SupabaseClient } from "@supabase/supabase-js";

// Client Supabase admin créé de manière lazy pour éviter les erreurs Edge runtime
let supabaseAdmin: SupabaseClient | null = null;

function getSupabaseAdmin() {
  if (!supabaseAdmin) {
    supabaseAdmin = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );
  }
  return supabaseAdmin;
}

// Extension des types NextAuth pour inclure le rôle
declare module "next-auth" {
  interface User {
    role?: string;
  }
  interface Session {
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: string;
    };
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    role?: string;
  }
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  secret: process.env.NEXTAUTH_SECRET || process.env.AUTH_SECRET,

  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],

  pages: {
    signIn: "/login",
    error: "/login",
  },

  callbacks: {
    async signIn({ user }) {
      if (!user.email) return false;

      // 1 requête: vérifie whitelist + récupère role
      const { data, error } = await getSupabaseAdmin()
        .from("dash_authorized_users")
        .select("role, active")
        .eq("email", user.email)
        .single();

      if (error || !data?.active) {
        return false;
      }

      // Attache le rôle pour le jwt callback
      user.role = data.role;
      return true;
    },

    async jwt({ token, user }) {
      // Première connexion: prend le role de user
      // Connexions suivantes: garde le token existant
      if (user?.role) {
        token.role = user.role;
      }
      return token;
    },

    async session({ session, token }) {
      // Expose le rôle dans la session côté client
      if (session.user) {
        session.user.id = token.sub as string;
        session.user.role = token.role;
      }
      return session;
    },
  },

  session: {
    strategy: "jwt",
  },
});
