"use client";

import { useState } from "react";
import {
  Target, Globe, Facebook, BarChart3, Car,
  ChevronDown, ChevronRight, MessageSquare, Crosshair, Users, Zap
} from "lucide-react";
import { SiteTripRequest } from "@/types/site-request";
import { cn } from "@/lib/utils";

/* ── Section Header ── */

function SectionHeader({
  icon: Icon, label, count, isOpen, onToggle, colorClass, bgClass
}: {
  icon: any;
  label: string;
  count: number;
  isOpen: boolean;
  onToggle: () => void;
  colorClass: string;
  bgClass: string;
}) {
  return (
    <button
      onClick={onToggle}
      className={cn("w-full flex items-center justify-between px-5 py-3 transition-all text-left", bgClass)}
    >
      <div className="flex items-center gap-2">
        <Icon className={cn("w-3.5 h-3.5", colorClass)} />
        <span className={cn("text-[10px] font-black uppercase tracking-[0.15em]", colorClass)}>
          {label}
        </span>
        <span className={cn(
          "text-[9px] font-black px-2 py-0.5 rounded-full",
          colorClass,
          bgClass === "bg-yellow-50/80" ? "bg-yellow-100" : "bg-white/60"
        )}>
          {count}
        </span>
      </div>
      {isOpen
        ? <ChevronDown className={cn("w-3.5 h-3.5", colorClass)} />
        : <ChevronRight className={cn("w-3.5 h-3.5", colorClass)} />
      }
    </button>
  );
}

/* ── Lead Item Universel avec Radar intégré ── */

function LeadItem({
  request, isSelected, onClick
}: {
  request: SiteTripRequest;
  isSelected: boolean;
  onClick: () => void;
}) {
  const matchCount = request.matches?.length || 0;
  const bestScore = matchCount > 0
    ? Math.round(Math.max(...request.matches!.map(m => m.proximity_score)) * 100)
    : 0;

  return (
    <div
      onClick={onClick}
      className={cn(
        "px-5 py-3 cursor-pointer transition-all border-l-4 hover:bg-slate-50/80",
        isSelected ? "bg-slate-50 border-l-klando-gold shadow-inner" : "border-l-transparent"
      )}
    >
      <div className="flex items-center justify-between text-left">
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center gap-1.5 text-[10px] font-black uppercase italic tracking-tight text-slate-900">
            <span className={cn(
              "not-italic px-1 rounded-[4px] text-[7px]",
              request.request_type === 'DRIVER' ? "bg-orange-100 text-orange-700" : "bg-purple-100 text-purple-700"
            )}>
              {request.request_type === 'DRIVER' ? "DRV" : "PSGR"}
            </span>
            <span>{request.origin_city || '?'}</span>
            <span className="text-slate-300">→</span>
            <span>{request.destination_city || '?'}</span>
          </div>
          <p className="text-[8px] font-bold text-slate-400 uppercase truncate max-w-[180px]">{request.contact_info}</p>
        </div>

        {/* Indicateur RADAR intégré */}
        {matchCount > 0 ? (
          <div className="flex flex-col items-end">
            <span className="text-[9px] font-black bg-klando-gold text-klando-dark px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
              <Target className="w-2.5 h-2.5" /> {matchCount}
            </span>
            <span className="text-[7px] font-bold text-klando-gold mt-0.5">{bestScore}% match</span>
          </div>
        ) : (
          <span className="text-[8px] font-bold text-slate-300 uppercase italic">No match</span>
        )}
      </div>
    </div>
  );
}

/* ── Lead Section ── */

