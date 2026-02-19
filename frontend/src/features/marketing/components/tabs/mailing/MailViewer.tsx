"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  FileText, ChevronRight, ImageIcon, Trash2, X, Edit3, Save, Loader2, Plus, Send
} from "lucide-react";
import { MarketingEmail } from "@/app/marketing/types";

interface MailViewerProps {
  email: MarketingEmail;
  onClose: () => void;
  onUpdate: (id: string, data: { subject: string; content: string }) => Promise<void>;
  onTrash: (id: string) => void;
  onConvertToDraft: (id: string) => void;
  onSend: (id: string) => void;
  isSaving: boolean;
  isTrashing: boolean;
  sendingEmailId: string | null;
}

export function MailViewer({
  email,
  onClose,
  onUpdate,
  onTrash,
  onConvertToDraft,
  onSend,
  isSaving,
  isTrashing,
  sendingEmailId
}: MailViewerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ subject: '', content: '' });

  useEffect(() => {
    setEditForm({ subject: email.subject, content: email.content });
    setIsEditing(false);
  }, [email]);

  const handleSave = async () => {
    await onUpdate(email.id, editForm);
    setIsEditing(false);
  };

  const insertImage = () => {
    const url = prompt("Entrez l'URL de l'image :");
    if (url) {
        const imgTag = `<img src="${url}" alt="image" style="max-width: 100%; border-radius: 8px; margin: 10px 0;" />`;
        setEditForm(prev => ({...prev, content: prev.content + "\n" + imgTag + "\n"}));
    }
  };

  return (
    <div className="flex-1 bg-slate-50 border border-white/10 rounded-[2rem] overflow-hidden flex flex-col animate-in slide-in-from-right-4 duration-500 shadow-2xl h-full">
      <div className="p-6 border-b border-slate-200 bg-white flex items-center justify-between">
        <div className="flex items-center gap-4 text-left">
          <div className="p-2.5 bg-purple-50 rounded-xl text-purple-600 border border-purple-100 shadow-sm">
            <FileText className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            {isEditing ? (
                <Input 
                    value={editForm.subject}
                    onChange={(e) => setEditForm({...editForm, subject: e.target.value})}
                    className="h-10 text-sm font-black uppercase tracking-tight bg-slate-100 border-slate-300 text-slate-900 min-w-[300px] outline-none focus:ring-purple-500/20"
                />
            ) : (
                <h4 className="text-sm font-black text-slate-900 uppercase tracking-tight line-clamp-1">{email.subject}</h4>
            )}
            <p className="text-[10px] font-bold text-slate-600 uppercase mt-0.5">À: {email.recipient_email}</p>
          </div>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500 shrink-0">
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 p-8 overflow-y-auto custom-scrollbar text-left bg-white">
        {isEditing ? (
            <div className="h-full flex flex-col gap-4 text-left">
                <div className="flex items-center gap-2 mb-2">
                    <Button onClick={insertImage} variant="outline" size="sm" className="h-8 text-[10px] uppercase font-bold text-slate-700 gap-2 border-slate-300 hover:bg-slate-50">
                        <ImageIcon className="w-3.5 h-3.5" /> Ajouter Image
                    </Button>
                </div>
                <Textarea 
                    value={editForm.content}
                    onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                    className="flex-1 min-h-[400px] bg-slate-50 border-slate-300 text-slate-900 p-6 rounded-2xl font-medium leading-relaxed resize-none outline-none focus:ring-2 focus:ring-purple-500/20 text-left"
                />
            </div>
        ) : (
            <div className="space-y-6 text-left">
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 text-sm text-slate-800 leading-relaxed font-medium whitespace-pre-wrap italic shadow-sm text-left">
                    {email.content}
                </div>
                {email.image_url && (
                    <div className="rounded-2xl overflow-hidden border-2 border-slate-200 shadow-lg max-w-[500px] mx-auto group relative bg-white p-2">
                        <img src={email.image_url} alt="Aperçu du trajet" className="w-full h-auto object-cover rounded-xl" />
                    </div>
                )}
            </div>
        )}
      </div>

      <div className="p-6 bg-slate-100 border-t border-slate-200 flex items-center justify-between">
        <div className="flex gap-2">
            {email.status !== 'TRASH' && (
                <Button 
                    variant="ghost" 
                    size="sm" 
                    disabled={isTrashing}
                    onClick={() => onTrash(email.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl uppercase font-black text-[10px] tracking-widest transition-colors"
                >
                    <Trash2 className="w-3.5 h-3.5 mr-2 text-red-600" /> <span>Supprimer</span>
                </Button>
            )}
            {!email.is_ai_generated && email.status === 'DRAFT' && (
                <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setIsEditing(!isEditing)}
                    className="text-blue-700 hover:text-blue-800 hover:bg-blue-50 rounded-xl uppercase font-black text-[10px] tracking-widest transition-colors"
                >
                    {isEditing ? <><X className="w-3.5 h-3.5 mr-2 text-blue-700" /> Annuler</> : <><Edit3 className="w-3.5 h-3.5 mr-2 text-blue-700" /> Éditer</>}
                </Button>
            )}
        </div>
        
        <div className="flex gap-2">
            {isEditing && (
                <Button 
                    onClick={handleSave}
                    disabled={isSaving}
                    className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 gap-2 shadow-lg transition-all"
                >
                    {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Save className="w-4 h-4 text-white" />}
                    Enregistrer
                </Button>
            )}

            {email.status === 'DRAFT' && (
                email.is_ai_generated ? (
                    <Button 
                        onClick={() => onConvertToDraft(email.id)}
                        disabled={isSaving}
                        className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 gap-2 shadow-lg shadow-purple-500/20 transition-all active:scale-95"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Plus className="w-4 h-4 text-white" />}
                        Créer Brouillon
                    </Button>
                ) : (
                    !isEditing && (
                        <Button 
                            onClick={() => onSend(email.id)}
                            disabled={sendingEmailId === email.id}
                            className="rounded-xl bg-slate-900 text-white hover:bg-slate-800 font-black text-[10px] uppercase tracking-widest px-10 h-11 gap-2 shadow-xl active:scale-95 transition-all"
                        >
                            {sendingEmailId === email.id ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Send className="w-4 h-4 text-white" />}
                            Envoyer maintenant
                        </Button>
                    )
                )
            )}
        </div>
      </div>
    </div>
  );
}
