"use client";

import { useState } from "react";
import { DashUser } from "@/lib/queries/admin";
import { Button } from "@/components/ui/button";
import { UserPlus } from "lucide-react";
import { useAdminActions } from "./hooks/useAdminActions";
import { AddUserForm } from "./components/AddUserForm";
import { AdminUserTable } from "./components/AdminUserTable";

interface Props {
  users: DashUser[];
}

export function AdminPageClient({ users: initialUsers }: Props) {
  const [showAddForm, setShowAddForm] = useState(false);
  const {
    users,
    loading,
    session,
    handleUpdateRole,
    handleToggleActive,
    handleDelete,
    handleAdd
  } = useAdminActions(initialUsers);

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
        <AddUserForm 
          onAdd={handleAdd}
          onCancel={() => setShowAddForm(false)}
          isLoading={loading === "add"}
        />
      )}

      {/* Table des utilisateurs */}
      <AdminUserTable 
        users={users}
        currentUserEmail={session?.user?.email}
        loading={loading}
        onUpdateRole={handleUpdateRole}
        onToggleActive={handleToggleActive}
        onDelete={handleDelete}
      />
    </div>
  );
}
