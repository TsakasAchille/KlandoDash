"use client";

import type { SupportComment } from "@/types/support";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { User, Shield } from "lucide-react";
import Image from "next/image";

// =======================================
// Avatar Component
// =======================================

interface AvatarProps {
  src: string | null | undefined;
  fallback: string;
  className?: string;
}

function Avatar({ src, fallback, className }: AvatarProps) {
  const getInitials = (name: string) => {
    if (!name) return "?";
    const names = name.split(" ");
    if (names.length > 1) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <div
      className={cn(
        "relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted",
        className
      )}
    >
      {src ? (
        <Image
          src={src}
          alt={fallback}
          width={40}
          height={40}
          className="rounded-full object-cover"
        />
      ) : (
        <span className="font-semibold text-klando-grizzly">
          {getInitials(fallback)}
        </span>
      )}
    </div>
  );
}

// =======================================
// CommentBubble Component
// =======================================

interface CommentBubbleProps {
  comment: SupportComment;
  isCurrentUserAdmin: boolean;
}

function CommentBubble({ comment, isCurrentUserAdmin }: CommentBubbleProps) {
  const {
    comment_text,
    created_at,
    comment_source,
    user_display_name,
    user_avatar_url,
  } = comment;

  const isAdmin = comment_source === "admin";
  const alignRight = isAdmin;

  const formatCommentDate = (date: string) => {
    try {
      return format(new Date(date), "dd/MM/yyyy HH:mm", { locale: fr });
    } catch {
      return date;
    }
  };

  // Helper component to parse and style mentions
  const ParsedComment = ({ text }: { text: string }) => {
    const mentionRegex = /@(\w+)/g;
    const parts = text.split(mentionRegex);

    return (
      <p className="text-sm whitespace-pre-wrap text-white">
        {parts.map((part, index) => {
          if (index % 2 === 1) { // Every odd part is a captured group (the mention)
            return (
              <strong key={index} className="font-semibold text-klando-gold">
                @{part}
              </strong>
            );
          }
          return part;
        })}
      </p>
    );
  };

  return (
    <div className={cn("flex items-start gap-3", alignRight && "flex-row-reverse")}>
      <Avatar
        src={user_avatar_url}
        fallback={user_display_name || "???"}
        className="mt-1"
      />
      <div
        className={cn(
          "max-w-xs lg:max-w-md rounded-lg p-3",
          alignRight
            ? "bg-klando-blue-light"
            : "bg-klando-dark-s"
        )}
      >
        <div className="flex items-center gap-2 mb-1">
          {isAdmin && <Shield className="w-4 h-4 text-klando-gold" />}
          <p className="font-semibold text-white">
            {user_display_name || "Utilisateur"}
          </p>
          <span className="text-xs text-muted-foreground">
            {formatCommentDate(created_at)}
          </span>
        </div>
        <ParsedComment text={comment_text} />
      </div>
    </div>
  );
}


// =======================================
// Main CommentThread Component
// =======================================

interface CommentThreadProps {
  comments: SupportComment[];
  className?: string;
}

export function CommentThread({ comments, className }: CommentThreadProps) {
  if (!comments || comments.length === 0) {
    return (
      <div className={cn("text-center text-muted-foreground py-4", className)}>
        Aucun commentaire pour le moment.
      </div>
    );
  }
  
  // NOTE: This is a placeholder for a real check.
  // In a real app, you would get the current user's role from the session.
  const isCurrentUserAdmin = true;

  return (
    <div className={cn("space-y-4", className)}>
      {comments.map((comment) => (
        <CommentBubble
          key={comment.comment_id}
          comment={comment}
          isCurrentUserAdmin={isCurrentUserAdmin}
        />
      ))}
    </div>
  );
}
