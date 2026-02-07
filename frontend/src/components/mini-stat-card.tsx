import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MiniStatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: "blue" | "green" | "purple" | "red" | "gold";
}

const themes = {
  blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
  green: "text-green-500 bg-green-500/10 border-green-500/20",
  purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
  red: "text-red-500 bg-red-500/10 border-red-500/20",
  gold: "text-klando-gold bg-klando-gold/10 border-klando-gold/20",
};

export function MiniStatCard({ title, value, icon: Icon, color }: MiniStatCardProps) {
  return (
    <Card className="border-none shadow-sm bg-card/50 backdrop-blur-md overflow-hidden relative group min-w-[140px] flex-1">
      {/* Glow Effect (instead of sharp circle) */}
      <div className={cn(
        "absolute -top-10 -right-10 w-32 h-32 blur-3xl opacity-20 transition-all duration-700 group-hover:opacity-40 z-0",
        themes[color].split(' ')[1]
      )} />
      
      <CardContent className="p-4 relative z-10 flex items-center justify-between gap-3">
        <div className="space-y-0.5">
          <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">{title}</p>
          <p className="text-xl font-black tracking-tight">{value}</p>
        </div>
        <div className={cn(
          "p-2.5 rounded-xl border transition-transform duration-500 group-hover:scale-110",
          themes[color]
        )}>
          <Icon className="w-4 h-4" />
        </div>
      </CardContent>
    </Card>
  );
}