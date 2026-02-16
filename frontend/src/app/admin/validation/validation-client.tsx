"use client";

import { useState, useEffect } from "react";
import { UserListItem } from "@/types/user";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { ValidationFilters } from "./components/ValidationFilters";
import { UserList } from "./components/UserList";
import { UserDetails } from "./components/UserDetails";

interface ValidationClientProps {
  pendingUsers: UserListItem[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  currentStatus: string;
}

export function ValidationClient({ 
  pendingUsers, 
  totalCount, 
  currentPage, 
  pageSize,
  currentStatus 
}: ValidationClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(
    pendingUsers.length > 0 ? pendingUsers[0] : null
  );

  // Reset selected user when the list changes
  useEffect(() => {
    if (pendingUsers.length > 0) {
      if (!selectedUser || !pendingUsers.some(u => u.uid === selectedUser.uid)) {
        setSelectedUser(pendingUsers[0]);
      }
    } else {
      setSelectedUser(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingUsers]);

  const updateFilters = (newStatus: string, newPage: number = 1) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("status", newStatus);
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
  };

  const handleValidate = () => {
    toast.error("Option non disponible pour l'instant");
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      <ValidationFilters 
        currentStatus={currentStatus}
        currentPage={currentPage}
        totalPages={totalPages}
        onUpdateFilters={updateFilters}
      />

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <UserList 
            users={pendingUsers}
            selectedUser={selectedUser}
            onSelectUser={setSelectedUser}
            currentStatus={currentStatus}
            totalCount={totalCount}
          />
        </div>

        <div className="lg:col-span-2">
          <UserDetails 
            selectedUser={selectedUser}
            onValidate={handleValidate}
          />
        </div>
      </div>
    </div>
  );
}
