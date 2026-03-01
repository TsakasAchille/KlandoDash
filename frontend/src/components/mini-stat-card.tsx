"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import React from "react";

interface MiniStatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: "blue" | "green" | "purple" | "red" | "gold";
  description?: string;
  onClick?: () => void;
  active?: boolean;
}

const themes = {
  blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
  green: "text-green-500 bg-green-500/10 border-green-500/20",
  purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
  red: "text-red-500 bg-red-500/10 border-red-500/20",
  gold: "text-klando-gold bg-klando-gold/10 border-klando-gold/20",
};

export function MiniStatCard({ title, value, icon: Icon, color, description, onClick, active }: MiniStatCardProps) {
  return (
    <Card 
      className={cn(
        "border-none shadow-sm bg-card/50 backdrop-blur-md overflow-hidden relative group min-w-[140px] flex-1 transition-all duration-300",
        onClick && "cursor-pointer hover:shadow-md hover:translate-y-[-2px]",
        active && "ring-2 ring-klando-gold bg-klando-gold/5"
      )}
      onClick={onClick}
    >
      {/* Glow Effect */}
      <div className={cn(
        "absolute -top-10 -right-10 w-32 h-32 blur-3xl opacity-20 transition-all duration-700 group-hover:opacity-40 z-0",
        themes[color].split(' ')[1]
      )} />
      
      <CardContent className="p-4 relative z-10 flex items-center justify-between gap-3">
        <div className="space-y-0.5 min-w-0">
          <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest truncate">{title}</p>
          <p className="text-xl font-black tracking-tight">{value}</p>
          {description && (
            <p className="text-[8px] font-bold text-muted-foreground/60 uppercase tracking-tighter truncate italic">
              {description}
            </p>
          )}
        </div>
        <div className={cn(
          "p-2.5 rounded-xl border transition-transform duration-500 group-hover:scale-110 shrink-0",
          themes[color]
        )}>
          <Icon className="w-4 h-4" />
        </div>
      </CardContent>
    </Card>
  );
}
