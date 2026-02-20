"use client";

import { useSession, signOut } from "next-auth/react";
import { LogOut } from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

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
    <div className="space-y-4">
      {/* Profil Card */}
      <div className="relative group/user">
        <div className="absolute -inset-2 bg-gradient-to-r from-klando-gold/10 to-transparent rounded-2xl opacity-0 group-hover/user:opacity-100 transition-all duration-500" />
        
        <div className="relative flex items-center gap-3 p-2">
          {/* Avatar avec Ring Glow */}
          <div className="relative shrink-0">
            <div className={cn(
              "w-11 h-11 rounded-xl flex items-center justify-center overflow-hidden border-2 transition-all duration-500",
              role === "admin" ? "border-klando-gold/30 group-hover/user:border-klando-gold shadow-lg shadow-klando-gold/5" : "border-white/10 group-hover/user:border-white/30"
            )}>
              {image ? (
                <Image
                  src={image}
                  alt={name || "Avatar"}
                  fill
                  className="object-cover transition-transform duration-700 group-hover/user:scale-110"
                  sizes="44px"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-klando-burgundy to-[#9b2c3d] flex items-center justify-center text-white text-xs font-black">
                  {initials || "?"}
                </div>
              )}
            </div>
            {/* Status Indicator */}
            <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-[#0f172a] rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
          </div>

          {/* User Infos */}
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-black text-white truncate tracking-tight group-hover/user:text-klando-gold transition-colors">
              {name}
            </p>
            <div className="flex items-center gap-1.5">
              <span className={cn(
                "text-[9px] font-black uppercase tracking-[0.1em] px-1.5 py-0.5 rounded-md",
                role === "admin" ? "bg-klando-gold/10 text-klando-gold" : "bg-white/5 text-slate-400"
              )}>
                {roleLabel}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between px-2">
        <div className="flex flex-col">
          <p className="text-[10px] font-bold text-slate-400 truncate max-w-[120px]">
            {email}
          </p>
        </div>

        <button
          onClick={() => signOut({ callbackUrl: "/login" })}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.05] border border-white/10 text-slate-200 hover:text-red-400 hover:bg-red-500/10 hover:border-red-500/20 transition-all duration-300 group/logout"
          title="Déconnexion"
        >
          <span className="text-[10px] font-black uppercase tracking-widest hidden lg:inline">Quitter</span>
          <LogOut className="w-3.5 h-3.5 transition-transform group-hover/logout:translate-x-0.5" />
        </button>
      </div>
    </div>
  );
}
