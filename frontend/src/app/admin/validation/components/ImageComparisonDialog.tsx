"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { X, Split } from "lucide-react";
import Image from "next/image";

interface ImageComparisonDialogProps {
  isOpen: boolean;
  onClose: () => void;
  image1: string | null;
  image2: string | null;
  label1: string;
  label2: string;
  userName: string;
}

export function ImageComparisonDialog({
  isOpen,
  onClose,
  image1,
  image2,
  label1,
  label2,
  userName
}: ImageComparisonDialogProps) {
  if (!image1 && !image2) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-[95vw] h-[90vh] p-0 gap-0 overflow-hidden bg-klando-dark border-none">
        <DialogHeader className="p-4 bg-background/10 backdrop-blur-md border-b border-white/10 flex flex-row items-center justify-between space-y-0 absolute top-0 left-0 right-0 z-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-klando-gold/20 rounded-xl">
              <Split className="w-5 h-5 text-klando-gold" />
            </div>
            <div>
              <DialogTitle className="text-white font-black uppercase tracking-tight text-lg">
                Comparaison des documents
              </DialogTitle>
              <p className="text-white/60 text-[10px] font-bold uppercase tracking-widest">{userName}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition-colors text-white/70"
          >
            <X className="w-6 h-6" />
          </button>
        </DialogHeader>

        <div className="flex flex-col md:flex-row h-full pt-[72px] overflow-y-auto md:overflow-hidden pb-20 md:pb-0">
          {/* Image 1 */}
          <div className="flex-1 min-h-[40vh] md:min-h-0 relative group border-b md:border-b-0 md:border-r border-white/5">
            {image1 ? (
              <>
                <div className="absolute top-4 left-4 z-10">
                  <div className="px-3 py-1.5 bg-black/60 backdrop-blur-md border border-white/20 rounded-lg">
                    <span className="text-white text-[10px] font-black uppercase tracking-widest">{label1}</span>
                  </div>
                </div>
                <div className="w-full h-full p-4 md:p-8 flex items-center justify-center bg-zinc-900/50">
                  <div className="relative w-full h-full min-h-[30vh]">
                    <Image
                      src={image1}
                      alt={label1}
                      fill
                      className="object-contain"
                      unoptimized
                    />
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full h-full min-h-[20vh] flex items-center justify-center bg-zinc-900/50">
                <p className="text-white/20 font-bold uppercase tracking-tighter italic">Document manquant</p>
              </div>
            )}
          </div>

          {/* Image 2 */}
          <div className="flex-1 min-h-[40vh] md:min-h-0 relative group">
            {image2 ? (
              <>
                <div className="absolute top-4 left-4 z-10">
                  <div className="px-3 py-1.5 bg-black/60 backdrop-blur-md border border-white/20 rounded-lg">
                    <span className="text-white text-[10px] font-black uppercase tracking-widest">{label2}</span>
                  </div>
                </div>
                <div className="w-full h-full p-4 md:p-8 flex items-center justify-center bg-zinc-900/50">
                  <div className="relative w-full h-full min-h-[30vh]">
                    <Image
                      src={image2}
                      alt={label2}
                      fill
                      className="object-contain"
                      unoptimized
                    />
                  </div>
                </div>
              </>
            ) : (
              <div className="w-full h-full min-h-[20vh] flex items-center justify-center bg-zinc-900/50">
                <p className="text-white/20 font-bold uppercase tracking-tighter italic">Document manquant</p>
              </div>
            )}
          </div>
        </div>

        {/* Floating Instruction */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-6 py-2 bg-klando-gold text-klando-dark rounded-full font-black text-[10px] uppercase tracking-[0.2em] shadow-2xl z-50 pointer-events-none">
          Inspection visuelle des pièces justificatives
        </div>
      </DialogContent>
    </Dialog>
  );
}
