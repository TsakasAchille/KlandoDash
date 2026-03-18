"use client";

import { useState } from "react";
import { Calendar, Plus, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RoadmapItem, PlanningBoard } from "./types";
import { useRoadmap } from "./use-roadmap";
import { PlanningGantt } from "./components/planning-gantt";
import { TaskDialogs } from "./components/task-dialogs";
import type { DashMember } from "@/lib/queries/admin";

interface RoadmapViewProps {
  items: RoadmapItem[];
  members: DashMember[];
  boards: PlanningBoard[];
}

export function RoadmapView({ items, members, boards }: RoadmapViewProps) {
  const roadmap = useRoadmap(items);
  const [selectedBoardId, setSelectedBoardId] = useState<string | null>(null);

  // On considère maintenant que toutes les tâches sont destinées au planning
  const planningItems = items;
  const filteredPlanningItems = selectedBoardId
    ? planningItems.filter(i => i.planning_board_id === selectedBoardId)
    : planningItems;

  const roadmapProps = {
    updatingId: roadmap.updatingId,
    localProgress: roadmap.localProgress,
    onProgressChange: roadmap.handleProgressChange,
    onTogglePlanning: (id: string, isPlanning: boolean) => {
      const defaultBoard = selectedBoardId || boards[0]?.id || null;
      roadmap.handleTogglePlanning(id, isPlanning, isPlanning ? defaultBoard : null);
    },
    onDelete: roadmap.handleDelete,
    onEdit: (item: RoadmapItem) => {
      roadmap.setEditingItem(item);
      roadmap.setIsEditOpen(true);
    },
    onSetLocalProgress: (id: string, val: number) => {
      roadmap.setLocalProgress(prev => ({ ...prev, [id]: val }));
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-klando-gold/10 text-klando-gold border border-klando-gold/20">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-black text-white uppercase tracking-tight">Gantt Planning</h2>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">{filteredPlanningItems.length} Tâches au total</p>
          </div>
        </div>

        <Button onClick={() => roadmap.setIsAddOpen(true)} className="bg-klando-gold hover:bg-klando-gold/90 text-black font-bold">
          <Plus className="w-4 h-4 mr-2" /> Nouvelle Tâche
        </Button>
      </div>

      <PlanningGantt
        items={filteredPlanningItems}
        members={members}
        boards={boards}
        selectedBoardId={selectedBoardId}
        onBoardChange={setSelectedBoardId}
        {...roadmapProps}
      />

      <TaskDialogs
        isAddOpen={roadmap.isAddOpen}
        setIsAddOpen={roadmap.setIsAddOpen}
        isEditOpen={roadmap.isEditOpen}
        setIsEditOpen={roadmap.setIsEditOpen}
        editingItem={roadmap.editingItem}
        members={members}
        boards={boards}
        defaultBoardId={selectedBoardId}
        onAdd={roadmap.handleAdd}
        onUpdate={roadmap.handleUpdate}
      />

      <Card className="bg-gradient-to-br from-klando-burgundy/20 to-slate-900/50 border-klando-burgundy/30 mt-8">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-full bg-klando-burgundy/30 text-klando-gold"><Rocket className="w-5 h-5" /></div>
            <CardTitle className="text-sm">Vision Stratégique</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-slate-300 leading-relaxed">
            Le <b>Diagramme de Gantt</b> permet de visualiser la planification temporelle des tâches.
            Les tâches sans date de début ou de fin sont listées dans la section "Tâches sans dates" ci-dessous pour être glissées dans le planning.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
