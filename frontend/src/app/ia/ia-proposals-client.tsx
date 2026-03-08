"use client";

import { useState, useEffect } from "react";
import { Check, X, MessageSquare, User, MapPin, RefreshCw, Edit3 } from "lucide-react";
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

export function IAProposalsClient() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [validatedProposals, setValidatedProposals] = useState<any[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);

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
      if (Array.isArray(data)) {
        setProposals(data);
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <h2 className="text-xs font-black uppercase text-slate-400 tracking-widest border-l-4 border-indigo-500 pl-3">Propositions Community Manager</h2>
        <div className="flex items-center gap-2">
          <button 
            onClick={loadProposals}
            className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 text-indigo-600 rounded-lg text-[10px] font-black uppercase hover:bg-indigo-100 transition-colors"
          >
            <RefreshCw className="w-3 h-3" /> Charger JSON
          </button>
        </div>
      </div>

      {/* Hidden Bridges */}
      <div id="ia-cm-proposals-input" className="hidden"></div>
      <div id="ia-validated-proposals" className="hidden text-[8px] opacity-0">[]</div>

      {proposals.length === 0 ? (
        <div className="py-12 bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl text-center">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest italic">En attente de propositions de l'IA...</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {proposals.map((p) => (
            <div key={p.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all animate-in slide-in-from-bottom-2 duration-300">
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 bg-slate-100 px-2 py-1 rounded-md text-[10px] font-black text-slate-700">
                    <User className="w-3 h-3" /> {p.author}
                  </div>
                  <div className="flex items-center gap-1.5 bg-indigo-50 px-2 py-1 rounded-md text-[10px] font-black text-indigo-600">
                    <MapPin className="w-3 h-3" /> {p.route}
                  </div>
                  <span className="text-[8px] font-black px-1.5 py-0.5 bg-slate-900 text-white rounded uppercase">{p.type}</span>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleReject(p.id)}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleValidate(p)}
                    className="p-2 bg-green-500 text-white hover:bg-green-600 rounded-xl shadow-lg shadow-green-500/20 transition-all active:scale-95"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Context */}
              <p className="text-[10px] text-slate-400 font-medium italic mb-4 line-clamp-1">
                Context: {p.context}
              </p>

              {/* Response Editor */}
              <div className="relative group">
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Edit3 className="w-3 h-3 text-slate-300" />
                </div>
                <textarea 
                  value={p.response}
                  onChange={(e) => handleUpdateResponse(p.id, e.target.value)}
                  className="w-full min-h-[80px] bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs font-medium text-slate-800 focus:bg-white focus:border-indigo-300 focus:ring-2 focus:ring-indigo-500/10 outline-none transition-all resize-none"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
