"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RoadmapItem, ICON_MAP, STAGE_CONFIG } from "../types";
import { cn } from "@/lib/utils";

interface TaskDialogsProps {
  isAddOpen: boolean;
  setIsAddOpen: (v: boolean) => void;
  isEditOpen: boolean;
  setIsEditOpen: (v: boolean) => void;
  editingItem: RoadmapItem | null;
  onAdd: (item: any) => void;
  onUpdate: (item: RoadmapItem) => void;
}

export function TaskDialogs({ 
  isAddOpen, setIsAddOpen, isEditOpen, setIsEditOpen, editingItem, onAdd, onUpdate 
}: TaskDialogsProps) {
  
  const [newItem, setNewItem] = useState({
    title: "", description: "", phase_name: "Phase 1: Automatisation & Temps Réel",
    timeline: "Court Terme", icon_name: "Target", is_planning: true,
    planning_stage: 'backlog', start_date: "", target_date: ""
  });

  const [localEditingItem, setLocalEditingItem] = useState<RoadmapItem | null>(null);

  useEffect(() => {
    if (editingItem) setLocalEditingItem(editingItem);
  }, [editingItem]);

  return (
    <>
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[500px]">
          <DialogHeader><DialogTitle>Nouvelle Tâche</DialogTitle></DialogHeader>
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
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Icône</label>
                <Select value={newItem.icon_name} onValueChange={v => setNewItem({...newItem, icon_name: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    {Object.keys(ICON_MAP).map(icon => <SelectItem key={icon} value={icon}>{icon}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
              <div className="space-y-0.5"><label className="text-sm font-medium">Dans le Planning ?</label></div>
              <div 
                className={cn("w-10 h-6 rounded-full p-1 cursor-pointer", newItem.is_planning ? "bg-klando-burgundy" : "bg-slate-700")}
                onClick={() => setNewItem({...newItem, is_planning: !newItem.is_planning})}
              >
                <div className={cn("w-4 h-4 bg-white rounded-full transition-transform", newItem.is_planning ? "translate-x-4" : "translate-x-0")} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddOpen(false)}>Annuler</Button>
            <Button className="bg-klando-gold text-black" onClick={() => onAdd(newItem)}>Créer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[500px]">
          <DialogHeader><DialogTitle>Modifier la tâche</DialogTitle></DialogHeader>
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

              <div className="grid grid-cols-2 gap-4">
                <Select value={localEditingItem.phase_name} onValueChange={v => setLocalEditingItem({...localEditingItem, phase_name: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    <SelectItem value="Phase 0: Réalisations Récentes">Phase 0: Réalisations</SelectItem>
                    <SelectItem value="Phase 1: Automatisation & Temps Réel">Phase 1: Automatisation</SelectItem>
                    <SelectItem value="Phase 2: Intelligence & Reporting">Phase 2: Intelligence</SelectItem>
                    <SelectItem value="Phase 3: Intelligence & Scale">Phase 3: Scale</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={localEditingItem.icon_name} onValueChange={v => setLocalEditingItem({...localEditingItem, icon_name: v})}>
                  <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-slate-800 text-white">
                    {Object.keys(ICON_MAP).map(icon => <SelectItem key={icon} value={icon}>{icon}</SelectItem>)}
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
