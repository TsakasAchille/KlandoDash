"use client";

import { useState, useEffect, Suspense } from "react";
import { UserListItem } from "@/types/user";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";
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

function ValidationClientContent({ 
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
  
  // Track if we should show details on mobile
  const [showMobileDetails, setShowMobileDetails] = useState(false);

  // Reset selected user when the list changes
  useEffect(() => {
    if (pendingUsers.length > 0) {
      // If no user selected or the selected user is no longer in the list, select first
      const exists = pendingUsers.some(u => u.uid === selectedUser?.uid);
      if (!selectedUser || !exists) {
        setSelectedUser(pendingUsers[0]);
      }
    } else {
      setSelectedUser(null);
      setShowMobileDetails(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingUsers]);

  const updateFilters = (newStatus: string, newPage: number = 1) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("status", newStatus);
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
    setShowMobileDetails(false); // Go back to list on mobile when filtering
  };

  const handleSelectUser = (user: UserListItem) => {
    setSelectedUser(user);
    setShowMobileDetails(true);
  };

  const handleValidate = () => {
    toast.error("Option non disponible pour l'instant");
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      <div className={cn(showMobileDetails ? "hidden md:block" : "block")}>
        <ValidationFilters 
          currentStatus={currentStatus}
          currentPage={currentPage}
          totalPages={totalPages}
          onUpdateFilters={updateFilters}
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6 relative">
        {/* List View */}
        <div className={cn(
          "lg:col-span-1",
          showMobileDetails ? "hidden lg:block" : "block"
        )}>
          <UserList 
            users={pendingUsers}
            selectedUser={selectedUser}
            onSelectUser={handleSelectUser}
            currentStatus={currentStatus}
            totalCount={totalCount}
          />
        </div>

        {/* Details View */}
        <div className={cn(
          "lg:col-span-2",
          !showMobileDetails ? "hidden lg:block" : "block"
        )}>
          <UserDetails 
            selectedUser={selectedUser}
            onValidate={handleValidate}
            onBack={() => setShowMobileDetails(false)}
          />
        </div>
      </div>
    </div>
  );
}

export function ValidationClient(props: ValidationClientProps) {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground animate-pulse">Chargement des validations...</p>
      </div>
    }>
      <ValidationClientContent {...props} />
    </Suspense>
  );
}
