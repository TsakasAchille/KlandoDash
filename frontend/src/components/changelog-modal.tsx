"use client";

import { useState } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { History, Loader2, ExternalLink } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getChangelogAction } from "@/app/admin/actions/changelog";

export function ChangelogModal({ version }: { version: string }) {
  const [content, setContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadChangelog = async () => {
    if (content) return;
    setIsLoading(true);
    const data = await getChangelogAction();
    setContent(data);
    setIsLoading(false);
  };

  return (
    <Dialog onOpenChange={(open) => open && loadChangelog()}>
      <DialogTrigger asChild>
        <button className="flex items-center gap-2 hover:text-klando-gold transition-colors">
          <span className="text-[10px] font-mono">v{version}</span>
          <ExternalLink className="w-2.5 h-2.5 opacity-50" />
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] bg-klando-dark border-white/10 text-white rounded-[2rem]">
        <DialogHeader className="border-b border-white/5 pb-4">
          <DialogTitle className="flex items-center gap-3 text-xl font-black uppercase tracking-tight">
            <History className="w-6 h-6 text-klando-gold" />
            Notes de Version
          </DialogTitle>
        </DialogHeader>
        
        <div className="pr-4 mt-4 h-[60vh] overflow-y-auto custom-scrollbar">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground animate-pulse">Lecture du journal des modifications...</p>
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none prose-headings:uppercase prose-headings:tracking-tighter prose-headings:font-black prose-h2:text-klando-gold prose-h2:border-b prose-h2:border-white/5 prose-h2:pb-2">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content || ""}
              </ReactMarkdown>
            </div>
          )}
        </div>
        
        <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center text-[9px] font-black uppercase tracking-widest text-muted-foreground">
          <span>KlandoDash Core</span>
          <span className="text-klando-gold">Version stable active</span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
