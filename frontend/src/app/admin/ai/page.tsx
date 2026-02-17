import { Sparkles } from "lucide-react";
import { KlandoAIClient } from "./ai-client";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Yobé - Intelligence Opérationnelle",
};

export default function AIPage() {
  return (
    <div className="container mx-auto py-6 space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-klando-gold animate-pulse" />
            Yobé
          </h1>
          <p className="text-muted-foreground mt-1 text-sm font-medium italic">
            Ton centre d&apos;intelligence opérationnelle.
          </p>
        </div>
      </div>

      <KlandoAIClient />
    </div>
  );
}
