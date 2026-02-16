import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { ArrowRight, LucideIcon } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color: "blue" | "purple" | "red" | "green";
  href: string;
  description?: string;
}

export function KPICard({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  href,
  description
}: KPICardProps) {
  const themes = {
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
    red: "text-red-500 bg-red-500/10 border-red-500/20",
    green: "text-green-500 bg-green-500/10 border-green-500/20",
  };

  return (
    <Link href={href} className="block group">
      <Card className="h-full border-none shadow-sm hover:shadow-xl transition-all duration-500 bg-card/80 backdrop-blur-md overflow-hidden relative">
        <div className={cn(
          "absolute -top-12 -right-12 w-40 h-40 blur-3xl opacity-[0.15] transition-all duration-1000 group-hover:opacity-30 group-hover:scale-150 z-0",
          themes[color].split(' ')[1]
        )} />
        
        <CardContent className="pt-6 relative z-10">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">{title}</p>
              <h3 className="text-3xl font-black tracking-tighter group-hover:text-klando-gold transition-colors">{value}</h3>
              {description && <p className="text-[10px] text-muted-foreground font-semibold italic">{description}</p>}
            </div>
            <div className={cn(
              "p-3.5 rounded-2xl border transition-all duration-500 group-hover:rotate-12 group-hover:shadow-lg",
              themes[color]
            )}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-6 flex items-center text-[10px] font-black text-klando-gold opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
            GÉRER LE MODULE <ArrowRight className="ml-1.5 w-3 h-3" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
