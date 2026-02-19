"use client";

import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  BarChart3, 
  Calendar, 
  Clock, 
  Sparkles 
} from "lucide-react";
import { MarketingInsight } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

interface InsightDetailModalProps {
  insight: MarketingInsight | null;
  onClose: () => void;
}

export function InsightDetailModal({ insight, onClose }: InsightDetailModalProps) {
  if (!insight) return null;

  return (
    <Dialog open={!!insight} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl bg-slate-900 border-white/10 rounded-[2.5rem] p-0 overflow-hidden outline-none shadow-2xl">
        <div className="flex flex-col h-[85vh] bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 text-left">
          <div className="absolute top-0 right-0 p-12 opacity-5 pointer-events-none">
            <BarChart3 className="w-64 h-64 text-blue-400" />
          </div>

          <DialogHeader className="p-10 pb-8 border-b border-white/5 relative z-10 bg-white/[0.02]">
            <div className="flex items-center justify-between mb-6 text-left">
              <span className={cn(
                "text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-[0.2em] border shadow-sm",
                insight.category === "REVENUE" ? "bg-green-500/10 text-green-500 border-green-500/20" :
                insight.category === "CONVERSION" ? "bg-purple-500/10 text-purple-500 border-purple-500/20" :
                "bg-blue-500/10 text-blue-500 border-blue-500/20"
              )}>
                {insight.category}
              </span>
              <div className="flex items-center gap-6 text-[10px] font-bold text-muted-foreground/60 uppercase tracking-widest">
                <div className="flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5 text-klando-gold" />
                  {new Date(insight.created_at).toLocaleDateString("fr-FR")}
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-klando-gold" />
                  {new Date(insight.created_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </div>
            <DialogTitle className="text-3xl font-black text-white uppercase tracking-tight leading-tight mb-2 text-left">
              {insight.title}
            </DialogTitle>
            <DialogDescription className="text-[12px] font-black text-blue-400 uppercase tracking-[0.3em] flex items-center gap-2 text-left">
              <Sparkles className="w-3 h-3" /> Intelligence Stratégique
            </DialogDescription>
          </DialogHeader>
          
          <div className="flex-1 overflow-y-auto p-10 pt-8 custom-scrollbar relative z-10 text-left">
            <div className="max-w-none">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ ...props }) => <h1 className="text-xl font-black text-white uppercase tracking-tight mt-8 mb-4 border-l-4 border-klando-gold pl-4 text-left" {...props} />,
                  h2: ({ ...props }) => <h2 className="text-lg font-bold text-white uppercase tracking-tight mt-6 mb-3 text-left" {...props} />,
                  h3: ({ ...props }) => <h3 className="text-md font-bold text-blue-400 uppercase tracking-wide mt-4 mb-2 text-left" {...props} />,
                  p: ({ ...props }) => <p className="text-sm text-muted-foreground leading-relaxed mb-4 font-medium text-left" {...props} />,
                  ul: ({ ...props }) => <ul className="list-none space-y-2 mb-6 text-left" {...props} />,
                  li: ({ ...props }) => (
                    <li className="flex gap-3 text-sm text-muted-foreground font-medium items-start text-left">
                      <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-klando-gold shrink-0" />
                      <span {...props} />
                    </li>
                  ),
                  strong: ({ ...props }) => <strong className="font-bold text-white" {...props} />,
                  code: ({ ...props }) => <code className="bg-white/5 px-1.5 py-0.5 rounded text-blue-300 font-mono text-xs" {...props} />,
                  blockquote: ({ ...props }) => <blockquote className="border-l-4 border-white/10 pl-4 italic text-muted-foreground/80 my-6 bg-white/[0.02] p-4 rounded-r-xl text-left" {...props} />,
                }}
              >
                {insight.content}
              </ReactMarkdown>
            </div>
          </div>

          <div className="p-8 bg-white/[0.03] border-t border-white/5 flex justify-end relative z-10">
            <Button 
              onClick={onClose}
              className="rounded-2xl bg-white/5 hover:bg-white/10 text-white font-black text-[11px] uppercase px-10 h-12 tracking-[0.2em] transition-all border border-white/10"
            >
              Fermer l&apos;analyse
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
