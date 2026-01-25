"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Home, Car, Users, BarChart3, MessageSquare } from "lucide-react";

const navItems = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/trips", label: "Trajets", icon: Car },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/stats", label: "Statistiques", icon: BarChart3 },
  { href: "/chats", label: "Messages", icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

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
        </ul>
      </nav>
    </aside>
  );
}
