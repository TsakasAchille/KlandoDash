"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import { cn } from "@/lib/utils";
import { Home, Car, Users, BarChart3, MessageSquare, Map, LifeBuoy, Shield } from "lucide-react";
import { UserMenu } from "@/components/user-menu";

const navItems = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/trips", label: "Trajets", icon: Car },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/map", label: "Carte", icon: Map },
  { href: "/stats", label: "Statistiques", icon: BarChart3 },
  { href: "/chats", label: "Messages", icon: MessageSquare },
];

const adminItems = [
  { href: "/support", label: "Support", icon: LifeBuoy },
  { href: "/admin", label: "Administration", icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const isAdmin = session?.user?.role === "admin";

  return (
    <aside className="w-64 bg-klando-dark border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-klando-gold">KlandoDash</h1>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                    isActive
                      ? "bg-klando-burgundy text-white"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </Link>
              </li>
            );
          })}

          {/* Section Admin - visible uniquement pour les admins */}
          {isAdmin && (
            <>
              <li className="pt-4 pb-2">
                <span className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Admin
                </span>
              </li>
              {adminItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                        isActive
                          ? "bg-klando-burgundy text-white"
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </>
          )}
        </ul>
      </nav>
      <UserMenu />
    </aside>
  );
}
