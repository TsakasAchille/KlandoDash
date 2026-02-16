import { useState } from "react";
import { useSession } from "next-auth/react";
import { DashUser } from "@/lib/queries/admin";

export function useAdminActions(initialUsers: DashUser[]) {
  const { data: session } = useSession();
  const [users, setUsers] = useState(initialUsers);
  const [loading, setLoading] = useState<string | null>(null);

  const handleUpdateRole = async (email: string, newRoleValue: string) => {
    if (email === session?.user?.email) {
      alert("Vous ne pouvez pas modifier votre propre rôle");
      return;
    }

    setLoading(email);

    const res = await fetch("/api/admin/users", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, action: "role", role: newRoleValue }),
    });

    if (res.ok) {
      setUsers((prev) =>
        prev.map((u) =>
          u.email === email ? { ...u, role: newRoleValue } : u
        )
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

  const handleAdd = async (email: string, role: string) => {
    setLoading("add");

    const res = await fetch("/api/admin/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        role,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      setUsers((prev) => [data.user, ...prev]);
      setLoading(null);
      return { success: true };
    } else {
      const error = await res.json();
      setLoading(null);
      return { success: false, message: error.message || "Erreur lors de l'ajout" };
    }
  };

  return {
    users,
    loading,
    session,
    handleUpdateRole,
    handleToggleActive,
    handleDelete,
    handleAdd
  };
}
