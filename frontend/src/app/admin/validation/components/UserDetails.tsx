"use client";

import { UserListItem } from "@/types/user";
import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Mail, Phone, CheckCircle, XCircle, User, Split, 
  ChevronLeft, Sparkles, Loader2, AlertTriangle, 
  Info, ShieldAlert
} from "lucide-react";
import Image from "next/image";
import { DocumentCard } from "./DocumentCard";
import { ImageComparisonDialog } from "./ImageComparisonDialog";
import { analyzeDocumentsAction } from "../actions";
import { toast } from "sonner";

interface UserDetailsProps {
  selectedUser: UserListItem | null;
  onValidate: () => void;
  onAIComplete?: (newStatus: string) => void;
  onBack?: () => void;
}

export function UserDetails({ selectedUser, onValidate, onAIComplete, onBack }: UserDetailsProps) {
  const router = useRouter();
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [isPending, startTransition] = useTransition();

  if (!selectedUser) {
    return (
      <div className="h-[400px] flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/20 bg-muted/5">
        <p className="text-muted-foreground text-sm">Sélectionnez un utilisateur pour voir ses documents</p>
      </div>
    );
  }

  const handleAIAnalysis = () => {
    startTransition(async () => {
      const res = await analyzeDocumentsAction(selectedUser.uid);
      if (res.success) {
        toast.success("Analyse IA terminée");
        
        // Déterminer l'onglet de destination
        const targetTab = res.status === 'SUCCESS' ? 'ai_verified' : 'ai_alert';
        
        if (onAIComplete) {
            onAIComplete(targetTab);
        } else {
            router.refresh();
        }
      } else {
        toast.error(res.message || "Échec de l'analyse");
      }
    });
  };

  const aiStatus = selectedUser.ai_validation_status;
  const aiReport = selectedUser.ai_validation_report;

  return (
    <>
      <div className="lg:hidden mb-4">
        <Button variant="ghost" onClick={onBack} className="gap-2 text-muted-foreground font-black uppercase text-[10px] tracking-widest">
          <ChevronLeft className="w-4 h-4" /> Retour à la liste
        </Button>
      </div>

      <Card className="border-klando-gold/20 overflow-hidden">
        <CardHeader className="bg-muted/30 pb-4">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div className="flex items-center gap-3 sm:gap-4">
              {selectedUser.photo_url ? (
                <div className="relative w-12 h-12 sm:w-16 sm:h-16 rounded-xl overflow-hidden border-2 border-white shadow-sm flex-shrink-0">
                  <Image
                    src={selectedUser.photo_url}
                    alt=""
                    fill
                    sizes="64px"
                    className="object-cover"
                  />
                </div>
              ) : (
                <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl bg-klando-burgundy text-white flex items-center justify-center text-xl sm:text-2xl font-black flex-shrink-0">
                  {(selectedUser.display_name || "?").charAt(0).toUpperCase()}
                </div>
              )}
              <div className="min-w-0">
                <CardTitle className="text-lg sm:text-xl font-black uppercase tracking-tight truncate">
                  {selectedUser.display_name}
                </CardTitle>
                {(selectedUser.first_name || selectedUser.name) && (
                    <p className="text-[9px] sm:text-[10px] font-black text-klando-gold uppercase tracking-widest -mt-0.5 truncate">
                        {selectedUser.first_name || "?"} {selectedUser.name || "?"}
                    </p>
                )}
                <div className="flex flex-wrap gap-x-3 gap-y-1 mt-1 text-[11px] sm:text-sm text-muted-foreground">
                  <div className="flex items-center gap-1.5 truncate max-w-[150px] sm:max-w-none">
                    <Mail className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                    <span className="truncate">{selectedUser.email}</span>
                  </div>
                  <div className="flex items-center gap-1.5 whitespace-nowrap">
                    <Phone className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                    {selectedUser.phone_number}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-2 border-t sm:border-t-0 border-slate-200/50 pt-3 sm:pt-0">
              <div className="flex flex-wrap gap-1.5 sm:gap-2">
                {aiStatus && aiStatus !== 'PENDING' && (
                  <Badge 
                    className={cn(
                      "font-black text-[8px] sm:text-[9px] tracking-widest uppercase px-1.5 sm:px-2 py-0.5",
                      aiStatus === 'SUCCESS' ? "bg-green-500 text-white" : 
                      aiStatus === 'WARNING' ? "bg-orange-500 text-white" : "bg-red-600 text-white"
                    )}
                  >
                    IA: {aiStatus}
                  </Badge>
                )}
                <Badge 
                  variant="outline" 
                  className={cn(
                    "font-black text-[8px] sm:text-[9px] tracking-widest uppercase px-1.5 sm:px-2 py-0.5 whitespace-nowrap",
                    selectedUser.is_driver_doc_validated 
                      ? "bg-green-500/10 text-green-600 border-green-500/20"
                      : "bg-yellow-500/10 text-yellow-600 border-yellow-500/20"
                  )}
                >
                  {selectedUser.is_driver_doc_validated ? "VALIDÉ" : "EN ATTENTE"}
                </Badge>
              </div>
              <div className="flex gap-1.5 sm:gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCompareOpen(true)}
                  className="h-7 sm:h-8 px-2 sm:px-3 gap-1.5 text-[8px] sm:text-[10px] font-black uppercase tracking-widest border-klando-gold/30 text-klando-gold hover:bg-klando-gold/10"
                >
                  <Split className="w-3 h-3" />
                  <span className="hidden xs:inline">Comparer</span>
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAIAnalysis}
                  disabled={isPending}
                  className="h-7 sm:h-8 px-2 sm:px-3 gap-1.5 text-[8px] sm:text-[10px] font-black uppercase tracking-widest border-purple-500/30 text-purple-600 hover:bg-purple-50"
                >
                  {isPending ? <Loader2 className="w-3 h-3 sm:w-3.5 sm:h-3.5 animate-spin" /> : <Sparkles className="w-3 h-3 sm:w-3.5 sm:h-3.5" />}
                  <span className="hidden xs:inline">Analyse IA</span>
                  <span className="xs:hidden">IA</span>
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4 sm:p-6 space-y-8">
          
          {/* AI REPORT SUMMARY */}
          {aiReport && (
            <div className={cn(
              "p-4 rounded-2xl border-2 space-y-4",
              aiStatus === 'SUCCESS' ? "bg-green-50/50 border-green-100" : 
              aiStatus === 'WARNING' ? "bg-orange-50/50 border-orange-100" : "bg-red-50/50 border-red-100"
            )}>
              <div className="flex items-center justify-between border-b border-slate-200/50 pb-2">
                <div className="flex items-center gap-2">
                  <Sparkles className={cn("w-4 h-4", aiStatus === 'SUCCESS' ? "text-green-600" : "text-purple-600")} />
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-900">Données extraites par IA</h4>
                </div>
                <span className="text-[9px] font-bold text-muted-foreground italic">
                  Analyse du {new Date(aiReport.analyzed_at).toLocaleDateString()}
                </span>
              </div>

              {/* TABLEAU DES DONNÉES EN DUR (BASE DE DONNÉES) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* BLOC CNI */}
                <div className="space-y-2">
                    <p className="text-[9px] font-black uppercase text-slate-400 flex items-center gap-2">
                        <User className="w-3 h-3" /> Carte d&apos;Identité
                    </p>
                    <div className="bg-white/80 rounded-xl border border-slate-200 p-4 space-y-4 shadow-sm">
                        <div className="flex flex-col gap-1.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-black uppercase text-slate-400 leading-none">Extraction IA</span>
                                {aiReport.reports?.id_card?.nameMatchesProfile ? (
                                    <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none text-[9px] h-5 px-2 font-black uppercase">NOM CONFORME</Badge>
                                ) : (
                                    <Badge className="bg-red-100 text-red-700 hover:bg-red-100 border-none text-[9px] h-5 px-2 font-black uppercase">NOM DIFFERENT</Badge>
                                )}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 tracking-tight">Nom lu sur ID</span>
                                <span className="text-sm font-black text-slate-900 leading-tight">{selectedUser.id_card_first_name_ai} {selectedUser.id_card_last_name_ai}</span>
                            </div>
                            {aiReport.reports?.id_card?.nameMatchesProfile && (
                                <div className="flex items-center gap-2 bg-green-50 px-3 py-1.5 rounded-lg border border-green-100 mt-1">
                                    <CheckCircle className="w-3 h-3 text-green-600" />
                                    <span className="text-[10px] font-black text-green-700 uppercase tracking-tight">Profil : {selectedUser.first_name} {selectedUser.name}</span>
                                </div>
                            )}
                        </div>
                        <div className="grid grid-cols-2 gap-4 border-t border-slate-50 pt-3">
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 leading-none mb-1">Numéro</span>
                                <span className="text-xs font-mono font-bold text-purple-700 tracking-tighter">{selectedUser.id_card_number || "N/A"}</span>
                                {aiReport.reports?.id_card?.isUnique === false && (
                                    <span className="text-[9px] font-black text-red-600 uppercase mt-1 flex items-center gap-1">⚠️ Doublon</span>
                                )}
                                {aiReport.reports?.id_card?.isUnique === true && (
                                    <span className="text-[9px] font-black text-green-600 uppercase mt-1 flex items-center gap-1">✅ Unique</span>
                                )}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 leading-none mb-1">Expiration</span>
                                <span className="text-xs font-bold text-slate-700">{selectedUser.id_card_expiry_ai || "N/A"}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* BLOC PERMIS */}
                <div className="space-y-2">
                    <p className="text-[9px] font-black uppercase text-slate-400 flex items-center gap-2">
                        <Split className="w-3 h-3" /> Permis de conduire
                    </p>
                    <div className="bg-white/80 rounded-xl border border-slate-200 p-4 space-y-4 shadow-sm">
                        <div className="flex flex-col gap-1.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-black uppercase text-slate-400 leading-none">Extraction IA</span>
                                {aiReport.reports?.driver_license?.nameMatchesProfile ? (
                                    <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none text-[9px] h-5 px-2 font-black uppercase">NOM CONFORME</Badge>
                                ) : (
                                    <Badge className="bg-red-100 text-red-700 hover:bg-red-100 border-none text-[9px] h-5 px-2 font-black uppercase">NOM DIFFERENT</Badge>
                                )}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 tracking-tight">Nom lu sur Permis</span>
                                <span className="text-sm font-black text-slate-900 leading-tight">{selectedUser.driver_license_first_name_ai} {selectedUser.driver_license_last_name_ai}</span>
                            </div>
                            {aiReport.reports?.driver_license?.nameMatchesProfile && (
                                <div className="flex items-center gap-2 bg-green-50 px-3 py-1.5 rounded-lg border border-green-100 mt-1">
                                    <CheckCircle className="w-3 h-3 text-green-600" />
                                    <span className="text-[10px] font-black text-green-700 uppercase tracking-tight">Profil : {selectedUser.first_name} {selectedUser.name}</span>
                                </div>
                            )}
                        </div>
                        <div className="grid grid-cols-2 gap-4 border-t border-slate-50 pt-3">
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 leading-none mb-1">Numéro</span>
                                <span className="text-xs font-mono font-bold text-purple-700 tracking-tighter">{selectedUser.driver_license_number || "N/A"}</span>
                                {aiReport.reports?.driver_license?.isUnique === false && (
                                    <span className="text-[9px] font-black text-red-600 uppercase mt-1 flex items-center gap-1">⚠️ Doublon</span>
                                )}
                                {aiReport.reports?.driver_license?.isUnique === true && (
                                    <span className="text-[9px] font-black text-green-600 uppercase mt-1 flex items-center gap-1">✅ Unique</span>
                                )}
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[9px] font-black uppercase text-slate-400 leading-none mb-1">Expiration</span>
                                <span className="text-xs font-bold text-slate-700">{selectedUser.driver_license_expiry_ai || "N/A"}</span>
                            </div>
                        </div>
                    </div>
                </div>
              </div>

              {aiReport.warnings && aiReport.warnings.length > 0 && (
                <div className="space-y-2 pt-2">
                  {aiReport.warnings.map((warning: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 bg-red-50/50 p-2.5 rounded-xl border border-red-100 shadow-sm">
                      {warning.includes("FRAUDE") ? (
                        <ShieldAlert className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                      )}
                      <p className="text-[11px] font-bold text-red-900 leading-tight">{warning}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <DocumentCard 
              title="Carte d'identité" 
              url={selectedUser.id_card_url} 
              type="id" 
            />
            <DocumentCard 
              title="Permis de conduire" 
              url={selectedUser.driver_license_url} 
              type="license" 
            />
          </div>

          <div className="mt-8 flex flex-col sm:flex-row gap-3 pt-4 border-t border-slate-100">
            <Button
              onClick={onValidate}
              className={cn(
                "flex-1 font-black uppercase text-[11px] tracking-widest text-white h-14 rounded-2xl shadow-xl transition-all",
                selectedUser.is_driver_doc_validated 
                  ? "bg-red-600 hover:bg-red-700 shadow-red-100" 
                  : "bg-green-600 hover:bg-green-700 shadow-green-100"
              )}
            >
              {selectedUser.is_driver_doc_validated ? (
                <XCircle className="w-5 h-5 mr-3" />
              ) : (
                <CheckCircle className="w-5 h-5 mr-3" />
              )}
              {selectedUser.is_driver_doc_validated ? "Invalider le conducteur" : "Approuver le conducteur"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="bg-blue-50 border border-blue-100 p-5 rounded-[2rem] flex gap-4 items-start shadow-inner">
        <div className="p-2 bg-blue-100 rounded-xl">
            <Info className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h4 className="text-xs font-black uppercase tracking-widest text-blue-900">Protocole de Validation</h4>
          <p className="text-[11px] text-blue-700 leading-relaxed mt-1 font-medium italic">
            {selectedUser.is_driver_doc_validated 
              ? "Ce conducteur a été validé. Vous pouvez révoquer son accès si les documents sont obsolètes."
              : "Utilisez la vérification IA pour détecter les doublons et extraire les numéros officiels. Vérifiez la cohérence entre le nom de profil et le nom sur les documents."}
          </p>
        </div>
      </div>

      <ImageComparisonDialog 
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        image1={selectedUser.id_card_url || null}
        image2={selectedUser.driver_license_url || null}
        label1="Carte d'identité"
        label2="Permis de conduire"
        userName={selectedUser.display_name || "Utilisateur"}
      />
    </>
  );
}
