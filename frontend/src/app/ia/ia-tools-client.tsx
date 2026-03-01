"use client";

import { useState, useEffect, Suspense, useRef } from "react";
import { Search, Send, User, Loader2, Phone, Mail, FileText, ImageIcon, X, UploadCloud, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
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
  
  // Multi-Image state
  const [attachedImages, setAttachedImages] = useState<{ url: string; description: string }[]>([]);
  const [isUploading, setIsUploading] = useState(false);

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
      const timer = setTimeout(() => { handleSearch(null, urlOrigin, urlDest); }, 800);
      return () => clearTimeout(timer);
    }
  }, [searchParams]);

  // Image Upload Logic
  const handleBase64Upload = async (base64: string, description: string = "Capture Facebook") => {
    setIsUploading(true);
    try {
      const res = await uploadMarketingImageAction(base64);
      if (res.success && res.url) {
        setAttachedImages(prev => [...prev, { url: res.url!, description }]);
        toast.success("Image ajoutée à la proposition !");
      }
    } catch (e) {
      toast.error("Erreur lors de l'upload.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = async () => { await handleBase64Upload(reader.result as string); };
    reader.readAsDataURL(file);
  };

  const removeImage = (index: number) => {
    setAttachedImages(prev => prev.filter((_, i) => i !== index));
  };

  const updateImageDescription = (index: number, desc: string) => {
    setAttachedImages(prev => prev.map((img, i) => i === index ? { ...img, description: desc } : img));
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
    if (!origin || !dest) { toast.error("Veuillez saisir un départ et une destination."); return; }
    setIsSearching(true);
    try {
      const results = await searchHistoricalDrivers(origin, dest);
      setSearchResults(results);
    } catch (error) { toast.error("Erreur lors de la recherche."); } finally { setIsSearching(false); }
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalTarget = getRobustValue(contactTarget, "ia-contact-target");
    const finalSubject = getRobustValue(contactSubject, "ia-contact-subject");
    const finalMessage = getRobustValue(contactMessage, "ia-contact-message");
    if (!finalMessage || !finalSubject) { toast.error("L'objet et le message sont obligatoires."); return; }
    setIsSending(true);
    try {
      const result = await createPropositionDraft(finalTarget, finalSubject, finalMessage, attachedImages);
      if (result.success) {
        toast.success("Brouillon créé avec succès !");
        setContactMessage("");
        setAttachedImages([]);
        if (typeof document !== 'undefined') {
          (document.getElementById('ia-contact-message') as HTMLTextAreaElement).value = "";
        }
      } else {
        toast.error(result.error || "Échec de la création.");
      }
    } catch (error) { toast.error("Erreur technique."); } finally { setIsSending(false); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* 1. MOTEUR DE RECHERCHE */}
      <div className="lg:col-span-1 bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col h-fit">
        <h2 className="text-xs font-black uppercase text-slate-400 mb-6 tracking-widest border-l-4 border-klando-gold pl-3">Historique</h2>
        <form onSubmit={(e) => handleSearch(e)} className="space-y-4 mb-6">
          <div className="flex flex-col gap-3">
            <input id="ia-search-origin" type="text" placeholder="Départ" value={searchOrigin} onChange={(e) => setSearchOrigin(e.target.value)} className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none" data-gramm="false" />
            <input id="ia-search-dest" type="text" placeholder="Arrivée" value={searchDest} onChange={(e) => setSearchDest(e.target.value)} className="bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-gold outline-none" data-gramm="false" />
          </div>
          <button id="ia-search-button" type="submit" disabled={isSearching} className="w-full bg-slate-900 text-white py-2 rounded text-xs font-bold hover:bg-slate-800 flex items-center justify-center gap-2 transition-colors disabled:opacity-50">
            {isSearching ? <Loader2 className="w-3 h-3 animate-spin" /> : <Search className="w-3 h-3" />} RECHERCHER
          </button>
        </form>
        <div className="overflow-auto max-h-[400px]">
          {searchResults.map((driver) => (
            <div key={driver.uid} className="flex flex-col p-3 bg-slate-50 border border-slate-100 rounded gap-2 mb-2">
              <div className="flex items-center justify-between">
                <p className="text-[11px] font-bold truncate max-w-[100px]">{driver.display_name}</p>
                <button id={`ia-select-driver-${driver.uid}`} type="button" onClick={() => setContactTarget(driver.uid)} className="text-[10px] font-bold text-klando-burgundy hover:underline uppercase">Sélectionner</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. CENTRE DE PRODUCTION */}
      <div className="lg:col-span-2 bg-white border border-slate-200 rounded shadow-sm p-6 flex flex-col gap-6 text-left">
        <h2 className="text-xs font-black uppercase text-slate-400 tracking-widest border-l-4 border-klando-burgundy pl-3">Proposition multi-contextuelle</h2>
        
        {/* User Card */}
        <div className="p-4 bg-slate-900 text-white rounded-lg min-h-[80px] flex items-center">
          {targetUserInfo ? (
            <div className="flex items-center gap-4 w-full">
              <img src={targetUserInfo.photo_url || "/logo-klando-sans-fond.png"} alt="" className="w-10 h-10 rounded-full border-2 border-klando-gold object-cover" />
              <div className="flex-1 min-w-0"><p className="text-xs font-black uppercase truncate">{targetUserInfo.display_name}</p><p className="text-[10px] text-klando-gold font-bold">{targetUserInfo.phone_number}</p></div>
            </div>
          ) : <p className="text-[10px] opacity-50 uppercase font-black w-full text-center">{contactTarget ? `Cible manuelle: ${contactTarget}` : 'Sélectionnez un destinataire'}</p>}
        </div>

        {/* Multi-Image Zone */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest flex items-center gap-2"><ImageIcon className="w-3 h-3" /> Captures de Contexte ({attachedImages.length})</label>
            <Button onClick={() => fileInputRef.current?.click()} variant="outline" size="sm" className="h-7 text-[9px] font-black uppercase gap-1.5 rounded-lg border-slate-200">
              <Plus className="w-3 h-3" /> Ajouter une preuve
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {attachedImages.map((img, index) => (
              <div key={index} className="bg-slate-50 border border-slate-200 rounded-xl p-3 flex flex-col gap-3 relative group animate-in zoom-in-95 duration-200">
                <button onClick={() => removeImage(index)} className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg z-10 opacity-0 group-hover:opacity-100 transition-opacity"><X className="w-3 h-3" /></button>
                <div className="h-24 w-full rounded-lg bg-slate-900 overflow-hidden"><img src={img.url} alt="" className="w-full h-full object-contain" /></div>
                <input 
                  type="text" 
                  value={img.description} 
                  onChange={(e) => updateImageDescription(index, e.target.value)}
                  placeholder="Légende de l'image..."
                  className="w-full bg-white border border-slate-200 rounded px-2 py-1.5 text-[10px] font-bold text-slate-700 focus:ring-1 focus:ring-klando-burgundy outline-none"
                />
              </div>
            ))}
            {attachedImages.length === 0 && (
              <div onClick={() => fileInputRef.current?.click()} className="col-span-full border-2 border-dashed border-slate-200 rounded-xl h-24 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-50 transition-colors opacity-40">
                <UploadCloud className="w-6 h-6 text-slate-300" />
                <p className="text-[9px] font-black uppercase text-slate-400 mt-1">Glisser ou coller vos captures Facebook</p>
              </div>
            )}
          </div>
        </div>

        {/* Hidden Bridge for AI */}
        <div className="hidden">
          <textarea id="ia-image-base64"></textarea>
          <input id="ia-image-description" type="text" />
          <button id="ia-image-upload-button" type="button" onClick={() => {
            const area = document.getElementById('ia-image-base64') as HTMLTextAreaElement;
            const descInput = document.getElementById('ia-image-description') as HTMLInputElement;
            if (area?.value.startsWith('data:image')) {
              handleBase64Upload(area.value, descInput?.value || "Capture IA");
              area.value = ''; descInput.value = '';
            }
          }}>Upload</button>
        </div>

        <form onSubmit={handleCreateDraft} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black uppercase text-slate-400">Identifiant Cible</label>
              <input id="ia-contact-target" type="text" value={contactTarget} onChange={(e) => setContactTarget(e.target.value)} className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none" data-gramm="false" />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-black uppercase text-slate-400">Objet</label>
              <input id="ia-contact-subject" type="text" value={contactSubject} onChange={(e) => setContactSubject(e.target.value)} className="w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none" required data-gramm="false" />
            </div>
          </div>
          <div className="flex-1 flex flex-col min-h-[150px] space-y-1">
            <label className="text-[10px] font-black uppercase text-slate-400">Message</label>
            <textarea id="ia-contact-message" value={contactMessage} onChange={(e) => setContactMessage(e.target.value)} className="flex-1 w-full bg-slate-50 border border-slate-200 rounded px-3 py-2 text-xs focus:ring-1 focus:ring-klando-burgundy outline-none resize-none" required data-gramm="false"></textarea>
          </div>
          <button id="ia-create-draft-button" type="submit" disabled={isSending || isUploading} className="w-full bg-klando-burgundy text-white py-4 rounded text-xs font-black uppercase tracking-widest hover:bg-klando-burgundy/90 transition-colors disabled:opacity-50 shadow-lg shadow-klando-burgundy/20">
            {isSending ? <Loader2 className="w-4 h-4 animate-spin mr-2 inline" /> : <FileText className="w-4 h-4 mr-2 inline" />} Envoyer au Centre Éditorial
          </button>
        </form>
        <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />
      </div>
    </div>
  );
}

export function IAToolsClient() {
  return (
    <Suspense fallback={<div className="p-10 text-center text-xs text-slate-400 animate-pulse font-mono tracking-widest">CHARGEMENT DU HUB...</div>}>
      <IAToolsContent />
    </Suspense>
  );
}
