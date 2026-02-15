import { Sparkles } from "lucide-react";
import { KlandoAIClient } from "./ai-client";

export const metadata = {
  title: "Klando AI - Assistant Intelligent",
};

export default function AIPage() {
  return (
    <div className="container mx-auto py-6 space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-klando-gold animate-pulse" />
            Klando AI
          </h1>
          <p className="text-muted-foreground mt-1 text-sm font-medium italic">
            Ton assistant intelligent alimenté par Gemini 1.5 Flash.
          </p>
        </div>
      </div>

      <KlandoAIClient />
    </div>
  );
}
