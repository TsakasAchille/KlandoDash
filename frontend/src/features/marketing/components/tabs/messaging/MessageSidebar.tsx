"use client";

import { Button } from "@/components/ui/button";
import {
  Plus, Sparkles, FileText, SendHorizontal, AlertCircle, Trash2
} from "lucide-react";
import { cn } from "@/lib/utils";

export type MessageFolder = 'SUGGESTIONS' | 'DRAFTS' | 'SENT' | 'FAILED' | 'TRASH';

interface MessageSidebarProps {
  activeFolder: MessageFolder;
  setActiveFolder: (f: MessageFolder) => void;
  onCompose: () => void;
  onScan: () => void;
  isScanning: boolean;
  counts: Record<string, number>;
}

export function MessageSidebar({
  activeFolder,
  setActiveFolder,
  onCompose,
  onScan,
  isScanning,
  counts
}: MessageSidebarProps) {
  return (
    <div className="w-full flex flex-col gap-2 text-left shrink-0">
      <Button
        onClick={onCompose}
        className="w-full h-11 lg:h-12 rounded-2xl bg-slate-900 text-white hover:bg-slate-800 font-black uppercase text-[9px] lg:text-[10px] tracking-widest gap-2 lg:gap-3 shadow-xl mb-2 border-none transition-all active:scale-95 group"
      >
        <Plus className="w-4 h-4 text-white group-hover:scale-110 transition-transform" />
        <span>Nouveau Message</span>
      </Button>

      {/* Folders: horizontal scroll on mobile, vertical on desktop */}
      <div className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-1 lg:pb-0 -mx-1 px-1 lg:mx-0 lg:px-0">
        <FolderItem
          icon={Sparkles}
          label="Suggestions ✨"
          count={counts.suggestions}
          active={activeFolder === 'SUGGESTIONS'}
          onClick={() => setActiveFolder('SUGGESTIONS')}
          color="text-purple-700"
        />
        <FolderItem
          icon={FileText}
          label="Brouillons"
          count={counts.drafts}
          active={activeFolder === 'DRAFTS'}
          onClick={() => setActiveFolder('DRAFTS')}
          color="text-blue-700"
        />
        <FolderItem
          icon={SendHorizontal}
          label="Envoyés"
          active={activeFolder === 'SENT'}
          onClick={() => setActiveFolder('SENT')}
          color="text-green-700"
        />
        <FolderItem
          icon={AlertCircle}
          label="Échecs"
          active={activeFolder === 'FAILED'}
          onClick={() => setActiveFolder('FAILED')}
          color="text-red-700"
        />
        <div className="lg:pt-4 lg:mt-4 lg:border-t border-slate-200">
          <FolderItem
              icon={Trash2}
              label="Corbeille"
              active={activeFolder === 'TRASH'}
              onClick={() => setActiveFolder('TRASH')}
              color="text-slate-600"
          />
        </div>
      </div>
    </div>
  );
}

interface FolderItemProps {
  icon: React.ElementType;
  label: string;
  active: boolean;
  onClick: () => void;
  count?: number;
  color?: string;
}

function FolderItem({ icon: Icon, label, active, onClick, count, color }: FolderItemProps) {
  const activeBg = color ? color.replace('text-', 'bg-') + '/15' : 'bg-slate-100';
  const hoverTextColor = color || "text-slate-900";

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-auto lg:w-full shrink-0 flex items-center justify-between px-3 lg:px-4 py-2.5 lg:py-3 rounded-xl transition-all duration-200 group whitespace-nowrap",
        active ? `${activeBg} shadow-sm border border-slate-200/50` : "text-slate-500 hover:bg-slate-100"
      )}
    >
      <div className="flex items-center gap-3">
        <Icon className={cn("w-4 h-4 transition-colors", active ? color : `text-slate-400 group-hover:${hoverTextColor}`)} />
        <span className={cn(
          "text-[11px] font-black uppercase tracking-widest transition-colors", 
          active ? color : `text-slate-500 group-hover:${hoverTextColor}`
        )}>
          {label}
        </span>
      </div>
      {count !== undefined && count > 0 && (
        <span className={cn(
            "text-[9px] font-black px-1.5 py-0.5 rounded-md transition-all border",
            active && color ? color.replace('text-', 'bg-') + '/20 ' + color + ' border-' + color.split('-')[1] + '-200' : `bg-slate-50 text-slate-400 border-slate-100 group-hover:${hoverTextColor}`
        )}>{count}</span>
      )}
    </button>
  );
}
