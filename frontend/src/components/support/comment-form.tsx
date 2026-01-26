"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Command,
  CommandInput,
  CommandList,
  CommandItem,
  CommandEmpty,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
  PopoverAnchor, // Import PopoverAnchor
} from "@/components/ui/popover";
import { Send, Loader2 } from "lucide-react";
import { toast } from "sonner"; // Import toast

interface CommentFormProps {
  onSubmit: (text: string) => Promise<void>;
  disabled?: boolean;
}

interface MentionUser {
  id: string;
  display: string;
  email: string;
}

const MIN_LENGTH = 3;

export function CommentForm({ onSubmit, disabled }: CommentFormProps) {
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // State for mention functionality
  const [isMentionPopoverOpen, setMentionPopoverOpen] = useState(false);
  const [mentionQuery, setMentionQuery] = useState("");
  const [mentionUsers, setMentionUsers] = useState<MentionUser[]>([]);
  const [mentionStartIndex, setMentionStartIndex] = useState<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isValid = text.trim().length >= MIN_LENGTH;

  // Fetch mentionable users when popover is open
  useEffect(() => {
    if (isMentionPopoverOpen) {
      const fetchUsers = async () => {
        const res = await fetch(`/api/mention-users?q=${mentionQuery}`);
        if (res.ok) {
          const users = await res.json();
          setMentionUsers(users);
        }
      };
      fetchUsers();
    }
  }, [mentionQuery, isMentionPopoverOpen]);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    const caretPosition = e.target.selectionStart;
    setText(newText);

    const atIndex = newText.lastIndexOf("@", caretPosition - 1);
    
    // Check if @ is at the beginning of the string or preceded by a space
    if (atIndex !== -1 && (atIndex === 0 || /\s/.test(newText[atIndex - 1]))) {
      const query = newText.substring(atIndex + 1, caretPosition);
      
      // Ensure the query does not contain spaces
      if (!/\s/.test(query)) {
        setMentionQuery(query);
        setMentionStartIndex(atIndex);
        setMentionPopoverOpen(true);
        return;
      }
    }
    setMentionPopoverOpen(false);
  };
  
  const handleMentionSelect = (mentionId: string) => {
    if (mentionStartIndex === null) return;

    const before = text.substring(0, mentionStartIndex);
    const after = text.substring(mentionStartIndex + mentionQuery.length + 1);
    const newText = `${before}@${mentionId} ${after}`;
    
    setText(newText);
    setMentionPopoverOpen(false);

    // Set focus and caret position after insertion
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        const newCaretPosition = before.length + mentionId.length + 2; // +2 for '@' and space
        textareaRef.current.setSelectionRange(newCaretPosition, newCaretPosition);
      }
    }, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || isSubmitting || disabled) return;
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit(text.trim());
      setText("");
      toast.success("Commentaire et notification envoyés !"); // Show success toast
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'envoi");
      toast.error("Échec de l'envoi du commentaire ou de la notification."); // Show error toast
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Popover open={isMentionPopoverOpen} onOpenChange={setMentionPopoverOpen}>
        <PopoverTrigger asChild>
          {/* Dummy trigger to satisfy Popover component, visually hidden */}
          <span style={{ display: 'none' }} />
        </PopoverTrigger>
                  <div className="relative">
                    <PopoverAnchor asChild>
                      <Textarea
                        ref={textareaRef}
                        value={text}
                        onChange={handleTextChange}
                        placeholder="Ajouter un commentaire... Utilisez @ pour mentionner."
                        className="min-h-[80px] resize-none"
                        disabled={isSubmitting || disabled}
                      />
                    </PopoverAnchor>          {text.length > 0 && text.length < MIN_LENGTH && (
            <p className="text-xs text-yellow-500">
              Minimum {MIN_LENGTH} caracteres ({MIN_LENGTH - text.length} restants)
            </p>
          )}
          {error && <p className="text-xs text-red-500">{error}</p>}
        </div>

        <PopoverContent className="w-[350px] p-0" align="start">
          <Command shouldFilter={false}>
            <CommandInput 
              placeholder="Taper un nom ou email..." 
            />
            <CommandList>
              <CommandEmpty>Aucun utilisateur trouvé.</CommandEmpty>
              {mentionUsers.map((user) => (
                <CommandItem
                  key={user.email}
                  onSelect={() => handleMentionSelect(user.id)}
                  value={user.display}
                >
                  {user.display}
                </CommandItem>
              ))}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

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