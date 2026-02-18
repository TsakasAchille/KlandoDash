"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2 } from "lucide-react";

interface AddUserFormProps {
  onAdd: (email: string, role: string) => Promise<{ success: boolean; message?: string }>;
  onCancel: () => void;
  isLoading: boolean;
}

export function AddUserForm({ onAdd, onCancel, isLoading }: AddUserFormProps) {
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState<"admin" | "user" | "support" | "marketing">("user");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail.trim()) return;

    const result = await onAdd(newEmail, newRole);
    if (result.success) {
      setNewEmail("");
      setNewRole("user");
      onCancel();
    } else if (result.message) {
      alert(result.message);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
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
        onChange={(e) => setNewRole(e.target.value as any)}
        className="px-3 py-2 rounded-md bg-background border border-border"
      >
        <option value="user">Utilisateur</option>
        <option value="support">Support</option>
        <option value="marketing">Marketing</option>
        <option value="admin">Administrateur</option>
      </select>
      <Button
        type="submit"
        disabled={isLoading}
        className="bg-green-600 hover:bg-green-700"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          "Ajouter"
        )}
      </Button>
      <Button
        type="button"
        variant="ghost"
        onClick={onCancel}
      >
        Annuler
      </Button>
    </form>
  );
}
