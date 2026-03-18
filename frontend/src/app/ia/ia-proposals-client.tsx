"use client";

import { useState, useEffect } from "react";
import { Check, X, MessageSquare, User, MapPin, RefreshCw, Edit3, Phone, ExternalLink, Car } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface Proposal {
  id: string;
  author: string;
  type: string;
  route: string;
  context: string;
  response: string;
}

interface Conductor {
  name: string;
  phone: string;
  route: string;
  message: string;
  whatsappLink: string;
}

export function IAProposalsClient() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [conductors, setConductors] = useState<Conductor[]>([]);
  const [validatedProposals, setValidatedProposals] = useState<any[]>([]);

  // 1. Charger les propositions depuis le DOM (ID ia-cm-proposals-input)
  const loadProposals = () => {
    const inputEl = document.getElementById('ia-cm-proposals-input');
    if (!inputEl) {
      toast.error("Élément #ia-cm-proposals-input non trouvé");
      return;
    }

    try {
      const content = inputEl.textContent?.trim() || "[]";
      const data = JSON.parse(content);
      
      // Support nouveau format objet { proposals, conductors } ou ancien format array
      if (data.proposals || data.conductors) {
        setProposals(data.proposals || []);
        setConductors(data.conductors || []);
        toast.success(`${(data.proposals?.length || 0) + (data.conductors?.length || 0)} éléments chargés`);
      } else if (Array.isArray(data)) {
        setProposals(data);
        setConductors([]);
        toast.success(`${data.length} propositions chargées`);
      }
    } catch (e) {
      console.error("[IA-PROPOSALS] Error parsing JSON input:", e);
      toast.error("Erreur de format JSON dans l'input");
    }
  };

  // 2. Mettre à jour l'output dans le DOM (ID ia-validated-proposals)
  useEffect(() => {
    const outputEl = document.getElementById('ia-validated-proposals');
    if (outputEl) {
      outputEl.textContent = JSON.stringify(validatedProposals);
    }
  }, [validatedProposals]);

  const handleValidate = (proposal: Proposal) => {
    setValidatedProposals(prev => [...prev, { id: proposal.id, response: proposal.response }]);
    setProposals(prev => prev.filter(p => p.id !== proposal.id));
    toast.success("Proposition validée");
  };

  const handleReject = (id: string) => {
    setProposals(prev => prev.filter(p => p.id !== id));
    toast.info("Proposition rejetée");
  };

  const handleUpdateResponse = (id: string, newText: string) => {
    setProposals(prev => prev.map(p => p.id === id ? { ...p, response: newText } : p));
  };

  const handleConductorWhatsApp = (conductor: Conductor) => {
    window.open(conductor.whatsappLink, '_blank');
    toast.success(`Lien WhatsApp ouvert pour ${conductor.name}`);
  };

  const handleRemoveConductor = (name: string) => {
    setConductors(prev => prev.filter(c => c.name !== name));
  };

  return (
    <div className="space-y-10 text-left">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <h2 className="text-xs font-black uppercase text-slate-400 tracking-widest border-l-4 border-indigo-500 pl-3">Espace Validation Community Manager</h2>
        <button 
          onClick={loadProposals}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-700 shadow-lg shadow-indigo-600/20 transition-all active:scale-95"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Charger le Flux IA
        </button>
      </div>

      {/* Hidden Bridges */}
      <div id="ia-cm-proposals-input" className="hidden"></div>
      <div id="ia-validated-proposals" className="hidden text-[8px] opacity-0">[]</div>

      {/* SECTION 1 : PROPOSITIONS RÉPONSES (SOCIAL MEDIA) */}
      <div className="space-y-6">
        <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
          <MessageSquare className="w-4 h-4" /> Propositions de Réponses ({proposals.length})
        </h3>
        {proposals.length === 0 ? (
          <div className="py-8 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl text-center">
            <p className="text-[9px] font-black text-slate-300 uppercase tracking-widest">Aucune proposition de réponse</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {proposals.map((p) => (
              <div key={p.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all animate-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-1.5 bg-slate-100 px-2 py-1 rounded-md text-[10px] font-black text-slate-700">
                      <User className="w-3 h-3" /> {p.author}
                    </div>
                    <div className="flex items-center gap-1.5 bg-indigo-50 px-2 py-1 rounded-md text-[10px] font-black text-indigo-600">
                      <MapPin className="w-3 h-3" /> {p.route}
                    </div>
                    <span className="text-[8px] font-black px-1.5 py-0.5 bg-slate-900 text-white rounded uppercase">{p.type}</span>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleReject(p.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"><X className="w-4 h-4" /></button>
                    <button onClick={() => handleValidate(p)} className="p-2 bg-green-500 text-white hover:bg-green-600 rounded-xl shadow-lg shadow-green-500/20 transition-all active:scale-95"><Check className="w-4 h-4" /></button>
                  </div>
                </div>
                <p className="text-[10px] text-slate-400 font-medium italic mb-4">Contexte: {p.context}</p>
                <textarea 
                  value={p.response}
                  onChange={(e) => handleUpdateResponse(p.id, e.target.value)}
                  className="w-full min-h-[80px] bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs font-medium text-slate-800 focus:bg-white focus:border-indigo-300 focus:ring-2 focus:ring-indigo-500/10 outline-none transition-all resize-none"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* SECTION 2 : CONDUCTEURS À CONTACTER (WHATSAPP) */}
      <div className="space-y-6">
        <h3 className="text-[10px] font-black uppercase tracking-widest text-emerald-600 flex items-center gap-2">
          <Phone className="w-4 h-4" /> Conducteurs à Contacter ({conductors.length})
        </h3>
        {conductors.length === 0 ? (
          <div className="py-8 bg-emerald-50/30 border-2 border-dashed border-emerald-100 rounded-2xl text-center">
            <p className="text-[9px] font-black text-emerald-300 uppercase tracking-widest">Aucun conducteur à contacter</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {conductors.map((c, i) => (
              <div key={i} className="bg-emerald-50/50 border border-emerald-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all animate-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-1.5 bg-emerald-100 px-2 py-1 rounded-md text-[10px] font-black text-emerald-700">
                      <Car className="w-3 h-3" /> {c.name}
                    </div>
                    <div className="flex items-center gap-1.5 bg-white border border-emerald-100 px-2 py-1 rounded-md text-[10px] font-black text-emerald-600">
                      <MapPin className="w-3 h-3 text-emerald-400" /> {c.route}
                    </div>
                    <span className="text-[10px] font-bold text-emerald-500 tabular-nums">{c.phone}</span>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleRemoveConductor(c.name)} className="p-2 text-emerald-300 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"><X className="w-4 h-4" /></button>
                    <button 
                      onClick={() => handleConductorWhatsApp(c)}
                      className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-emerald-700 shadow-lg shadow-emerald-600/20 transition-all active:scale-95"
                    >
                      <MessageSquare className="w-3.5 h-3.5" /> WhatsApp Direct
                    </button>
                  </div>
                </div>
                <div className="bg-white/80 p-4 rounded-xl border border-emerald-100 text-xs font-medium text-emerald-900 italic leading-relaxed">
                  "{c.message}"
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
