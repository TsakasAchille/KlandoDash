import { getUsers } from "@/lib/queries/users";
import { ValidationClient } from "./validation-client";
import { ShieldCheck } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function ValidationPage() {
  const { users: pendingUsers } = await getUsers(1, 100, {
    verified: "pending"
  });

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-klando-gold" />
            Validation Conducteurs
          </h1>
          <p className="text-muted-foreground mt-1">
            Vérifiez et approuvez les documents d&apos;identité et permis de conduire.
          </p>
        </div>
      </div>

      <ValidationClient pendingUsers={pendingUsers} />
    </div>
  );
}
