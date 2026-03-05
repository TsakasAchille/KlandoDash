"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { ArrowRight, Car, Users, AlertCircle, TrendingUp, LucideIcon, RefreshCw, Info, HelpCircle, Target, CheckCircle2 } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

const icons = {
  Car, Users, AlertCircle, TrendingUp, RefreshCw, Target, CheckCircle2
};

interface KPICardProps {
  title: string;
  value: string | number;
  icon: keyof typeof icons | React.ElementType;
  color: "blue" | "purple" | "red" | "green" | "orange";
  href?: string;
  description?: string;
  info?: {
    formula: string;
    tables: string[];
    details: string;
  };
}

export function KPICard({ 
  title, 
  value, 
  icon, 
  color, 
  href,
  description,
  info
}: KPICardProps) {
  const themes = {
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
    red: "text-red-500 bg-red-500/10 border-red-500/20",
    green: "text-green-500 bg-green-500/10 border-green-500/20",
    orange: "text-orange-500 bg-orange-500/10 border-orange-500/20",
  };

  const selectedTheme = themes[color] || themes.blue;

  const IconComponent = typeof icon === 'string' 
    ? (icons[icon as keyof typeof icons] as LucideIcon)
    : icon as LucideIcon;

  const content = (
    <Card className={cn(
        "h-full border-none shadow-sm hover:shadow-xl transition-all duration-500 bg-card/80 backdrop-blur-md overflow-hidden relative",
        href && "group"
    )}>
      <div className={cn(
        "absolute -top-12 -right-12 w-40 h-40 blur-3xl opacity-[0.15] transition-all duration-1000 z-0",
        href && "group-hover:opacity-30 group-hover:scale-150",
        selectedTheme.split(' ')[1]
      )} />
      
      <CardContent className="pt-6 relative z-10">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">{title}</p>
              {info && (
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="text-muted-foreground/40 hover:text-klando-gold transition-colors" onClick={(e) => e.stopPropagation()}>
                      <HelpCircle className="w-3 h-3" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80 p-4 bg-slate-900/95 border-white/10 backdrop-blur-xl text-white shadow-2xl z-50">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 border-b border-white/5 pb-2">
                        <Info className="w-4 h-4 text-klando-gold" />
                        <h4 className="font-black text-xs uppercase tracking-widest text-klando-gold">Méthode de Calcul</h4>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Formule :</p>
                        <code className="block p-2 bg-black/40 rounded text-[11px] font-mono text-indigo-300 leading-relaxed">
                          {info.formula}
                        </code>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Tables & Colonnes :</p>
                        <div className="flex flex-wrap gap-1.5">
                          {info.tables.map((table, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-white/5 rounded text-[10px] font-black text-white/80 border border-white/5 uppercase">
                              {table}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Logique :</p>
                        <p className="text-[11px] leading-relaxed text-slate-300 italic">
                          {info.details}
                        </p>
                      </div>
                    </div>
                  </PopoverContent>
                </Popover>
              )}
            </div>
            <h3 className={cn(
                "text-3xl font-black tracking-tighter transition-colors",
                href && "group-hover:text-klando-gold"
            )}>{value}</h3>
            {description && <p className="text-[10px] text-muted-foreground font-semibold italic">{description}</p>}
          </div>
          <div className={cn(
            "p-3.5 rounded-2xl border transition-all duration-500",
            href && "group-hover:rotate-12 group-hover:shadow-lg",
            selectedTheme
          )}>
            {IconComponent && <IconComponent className="w-6 h-6" />}
          </div>
        </div>
        {href && (
          <div className="mt-6 flex items-center text-[10px] font-black text-klando-gold opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
            GÉRER LE MODULE <ArrowRight className="ml-1.5 w-3 h-3" />
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link href={href} className="block">
        {content}
      </Link>
    );
  }

  return content;
}
