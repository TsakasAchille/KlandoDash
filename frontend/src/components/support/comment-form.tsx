"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Loader2 } from "lucide-react";

interface CommentFormProps {
  onSubmit: (text: string) => Promise<void>;
  disabled?: boolean;
}

const MIN_LENGTH = 10;

export function CommentForm({ onSubmit, disabled }: CommentFormProps) {
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isValid = text.trim().length >= MIN_LENGTH;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isValid || isSubmitting || disabled) return;

    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(text.trim());
      setText(""); // Reset form on success
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de l'envoi"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-2">
        <Textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ajouter un commentaire..."
          className="min-h-[80px] resize-none"
          disabled={isSubmitting || disabled}
        />
        {text.length > 0 && text.length < MIN_LENGTH && (
          <p className="text-xs text-yellow-500">
            Minimum {MIN_LENGTH} caracteres ({MIN_LENGTH - text.length} restants)
          </p>
        )}
        {error && <p className="text-xs text-red-500">{error}</p>}
      </div>

      <div className="flex justify-end">
        <Button
          type="submit"
          size="sm"
          disabled={!isValid || isSubmitting || disabled}
          className="bg-klando-gold hover:bg-klando-gold/90 text-klando-dark"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Envoi...
            </>
          ) : (
            <>
              <Send className="w-4 h-4 mr-2" />
              Envoyer
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
