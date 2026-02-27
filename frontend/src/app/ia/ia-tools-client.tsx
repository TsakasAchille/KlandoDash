"use client";

import { useState, useEffect, Suspense } from "react";
import { Search, Send, User, Loader2, Phone, Mail, FileText } from "lucide-react";
import { searchHistoricalDrivers, createPropositionDraft, getUserInfo } from "./actions";
import { formatDateShort } from "@/lib/utils";
import { toast } from "sonner";
import { useSearchParams } from "next/navigation";

function IAToolsContent() {
  const searchParams = useSearchParams();
  
  // Search state
  const [searchOrigin, setSearchOrigin] = useState("");
  const [searchDest, setSearchDest] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Proposition state
  const [contactTarget, setContactTarget] = useState("");
  const [contactSubject, setContactSubject] = useState("Opportunité de trajet sur Klando");
  const [contactMessage, setContactMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  
  // User info state
  const [targetUserInfo, setTargetUserInfo] = useState<any>(null);
  const [isLoadingUser, setIsLoadingUser] = useState(false);

  // Auto-search from URL parameters
  useEffect(() => {
    const urlOrigin = searchParams.get("origin");
    const urlDest = searchParams.get("dest");
    
    if (urlOrigin) setSearchOrigin(urlOrigin);
    if (urlDest) setSearchDest(urlDest);
    
    if (urlOrigin && urlDest) {
      const timer = setTimeout(() => {
        handleSearch(null, urlOrigin, urlDest);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [searchParams]);

  // Debounce user info fetching
  useEffect(() => {
    const trimmedTarget = contactTarget.trim();
    if (!trimmedTarget || trimmedTarget.length < 1) {
      setTargetUserInfo(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoadingUser(true);
      try {
        const info = await getUserInfo(trimmedTarget);
        setTargetUserInfo(info);
      } catch (e) {
        setTargetUserInfo(null);
      } finally {
        setIsLoadingUser(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [contactTarget]);

  // Helper to get value from state OR direct DOM (crucial for AI automation)
  const getRobustValue = (stateValue: string, elementId: string) => {
    if (stateValue.trim()) return stateValue.trim();
    if (typeof document !== 'undefined') {
      const el = document.getElementById(elementId) as HTMLInputElement;
      return el?.value?.trim() || "";
    }
    return "";
  };

  const handleSearch = async (e: React.FormEvent | null, manualOrigin?: string, manualDest?: string) => {
    if (e) e.preventDefault();
    
    const origin = manualOrigin || getRobustValue(searchOrigin, "ia-search-origin");
    const dest = manualDest || getRobustValue(searchDest, "ia-search-dest");
    
    if (!origin || !dest) {
      toast.error("Veuillez saisir un départ et une destination.");
      return;
    }
    
    setIsSearching(true);
    try {
      const results = await searchHistoricalDrivers(origin, dest);
      setSearchResults(results);
      if (results.length === 0 && !manualOrigin) toast.info("Aucun conducteur trouvé.");
    } catch (error) {
      toast.error("Erreur lors de la recherche.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Robust value collection (State or DOM)
    const finalTarget = getRobustValue(contactTarget, "ia-contact-target");
    const finalSubject = getRobustValue(contactSubject, "ia-contact-subject");
    const finalMessage = getRobustValue(contactMessage, "ia-contact-message");

    if (!finalMessage || !finalSubject) {
      toast.error("L'objet et le message sont obligatoires.");
      return;
    }
    
    setIsSending(true);
    try {
      const result = await createPropositionDraft(finalTarget, finalSubject, finalMessage);
      if (result.success) {
        toast.success("Brouillon créé dans le Centre Éditorial !");
        setContactMessage("");
        // Also clear DOM if needed
        if (typeof document !== 'undefined') {
          (document.getElementById('ia-contact-message') as HTMLTextAreaElement).value = "";
        }
      } else {
        toast.error(result.error || "Échec de la création.");
      }
    } catch (error) {
      toast.error("Erreur technique lors de la création.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* MOTEUR DE RECHERCHE HISTORIQUE */}
      <div className="bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col">
        <h2 className="text-xs font-black uppercase text-slate-400 mb-6 tracking-widest border-l-4 border-klando-gold pl-3">
          Historique des Trajets
        </h2>
        <form onSubmit={(e) => handleSearch(e)} className="space-y-4 mb-6">
          <div className="flex gap-3">
            <input
              id="ia-search-origin"
              type="text"
              placeholder="Départ (ex: Dakar)"
              value={searchOrigin}
              onChange={(e) => setSearchOrigin(e.target.value)}
              className="flex-1 bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none"
              data-gramm="false"
            />
            <input
              id="ia-search-dest"
              type="text"
              placeholder="Arrivée (ex: Thiès)"
              value={searchDest}
              onChange={(e) => setSearchDest(e.target.value)}
              className="flex-1 bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none"
              data-gramm="false"
            />
          </div>
          <button
            id="ia-search-button"
            type="submit"
            disabled={isSearching}
            className="w-full bg-slate-900 text-white py-2 rounded text-xs font-bold hover:bg-slate-800 flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isSearching ? <Loader2 className="w-3 h-3 animate-spin" /> : <Search className="w-3 h-3" />}
            RECHERCHER DES CONDUCTEURS
          </button>
        </form>

        <div className="flex-1 overflow-auto max-h-[300px]">
          {searchResults.length > 0 ? (
            <div className="space-y-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">{searchResults.length} conducteurs trouvés</p>
              {searchResults.map((driver) => (
                <div key={driver.uid} className="flex items-center justify-between p-2 bg-slate-50 border border-slate-100 rounded">
                  <div className="flex items-center gap-3">
                    {driver.photo_url ? (
                      <img src={driver.photo_url} alt="" className="w-8 h-8 rounded-full border border-slate-200" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                        <User className="w-4 h-4 text-slate-400" />
                      </div>
                    )}
                    <div>
                      <p className="text-xs font-bold leading-none">{driver.display_name}</p>
                      <p className="text-[10px] text-slate-500 mt-1 flex items-center gap-1">
                        <Phone className="w-2.5 h-2.5" /> {driver.phone_number || "Pas de tel"}
                      </p>
                      <p className="text-[9px] text-klando-gold font-bold mt-1 uppercase">
                        Historique: {driver.matched_trip.departure?.split(',')[0]} → {driver.matched_trip.destination?.split(',')[0]} ({formatDateShort(driver.matched_trip.date)})
                      </p>
                    </div>
                  </div>
                  <button 
                    id={`ia-select-driver-${driver.uid}`}
                    type="button"
                    onClick={() => setContactTarget(driver.uid)}
                    className="text-[10px] font-bold text-klando-burgundy hover:underline uppercase"
                  >
                    Sélectionner
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 italic text-[10px] py-10 opacity-60">
              Saisissez un trajet pour voir la mémoire du système.
            </div>
          )}
        </div>
      </div>

      {/* FORMULAIRE DE PROPOSITION DRAFT */}
      <div className="bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col">
        <h2 className="text-xs font-black uppercase text-slate-400 mb-6 tracking-widest border-l-4 border-klando-burgundy pl-3">
          Préparer une Proposition
        </h2>
        
        {/* User Card Display */}
        <div className="mb-6 p-3 bg-slate-900 text-white rounded-lg flex items-center justify-between min-h-[60px]">
          {isLoadingUser ? (
            <div className="flex items-center gap-2 text-[10px] opacity-50 uppercase font-bold w-full justify-center">
              <Loader2 className="w-3 h-3 animate-spin" /> Recherche en cours...
            </div>
          ) : targetUserInfo ? (
            <>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-klando-gold">
                  <img src={targetUserInfo.photo_url || "/logo-klando-sans-fond.png"} alt="" className="w-full h-full object-cover" />
                </div>
                <div>
                  <p className="text-xs font-black uppercase tracking-tight">{targetUserInfo.display_name}</p>
                  <p className="text-[10px] text-klando-gold font-bold flex items-center gap-1">
                    <Phone className="w-2.5 h-2.5" /> {targetUserInfo.phone_number || "NUMÉRO MANQUANT"}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-[9px] opacity-50 uppercase font-black">Email</p>
                <p className={`text-[10px] truncate max-w-[120px] ${!targetUserInfo.email ? 'text-red-400 font-bold' : ''}`}>
                  {targetUserInfo.email || "EMAIL MANQUANT"}
                </p>
              </div>
            </>
          ) : contactTarget.trim().length > 0 ? (
            <div className="text-[10px] text-blue-400 uppercase font-black w-full text-center">
              Mode manuel: "{contactTarget}" sera utilisé comme cible.
            </div>
          ) : (
            <div className="text-[10px] opacity-50 uppercase font-black w-full text-center">
              Sélectionnez un conducteur, entrez un ID, un email, ou "GLOBAL"
            </div>
          )}
        </div>

        <form onSubmit={handleCreateDraft} className="flex flex-col flex-1 gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1">Cible (ID, Email ou GLOBAL)</label>
              <input
                id="ia-contact-target"
                type="text"
                placeholder="ex: user_123, test@mail.com ou GLOBAL"
                value={contactTarget}
                onChange={(e) => setContactTarget(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none"
                data-gramm="false"
              />
            </div>
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1">Objet du mail</label>
              <input
                id="ia-contact-subject"
                type="text"
                value={contactSubject}
                onChange={(e) => setContactSubject(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none"
                required
                data-gramm="false"
              />
            </div>
          </div>
          <div className="flex-1 flex flex-col min-h-[150px]">
            <div className="flex justify-between items-center mb-1">
              <label className="text-[10px] font-black uppercase text-slate-400 block">Message de proposition</label>
              <span className="text-[9px] text-klando-burgundy font-bold animate-pulse">💡 INDIQUEZ BIEN LE NOM ET PRÉNOM</span>
            </div>
            <textarea
              id="ia-contact-message"
              placeholder={`Bonjour ${targetUserInfo?.display_name || "[Nom]"}, nous avons remarqué une forte demande pour Dakar-Thiès. Seriez-vous disponible ?`}
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
              className="flex-1 w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none resize-none"
              required
              data-gramm="false"
            ></textarea>
            <p className="text-[9px] text-slate-400 mt-1 italic">
              Conseil : Personnalisez toujours le message avec le nom complet pour maximiser le taux de réponse.
            </p>
          </div>
          <button
            id="ia-create-draft-button"
            type="submit"
            disabled={isSending}
            className="w-full bg-klando-burgundy text-white py-3 rounded text-xs font-bold hover:bg-klando-burgundy/90 flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isSending ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" /> CRÉATION...
              </>
            ) : (
              <>
                <FileText className="w-3 h-3" /> CRÉER LE BROUILLON ÉDITORIAL
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export function IAToolsClient() {
  return (
    <Suspense fallback={<div className="p-10 text-center text-xs text-slate-400 animate-pulse">CHARGEMENT DU HUB...</div>}>
      <IAToolsContent />
    </Suspense>
  );
}
