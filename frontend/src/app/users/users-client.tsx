"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UserListItem } from "@/types/user";
import { UserTable } from "@/components/users/user-table";
import { UserDetails } from "@/components/users/user-details";

interface UsersPageClientProps {
  users: UserListItem[];
  initialSelectedId: string | null;
  initialSelectedUser: UserListItem | null;
}

// Abstraction pour scroll (future-proof pour virtualisation)
function scrollToRow(id: string, prefix: string = "user") {
  const element = document.querySelector(`[data-${prefix}-id="${id}"]`);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    // Highlight temporaire
    element.classList.add("ring-2", "ring-klando-gold");
    setTimeout(() => {
      element.classList.remove("ring-2", "ring-klando-gold");
    }, 2000);
  }
}

export function UsersPageClient({
  users,
  initialSelectedId,
  initialSelectedUser,
}: UsersPageClientProps) {
  const router = useRouter();
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(initialSelectedUser);

  // Sync URL on selection change (replace pour éviter pollution historique)
  const handleSelectUser = useCallback(
    (user: UserListItem) => {
      setSelectedUser(user);
      router.replace(`/users?selected=${user.uid}`, { scroll: false });
    },
    [router]
  );

  // Scroll to selected row on mount
  useEffect(() => {
    if (initialSelectedId) {
      // Petit délai pour laisser le DOM se rendre
      setTimeout(() => scrollToRow(initialSelectedId, "user"), 100);
    }
  }, [initialSelectedId]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Table - 2/3 width on large screens */}
      <div className="lg:col-span-2">
        <UserTable
          users={users}
          selectedUserId={selectedUser?.uid || null}
          onSelectUser={handleSelectUser}
        />
      </div>

      {/* Details - 1/3 width on large screens */}
      <div className="lg:col-span-1">
        {selectedUser ? (
          <UserDetails user={selectedUser} />
        ) : (
          <div className="flex items-center justify-center h-64 rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">
              Sélectionnez un utilisateur
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
