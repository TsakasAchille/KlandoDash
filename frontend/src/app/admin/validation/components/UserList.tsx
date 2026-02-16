"use client";

import { UserListItem } from "@/types/user";
import { cn } from "@/lib/utils";
import { ShieldAlert, CheckCircle, User, FileText, CreditCard } from "lucide-react";
import Image from "next/image";

interface UserListProps {
  users: UserListItem[];
  selectedUser: UserListItem | null;
  onSelectUser: (user: UserListItem) => void;
  currentStatus: string;
  totalCount: number;
}

export function UserList({
  users,
  selectedUser,
  onSelectUser,
  currentStatus,
  totalCount
}: UserListProps) {
  return (
    <div className="space-y-4">
      <h3 className="font-bold flex items-center gap-2 px-2 text-sm uppercase tracking-wider">
        {currentStatus === "pending" ? (
          <ShieldAlert className="w-4 h-4 text-klando-gold" />
        ) : currentStatus === "true" ? (
          <CheckCircle className="w-4 h-4 text-green-500" />
        ) : (
          <User className="w-4 h-4 text-muted-foreground" />
        )}
        Résultats ({totalCount})
      </h3>
      
      {users.length === 0 ? (
        <div className="py-10 text-center bg-muted/10 rounded-xl border border-dashed">
          <p className="text-sm text-muted-foreground italic">Aucun utilisateur trouvé</p>
        </div>
      ) : (
        <div className="space-y-2 overflow-auto max-h-[calc(100vh-320px)] pr-2 scrollbar-thin">
          {users.map((user) => (
            <button
              key={user.uid}
              onClick={() => onSelectUser(user)}
              className={cn(
                "w-full text-left p-4 rounded-xl border transition-all flex items-center gap-4 relative overflow-hidden group",
                selectedUser?.uid === user.uid
                  ? "bg-klando-burgundy text-white border-klando-burgundy shadow-md scale-[1.02]"
                  : "bg-card hover:bg-accent border-border"
              )}
            >
              {user.photo_url ? (
                <div className="relative w-10 h-10 flex-shrink-0">
                  <Image
                    src={user.photo_url}
                    alt=""
                    fill
                    className="rounded-lg object-cover"
                  />
                </div>
              ) : (
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center font-bold",
                  selectedUser?.uid === user.uid ? "bg-white/20" : "bg-muted"
                )}>
                  {(user.display_name || "?").charAt(0).toUpperCase()}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="font-bold truncate text-sm">
                  {user.display_name || "Utilisateur sans nom"}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {user.driver_license_url && <FileText className="w-3 h-3 opacity-70" />}
                  {user.id_card_url && <CreditCard className="w-3 h-3 opacity-70" />}
                  <span className={cn(
                    "text-[10px] font-mono",
                    selectedUser?.uid === user.uid ? "text-white/60" : "text-muted-foreground"
                  )}>
                    {user.uid.slice(0, 8)}...
                  </span>
                </div>
              </div>
              {user.is_driver_doc_validated && (
                <div className="absolute top-1 right-1">
                  <CheckCircle className="w-3 h-3 text-green-500 fill-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
