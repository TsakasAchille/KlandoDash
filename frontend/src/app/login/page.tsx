"use client";

import { signIn } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { Logo } from "@/components/logo";

function LoginContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  const callbackUrl = searchParams.get("callbackUrl") || "/";

  return (
    <div className="min-h-screen flex items-center justify-center bg-klando-dark px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Logo / Titre */}
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <Logo size="xlarge" />
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tighter text-white">Klando Dash</h1>
          <p className="mt-2 text-sm text-muted-foreground font-medium">
            Tableau de bord administration v1.4.0
          </p>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-xl text-center text-sm font-bold animate-in fade-in zoom-in duration-300">
            {error === "AccessDenied" ? (
              <>
                <p>Accès refusé</p>
                <p className="text-[10px] opacity-80 mt-1 uppercase tracking-wider">
                  Votre email n&apos;est pas dans la liste autorisée.
                </p>
              </>
            ) : (
              <p>Erreur de connexion : {error}</p>
            )}
          </div>
        )}

        {/* Carte de connexion */}
        <div className="bg-card/50 backdrop-blur-xl border border-white/5 rounded-[2rem] p-8 space-y-8 shadow-2xl">
          <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-white uppercase tracking-tight">Connexion</h2>
            <p className="text-xs text-muted-foreground font-medium italic">
              Réservé aux administrateurs Klando
            </p>
          </div>

          {/* Bouton Google */}
          <button
            onClick={() => signIn("google", { callbackUrl })}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-white text-black font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-klando-gold transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-white/5"
          >
            <GoogleIcon />
            Continuer avec Google
          </button>
        </div>

        {/* Footer */}
        <div className="text-center space-y-4">
          <p className="text-[9px] font-black uppercase tracking-[0.2em] text-muted-foreground/40">
            Sécurité renforcée par NextAuth & Supabase
          </p>
        </div>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24">
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
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex flex-col items-center justify-center bg-klando-dark space-y-4">
          <div className="w-12 h-12 border-4 border-klando-gold border-t-transparent rounded-full animate-spin"></div>
          <div className="text-[10px] font-black uppercase tracking-widest text-klando-gold">Chargement sécurisé...</div>
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
