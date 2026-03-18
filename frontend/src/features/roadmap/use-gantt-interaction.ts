"use client";

import { useState, useCallback, useRef } from "react";
import { RoadmapItem } from "./types";

interface InteractionState {
  itemId: string;
  type: 'move' | 'resize';
  initialX: number;
  initialStart: number;
  initialEnd: number;
  currentDelta: number;
}

export function useGanttInteraction(
  timelineStart: number,
  timelineDuration: number,
  onUpdate: (id: string, data: { start_date: string; target_date: string }) => void
) {
  const [interaction, setInteraction] = useState<InteractionState | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const startInteraction = (
    e: React.MouseEvent | React.TouchEvent,
    item: RoadmapItem,
    type: 'move' | 'resize'
  ) => {
    // Ne pas empêcher le clic sur les boutons d'édition
    if ((e.target as HTMLElement).closest('button')) return;

    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    
    if (!item.start_date || !item.target_date) {
      // Si pas de date, on simule un début aujourd'hui pour permettre le drag
      const now = new Date();
      item.start_date = now.toISOString().split('T')[0];
      item.target_date = new Date(now.getTime() + 7 * 86400000).toISOString().split('T')[0];
    }

    setInteraction({
      itemId: item.id,
      type,
      initialX: clientX,
      initialStart: new Date(item.start_date).getTime(),
      initialEnd: new Date(item.target_date).getTime(),
      currentDelta: 0
    });
  };

  const handleMouseMove = useCallback((e: MouseEvent | TouchEvent) => {
    if (!interaction) return;
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const deltaX = clientX - interaction.initialX;
    setInteraction(prev => prev ? { ...prev, currentDelta: deltaX } : null);
  }, [interaction]);

  const calculateNewDates = (state: InteractionState) => {
    if (!containerRef.current) return null;
    const rect = containerRef.current.getBoundingClientRect();
    const deltaTime = (state.currentDelta / rect.width) * timelineDuration;

    let newStart = state.initialStart;
    let newEnd = state.initialEnd;

    if (state.type === 'move') {
      newStart += deltaTime;
      newEnd += deltaTime;
    } else {
      newEnd += deltaTime;
    }

    // Minimum 1 jour
    if (newEnd - newStart < 86400000) newEnd = newStart + 86400000;

    return {
      start_date: new Date(newStart).toISOString().split('T')[0],
      target_date: new Date(newEnd).toISOString().split('T')[0]
    };
  };

  const handleMouseUp = useCallback(() => {
    if (!interaction) return;

    const newDates = calculateNewDates(interaction);
    if (newDates) {
      onUpdate(interaction.itemId, newDates);
    }

    setInteraction(null);
  }, [interaction, onUpdate]);

  return {
    containerRef,
    interaction,
    startInteraction,
    handleMouseMove,
    handleMouseUp,
    calculateNewDates
  };
}
