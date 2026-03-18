"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RoadmapItem, ICON_MAP, STAGE_CONFIG, COLOR_PRESETS, PlanningBoard } from "../types";
import type { DashMember } from "@/lib/queries/admin";
import { cn } from "@/lib/utils";

interface TaskDialogsProps {
  isAddOpen: boolean;
  setIsAddOpen: (v: boolean) => void;
  isEditOpen: boolean;
  setIsEditOpen: (v: boolean) => void;
  editingItem: RoadmapItem | null;
  members: DashMember[];
  boards: PlanningBoard[];
  onAdd: (item: any) => void;
  onUpdate: (item: RoadmapItem) => void;
}

function MemberPicker({ members, selected, onChange }: { members: DashMember[]; selected: string[]; onChange: (v: string[]) => void }) {
  const toggle = (email: string) => {
    onChange(selected.includes(email) ? selected.filter(e => e !== email) : [...selected, email]);
  };

  return (
    <div className="space-y-1">
      <label className="text-[10px] uppercase font-bold text-slate-500">Assignés</label>
      <div className="flex flex-wrap gap-2 p-2 rounded-lg bg-white/5">
        {members.map(m => {
          const isActive = selected.includes(m.email);
          return (
            <button
              key={m.email}
              type="button"
              className={cn(
                "flex items-center gap-1.5 px-2 py-1 rounded-full border text-xs transition-all",
                isActive ? "border-klando-gold bg-klando-gold/20 text-klando-gold" : "border-white/10 text-slate-400 hover:border-white/30 hover:text-white"
              )}
              onClick={() => toggle(m.email)}
            >
              <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[7px] font-black shrink-0">
                {(m.display_name || m.email).split(' ').map(w => w[0]?.toUpperCase()).slice(0, 2).join('')}
              </div>
              <span className="font-medium">{m.display_name || m.email.split('@')[0]}</span>
            </button>
          );
        })}
        {members.length === 0 && <span className="text-xs text-slate-500 italic">Aucun membre</span>}
      </div>
    </div>
  );
}

