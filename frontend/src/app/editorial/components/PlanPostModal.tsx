"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { MarketingComm } from "@/app/marketing/types";
import { 
  Send, Layout, Calendar
} from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { updateMarketingCommAction } from "@/app/marketing/actions/communication";
import { toast } from "sonner";

interface PlanPostModalProps {
  date: Date | null;
  isOpen: boolean;
  onClose: () => void;
  drafts: MarketingComm[];
}

export function PlanPostModal({ date, isOpen, onClose, drafts }: PlanPostModalProps) {
  const [loading, setLoading] = useState(false);

  const handlePlanDraft = async (draftId: string) => {
    if (!date) return;
    setLoading(true);
    const res = await updateMarketingCommAction(draftId, {
      scheduled_at: date.toISOString()
    });
    
    if (res.success) {
      toast.success("Contenu planifié !");
      onClose();
    } else {
      toast.error("Échec de la planification.");
    }
    setLoading(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md p-0 overflow-hidden bg-white border-none rounded-[2.5rem] shadow-2xl">
        <DialogHeader className="sr-only">
          <DialogTitle>
            Planifier pour le {date ? format(date, 'dd MMMM yyyy', { locale: fr }) : ''}
          </DialogTitle>
          <DialogDescription>
            Sélectionnez un contenu existant à planifier pour cette date.
          </DialogDescription>
        </DialogHeader>

        {date ? (
          <div className="p-8 space-y-6">
            <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-50 rounded-2xl">
                    <Calendar className="w-6 h-6 text-purple-600" />
                </div>
                <div className="space-y-0.5">
                    <h2 className="text-xl font-black uppercase tracking-tight text-slate-900 leading-tight">
                        {format(date, 'dd MMMM', { locale: fr })}
                    </h2>
                    <p className="text-[10px] font-black uppercase tracking-widest text-purple-600">Choisir un contenu</p>
                </div>
            </div>

            <div className="space-y-3 animate-in fade-in duration-300 max-h-[400px] overflow-y-auto custom-scrollbar pr-2 text-left">
                {drafts.length > 0 ? (
                    drafts.map((d) => (
                        <div 
                            key={d.id} 
                            onClick={() => !loading && handlePlanDraft(d.id)}
                            className="p-4 bg-slate-50 border border-slate-100 rounded-2xl hover:border-purple-400 cursor-pointer group transition-all relative overflow-hidden"
                        >
                            <div className="flex justify-between items-start mb-2 relative z-10">
                                <span className="text-[8px] font-black uppercase text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-100">{d.platform}</span>
                                <Send className="w-3 h-3 text-slate-300 group-hover:text-purple-600 transition-colors" />
                            </div>
                            <p className="text-[10px] font-black text-slate-900 uppercase truncate relative z-10">{d.title}</p>
                            <p className="text-[9px] text-slate-500 line-clamp-1 italic mt-1 relative z-10">{d.content}</p>
                            
                            {/* Hover effect bg */}
                            <div className="absolute inset-0 bg-purple-600/0 group-hover:bg-purple-600/[0.02] transition-colors" />
                        </div>
                    ))
                ) : (
                    <div className="py-12 text-center text-slate-300 italic flex flex-col items-center gap-2 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                        <Layout className="w-8 h-8 opacity-20" />
                        <p className="text-[9px] font-black uppercase tracking-widest">Aucun brouillon disponible</p>
                        <p className="text-[8px] font-medium max-w-[150px]">Créez du contenu dans l&apos;onglet Social Media d&apos;abord.</p>
                    </div>
                )}
            </div>

            <Button 
                variant="ghost" 
                onClick={onClose}
                className="w-full text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-slate-900"
            >
                Annuler
            </Button>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400">
            Veuillez sélectionner une date.
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
