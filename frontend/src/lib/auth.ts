import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import { createClient } from "@supabase/supabase-js";

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
  trustHost: true,

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

      // Initialisation du client admin uniquement ici pour éviter les erreurs Edge au build
      const supabaseAdmin = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!
      );

      // 1 requête: vérifie whitelist + récupère role
      const { data, error } = await supabaseAdmin
        .from("dash_authorized_users")
        .select("role, active")
        .eq("email", user.email)
        .single();

      if (error || !data?.active) {
        return false;
      }

      // Attache le rôle pour le jwt callback
      user.role = data.role;

      // Enrichir la table dash_authorized_users avec le nom et l'image
      if (user.name && user.image) {
        await supabaseAdmin
          .from("dash_authorized_users")
          .update({
            display_name: user.name,
            avatar_url: user.image,
          })
          .eq("email", user.email);
      }
      return true;
    },

    async jwt({ token, user }) {
      if (user?.role) {
        token.role = user.role;
      }
      return token;
    },

    async session({ session, token }) {
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
