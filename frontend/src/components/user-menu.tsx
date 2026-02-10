"use client";

import { useSession, signOut } from "next-auth/react";
import { LogOut } from "lucide-react";
import Image from "next/image";

export function UserMenu() {
  const { data: session } = useSession();

  if (!session?.user) return null;

  const { name, email, image, role } = session.user;
  const initials = name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const roleLabel = role === "admin" ? "Administrateur" : "Utilisateur";

  return (
    <div className="p-4 border-t border-border">
      <div className="flex items-center gap-3">
        {/* Avatar */}
        {image ? (
          <Image
            src={image}
            alt={name || "Avatar"}
            width={40}
            height={40}
            className="w-10 h-10 rounded-full"
          />
        ) : (
          <div className="w-10 h-10 rounded-full bg-klando-burgundy flex items-center justify-center text-white font-medium">
            {initials || "?"}
          </div>
        )}

        {/* Infos utilisateur */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate text-white">{name}</p>
          <p className="text-xs text-muted-foreground truncate">{email}</p>
        </div>
      </div>

      {/* Badge rôle + Déconnexion */}
      <div className="mt-3 flex items-center justify-between">
        <span
          className={`text-xs px-2 py-1 rounded-full ${
            role === "admin"
              ? "bg-klando-gold/20 text-klando-gold"
              : "bg-secondary text-muted-foreground"
          }`}
        >
          {roleLabel}
        </span>

        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="flex items-center gap-1 text-xs text-white hover:text-klando-gold transition-colors"
        >
          <LogOut className="w-3 h-3" />
          <span className="hidden sm:inline">Déconnexion</span>
          <span className="sm:hidden">Déco</span>
        </button>
      </div>
    </div>
  );
}
