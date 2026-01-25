import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      <h1 className="text-4xl font-bold text-klando-gold mb-4">KlandoDash</h1>
      <p className="text-muted-foreground mb-8">
        Bienvenue sur le tableau de bord Klando
      </p>
      <Link
        href="/trips"
        className="px-6 py-3 bg-klando-burgundy text-white rounded-lg hover:bg-klando-burgundy/90 transition"
      >
        Voir les trajets
      </Link>
    </div>
  );
}
