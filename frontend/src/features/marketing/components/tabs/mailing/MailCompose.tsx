"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { 
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Plus, Loader2, User, Tag
} from "lucide-react";

interface MailComposeProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (data: any) => Promise<void>;
  isSaving: boolean;
}

export function MailCompose({
  isOpen,
  onOpenChange,
  onSave,
  isSaving
}: MailComposeProps) {
  const [newDraft, setNewDraft] = useState({
    recipient_email: '',
    recipient_name: '',
    subject: '',
    content: '',
    category: 'GENERAL' as any
  });

  const handleSave = async () => {
    await onSave(newDraft);
    setNewDraft({ recipient_email: '', recipient_name: '', subject: '', content: '', category: 'GENERAL' });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-slate-50 border-slate-300 rounded-[2.5rem] p-0 overflow-hidden outline-none shadow-2xl">
        <div className="flex flex-col h-[600px]">
          <DialogHeader className="p-8 pb-6 bg-white border-b border-slate-200 text-left">
            <DialogTitle className="text-xl font-black text-slate-900 uppercase tracking-tight flex items-center gap-3 text-left">
              <Plus className="w-5 h-5 text-purple-600" /> Nouveau Message
            </DialogTitle>
            <DialogDescription className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mt-1 text-left">
              Rédiger un mail de croissance
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 p-8 space-y-4 overflow-y-auto custom-scrollbar text-left bg-white">
            <div className="grid grid-cols-2 gap-4 text-left">
              <div className="space-y-1.5 text-left">
                <label className="text-[10px] font-black text-slate-700 uppercase pl-1 flex items-center gap-2"><User className="w-3 h-3 text-purple-600"/> Destinataire (Email)</label>
                <Input 
                  value={newDraft.recipient_email}
                  onChange={(e) => setNewDraft({...newDraft, recipient_email: e.target.value})}
                  placeholder="ex: client@mail.com" 
                  className="bg-slate-50 border-slate-300 rounded-xl text-slate-900 h-11 placeholder:text-slate-400 focus:border-purple-500/50 transition-all outline-none text-left" 
                />
              </div>
              <div className="space-y-1.5 text-left">
                <label className="text-[10px] font-black text-slate-700 uppercase pl-1">Nom (Optionnel)</label>
                <Input 
                  value={newDraft.recipient_name}
                  onChange={(e) => setNewDraft({...newDraft, recipient_name: e.target.value})}
                  placeholder="ex: Mamadou" 
                  className="bg-slate-50 border-slate-300 rounded-xl text-slate-900 h-11 placeholder:text-slate-400 focus:border-purple-500/50 transition-all outline-none text-left" 
                />
              </div>
            </div>

            <div className="space-y-1.5 text-left">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1 flex items-center gap-2"><Tag className="w-3 h-3 text-purple-600"/> Objet du mail</label>
              <Input 
                value={newDraft.subject}
                onChange={(e) => setNewDraft({...newDraft, subject: e.target.value})}
                placeholder="Sujet accrocheur..." 
                className="bg-slate-50 border-slate-300 rounded-xl text-slate-900 h-11 placeholder:text-slate-400 focus:border-purple-500/50 transition-all outline-none text-left" 
              />
            </div>

            <div className="space-y-1.5 flex-1 flex flex-col text-left">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1 text-left">Message</label>
              <Textarea 
                value={newDraft.content}
                onChange={(e) => setNewDraft({...newDraft, content: e.target.value})}
                placeholder="Bonjour, nous avons trouvé..." 
                className="flex-1 bg-slate-50 border-slate-300 rounded-2xl text-slate-900 min-h-[200px] placeholder:text-slate-400 focus:border-purple-500/50 transition-all resize-none p-4 outline-none font-medium text-left" 
              />
            </div>
          </div>

          <DialogFooter className="p-6 bg-slate-50 border-t border-slate-200 gap-3">
            <Button variant="ghost" onClick={() => onOpenChange(false)} className="rounded-xl text-slate-600 font-black text-[10px] uppercase hover:bg-slate-200 transition-colors">Annuler</Button>
            <Button 
              onClick={handleSave}
              disabled={isSaving || !newDraft.recipient_email || !newDraft.subject}
              className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 shadow-lg shadow-purple-500/20 transition-all active:scale-95"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Plus className="w-4 h-4 text-white" />}
              Créer le brouillon
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
}
