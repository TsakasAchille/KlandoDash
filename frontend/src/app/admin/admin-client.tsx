"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { DashUser } from "@/lib/queries/admin";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  UserPlus,
  Shield,
  User,
  Check,
  X,
  Trash2,
  Loader2,
} from "lucide-react";

interface Props {
  users: DashUser[];
}

export function AdminPageClient({ users: initialUsers }: Props) {
  const { data: session } = useSession();
  const router = useRouter();
  const [users, setUsers] = useState(initialUsers);
  const [loading, setLoading] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"admin" | "user">("user");

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleToggleRole = async (email: string, currentRole: string) => {
    if (email === session?.user?.email) {
      alert("Vous ne pouvez pas modifier votre propre rôle");
      return;
    }

    setLoading(email);
    const newRole = currentRole === "admin" ? "user" : "admin";

    const res = await fetch("/api/admin/users", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, action: "role", role: newRole }),
    });

    if (res.ok) {
      setUsers((prev) =>
        prev.map((u) => (u.email === email ? { ...u, role: newRole } : u))
      );
    }
    setLoading(null);
  };

  const handleToggleActive = async (email: string, currentActive: boolean) => {
    if (email === session?.user?.email) {
      alert("Vous ne pouvez pas vous désactiver vous-même");
      return;
    }

    setLoading(email);

    const res = await fetch("/api/admin/users", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, action: "active", active: !currentActive }),
    });

    if (res.ok) {
      setUsers((prev) =>
        prev.map((u) =>
          u.email === email ? { ...u, active: !currentActive } : u
        )
      );
    }
    setLoading(null);
  };

  const handleDelete = async (email: string) => {
    if (email === session?.user?.email) {
      alert("Vous ne pouvez pas vous supprimer vous-même");
      return;
    }

    if (!confirm(`Supprimer ${email} de la liste des utilisateurs autorisés ?`)) {
      return;
    }

    setLoading(email);

    const res = await fetch("/api/admin/users", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (res.ok) {
      setUsers((prev) => prev.filter((u) => u.email !== email));
    }
    setLoading(null);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim()) return;

    setLoading("add");

    const res = await fetch("/api/admin/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: newEmail.trim().toLowerCase(),
        role: newRole,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      setUsers((prev) => [data.user, ...prev]);
      setNewEmail("");
      setNewRole("user");
      setShowAddForm(false);
    } else {
      const error = await res.json();
      alert(error.message || "Erreur lors de l'ajout");
    }
    setLoading(null);
  };

  return (
    <div className="space-y-4">
      {/* Bouton ajouter */}
      <div className="flex justify-end">
        <Button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-klando-gold hover:bg-klando-gold/90 text-black"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Ajouter un utilisateur
        </Button>
      </div>

      {/* Formulaire d'ajout */}
      {showAddForm && (
        <form
          onSubmit={handleAdd}
          className="flex items-center gap-4 p-4 bg-secondary rounded-lg"
        >
          <Input
            type="email"
            placeholder="email@example.com"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            className="flex-1"
            required
          />
          <select
            value={newRole}
            onChange={(e) => setNewRole(e.target.value as "admin" | "user")}
            className="px-3 py-2 rounded-md bg-background border border-border"
          >
            <option value="user">Utilisateur</option>
            <option value="admin">Administrateur</option>
          </select>
          <Button
            type="submit"
            disabled={loading === "add"}
            className="bg-green-600 hover:bg-green-700"
          >
            {loading === "add" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              "Ajouter"
            )}
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={() => setShowAddForm(false)}
          >
            Annuler
          </Button>
        </form>
      )}

      {/* Table des utilisateurs */}
      <div className="rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-secondary/50">
              <TableHead>Email</TableHead>
              <TableHead>Rôle</TableHead>
              <TableHead>Statut</TableHead>
              <TableHead>Ajouté le</TableHead>
              <TableHead>Ajouté par</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow
                key={user.email}
                className={
                  user.email === session?.user?.email
                    ? "bg-klando-gold/5"
                    : undefined
                }
              >
                <TableCell className="font-medium">
                  {user.email}
                  {user.email === session?.user?.email && (
                    <span className="ml-2 text-xs text-muted-foreground">
                      (vous)
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                      user.role === "admin"
                        ? "bg-klando-gold/20 text-klando-gold"
                        : "bg-secondary text-muted-foreground"
                    }`}
                  >
                    {user.role === "admin" ? (
                      <Shield className="w-3 h-3" />
                    ) : (
                      <User className="w-3 h-3" />
                    )}
                    {user.role === "admin" ? "Admin" : "User"}
                  </span>
                </TableCell>
                <TableCell>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                      user.active
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {user.active ? (
                      <>
                        <Check className="w-3 h-3" /> Actif
                      </>
                    ) : (
                      <>
                        <X className="w-3 h-3" /> Inactif
                      </>
                    )}
                  </span>
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {formatDate(user.added_at)}
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {user.added_by || "-"}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    {/* Toggle role */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleRole(user.email, user.role)}
                      disabled={
                        loading === user.email ||
                        user.email === session?.user?.email
                      }
                      title={
                        user.role === "admin"
                          ? "Rétrograder en User"
                          : "Promouvoir en Admin"
                      }
                    >
                      {loading === user.email ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : user.role === "admin" ? (
                        <User className="w-4 h-4" />
                      ) : (
                        <Shield className="w-4 h-4" />
                      )}
                    </Button>

                    {/* Toggle active */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        handleToggleActive(user.email, user.active)
                      }
                      disabled={
                        loading === user.email ||
                        user.email === session?.user?.email
                      }
                      title={user.active ? "Désactiver" : "Activer"}
                    >
                      {user.active ? (
                        <X className="w-4 h-4 text-red-400" />
                      ) : (
                        <Check className="w-4 h-4 text-green-400" />
                      )}
                    </Button>

                    {/* Delete */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(user.email)}
                      disabled={
                        loading === user.email ||
                        user.email === session?.user?.email
                      }
                      title="Supprimer"
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
