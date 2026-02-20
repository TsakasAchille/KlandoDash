"use client";

import { useState } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogTrigger 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { History, Loader2, ExternalLink, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getChangelogAction } from "@/app/admin/actions/changelog";

// Cache simple hors du composant pour persister durant la session
let cachedChangelog: string | null = null;

export function ChangelogModal({ version }: { version: string }) {
  const [content, setContent] = useState<string | null>(cachedChangelog);
  const [isLoading, setIsLoading] = useState(false);

  const loadChangelog = async () => {
    if (content) return;
    setIsLoading(true);
    const data = await getChangelogAction();
    cachedChangelog = data;
    setContent(data);
    setIsLoading(false);
  };

  return (
    <Dialog onOpenChange={(open) => open && loadChangelog()}>
      <DialogTrigger asChild>
        <button className="flex items-center gap-2 text-slate-400 hover:text-klando-gold transition-all duration-300 group/btn">
          <div className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 group-hover/btn:border-klando-gold/30 transition-colors">
            <span className="text-[10px] font-mono font-bold">v{version}</span>
          </div>
          <ExternalLink className="w-3 h-3 opacity-0 group-hover/btn:opacity-100 transition-all -translate-x-1 group-hover/btn:translate-x-0" />
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[85vh] bg-[#081C36] border-white/10 text-white rounded-[2.5rem] shadow-2xl p-0 overflow-hidden gap-0">
        <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
            <History className="w-48 h-48 text-klando-gold" />
        </div>

        <DialogHeader className="p-8 border-b border-white/5 bg-white/5 backdrop-blur-md relative z-10">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-klando-gold/10 border border-klando-gold/20 shadow-lg shadow-klando-gold/5">
                <History className="w-6 h-6 text-klando-gold" />
            </div>
            <div>
                <DialogTitle className="text-2xl font-black uppercase tracking-tighter">
                    Notes de Version
                </DialogTitle>
                <DialogDescription className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mt-1">
                    Évolutions du système KlandoDash
                </DialogDescription>
            </div>
          </div>
        </DialogHeader>
        
        <div className="px-8 py-6 h-[60vh] overflow-y-auto custom-scrollbar relative z-10">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-full space-y-4">
              <Loader2 className="w-12 h-12 text-klando-gold animate-spin" />
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 animate-pulse">Synchronisation du journal...</p>
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none 
                prose-headings:uppercase prose-headings:tracking-tighter prose-headings:font-black 
                prose-h1:hidden
                prose-h2:text-xl prose-h2:text-klando-gold prose-h2:mt-10 prose-h2:mb-4 prose-h2:flex prose-h2:items-center prose-h2:gap-3
                prose-h3:text-xs prose-h3:text-blue-400 prose-h3:mt-6 prose-h3:tracking-[0.2em]
                prose-ul:list-none prose-ul:pl-0
                prose-li:bg-white/5 prose-li:border prose-li:border-white/5 prose-li:rounded-xl prose-li:p-4 prose-li:mb-2 prose-li:shadow-sm
                prose-p:text-slate-300 prose-p:leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content || ""}
              </ReactMarkdown>
            </div>
          )}
        </div>
        
        <div className="p-8 bg-black/20 border-t border-white/5 flex justify-between items-center relative z-10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-[9px] font-black uppercase tracking-widest text-slate-400">Système à jour</span>
          </div>
          <span className="text-[10px] font-black uppercase tracking-widest text-klando-gold bg-klando-gold/10 px-3 py-1 rounded-full border border-klando-gold/20">
            KlandoDash v{version}
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
