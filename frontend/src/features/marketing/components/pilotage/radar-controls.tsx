"use client";

import { Target, Globe, Facebook, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface RadarControlsProps {
  showFacebook: boolean;
  setShowFacebook: (v: boolean) => void;
  showSite: boolean;
  setShowSite: (v: boolean) => void;
  showRadarOnly: boolean;
  setShowRadarOnly: (v: boolean) => void;
  hasSelection: boolean;
  onReset: () => void;
}

export function RadarControls({
  showFacebook, setShowFacebook,
  showSite, setShowSite,
  showRadarOnly, setShowRadarOnly,
  hasSelection, onReset
}: RadarControlsProps) {
  return (
    <div className="flex flex-wrap gap-3 items-center justify-between bg-slate-900 p-4 rounded-[2rem] border border-white/5 shadow-2xl">
      <div className="flex flex-wrap gap-2 items-center">
        {/* Toggle FACEBOOK */}
        <button
          onClick={() => setShowFacebook(!showFacebook)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showFacebook 
              ? "bg-blue-600 text-white border-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.4)]" 
              : "bg-slate-800/50 text-slate-500 border-slate-700 hover:text-slate-300"
          )}
        >
          <Facebook className="w-3.5 h-3.5" /> Facebook
        </button>

        {/* Toggle SITE */}
        <button
          onClick={() => setShowSite(!showSite)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showSite 
              ? "bg-emerald-600 text-white border-emerald-500 shadow-[0_0_15px_rgba(5,150,105,0.4)]" 
              : "bg-slate-800/50 text-slate-500 border-slate-700 hover:text-slate-300"
          )}
        >
          <Globe className="w-3.5 h-3.5" /> Site Web
        </button>

        {/* Toggle RADAR MATCH */}
        <button
          onClick={() => setShowRadarOnly(!showRadarOnly)}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
            showRadarOnly 
              ? "bg-klando-gold text-klando-dark border-klando-gold shadow-[0_0_15px_rgba(235,195,63,0.4)]" 
              : "bg-slate-800/50 text-slate-500 border-slate-700 hover:text-slate-300"
          )}
        >
          <Target className="w-3.5 h-3.5" /> Radar Match
        </button>
      </div>

      {hasSelection && (
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 bg-white text-slate-900 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-100 transition-all shadow-lg"
        >
          <X className="w-3.5 h-3.5" /> Reset Focus
        </button>
      )}
    </div>
  );
}
