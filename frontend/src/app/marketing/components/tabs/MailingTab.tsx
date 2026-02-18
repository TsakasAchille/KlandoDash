"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Sparkles, Loader2, Send, History, Mail, FileText, 
  SendHorizontal, AlertCircle, Trash2, ChevronRight,
  Search, Filter, Inbox, Clock, Plus, User, Tag, Edit3, Save, X, Image as ImageIcon
} from "lucide-react";
import { MarketingEmail, createEmailDraftAction, moveEmailToTrashAction, updateMarketingEmailAction } from "../../mailing-actions";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface MailingTabProps {
  emails: MarketingEmail[];
  isScanning: boolean;
  sendingEmailId: string | null;
  onScan: () => void;
  onSendEmail: (id: string) => void;
}

type MailFolder = 'SUGGESTIONS' | 'DRAFTS' | 'SENT' | 'FAILED' | 'TRASH';

export function MailingTab({ 
  emails, 
  isScanning, 
  sendingEmailId, 
  onScan, 
  onSendEmail 
}: MailingTabProps) {
  const [activeFolder, setActiveFolder] = useState<MailFolder>('SUGGESTIONS');
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTrashing, setIsTrashing] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ subject: '', content: '' });

  // Form state for new draft
  const [newDraft, setNewDraft] = useState({
    recipient_email: '',
    recipient_name: '',
    subject: '',
    content: '',
    category: 'GENERAL' as any
  });

  const filteredEmails = emails.filter(e => {
    if (activeFolder === 'SUGGESTIONS') return e.status === 'DRAFT' && e.is_ai_generated;
    if (activeFolder === 'DRAFTS') return e.status === 'DRAFT' && !e.is_ai_generated;
    if (activeFolder === 'SENT') return e.status === 'SENT';
    if (activeFolder === 'FAILED') return e.status === 'FAILED';
    if (activeFolder === 'TRASH') return e.status === 'TRASH';
    return false;
  });

  const selectedEmail = emails.find(e => e.id === selectedEmailId);

  // Initialiser le formulaire d'édition quand on sélectionne un mail
  useEffect(() => {
    if (selectedEmail) {
        setEditForm({ subject: selectedEmail.subject, content: selectedEmail.content });
        setIsEditing(false);
    }
  }, [selectedEmailId]);

  const handleSaveManualDraft = async () => {
    if (!newDraft.recipient_email || !newDraft.subject) {
        toast.error("Email et sujet obligatoires");
        return;
    }
    setIsSaving(true);
    try {
        const res = await createEmailDraftAction({
            ...newDraft,
            is_ai_generated: false
        });
        if (res.success) {
            toast.success("Brouillon créé !");
            setIsComposeOpen(false);
            setNewDraft({ recipient_email: '', recipient_name: '', subject: '', content: '', category: 'GENERAL' });
            setActiveFolder('DRAFTS');
        }
    } catch (e) {
        toast.error("Erreur de sauvegarde");
    } finally {
        setIsSaving(false);
    }
  };

  const handleMoveToTrash = async (id: string) => {
    setIsTrashing(true);
    try {
        const res = await moveEmailToTrashAction(id);
        if (res.success) {
            toast.success("Déplacé vers la corbeille");
            setSelectedEmailId(null);
        }
    } catch (e) {
        toast.error("Erreur");
    } finally {
        setIsTrashing(false);
    }
  };

  const handleConvertToDraft = async (id: string) => {
    setIsSaving(true);
    try {
        const res = await updateMarketingEmailAction(id, { is_ai_generated: false });
        if (res.success) {
            toast.success("Converti en brouillon !");
            setActiveFolder('DRAFTS');
        }
    } catch (e) {
        toast.error("Erreur");
    } finally {
        setIsSaving(false);
    }
  };

  const handleUpdateContent = async () => {
    if (!selectedEmailId) return;
    setIsSaving(true);
    try {
        const res = await updateMarketingEmailAction(selectedEmailId, editForm);
        if (res.success) {
            toast.success("Brouillon mis à jour");
            setIsEditing(false);
        }
    } catch (e) {
        toast.error("Erreur de mise à jour");
    } finally {
        setIsSaving(false);
    }
  };

  return (
    <div className="flex gap-6 h-[750px] animate-in fade-in duration-500">
      
      {/* 1. SIDEBAR */}
      <div className="w-64 flex flex-col gap-2">
        <Button 
          onClick={() => setIsComposeOpen(true)}
          className="w-full h-12 rounded-2xl bg-white text-slate-950 hover:bg-slate-200 font-black uppercase text-[10px] tracking-widest gap-3 shadow-xl mb-2 border-none transition-all active:scale-95 group"
        >
          <Plus className="w-4 h-4 text-slate-950 group-hover:scale-110 transition-transform" /> 
          <span className="text-slate-950">Nouveau Message</span>
        </Button>

        <Button 
          onClick={onScan}
          disabled={isScanning}
          variant="outline"
          className="w-full h-10 rounded-xl border-purple-500/40 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 hover:text-purple-300 font-black uppercase text-[10px] tracking-widest gap-3 mb-4 transition-all"
        >
          {isScanning ? <Loader2 className="w-4 h-4 animate-spin text-purple-400" /> : <Sparkles className="w-4 h-4 text-purple-400" />}
          <span className="text-purple-400">Scan Opportunités</span>
        </Button>

        <div className="space-y-1">
          <FolderItem 
            icon={Sparkles} 
            label="Suggestions ✨" 
            count={emails.filter(e => e.status === 'DRAFT' && e.is_ai_generated).length}
            active={activeFolder === 'SUGGESTIONS'}
            onClick={() => setActiveFolder('SUGGESTIONS')}
            color="text-purple-400"
          />
          <FolderItem 
            icon={FileText} 
            label="Brouillons" 
            count={emails.filter(e => e.status === 'DRAFT' && !e.is_ai_generated).length}
            active={activeFolder === 'DRAFTS'}
            onClick={() => setActiveFolder('DRAFTS')}
            color="text-blue-400"
          />
          <FolderItem 
            icon={SendHorizontal} 
            label="Envoyés" 
            active={activeFolder === 'SENT'}
            onClick={() => setActiveFolder('SENT')}
            color="text-green-400"
          />
          <FolderItem 
            icon={AlertCircle} 
            label="Échecs" 
            active={activeFolder === 'FAILED'}
            onClick={() => setActiveFolder('FAILED')}
            color="text-red-400"
          />
          <div className="pt-4 mt-4 border-t border-white/5">
            <FolderItem 
                icon={Trash2} 
                label="Corbeille" 
                active={activeFolder === 'TRASH'}
                onClick={() => setActiveFolder('TRASH')}
                color="text-slate-400"
            />
          </div>
        </div>
      </div>

      {/* 2. LIST */}
      <div className={cn(
        "flex-1 bg-card/30 border border-white/5 rounded-[2rem] overflow-hidden flex flex-col transition-all duration-500 shadow-2xl",
        selectedEmailId ? "flex-[0.4]" : "flex-1"
      )}>
        <div className="p-4 border-b border-white/5 bg-white/[0.02] flex items-center justify-between text-left">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground pl-2">{activeFolder}</h3>
          <div className="flex items-center gap-2 pr-2">
            <Search className="w-3.5 h-3.5 text-muted-foreground/40" />
            <Filter className="w-3.5 h-3.5 text-muted-foreground/40" />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {filteredEmails.length > 0 ? (
            filteredEmails.map((email) => (
              <div 
                key={email.id}
                onClick={() => setSelectedEmailId(email.id)}
                className={cn(
                  "flex items-center gap-4 px-6 py-4 border-b border-white/[0.03] cursor-pointer transition-all hover:bg-white/[0.03] group text-left",
                  selectedEmailId === email.id ? "bg-white/[0.05] border-l-4 border-l-purple-500" : ""
                )}
              >
                <div className="flex-shrink-0">
                  {email.status === 'SENT' ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Mail className="w-4 h-4 text-muted-foreground/40 group-hover:text-purple-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-0.5">
                    <span className="text-xs font-black text-white uppercase truncate pr-4">
                      {email.recipient_name || email.recipient_email.split('@')[0]}
                    </span>
                    <span className="text-[10px] font-medium text-muted-foreground/40 tabular-nums">
                      {new Date(email.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                    </span>
                  </div>
                  <p className="text-[11px] font-bold text-white/70 truncate">{email.subject}</p>
                  <p className="text-[10px] text-muted-foreground/60 truncate mt-0.5">{email.content.substring(0, 60)}...</p>
                </div>
              </div>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center opacity-20 italic text-white">
              <Inbox className="w-12 h-12 mb-4" />
              <p className="text-[10px] font-black uppercase tracking-widest">Dossier vide</p>
            </div>
          )}
        </div>
      </div>

      {/* 3. EDITOR / VIEWER */}
      {selectedEmail && (
        <div className="flex-1 bg-slate-50 border border-white/10 rounded-[2rem] overflow-hidden flex flex-col animate-in slide-in-from-right-4 duration-500 shadow-2xl">
          {/* Header Editor */}
          <div className="p-6 border-b border-slate-200 bg-white flex items-center justify-between">
            <div className="flex items-center gap-4 text-left">
              <div className="p-2.5 bg-purple-500/10 rounded-xl text-purple-600">
                <FileText className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                {isEditing ? (
                    <Input 
                        value={editForm.subject}
                        onChange={(e) => setEditForm({...editForm, subject: e.target.value})}
                        className="h-8 text-sm font-black uppercase tracking-tight bg-slate-100 border-slate-200 text-slate-900 min-w-[300px]"
                    />
                ) : (
                    <h4 className="text-sm font-black text-slate-900 uppercase tracking-tight line-clamp-1">{selectedEmail.subject}</h4>
                )}
                <p className="text-[10px] font-bold text-slate-500 uppercase">À: {selectedEmail.recipient_email}</p>
              </div>
            </div>
            <button onClick={() => setSelectedEmailId(null)} className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 shrink-0">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 p-8 overflow-y-auto custom-scrollbar text-left bg-white">
            {isEditing ? (
                <div className="h-full flex flex-col gap-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Button variant="outline" size="sm" className="h-8 text-[10px] uppercase font-bold text-slate-600 gap-2 border-slate-200">
                            <ImageIcon className="w-3 h-3" /> Ajouter Image
                        </Button>
                        <p className="text-[9px] text-slate-400 font-medium italic">Note: Le support HTML est activé pour les images.</p>
                    </div>
                    <Textarea 
                        value={editForm.content}
                        onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                        className="flex-1 min-h-[400px] bg-slate-50 border-slate-200 text-slate-800 p-6 rounded-2xl font-medium leading-relaxed resize-none outline-none focus:ring-2 focus:ring-purple-500/20"
                    />
                </div>
            ) : (
                <div className="bg-slate-50 border border-slate-100 rounded-2xl p-8 text-sm text-slate-700 leading-relaxed font-medium whitespace-pre-wrap italic shadow-sm min-h-full">
                    {selectedEmail.content}
                </div>
            )}
          </div>

          {/* Actions Bottom */}
          <div className="p-6 bg-slate-100 border-t border-slate-200 flex items-center justify-between">
            <div className="flex gap-2">
                {selectedEmail.status !== 'TRASH' && (
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        disabled={isTrashing}
                        onClick={() => handleMoveToTrash(selectedEmail.id)}
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl uppercase font-black text-[10px] tracking-widest"
                    >
                        <Trash2 className="w-3.5 h-3.5 mr-2" /> Supprimer
                    </Button>
                )}
                {!selectedEmail.is_ai_generated && selectedEmail.status === 'DRAFT' && (
                    <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setIsEditing(!isEditing)}
                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-xl uppercase font-black text-[10px] tracking-widest"
                    >
                        {isEditing ? <><X className="w-3.5 h-3.5 mr-2" /> Annuler</> : <><Edit3 className="w-3.5 h-3.5 mr-2" /> Éditer</>}
                    </Button>
                )}
            </div>
            
            <div className="flex gap-2">
                {isEditing && (
                    <Button 
                        onClick={handleUpdateContent}
                        disabled={isSaving}
                        className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 gap-2 shadow-lg"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Enregistrer
                    </Button>
                )}

                {selectedEmail.status === 'DRAFT' && (
                    selectedEmail.is_ai_generated ? (
                        <Button 
                            onClick={() => handleConvertToDraft(selectedEmail.id)}
                            disabled={isSaving}
                            className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 gap-2 shadow-lg shadow-purple-500/20"
                        >
                            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                            Créer Brouillon
                        </Button>
                    ) : (
                        !isEditing && (
                            <Button 
                                onClick={() => onSendEmail(selectedEmail.id)}
                                disabled={sendingEmailId === selectedEmail.id}
                                className="rounded-xl bg-slate-900 text-white hover:bg-slate-800 font-black text-[10px] uppercase tracking-widest px-10 h-11 gap-2 shadow-xl active:scale-95 transition-all"
                            >
                                {sendingEmailId === selectedEmail.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                                Envoyer maintenant
                            </Button>
                        )
                    )
                )}
            </div>
          </div>
        </div>
      )}

      {/* --- COMPOSE DIALOG --- */}
      <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
        <DialogContent className="sm:max-w-[600px] bg-slate-950 border-white/10 rounded-[2.5rem] p-0 overflow-hidden outline-none shadow-2xl">
            <div className="flex flex-col h-[600px]">
                <DialogHeader className="p-8 pb-6 bg-white/[0.02] border-b border-white/5 text-left">
                    <DialogTitle className="text-xl font-black text-white uppercase tracking-tight flex items-center gap-3">
                        <Plus className="w-5 h-5 text-purple-500" /> Nouveau Message
                    </DialogTitle>
                    <DialogDescription className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mt-1">Rédiger un mail de croissance</DialogDescription>
                </DialogHeader>

                <div className="flex-1 p-8 space-y-4 overflow-y-auto custom-scrollbar text-left">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black text-muted-foreground uppercase pl-1 flex items-center gap-2"><User className="w-3 h-3 text-purple-400"/> Destinataire (Email)</label>
                            <Input 
                                value={newDraft.recipient_email}
                                onChange={(e) => setNewDraft({...newDraft, recipient_email: e.target.value})}
                                placeholder="ex: client@mail.com" 
                                className="bg-white/5 border-white/10 rounded-xl text-white h-11 placeholder:text-white/20 focus:border-purple-500/50 transition-all outline-none" 
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black text-muted-foreground uppercase pl-1">Nom (Optionnel)</label>
                            <Input 
                                value={newDraft.recipient_name}
                                onChange={(e) => setNewDraft({...newDraft, recipient_name: e.target.value})}
                                placeholder="ex: Mamadou" 
                                className="bg-white/5 border-white/10 rounded-xl text-white h-11 placeholder:text-white/20 focus:border-purple-500/50 transition-all outline-none" 
                            />
                        </div>
                    </div>

                    <div className="space-y-1.5">
                        <label className="text-[10px] font-black text-muted-foreground uppercase pl-1 flex items-center gap-2"><Tag className="w-3 h-3 text-purple-400"/> Objet du mail</label>
                        <Input 
                            value={newDraft.subject}
                            onChange={(e) => setNewDraft({...newDraft, subject: e.target.value})}
                            placeholder="Sujet accrocheur..." 
                            className="bg-white/5 border-white/10 rounded-xl text-white h-11 placeholder:text-white/20 focus:border-purple-500/50 transition-all outline-none" 
                        />
                    </div>

                    <div className="space-y-1.5 flex-1 flex flex-col">
                        <label className="text-[10px] font-black text-muted-foreground uppercase pl-1">Message</label>
                        <Textarea 
                            value={newDraft.content}
                            onChange={(e) => setNewDraft({...newDraft, content: e.target.value})}
                            placeholder="Bonjour, nous avons trouvé..." 
                            className="flex-1 bg-white/5 border-white/10 rounded-2xl text-white min-h-[200px] placeholder:text-white/20 focus:border-purple-500/50 transition-all resize-none p-4 outline-none font-medium text-left" 
                        />
                    </div>
                </div>

                <DialogFooter className="p-6 bg-white/[0.02] border-t border-white/5 gap-3">
                    <Button variant="ghost" onClick={() => setIsComposeOpen(false)} className="rounded-xl text-white font-black text-[10px] uppercase hover:bg-white/5 transition-colors">Annuler</Button>
                    <Button 
                        onClick={handleSaveManualDraft}
                        disabled={isSaving}
                        className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 shadow-lg shadow-purple-500/20 transition-all active:scale-95"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
                        Créer le brouillon
                    </Button>
                </DialogFooter>
            </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function FolderItem({ icon: Icon, label, active, onClick, count, color }: any) {
  const activeBg = color ? color.replace('text-', 'bg-') + '/10' : 'bg-white/10';
  const hoverTextColor = color || "text-white";

  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group",
        active ? `${activeBg} shadow-inner` : "text-muted-foreground/60 hover:bg-white/[0.03]"
      )}
    >
      <div className="flex items-center gap-3">
        <Icon className={cn("w-4 h-4 transition-colors", active ? color : `text-muted-foreground/40 group-hover:${hoverTextColor.replace('text-', 'text-')}`)} />
        <span className={cn(
          "text-[11px] font-black uppercase tracking-widest transition-colors", 
          active ? color : `text-muted-foreground/60 group-hover:${hoverTextColor.replace('text-', 'text-')}`
        )}>
          {label}
        </span>
      </div>
      {count !== undefined && count > 0 && (
        <span className={cn(
            "text-[9px] font-black px-1.5 py-0.5 rounded-md transition-all",
            active ? color.replace('text-', 'bg-') + '/20 ' + color : `bg-white/5 text-muted-foreground/40 group-hover:${hoverTextColor.replace('text-', 'text-')}`
        )}>{count}</span>
      )}
    </button>
  );
}

function CheckCircle2(props: any) {
  return (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}
