"use client";

import { useState } from "react";
import { RoadmapItem } from "./types";
import { 
  updateRoadmapProgress, 
  toggleRoadmapPlanning, 
  deleteRoadmapItem,
  addRoadmapItem,
  updateRoadmapItem
} from "@/app/admin/roadmap/actions";
import { toast } from "sonner";

export function useRoadmap(initialItems: RoadmapItem[]) {
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<RoadmapItem | null>(null);
  
  const [localProgress, setLocalProgress] = useState<Record<string, number>>(
    initialItems.reduce((acc, item) => ({ ...acc, [item.id]: item.progress }), {})
  );

  const handleProgressChange = async (itemId: string, newProgress: number) => {
    setUpdatingId(itemId);
    const result = await updateRoadmapProgress(itemId, newProgress);
    if (result.success) toast.success("Progrès mis à jour");
    else toast.error("Erreur lors de la mise à jour");
    setUpdatingId(null);
  };

  const handleTogglePlanning = async (itemId: string, isPlanning: boolean, boardId?: string | null) => {
    setUpdatingId(itemId);
    const result = await toggleRoadmapPlanning(itemId, isPlanning, boardId);
    if (result.success) toast.success(isPlanning ? "Déplacé vers Planning" : "Promu vers Roadmap");
    else toast.error("Erreur");
    setUpdatingId(null);
  };

  const handleDelete = async (itemId: string) => {
    if (!confirm("Supprimer cette tâche ?")) return;
    setUpdatingId(itemId);
    const result = await deleteRoadmapItem(itemId);
    if (result.success) toast.success("Supprimé");
    else toast.error("Erreur");
    setUpdatingId(null);
  };

  const handleAdd = async (item: any) => {
    const result = await addRoadmapItem(item);
    if (result.success) {
      toast.success("Ajouté");
      setIsAddOpen(false);
    } else toast.error("Erreur");
  };

  const handleUpdate = async (item: RoadmapItem) => {
    setUpdatingId(item.id);
    const result = await updateRoadmapItem(item.id, item);
    if (result.success) {
      toast.success("Mis à jour");
      setIsEditOpen(false);
    } else toast.error("Erreur");
    setUpdatingId(null);
  };

  return {
    updatingId,
    localProgress,
    setLocalProgress,
    handleProgressChange,
    handleTogglePlanning,
    handleDelete,
    handleAdd,
    handleUpdate,
    isAddOpen,
    setIsAddOpen,
    isEditOpen,
    setIsEditOpen,
    editingItem,
    setEditingItem
  };
}
