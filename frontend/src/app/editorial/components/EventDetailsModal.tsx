"use client";

import { useState, useEffect } from "react";
import { MarketingComment } from "@/app/marketing/types";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Music, Instagram, Twitter, Mail, 
  Send, Calendar, Tag,
  Image as ImageIcon,
  Loader2
} from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { getMarketingComments, addMarketingComment } from "../actions";
import { useSession } from "next-auth/react";

interface EventDetailsModalProps {
  event: any | null;
  onClose: () => void;
}

export function EventDetailsModal({ event, onClose }: EventDetailsModalProps) {
  const { data: session } = useSession();
  const [comments, setComments] = useState<MarketingComment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const loadComments = async () => {
        if (!event) return;
        setLoading(true);
        const params = event.eventType === 'COMM' 
          ? { commId: event.id } 
          : { emailId: event.id };
        
        const data = await getMarketingComments(params);
        setComments(data);
        setLoading(false);
      };

    if (event) {
      loadComments();
    }
  }, [event]);

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !session?.user?.email || !event) return;

    setSubmitting(true);
    const params = event.eventType === 'COMM'
      ? { commId: event.id, content: newComment, userEmail: session.user.email }
      : { emailId: event.id, content: newComment, userEmail: session.user.email };

    const result = await addMarketingComment(params);
    if (result.success) {
      setNewComment("");
      // Reload comments
      const refreshParams = event.eventType === 'COMM' ? { commId: event.id } : { emailId: event.id };
      const data = await getMarketingComments(refreshParams);
      setComments(data);
    }
    setSubmitting(false);
  };

  if (!event) return null;

  const title = event.title || event.subject || "Détails du contenu";
  const date = event.date ? new Date(event.date) : new Date();

  return (
    <Dialog open={!!event} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl p-0 overflow-hidden bg-slate-50 border-none rounded-[2.5rem] shadow-2xl">
        <DialogHeader className="sr-only">
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            Détails et commentaires de la publication ou de l&apos;email.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid md:grid-cols-2 h-[600px]">
          
          {/* LEFT: VISUAL & INFO */}
          <div className="flex flex-col bg-white overflow-y-auto custom-scrollbar">
            {/* Visual Area */}
            <div className="relative min-h-[300px] bg-slate-100 flex items-center justify-center border-b border-slate-100 group">
              {event.image_url ? (
                event.image_url.endsWith('.pdf') ? (
                    <div className="flex flex-col items-center gap-3 text-slate-400">
                        <FileText className="w-16 h-16 text-red-500 opacity-50" />
                        <p className="text-[10px] font-black uppercase">Document PDF attaché</p>
                    </div>
                ) : (
                    <img 
                        src={event.image_url} 
                        alt={title} 
                        className="w-full h-full object-contain bg-slate-900"
                    />
                )
              ) : (
                <div className="flex flex-col items-center gap-2 text-slate-400">
                  <ImageIcon className="w-12 h-12 opacity-20" />
                  <p className="text-[10px] font-black uppercase tracking-widest italic">Aucun visuel</p>
                </div>
              )}
              
              {/* Platform Tag */}
              <div className="absolute top-4 left-4 flex items-center gap-2 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl shadow-sm border border-slate-200">
                {event.platform === 'TIKTOK' && <Music className="w-3.5 h-3.5 text-black" />}
                {event.platform === 'INSTAGRAM' && <Instagram className="w-3.5 h-3.5 text-pink-600" />}
                {event.platform === 'X' && <Twitter className="w-3.5 h-3.5 text-blue-400" />}
                {event.eventType === 'EMAIL' && <Mail className="w-3.5 h-3.5 text-green-500" />}
                <span className="text-[10px] font-black uppercase tracking-tight text-slate-900">
                  {event.platform || 'EMAIL'}
                </span>
              </div>
            </div>

            {/* Content Area */}
            <div className="p-8 space-y-6 text-left">
              <div className="space-y-2">
                <h2 className="text-xl font-black uppercase tracking-tight text-slate-900 leading-tight">
                  {title}
                </h2>
                <div className="flex items-center gap-4 text-slate-400">
                    <div className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5" />
                        <span className="text-[10px] font-black uppercase tracking-widest italic">
                            {format(date, 'dd MMMM yyyy', { locale: fr })}
                        </span>
                    </div>
                </div>
              </div>

              <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100">
                <p className="text-xs text-slate-600 leading-relaxed font-medium italic">
                  &quot;{event.content}&quot;
                </p>
              </div>

              {event.hashtags && event.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {event.hashtags.map((tag: string, i: number) => (
                        <div key={i} className="flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-600 border border-purple-100 rounded-lg">
                            <Tag className="w-3 h-3" />
                            <span className="text-[9px] font-bold">#{tag}</span>
                        </div>
                    ))}
                </div>
              )}
            </div>
          </div>

          {/* RIGHT: COMMENTS */}
          <div className="flex flex-col bg-slate-50 border-l border-slate-200">
            <div className="p-6 border-b border-slate-200 bg-white">
                <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-2">
                    Commentaires <span className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-400">{comments.length}</span>
                </h3>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
              {loading ? (
                <div className="flex flex-col items-center justify-center h-40 opacity-20">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : comments.length > 0 ? (
                comments.map((comment) => (
                  <div key={comment.id} className="flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <Avatar className="w-8 h-8 border border-white shadow-sm">
                      <AvatarImage src={comment.author?.avatar_url || ""} />
                      <AvatarFallback className="bg-purple-100 text-purple-600 font-bold text-[10px]">
                        {comment.user_email.substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-black text-slate-900">
                          {comment.author?.display_name || comment.user_email.split('@')[0]}
                        </span>
                        <span className="text-[8px] font-bold text-slate-400">
                          {format(new Date(comment.created_at), 'HH:mm', { locale: fr })}
                        </span>
                      </div>
                      <div className="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 shadow-sm">
                        <p className="text-[11px] text-slate-600 leading-relaxed">{comment.content}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-40 flex flex-col items-center justify-center opacity-30 italic text-slate-400">
                  <p className="text-[9px] font-black uppercase text-center">Aucun commentaire pour le moment</p>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-6 bg-white border-t border-slate-200">
              <form onSubmit={handleAddComment} className="flex items-center gap-3">
                <Input 
                  placeholder="Votre avis..." 
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="flex-1 h-12 bg-slate-50 border-none rounded-xl text-[11px] font-medium px-4 focus-visible:ring-purple-400"
                />
                <Button 
                  type="submit" 
                  disabled={submitting || !newComment.trim()}
                  className="w-12 h-12 rounded-xl bg-purple-600 hover:bg-purple-700 shadow-lg shadow-purple-200 transition-all flex items-center justify-center"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4 text-white" />}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
