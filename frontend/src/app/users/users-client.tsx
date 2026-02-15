"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UserListItem } from "@/types/user";
import { UserTable } from "@/components/users/user-table";
import { UserDetails } from "@/components/users/user-details";

interface UsersPageClientProps {
  users: UserListItem[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  initialSelectedId?: string | null;
  initialSelectedUser?: UserListItem | null;
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
  totalCount,
  currentPage,
  pageSize,
  initialSelectedId,
  initialSelectedUser,
}: UsersPageClientProps) {
  const router = useRouter();
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(
    initialSelectedUser || null
  );

  const displayUsers =
    initialSelectedUser && !users.some((u) => u.uid === initialSelectedUser.uid)
      ? [initialSelectedUser, ...users]
      : users;

  // Sync URL on selection change (replace pour éviter pollution historique)
  const handleSelectUser = useCallback(
    (user: UserListItem) => {
      setSelectedUser(user);
      const url = new URL(window.location.href);
      url.searchParams.set("selected", user.uid);
      router.replace(url.pathname + url.search, { scroll: false });
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
    <div className="space-y-4 lg:space-y-6">
      {/* Mobile: Layout vertical */}
      <div className="lg:hidden space-y-4">
        {/* Tableau mobile - Full width */}
        <div className="w-full">
          <UserTable
            users={displayUsers}
            totalCount={totalCount}
            currentPage={currentPage}
            pageSize={pageSize}
            selectedUserId={selectedUser?.uid || null}
            initialSelectedId={initialSelectedId}
            onSelectUser={handleSelectUser}
          />
        </div>

        {/* Détails mobile - Full width */}
        {selectedUser && (
          <div className="w-full">
            <UserDetails user={selectedUser} />
          </div>
        )}
      </div>

      {/* Desktop: Layout côte à côte */}
      <div className="hidden lg:block">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Table - 2/3 width on large screens */}
          <div className="lg:col-span-2">
            <UserTable
              users={displayUsers}
              totalCount={totalCount}
              currentPage={currentPage}
              pageSize={pageSize}
              selectedUserId={selectedUser?.uid || null}
              initialSelectedId={initialSelectedId}
              onSelectUser={handleSelectUser}
            />
          </div>

          {/* Details - 1/3 width on large screens */}
          <div className="lg:col-span-1">
            {selectedUser ? (
              <UserDetails user={selectedUser} />
            ) : (
              <div className="flex items-center justify-center h-64 rounded-lg border border-dashed border-border">
                <p className="text-muted-foreground text-center px-4">
                  Sélectionnez un utilisateur
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

