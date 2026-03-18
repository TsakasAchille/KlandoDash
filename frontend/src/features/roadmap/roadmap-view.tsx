"use client";

import { useState } from "react";
import { Milestone, Calendar, Plus, Rocket } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RoadmapItem, PlanningBoard } from "./types";
import { useRoadmap } from "./use-roadmap";
import { RoadmapGrid } from "./components/roadmap-grid";
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

  const roadmapItems = items.filter(i => !i.is_planning);
  const planningItems = items.filter(i => i.is_planning);
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
      <Tabs defaultValue="roadmap" className="w-full">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <TabsList className="bg-slate-900 border border-white/5 p-1 rounded-xl">
            <TabsTrigger value="roadmap" className="rounded-lg px-6">
              <Milestone className="w-4 h-4 mr-2" /> Roadmap
            </TabsTrigger>
            <TabsTrigger value="planning" className="rounded-lg px-6">
              <Calendar className="w-4 h-4 mr-2" /> Gantt Planning ({filteredPlanningItems.length})
            </TabsTrigger>
          </TabsList>

          <Button onClick={() => roadmap.setIsAddOpen(true)} className="bg-klando-gold hover:bg-klando-gold/90 text-black font-bold">
            <Plus className="w-4 h-4 mr-2" /> Nouvelle Tâche
          </Button>
        </div>

        <TabsContent value="roadmap" className="mt-0">
          <RoadmapGrid items={roadmapItems} {...roadmapProps} />
        </TabsContent>

        <TabsContent value="planning" className="mt-0">
          <PlanningGantt
            items={filteredPlanningItems}
            members={members}
            boards={boards}
            selectedBoardId={selectedBoardId}
            onBoardChange={setSelectedBoardId}
            {...roadmapProps}
          />
        </TabsContent>
      </Tabs>

      <TaskDialogs
        isAddOpen={roadmap.isAddOpen}
        setIsAddOpen={roadmap.setIsAddOpen}
        isEditOpen={roadmap.isEditOpen}
        setIsEditOpen={roadmap.setIsEditOpen}
        editingItem={roadmap.editingItem}
        members={members}
        boards={boards}
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
            Le <b>Diagramme de Gantt</b> permet de visualiser la planification temporelle des tâches sur les 6 prochains mois.
            Les tâches sans date de début ou de fin seront listées dans le backlog ci-dessous.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
