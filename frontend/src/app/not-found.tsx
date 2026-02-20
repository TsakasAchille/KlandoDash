import Link from "next/link";
import { Home, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-6 px-4 text-center">
      <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mb-2">
        <AlertCircle className="w-10 h-10 text-red-500" />
      </div>
      
      <div className="space-y-2">
        <h1 className="text-4xl font-black uppercase tracking-tighter text-foreground">404</h1>
        <h2 className="text-xl font-bold uppercase tracking-tight text-muted-foreground">Page Introuvable</h2>
        <p className="text-sm text-muted-foreground max-w-xs mx-auto">
          Désolé, la page que vous recherchez n&apos;existe pas ou a été déplacée.
        </p>
      </div>

      <Link href="/">
        <Button className="bg-klando-gold hover:bg-klando-gold/90 text-klando-dark font-black rounded-2xl px-8 h-12 gap-2 shadow-lg shadow-klando-gold/10">
          <Home className="w-4 h-4" />
          Retour à l&apos;accueil
        </Button>
      </Link>
    </div>
  );
}