function LeadSection({
  leads, selectedRequestId, onSelect, emptyLabel, icon, label, colorClass, bgClass, isOpen, onToggle
}: {
  leads: SiteTripRequest[];
  selectedRequestId: string | null;
  onSelect: (r: SiteTripRequest) => void;
  emptyLabel: string;
  icon: any;
  label: string;
  colorClass: string;
  bgClass: string;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <div>
      <SectionHeader icon={icon} label={label} count={leads.length} isOpen={isOpen} onToggle={onToggle} colorClass={colorClass} bgClass={bgClass} />
      {isOpen && (
        <div className="divide-y divide-slate-50">
          {leads.length === 0 && (
            <p className="px-5 py-6 text-[9px] text-slate-300 uppercase tracking-widest text-center italic">{emptyLabel}</p>
          )}
          {leads.map(r => (
            <LeadItem key={r.id} request={r} isSelected={selectedRequestId === r.id} onClick={() => onSelect(r)} />
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Sidebar Principal ── */

export interface RadarSidebarProps {
  showFlows: boolean;
  showFacebook: boolean;
  showSite: boolean;
  corridors: any[];
  facebookLeads: SiteTripRequest[];
  siteLeads: SiteTripRequest[];
  whatsappLeads: SiteTripRequest[];
  matchedProspects: SiteTripRequest[];
  selectedRequestId: string | null;
  selectedCorridor: any | null;
  onSelectCorridor: (c: any) => void;
  onSelectRequest: (r: SiteTripRequest) => void;
}

export function RadarSidebar({
  showFlows, showFacebook, showSite,
  corridors, facebookLeads, siteLeads, whatsappLeads,
  selectedRequestId, selectedCorridor,
  onSelectCorridor, onSelectRequest
}: RadarSidebarProps) {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    corridors: true, facebook: true, site: true, whatsapp: true
  });

  const toggleSection = (key: string) => {
    setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="flex flex-col h-full text-left">
      <div className="flex-1 overflow-y-auto no-scrollbar divide-y divide-slate-100 pb-20">

        {/* Axes de Traffic (Offre + Demande) */}
        {showFlows && (
          <div>
            <SectionHeader icon={BarChart3} label="Axes de Traffic" count={corridors.length} isOpen={openSections.corridors} onToggle={() => toggleSection('corridors')} colorClass="text-indigo-600" bgClass="bg-indigo-50/50" />
            {openSections.corridors && (
              <div className="divide-y divide-slate-50">
                {corridors.length > 0 ? corridors.map((c, i) => (
                  <div
                    key={i}
                    onClick={() => onSelectCorridor(c)}
                    className={cn(
                      "px-5 py-3 cursor-pointer transition-all border-l-4 hover:bg-indigo-50/30",
                      selectedCorridor?.origin === c.origin && selectedCorridor?.destination === c.destination
                        ? "bg-indigo-50/50 border-l-indigo-500 shadow-inner" : "border-l-transparent"
                    )}
                  >
                    <div className="flex items-center justify-between text-left">
                      <div className="flex items-center gap-1.5 text-[10px] font-black uppercase italic tracking-tight text-slate-900">
                        <span>{c.origin}</span>
                        <span className="text-slate-300">→</span>
                        <span>{c.destination}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {c.trips > 0 && (
                          <span className="text-[9px] font-black text-indigo-600 flex items-center gap-1">
                            <Car className="w-2.5 h-2.5" /> {c.trips}
                          </span>
                        )}
                        {c.leads > 0 && (
                          <span className="text-[9px] font-black text-pink-600 flex items-center gap-1">
                            <Users className="w-2.5 h-2.5" /> {c.leads}
                          </span>
                        )}
                      </div>
                    </div>
                    {c.trips > 0 && (
                      <div className="flex items-center gap-2 mt-1.5 text-left">
                        <div className="flex-1 h-1 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500 rounded-full transition-all" style={{ width: `${c.fill || 0}%` }} />
                        </div>
                        <span className="text-[8px] font-bold text-slate-400">{Math.round(c.fill || 0)}% fill</span>
                      </div>
                    )}
                  </div>
                )) : (
                  <p className="px-5 py-6 text-[9px] text-slate-300 uppercase tracking-widest text-center italic">Aucun axe actif</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Facebook Leads */}
        {showFacebook && (
          <LeadSection leads={facebookLeads} selectedRequestId={selectedRequestId} onSelect={onSelectRequest} emptyLabel="Aucun lead Facebook" icon={Facebook} label="Facebook" colorClass="text-blue-600" bgClass="bg-blue-50/50" isOpen={openSections.facebook} onToggle={() => toggleSection('facebook')} />
        )}

        {/* Site Web Leads */}
        {showSite && (
          <LeadSection leads={siteLeads} selectedRequestId={selectedRequestId} onSelect={onSelectRequest} emptyLabel="Aucun lead Site" icon={Globe} label="Site Web" colorClass="text-emerald-600" bgClass="bg-emerald-50/50" isOpen={openSections.site} onToggle={() => toggleSection('site')} />
        )}

        {/* WhatsApp Leads */}
        {whatsappLeads.length > 0 && (
          <LeadSection leads={whatsappLeads} selectedRequestId={selectedRequestId} onSelect={onSelectRequest} emptyLabel="" icon={MessageSquare} label="WhatsApp" colorClass="text-green-600" bgClass="bg-green-50/50" isOpen={openSections.whatsapp} onToggle={() => toggleSection('whatsapp')} />
        )}

      </div>
    </div>
  );
}
