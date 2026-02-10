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
    <div className="min-h-screen flex items-center justify-center bg-klando-dark">
      <div className="w-full max-w-md p-8 space-y-8">
        {/* Logo / Titre */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Logo size="xlarge" />
          </div>
          <p className="mt-2 text-muted-foreground">
            Tableau de bord administrateur
          </p>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="bg-destructive/20 border border-destructive text-destructive-foreground px-4 py-3 rounded-lg text-center">
            {error === "AccessDenied" ? (
              <>
                <p className="font-semibold">Accès refusé</p>
                <p className="text-sm mt-1">
                  Votre adresse email n&apos;est pas autorisée à accéder au
                  dashboard.
                </p>
              </>
            ) : (
              <p>Une erreur est survenue lors de la connexion.</p>
            )}
          </div>
        )}

        {/* Carte de connexion */}
        <div className="bg-card border border-border rounded-lg p-6 space-y-6">
          <div className="text-center">
            <h2 className="text-xl font-semibold">Connexion</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Connectez-vous avec votre compte Google autorisé
            </p>
          </div>

          {/* Bouton Google */}
          <button
            onClick={() => signIn("google", { callbackUrl })}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white text-gray-800 font-medium rounded-lg hover:bg-gray-100 transition-colors"
          >
            <GoogleIcon />
            Continuer avec Google
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground">
          Seuls les utilisateurs autorisés peuvent accéder au dashboard.
        </p>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-klando-dark">
          <div className="text-klando-gold">Chargement...</div>
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
