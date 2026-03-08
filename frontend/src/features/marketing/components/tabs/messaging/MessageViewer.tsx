"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  FileText, ChevronRight, ChevronLeft, ImageIcon, Trash2, X, Edit3, Save, Loader2, Plus, Send,
  HelpCircle, Sparkles, PenLine, Mail, MessageSquare, Maximize2
} from "lucide-react";
import { MarketingMessage } from "@/app/marketing/types";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";

interface MessageViewerProps {
  message: MarketingMessage;
  onClose: () => void;
  onUpdate: (id: string, data: Partial<MarketingMessage>) => Promise<void>;
  onTrash: (id: string) => void;
  onConvertToDraft: (id: string) => void;
  onSend: (id: string) => void;
  isSaving: boolean;
  isTrashing: boolean;
  sendingMessageId: string | null;
  onMobileBack?: () => void;
}

export function MessageViewer({
  message,
  onClose,
  onUpdate,
  onTrash,
  onConvertToDraft,
  onSend,
  isSaving,
  isTrashing,
  sendingMessageId,
  onMobileBack
}: MessageViewerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingMessage>>({});
  const [selectedLightboxImage, setSelectedLightboxImage] = useState<string | null>(null);

  useEffect(() => {
    setEditForm({ 
      subject: message.subject || '', 
      content: message.content,
      images: message.images || (message.image_url ? [{ url: message.image_url, description: 'Image principale' }] : [])
    });
    setIsEditing(false);
    setShowReasoning(false);
  }, [message]);

  const handleSave = async () => {
    await onUpdate(message.id, editForm);
    setIsEditing(false);
  };

  const handleManualWhatsAppSend = () => {
    const text = message.content;
    const url = `https://wa.me/${message.recipient_contact.replace(/\D/g, '')}?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');
    onSend(message.id); // Mark as sent in DB
  };

  const removeImage = (index: number) => {
    setEditForm(prev => ({
      ...prev,
      images: (prev.images || []).filter((_, i) => i !== index)
    }));
  };

  const updateImageDescription = (index: number, desc: string) => {
    setEditForm(prev => ({
      ...prev,
      images: (prev.images || []).map((img, i) => i === index ? { ...img, description: desc } : img)
    }));
  };

  const insertImage = () => {
    const url = prompt("Entrez l'URL de l'image :");
    const description = prompt("Entrez une légende pour cette image :", "Capture visuelle");
    if (url) {
        setEditForm(prev => ({
          ...prev, 
          images: [...(prev.images || []), { url, description: description || 'Capture visuelle' }]
        }));
    }
  };

  const isWhatsApp = message.channel === 'WHATSAPP';

  // Custom components for Markdown to handle image clicks
  const markdownComponents = {
    img: ({ src, alt }: any) => (
      <div 
        className="relative group cursor-zoom-in my-4 inline-block max-w-full"
        onClick={() => setSelectedLightboxImage(src)}
      >
        <img 
          src={src} 
          alt={alt} 
          className="rounded-xl border border-slate-200 shadow-sm transition-transform group-hover:scale-[1.01]" 
        />
        <div className="absolute top-2 right-2 p-1.5 bg-black/50 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
          <Maximize2 className="w-3.5 h-3.5" />
        </div>
      </div>
    )
  };

  return (
    <div className="flex-1 bg-slate-50 border border-white/10 rounded-2xl lg:rounded-[2rem] overflow-hidden flex flex-col animate-in slide-in-from-right-4 duration-500 shadow-2xl h-full">
      <div className="p-4 lg:p-6 border-b border-slate-200 bg-white flex items-center justify-between">
        <div className="flex items-center gap-3 lg:gap-4 text-left min-w-0">
          {onMobileBack && (
            <button onClick={onMobileBack} className="lg:hidden p-1.5 -ml-1 rounded-lg hover:bg-slate-100 text-slate-500 shrink-0">
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div className={cn(
            "p-2 lg:p-2.5 rounded-xl border shadow-sm shrink-0",
            isWhatsApp ? "bg-green-50 text-green-600 border-green-100" : "bg-purple-50 text-purple-600 border-purple-100"
          )}>
            {isWhatsApp ? <MessageSquare className="w-5 h-5" /> : <Mail className="w-5 h-5" />}
          </div>
          <div className="flex-1 min-w-0">
            {isEditing ? (
                !isWhatsApp ? (
                  <Input 
                      value={editForm.subject || ''}
                      onChange={(e) => setEditForm({...editForm, subject: e.target.value})}
                      className="h-10 text-sm font-black uppercase tracking-tight bg-slate-100 border-slate-300 text-slate-900 w-full lg:min-w-[300px] outline-none focus:ring-purple-500/20"
                  />
                ) : (
                  <h4 className="text-sm font-black text-slate-900 uppercase tracking-tight">Message WhatsApp</h4>
                )
            ) : (
                <h4 className="text-sm font-black text-slate-900 uppercase tracking-tight line-clamp-1">
                  {isWhatsApp ? "WhatsApp Direct" : (message.subject || "(Sans objet)")}
                </h4>
            )}
            <p className="text-[10px] font-bold text-slate-600 uppercase mt-0.5 flex items-center gap-2">
              Canal: <span className={cn(isWhatsApp ? "text-green-600" : "text-blue-600")}>{message.channel}</span>
              {message.source && (
                <>
                  <span className="w-1 h-1 rounded-full bg-slate-300" />
                  Source: <span className="text-slate-900">{message.source}</span>
                </>
              )}
              {message.request_type && (
                <>
                  <span className="w-1 h-1 rounded-full bg-slate-300" />
                  Type: <span className={cn(message.request_type === 'DRIVER' ? "text-orange-600" : "text-purple-600")}>{message.request_type}</span>
                </>
              )}
              <span className="w-1 h-1 rounded-full bg-slate-300" />
              Vers: {message.recipient_contact}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
            {message.is_ai_generated && (
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowReasoning(!showReasoning)}
                    className={cn(
                        "h-8 text-[10px] uppercase font-black tracking-widest gap-2 rounded-xl",
                        showReasoning ? "bg-purple-100 text-purple-700" : "text-slate-500 hover:bg-slate-100"
                    )}
                >
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">Pourquoi ce message ?</span>
                </Button>
            )}
            <button onClick={onClose} className="hidden lg:block p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500 shrink-0">
                <ChevronRight className="w-5 h-5" />
            </button>
        </div>
      </div>

      <div className="flex-1 p-4 lg:p-8 overflow-y-auto custom-scrollbar text-left bg-white">
        {showReasoning && message.ai_reasoning && (
            <div className="mb-8 p-6 bg-purple-50 border border-purple-100 rounded-2xl animate-in slide-in-from-top-4 duration-300 text-left">
                <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-4 h-4 text-purple-600" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-purple-700">Raisonnement de l'IA</span>
                </div>
                <div className="text-sm text-purple-900 font-medium leading-relaxed italic prose-klando max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                        {message.ai_reasoning}
                    </ReactMarkdown>
                </div>
            </div>
        )}

        {isEditing ? (
            <div className="h-full flex flex-col gap-6 text-left">
                {!isWhatsApp && (
                  <div className="space-y-4">
                      <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
                          <ImageIcon className="w-3.5 h-3.5" /> Gérer les images ({(editForm.images || []).length})
                      </label>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {(editForm.images || []).map((img, idx) => (
                              <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-3 flex flex-col gap-2 relative group">
                                  <button 
                                      onClick={() => removeImage(idx)}
                                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg z-10 opacity-0 group-hover:opacity-100 transition-opacity"
                                  >
                                      <X className="w-3 h-3" />
                                  </button>
                                  <div 
                                    className="h-24 w-full rounded-lg bg-slate-900 overflow-hidden cursor-zoom-in"
                                    onClick={() => setSelectedLightboxImage(img.url)}
                                  >
                                      <img src={img.url} alt="" className="w-full h-full object-contain" />
                                  </div>
                                  <Input 
                                      value={img.description}
                                      onChange={(e) => updateImageDescription(idx, e.target.value)}
                                      className="h-8 text-[10px] font-bold bg-white"
                                      placeholder="Légende..."
                                  />
                              </div>
                          ))}
                          <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={insertImage}
                              className="h-24 border-dashed border-2 flex flex-col gap-2 rounded-xl text-slate-400 hover:text-purple-600 hover:border-purple-200"
                          >
                              <Plus className="w-5 h-5" />
                              <span className="text-[10px] font-black uppercase tracking-widest">Ajouter une capture</span>
                          </Button>
                      </div>
                  </div>
                )}

                <div className="flex-1 flex flex-col gap-2">
                    <label className="text-[10px] font-black uppercase text-slate-400 tracking-widest flex items-center gap-2">
                        <PenLine className="w-3.5 h-3.5" /> Contenu du message
                    </label>
                    <Textarea 
                        value={editForm.content}
                        onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                        className="flex-1 min-h-[300px] bg-slate-50 border-slate-300 text-slate-900 p-6 rounded-2xl font-medium leading-relaxed resize-none outline-none focus:ring-2 focus:ring-purple-500/20 text-left"
                    />
                </div>
            </div>
        ) : (
            <div className="space-y-6 text-left">
                <div className={cn(
                  "bg-slate-50 border border-slate-200 rounded-2xl p-8 text-sm text-slate-800 leading-relaxed font-medium shadow-sm text-left prose-klando max-w-none",
                  isWhatsApp && "border-l-8 border-l-[#25D366]"
                )}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                        {message.content}
                    </ReactMarkdown>
                </div>
                
                {/* MULTI-IMAGES DISPLAY (EMAIL ONLY FOR NOW) */}
                {!isWhatsApp && message.images && message.images.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                    {message.images.map((img, idx) => (
                      <div key={idx} className="space-y-2 group cursor-zoom-in" onClick={() => setSelectedLightboxImage(img.url)}>
                        <div className="rounded-2xl overflow-hidden border-2 border-slate-200 shadow-md bg-white p-1 relative">
                          <img src={img.url} alt={img.description} className="w-full h-auto object-cover rounded-xl transition-transform group-hover:scale-[1.02]" />
                          <div className="absolute top-4 right-4 p-2 bg-black/50 text-white rounded-xl opacity-0 group-hover:opacity-100 transition-opacity">
                            <Maximize2 className="w-4 h-4" />
                          </div>
                        </div>
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight text-center italic">
                          — {img.description}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : !isWhatsApp && message.image_url ? (
                    <div 
                      className="rounded-2xl overflow-hidden border-2 border-slate-200 shadow-lg max-w-[500px] mx-auto group relative bg-white p-2 cursor-zoom-in"
                      onClick={() => setSelectedLightboxImage(message.image_url!)}
                    >
                        <img src={message.image_url} alt="Aperçu du trajet" className="w-full h-auto object-cover rounded-xl transition-transform group-hover:scale-[1.01]" />
                        <div className="absolute top-6 right-6 p-2 bg-black/50 text-white rounded-xl opacity-0 group-hover:opacity-100 transition-opacity">
                          <Maximize2 className="w-4 h-4" />
                        </div>
                    </div>
                ) : null}
            </div>
        )}
      </div>

      <div className="p-4 lg:p-6 bg-slate-100 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
            {message.status !== 'TRASH' && (
                <Button 
                    variant="ghost" 
                    size="sm" 
                    disabled={isTrashing}
                    onClick={() => onTrash(message.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl uppercase font-black text-[10px] tracking-widest transition-colors"
                >
                    <Trash2 className="w-3.5 h-3.5 mr-2 text-red-600" /> <span>Supprimer</span>
                </Button>
            )}
            {!message.is_ai_generated && message.status === 'DRAFT' && (
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

            {message.status === 'DRAFT' && (
                message.is_ai_generated ? (
                    <Button 
                        onClick={() => onConvertToDraft(message.id)}
                        disabled={isSaving}
                        className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 gap-2 shadow-lg shadow-purple-500/20 transition-all active:scale-95"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Plus className="w-4 h-4 text-white" />}
                        Créer Brouillon
                    </Button>
                ) : (
                    !isEditing && (
                        <Button 
                            onClick={isWhatsApp ? handleManualWhatsAppSend : () => onSend(message.id)}
                            disabled={sendingMessageId === message.id}
                            className={cn(
                              "rounded-xl font-black text-[10px] uppercase tracking-widest px-10 h-11 gap-2 shadow-xl active:scale-95 transition-all",
                              isWhatsApp ? "bg-[#25D366] hover:bg-[#128C7E] text-white" : "bg-slate-900 text-white hover:bg-slate-800"
                            )}
                        >
                            {sendingMessageId === message.id ? (
                              <Loader2 className="w-4 h-4 animate-spin text-white" />
                            ) : (
                              isWhatsApp ? <MessageSquare className="w-4 h-4 text-white" /> : <Send className="w-4 h-4 text-white" />
                            )}
                            {isWhatsApp ? "Ouvrir WhatsApp" : "Envoyer par Email"}
                        </Button>
                    )
                )
            )}
        </div>
      </div>

      {/* LIGHTBOX DIALOG */}
      <Dialog open={!!selectedLightboxImage} onOpenChange={(open) => !open && setSelectedLightboxImage(null)}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0 border-none bg-transparent shadow-none overflow-hidden flex items-center justify-center">
          <DialogTitle className="sr-only">Aperçu de l'image</DialogTitle>
          {selectedLightboxImage && (
            <div className="relative w-full h-full flex items-center justify-center animate-in zoom-in-95 duration-300">
              <img 
                src={selectedLightboxImage} 
                alt="Full size preview" 
                className="max-w-full max-h-[90vh] object-contain rounded-2xl shadow-2xl border-4 border-white/10" 
              />
              <button 
                onClick={() => setSelectedLightboxImage(null)}
                className="absolute top-4 right-4 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