export function TaskDialogs({
  isAddOpen, setIsAddOpen, isEditOpen, setIsEditOpen, editingItem, members, boards, onAdd, onUpdate
}: TaskDialogsProps) {

  const [newItem, setNewItem] = useState({
    title: "", description: "", phase_name: "Phase 1: Automatisation & Temps Réel",
    timeline: "Court Terme", icon_name: "Target", is_planning: true,
    planning_stage: 'backlog', start_date: "", target_date: "", custom_color: "",
    assigned_to: [] as string[], planning_board_id: "" as string
  });

  const [localEditingItem, setLocalEditingItem] = useState<RoadmapItem | null>(null);

  useEffect(() => {
    if (editingItem) setLocalEditingItem(editingItem);
  }, [editingItem]);

  return (
    <>
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Nouvelle Tâche</DialogTitle>
            <DialogDescription>Créer une nouvelle tâche dans le planning.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Input placeholder="Titre" className="bg-white/5 border-white/10" value={newItem.title} onChange={e => setNewItem({...newItem, title: e.target.value})} />
            <Textarea placeholder="Description" className="bg-white/5 border-white/10 h-24" value={newItem.description} onChange={e => setNewItem({...newItem, description: e.target.value})} />
            
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Temporalité</label>
                <Select value={newItem.planning_stage} onValueChange={v => setNewItem({...newItem, planning_stage: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    {Object.entries(STAGE_CONFIG).map(([key, config]) => (
                      <SelectItem key={key} value={key}>{config.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Début</label>
                <Input type="date" className="bg-white/5 border-white/10 text-xs" value={newItem.start_date} onChange={e => setNewItem({...newItem, start_date: e.target.value})} />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Fin (Jalon)</label>
                <Input type="date" className="bg-white/5 border-white/10 text-xs" value={newItem.target_date} onChange={e => setNewItem({...newItem, target_date: e.target.value})} />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-500">Couleur</label>
              <div className="flex flex-wrap gap-2 p-2 rounded-lg bg-white/5">
                <button
                  type="button"
                  className={cn("w-7 h-7 rounded-full border-2 text-[8px] font-bold text-slate-400", !newItem.custom_color ? "border-white ring-2 ring-white/30" : "border-white/10")}
                  onClick={() => setNewItem({...newItem, custom_color: ""})}
                  title="Auto (selon temporalité)"
                >Auto</button>
                {COLOR_PRESETS.map(c => (
                  <button
                    key={c.value}
                    type="button"
                    className={cn("w-7 h-7 rounded-full border-2 transition-all", newItem.custom_color === c.value ? "border-white ring-2 ring-white/30 scale-110" : "border-white/10 hover:scale-110")}
                    style={{ backgroundColor: c.value }}
                    onClick={() => setNewItem({...newItem, custom_color: c.value})}
                    title={c.label}
                  />
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] uppercase font-bold text-slate-500">Icône</label>
              <div className="flex flex-wrap gap-2 p-2 rounded-lg bg-white/5">
                {Object.entries(ICON_MAP).map(([name, Icon]) => (
                  <button
                    key={name}
                    type="button"
                    className={cn("w-8 h-8 rounded-lg flex items-center justify-center border transition-all", newItem.icon_name === name ? "border-klando-gold bg-klando-gold/20 text-klando-gold" : "border-white/10 text-slate-400 hover:text-white hover:border-white/30")}
                    onClick={() => setNewItem({...newItem, icon_name: name})}
                    title={name}
                  >
                    <Icon className="w-4 h-4" />
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Phase</label>
                <Select value={newItem.phase_name} onValueChange={v => setNewItem({...newItem, phase_name: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    <SelectItem value="Phase 0: Réalisations Récentes">Phase 0: Réalisations</SelectItem>
                    <SelectItem value="Phase 1: Automatisation & Temps Réel">Phase 1: Automatisation</SelectItem>
                    <SelectItem value="Phase 2: Intelligence & Reporting">Phase 2: Intelligence</SelectItem>
                    <SelectItem value="Phase 3: Intelligence & Scale">Phase 3: Scale</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <MemberPicker members={members} selected={newItem.assigned_to} onChange={v => setNewItem({...newItem, assigned_to: v})} />

            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div className="space-y-0.5"><label className="text-sm font-medium">Dans le Planning ?</label></div>
              <div
                className={cn("w-10 h-6 rounded-full p-1 cursor-pointer", newItem.is_planning ? "bg-klando-burgundy" : "bg-slate-700")}
                onClick={() => setNewItem({...newItem, is_planning: !newItem.is_planning})}
              >
                <div className={cn("w-4 h-4 bg-white rounded-full transition-transform", newItem.is_planning ? "translate-x-4" : "translate-x-0")} />
              </div>
            </div>

            {newItem.is_planning && boards.length > 0 && (
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Tableau</label>
                <Select value={newItem.planning_board_id || "none"} onValueChange={v => setNewItem({...newItem, planning_board_id: v === "none" ? "" : v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    <SelectItem value="none">Aucun (Backlog)</SelectItem>
                    {boards.map(b => <SelectItem key={b.id} value={b.id}>{b.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddOpen(false)}>Annuler</Button>
            <Button className="bg-klando-gold text-black" onClick={() => onAdd(newItem)}>Créer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Modifier la tâche</DialogTitle>
            <DialogDescription>Modifier les détails de la tâche.</DialogDescription>
          </DialogHeader>
          {localEditingItem && (
            <div className="space-y-4 py-4">
              <Input className="bg-white/5 border-white/10" value={localEditingItem.title} onChange={e => setLocalEditingItem({...localEditingItem, title: e.target.value})} />
              <Textarea className="bg-white/5 border-white/10 h-24" value={localEditingItem.description} onChange={e => setLocalEditingItem({...localEditingItem, description: e.target.value})} />
              
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Temporalité</label>
                  <Select value={localEditingItem.planning_stage} onValueChange={(v: any) => setLocalEditingItem({...localEditingItem, planning_stage: v})}>
                    <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-slate-800 text-white">
                      {Object.entries(STAGE_CONFIG).map(([key, config]) => (
                        <SelectItem key={key} value={key}>{config.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Début</label>
                  <Input type="date" className="bg-white/5 border-white/10 text-xs" value={localEditingItem.start_date || ""} onChange={e => setLocalEditingItem({...localEditingItem, start_date: e.target.value})} />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Fin</label>
                  <Input type="date" className="bg-white/5 border-white/10 text-xs" value={localEditingItem.target_date || ""} onChange={e => setLocalEditingItem({...localEditingItem, target_date: e.target.value})} />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Couleur</label>
                <div className="flex flex-wrap gap-2 p-2 rounded-lg bg-white/5">
                  <button
                    type="button"
                    className={cn("w-7 h-7 rounded-full border-2 text-[8px] font-bold text-slate-400", !localEditingItem.custom_color ? "border-white ring-2 ring-white/30" : "border-white/10")}
                    onClick={() => setLocalEditingItem({...localEditingItem, custom_color: null})}
                    title="Auto (selon temporalité)"
                  >Auto</button>
                  {COLOR_PRESETS.map(c => (
                    <button
                      key={c.value}
                      type="button"
                      className={cn("w-7 h-7 rounded-full border-2 transition-all", localEditingItem.custom_color === c.value ? "border-white ring-2 ring-white/30 scale-110" : "border-white/10 hover:scale-110")}
                      style={{ backgroundColor: c.value }}
                      onClick={() => setLocalEditingItem({...localEditingItem, custom_color: c.value})}
                      title={c.label}
                    />
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Icône</label>
                <div className="flex flex-wrap gap-2 p-2 rounded-lg bg-white/5">
                  {Object.entries(ICON_MAP).map(([name, Icon]) => (
                    <button
                      key={name}
                      type="button"
                      className={cn("w-8 h-8 rounded-lg flex items-center justify-center border transition-all", localEditingItem.icon_name === name ? "border-klando-gold bg-klando-gold/20 text-klando-gold" : "border-white/10 text-slate-400 hover:text-white hover:border-white/30")}
                      onClick={() => setLocalEditingItem({...localEditingItem, icon_name: name})}
                      title={name}
                    >
                      <Icon className="w-4 h-4" />
                    </button>
                  ))}
                </div>
              </div>

              <MemberPicker members={members} selected={localEditingItem.assigned_to || []} onChange={v => setLocalEditingItem({...localEditingItem, assigned_to: v})} />

              {boards.length > 0 && (
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Tableau</label>
                  <Select value={localEditingItem.planning_board_id || "none"} onValueChange={v => setLocalEditingItem({...localEditingItem, planning_board_id: v === "none" ? null : v})}>
                    <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                    <SelectContent className="bg-slate-800 text-white">
                      <SelectItem value="none">Aucun (Backlog)</SelectItem>
                      {boards.map(b => <SelectItem key={b.id} value={b.id}>{b.name}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Phase</label>
                <Select value={localEditingItem.phase_name} onValueChange={v => setLocalEditingItem({...localEditingItem, phase_name: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    <SelectItem value="Phase 0: Réalisations Récentes">Phase 0: Réalisations</SelectItem>
                    <SelectItem value="Phase 1: Automatisation & Temps Réel">Phase 1: Automatisation</SelectItem>
                    <SelectItem value="Phase 2: Intelligence & Reporting">Phase 2: Intelligence</SelectItem>
                    <SelectItem value="Phase 3: Intelligence & Scale">Phase 3: Scale</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditOpen(false)}>Annuler</Button>
            <Button className="bg-klando-gold text-black" onClick={() => localEditingItem && onUpdate(localEditingItem)}>Enregistrer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
