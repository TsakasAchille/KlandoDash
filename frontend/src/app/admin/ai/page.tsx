import { Sparkles } from "lucide-react";
import { KlandoAIClient } from "./ai-client";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Yobé - Intelligence Opérationnelle",
};

export default function AIPage() {
  return (
    <div className="container mx-auto py-6 space-y-8 animate-in fade-in duration-700">
      <KlandoAIClient />
    </div>
  );
}
