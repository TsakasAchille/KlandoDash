"use client";

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
import {
  Shield,
  User,
  Check,
  X,
  Trash2,
  LifeBuoy,
  TrendingUp,
} from "lucide-react";

interface AdminUserTableProps {
  users: DashUser[];
  currentUserEmail: string | null | undefined;
  loading: string | null;
  onUpdateRole: (email: string, newRole: string) => void;
  onToggleActive: (email: string, currentActive: boolean) => void;
  onDelete: (email: string) => void;
}

export function AdminUserTable({
  users,
  currentUserEmail,
  loading,
  onUpdateRole,
  onToggleActive,
  onDelete
}: AdminUserTableProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
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
                user.email === currentUserEmail
                  ? "bg-klando-gold/5"
                  : undefined
              }
            >
              <TableCell className="font-medium">
                {user.email}
                {user.email === currentUserEmail && (
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
                      : user.role === "support"
                      ? "bg-blue-500/20 text-blue-400"
                      : user.role === "marketing"
                      ? "bg-purple-500/20 text-purple-400"
                      : "bg-secondary text-muted-foreground"
                  }`}
                >
                  {user.role === "admin" ? (
                    <Shield className="w-3 h-3" />
                  ) : user.role === "support" ? (
                    <LifeBuoy className="w-3 h-3" />
                  ) : user.role === "marketing" ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <User className="w-3 h-3" />
                  )}
                  {user.role === "admin"
                    ? "Admin"
                    : user.role === "support"
                    ? "Support"
                    : user.role === "marketing"
                    ? "Marketing"
                    : "User"}
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
                  <select
                    value={user.role}
                    onChange={(e) =>
                      onUpdateRole(user.email, e.target.value)
                    }
                    disabled={
                      loading === user.email ||
                      user.email === currentUserEmail
                    }
                    className="px-2 py-1 rounded-md bg-background border border-border text-xs"
                    title="Changer le rôle"
                  >
                    <option value="user">User</option>
                    <option value="support">Support</option>
                    <option value="marketing">Marketing</option>
                    <option value="admin">Admin</option>
                  </select>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      onToggleActive(user.email, user.active)
                    }
                    disabled={
                      loading === user.email ||
                      user.email === currentUserEmail
                    }
                    title={user.active ? "Désactiver" : "Activer"}
                  >
                    {user.active ? (
                      <X className="w-4 h-4 text-red-400" />
                    ) : (
                      <Check className="w-4 h-4 text-green-400" />
                    )}
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(user.email)}
                    disabled={
                      loading === user.email ||
                      user.email === currentUserEmail
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
  );
}
