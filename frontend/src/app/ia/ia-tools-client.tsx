"use client";

import { useState, useEffect, Suspense, useRef } from "react";
import { Search, Send, User, Loader2, Phone, Mail, FileText, ImageIcon, X, UploadCloud } from "lucide-react";
import { searchHistoricalDrivers, createPropositionDraft, getUserInfo } from "./actions";
import { uploadMarketingImageAction } from "@/app/marketing/actions/mailing";
import { formatDateShort, cn } from "@/lib/utils";
import { toast } from "sonner";
import { useSearchParams } from "next/navigation";

function IAToolsContent() {
  const searchParams = useSearchParams();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
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
  
  // Image context state
  const [attachedImageUrl, setAttachedImageUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [aiBase64, setAiBase64] = useState(""); // For direct AI injection

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

  // Handle image upload from AI Base64 field
  useEffect(() => {
    if (aiBase64 && aiBase64.startsWith("data:image")) {
      handleBase64Upload(aiBase64);
    }
  }, [aiBase64]);

  const handleBase64Upload = async (base64: string) => {
    setIsUploading(true);
    try {
      const res = await uploadMarketingImageAction(base64);
      if (res.success && res.url) {
        setAttachedImageUrl(res.url);
        toast.success("Capture visuelle synchronisée !");
      }
    } catch (e) {
      toast.error("Erreur lors de l'upload de la capture.");
    } finally {
      setIsUploading(false);
      setAiBase64(""); // Clear the bridge
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = async () => {
      await handleBase64Upload(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

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
    
    const finalTarget = getRobustValue(contactTarget, "ia-contact-target");
    const finalSubject = getRobustValue(contactSubject, "ia-contact-subject");
    const finalMessage = getRobustValue(contactMessage, "ia-contact-message");

    if (!finalMessage || !finalSubject) {
      toast.error("L'objet et le message sont obligatoires.");
      return;
    }
    
    setIsSending(true);
    try {
      const result = await createPropositionDraft(finalTarget, finalSubject, finalMessage, attachedImageUrl || undefined);
      if (result.success) {
        toast.success("Brouillon créé avec capture visuelle !");
        setContactMessage("");
        setAttachedImageUrl(null);
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
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* 1. MOTEUR DE RECHERCHE HISTORIQUE */}
      <div className="lg:col-span-1 bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col h-fit">
        <h2 className="text-xs font-black uppercase text-slate-400 mb-6 tracking-widest border-l-4 border-klando-gold pl-3">
          Historique des Trajets
        </h2>
        <form onSubmit={(e) => handleSearch(e)} className="space-y-4 mb-6">
          <div className="flex flex-col gap-3">
            <input
              id="ia-search-origin"
              type="text"
              placeholder="Départ (ex: Dakar)"
              value={searchOrigin}
              onChange={(e) => setSearchOrigin(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none"
              data-gramm="false"
            />
            <input
              id="ia-search-dest"
              type="text"
              placeholder="Arrivée (ex: Thiès)"
              value={searchDest}
              onChange={(e) => setSearchDest(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none"
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
            RECHERCHER
          </button>
        </form>

        <div className="overflow-auto max-h-[400px]">
          {searchResults.length > 0 ? (
            <div className="space-y-2">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">{searchResults.length} conducteurs trouvés</p>
              {searchResults.map((driver) => (
                <div key={driver.uid} className="flex flex-col p-3 bg-slate-50 border border-slate-100 rounded gap-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden border border-slate-300">
                        {driver.photo_url ? <img src={driver.photo_url} alt="" /> : <User className="w-3 h-3 text-slate-400" />}
                      </div>
                      <p className="text-[11px] font-bold truncate max-w-[100px]">{driver.display_name}</p>
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
                  <p className="text-[9px] text-slate-500 italic">
                    {driver.matched_trip.departure?.split(',')[0]} → {driver.matched_trip.destination?.split(',')[0]} ({formatDateShort(driver.matched_trip.date)})
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 italic text-[10px] py-10 opacity-60">
              Saisissez un trajet pour interroger la mémoire.
            </div>
          )}
        </div>
      </div>

      {/* 2. CENTRE DE PRODUCTION & CAPTURE */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col gap-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <h2 className="text-xs font-black uppercase text-slate-400 tracking-widest border-l-4 border-klando-burgundy pl-3">
            Préparer une Proposition
          </h2>
          {attachedImageUrl && (
            <div className="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-[10px] font-bold animate-pulse">
              <ImageIcon className="w-3 h-3" /> CAPTURE ATTACHÉE
            </div>
          )}
        </div>
        
        {/* Row Upper: User Info & Image Dropzone */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User Card Display */}
          <div className="p-4 bg-slate-900 text-white rounded-lg flex flex-col justify-center min-h-[100px]">
            {isLoadingUser ? (
              <div className="flex items-center gap-2 text-[10px] opacity-50 uppercase font-bold justify-center">
                <Loader2 className="w-3 h-3 animate-spin" /> Analyse ID...
              </div>
            ) : targetUserInfo ? (
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-klando-gold shrink-0">
                  <img src={targetUserInfo.photo_url || "/logo-klando-sans-fond.png"} alt="" className="w-full h-full object-cover" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-black uppercase tracking-tight truncate">{targetUserInfo.display_name}</p>
                  <p className="text-[10px] text-klando-gold font-bold flex items-center gap-1">
                    <Phone className="w-2.5 h-2.5" /> {targetUserInfo.phone_number || "NON RENSEIGNÉ"}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate mt-0.5">{targetUserInfo.email}</p>
                </div>
              </div>
            ) : contactTarget.trim().length > 0 ? (
              <div className="text-[10px] text-blue-400 uppercase font-black text-center">
                Cible manuelle: "{contactTarget}"
              </div>
            ) : (
              <div className="text-[10px] opacity-50 uppercase font-black text-center">
                Cible (ID, Email ou GLOBAL)
              </div>
            )}
          </div>

          {/* Image Upload / Capture Hub */}
          <div 
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "border-2 border-dashed rounded-lg flex flex-col items-center justify-center p-4 cursor-pointer transition-all min-h-[100px] overflow-hidden group",
              attachedImageUrl ? "border-emerald-500 bg-emerald-50/30" : "border-slate-200 bg-slate-50 hover:border-klando-gold hover:bg-slate-100"
            )}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept="image/*" 
              className="hidden" 
            />
            {isUploading ? (
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            ) : attachedImageUrl ? (
              <div className="relative w-full h-full group">
                <img src={attachedImageUrl} alt="Context" className="h-16 w-auto mx-auto rounded shadow-sm object-cover" />
                <button 
                  onClick={(e) => { e.stopPropagation(); setAttachedImageUrl(null); }}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <>
                <UploadCloud className="w-6 h-6 text-slate-400 mb-2 group-hover:text-klando-gold" />
                <p className="text-[9px] font-black text-slate-400 uppercase group-hover:text-klando-gold">Capture Facebook / Preuve</p>
                <p className="text-[8px] text-slate-400 italic">Clic ou Coller Base64 ci-dessous</p>
              </>
            )}
          </div>
        </div>

        {/* Hidden Bridge for AI Image injection */}
        <div className="hidden">
          <textarea id="ia-image-base64"></textarea>
          <button 
            id="ia-image-upload-button" 
            type="button" 
            onClick={() => {
              const el = document.getElementById('ia-image-base64') as HTMLTextAreaElement;
              const val = el?.value;
              if (val && val.startsWith('data:image')) {
                handleBase64Upload(val);
                el.value = ''; // Clean up after
              } else {
                toast.error("Format d'image invalide (doit commencer par data:image)");
              }
            }}
          >Upload</button>
        </div>

        <form onSubmit={handleCreateDraft} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1">Identifiant Cible</label>
              <input
                id="ia-contact-target"
                type="text"
                placeholder="ID, Email ou GLOBAL"
                value={contactTarget}
                onChange={(e) => setContactTarget(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none"
                data-gramm="false"
              />
            </div>
            <div>
              <label className="text-[10px] font-black uppercase text-slate-400 block mb-1">Objet Stratégique</label>
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
          <div className="flex-1 flex flex-col min-h-[200px]">
            <div className="flex justify-between items-center mb-1">
              <label className="text-[10px] font-black uppercase text-slate-400 block">Message de la Proposition</label>
              <span className="text-[9px] text-klando-burgundy font-bold animate-pulse">💡 PERSONNALISEZ LE NOM</span>
            </div>
            <textarea
              id="ia-contact-message"
              placeholder={`Bonjour ${targetUserInfo?.display_name || "[Nom]"}, vu la capture ci-jointe, il y a une forte demande...`}
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
              className="flex-1 w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none resize-none"
              required
              data-gramm="false"
            ></textarea>
          </div>
          <button
            id="ia-create-draft-button"
            type="submit"
            disabled={isSending || isUploading}
            className="w-full bg-klando-burgundy text-white py-4 rounded text-xs font-bold hover:bg-klando-burgundy/90 flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-md shadow-klando-burgundy/20"
          >
            {isSending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> GÉNÉRATION DU BROUILLON...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" /> ENVOYER AU CENTRE ÉDITORIAL
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
    <Suspense fallback={<div className="p-10 text-center text-xs text-slate-400 animate-pulse font-mono tracking-widest">CHARGEMENT DU HUB DE DONNÉES BRUTES...</div>}>
      <IAToolsContent />
    </Suspense>
  );
}
