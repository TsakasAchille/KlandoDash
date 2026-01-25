"use client";

import type { SupportComment } from "@/types/support";
import { COMMENT_SOURCE_LABELS } from "@/types/support";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { User, Bot, Shield } from "lucide-react";

interface CommentThreadProps {
  comments: SupportComment[];
  className?: string;
}

export function CommentThread({ comments, className }: CommentThreadProps) {
  if (comments.length === 0) {
    return (
      <div className={cn("text-center text-muted-foreground py-4", className)}>
        Aucun commentaire
      </div>
    );
  }

  const formatCommentDate = (date: string) => {
    try {
      return format(new Date(date), "dd/MM/yyyy HH:mm", { locale: fr });
    } catch {
      return date;
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case "admin":
        return <Shield className="w-3 h-3" />;
      case "system":
        return <Bot className="w-3 h-3" />;
      default:
        return <User className="w-3 h-3" />;
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case "admin":
        return "bg-klando-burgundy/20 border-klando-burgundy/30";
      case "system":
        return "bg-gray-500/20 border-gray-500/30";
      default:
        return "bg-klando-dark border-klando-dark/50";
    }
  };

  return (
    <div className={cn("space-y-3", className)}>
      {comments.map((comment) => (
        <div
          key={comment.comment_id}
          className={cn(
            "rounded-lg border p-3",
            getSourceColor(comment.comment_source)
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {getSourceIcon(comment.comment_source)}
              <span className="font-medium">
                {COMMENT_SOURCE_LABELS[comment.comment_source as keyof typeof COMMENT_SOURCE_LABELS] ||
                  comment.comment_source}
              </span>
            </div>
            <span className="text-xs text-muted-foreground">
              {formatCommentDate(comment.created_at)}
            </span>
          </div>

          {/* Content */}
          <p className="text-sm whitespace-pre-wrap">{comment.comment_text}</p>
        </div>
      ))}
    </div>
  );
}
