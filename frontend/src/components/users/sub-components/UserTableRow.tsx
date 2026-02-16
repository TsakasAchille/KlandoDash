"use client";

import { UserListItem } from "@/types/user";
import { formatDate, cn } from "@/lib/utils";
import { TableCell, TableRow } from "@/components/ui/table";
import { Star } from "lucide-react";
import Image from "next/image";

interface UserTableRowProps {
  user: UserListItem;
  isSelected: boolean;
  onSelect: (user: UserListItem) => void;
}

export function UserTableRow({ user, isSelected, onSelect }: UserTableRowProps) {
  return (
    <TableRow
      key={user.uid}
      data-user-id={user.uid}
      data-state={isSelected ? "selected" : undefined}
      className="cursor-pointer transition-colors hover:bg-secondary/20 border-b border-border/10 last:border-0"
      onClick={() => onSelect(user)}
    >
      <TableCell className="py-3">
        <div className="flex items-center gap-3">
          <div className="relative flex-shrink-0">
            {user.photo_url ? (
              <Image
                src={user.photo_url}
                alt=""
                width={32}
                height={32}
                className="w-8 h-8 rounded-lg object-cover border border-border/50"
              />
            ) : (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-klando-burgundy to-klando-burgundy/60 flex items-center justify-center text-white text-[10px] font-black shadow-inner">
                {(user.display_name || "?").charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 mb-0.5">
              <p className="font-bold truncate text-xs uppercase tracking-tight leading-none">
                {user.display_name || "Sans nom"}
              </p>
              {user.created_at && new Date(user.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) && (
                <span className="h-1.5 w-1.5 rounded-full bg-blue-500" title="Nouveau membre" />
              )}
            </div>
            <p className="text-[9px] sm:hidden text-muted-foreground truncate font-medium">
              {user.email || "-"}
            </p>
          </div>
        </div>
      </TableCell>
      <TableCell className="hidden sm:table-cell text-[11px] font-medium text-muted-foreground truncate max-w-[150px]">
        {user.email || "-"}
      </TableCell>
      <TableCell className="hidden md:table-cell text-[11px] font-mono font-bold">
        {user.phone_number || "-"}
      </TableCell>
      <TableCell>
        {user.rating ? (
          <div className="flex items-center gap-1">
            <Star className="w-3 h-3 fill-klando-gold text-klando-gold" />
            <span className="text-xs font-black">{user.rating.toFixed(1)}</span>
          </div>
        ) : (
          <span className="text-muted-foreground text-[10px]">-</span>
        )}
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1.5">
          <span
            className={cn(
              "px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider",
              user.is_driver_doc_validated
                ? "bg-green-500/10 text-green-500 border border-green-500/20"
                : user.role === "driver"
                ? "bg-blue-500/10 text-blue-500 border border-blue-500/20"
                : user.role === "passenger"
                ? "bg-purple-500/10 text-purple-500 border border-purple-500/20"
                : "bg-secondary text-muted-foreground border border-border/50"
            )}
          >
            {user.is_driver_doc_validated 
              ? "Vérifié" 
              : user.role === "driver" 
              ? "Conducteur" 
              : user.role === "passenger"
              ? "Passager"
              : "Membre"}
          </span>
          {user.gender && (
            <span className={cn(
              "text-[10px]",
              user.gender.toLowerCase() === "man" ? "text-blue-400" : "text-pink-400"
            )}>
              {user.gender.toLowerCase() === "man" ? "♂" : "♀"}
            </span>
          )}
        </div>
      </TableCell>
      <TableCell className="hidden lg:table-cell text-[10px] font-mono text-muted-foreground">
        {user.created_at ? formatDate(user.created_at) : "-"}
      </TableCell>
    </TableRow>
  );
}
