"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { RoadmapItem } from "./types";

interface InteractionState {
  itemId: string;
  type: 'move' | 'resize-left' | 'resize-right';
  initialX: number;
  initialStart: number;
  initialEnd: number;
  currentDelta: number;
}

// Pending state before drag threshold is met
interface PendingInteraction {
  itemId: string;
  type: 'move' | 'resize-left' | 'resize-right';
  initialX: number;
  startDate: string;
  targetDate: string;
}

const DRAG_THRESHOLD = 5; // px — must move at least this far before activating

export function useGanttInteraction(
  timelineStart: number,
  timelineDuration: number,
  onUpdate: (id: string, data: { start_date: string; target_date: string }) => void
) {
  // Ref for real-time tracking (no re-renders during drag)
  const interactionRef = useRef<InteractionState | null>(null);
  // Pending interaction waiting to pass threshold
  const pendingRef = useRef<PendingInteraction | null>(null);
  // True when listeners should be attached (pending or active)
  const [listening, setListening] = useState(false);
  // State only for triggering visual re-renders via rAF
  const [renderState, setRenderState] = useState<InteractionState | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number>(0);

  // Keep stable refs for values needed in listeners
  const timelineStartRef = useRef(timelineStart);
  const timelineDurationRef = useRef(timelineDuration);
  const onUpdateRef = useRef(onUpdate);

  timelineStartRef.current = timelineStart;
  timelineDurationRef.current = timelineDuration;
  onUpdateRef.current = onUpdate;

  const calculateNewDates = useCallback((state: InteractionState) => {
    if (!containerRef.current) return null;
    const rect = containerRef.current.getBoundingClientRect();
    const deltaTime = (state.currentDelta / rect.width) * timelineDurationRef.current;

    let newStart = state.initialStart;
    let newEnd = state.initialEnd;

    if (state.type === 'move') {
      newStart += deltaTime;
      newEnd += deltaTime;
    } else if (state.type === 'resize-left') {
      newStart += deltaTime;
      if (newEnd - newStart < 86400000) newStart = newEnd - 86400000;
    } else if (state.type === 'resize-right') {
      newEnd += deltaTime;
      if (newEnd - newStart < 86400000) newEnd = newStart + 86400000;
    }

    // Snap to nearest day (midnight)
    const snapToDay = (ts: number) => {
      const d = new Date(ts);
      // Round to nearest day
      d.setHours(12, 0, 0, 0); // noon to avoid DST edge cases
      d.setHours(0, 0, 0, 0);
      return d.getTime();
    };

    newStart = snapToDay(newStart);
    newEnd = snapToDay(newEnd);

    return {
      start_date: new Date(newStart).toISOString().split('T')[0],
      target_date: new Date(newEnd).toISOString().split('T')[0],
      diffDays: Math.round((newEnd - newStart) / 86400000)
    };
  }, []);

  const startInteraction = useCallback((
    e: React.MouseEvent | React.TouchEvent,
    item: RoadmapItem,
    type: 'move' | 'resize-left' | 'resize-right'
  ) => {
    if ((e.target as HTMLElement).closest('button')) return;

    const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;

    // Use fallback dates without mutating the original item
    let startDate = item.start_date;
    let targetDate = item.target_date;
    if (!startDate || !targetDate) {
      const now = new Date();
      startDate = now.toISOString().split('T')[0];
      targetDate = new Date(now.getTime() + 7 * 86400000).toISOString().split('T')[0];
    }

    // Store as pending — will only activate after threshold is crossed
    pendingRef.current = { itemId: item.id, type, initialX: clientX, startDate, targetDate };
    setListening(true);
  }, []);

  // Activate the real interaction once threshold is met
  const activateInteraction = useCallback((pending: PendingInteraction, deltaX: number) => {
    const state: InteractionState = {
      itemId: pending.itemId,
      type: pending.type,
      initialX: pending.initialX,
      initialStart: new Date(pending.startDate).getTime(),
      initialEnd: new Date(pending.targetDate).getTime(),
      currentDelta: deltaX
    };
    pendingRef.current = null;
    interactionRef.current = state;
    setRenderState(state);
  }, []);

  // Stable listeners that read from ref — never recreated
  const handlePointerMove = useCallback((e: MouseEvent | TouchEvent) => {
    const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;

    // Phase 1: still pending — check threshold
    const pending = pendingRef.current;
    if (pending) {
      const dx = clientX - pending.initialX;
      if (Math.abs(dx) >= DRAG_THRESHOLD) {
        activateInteraction(pending, dx);
      }
      return;
    }

    // Phase 2: active interaction — update delta
    const current = interactionRef.current;
    if (!current) return;

    const deltaX = clientX - current.initialX;
    current.currentDelta = deltaX;

    // Throttle visual updates via rAF
    if (!rafRef.current) {
      rafRef.current = requestAnimationFrame(() => {
        rafRef.current = 0;
        if (interactionRef.current) {
          setRenderState({ ...interactionRef.current });
        }
      });
    }
  }, [activateInteraction]);

  const handlePointerUp = useCallback(() => {
    // If still pending (threshold never crossed), just cancel — it was a click
    if (pendingRef.current) {
      pendingRef.current = null;
      setListening(false);
      return;
    }

    const current = interactionRef.current;
    if (!current) return;

    // Cancel any pending rAF
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = 0;
    }

    if (current.currentDelta !== 0) {
      const newDates = calculateNewDates(current);
      if (newDates) {
        onUpdateRef.current(current.itemId, newDates);
      }
    }

    interactionRef.current = null;
    setRenderState(null);
    setListening(false);
  }, [calculateNewDates]);

  useEffect(() => {
    if (listening) {
      window.addEventListener('mousemove', handlePointerMove);
      window.addEventListener('mouseup', handlePointerUp);
      window.addEventListener('touchmove', handlePointerMove, { passive: false });
      window.addEventListener('touchend', handlePointerUp);
      window.addEventListener('touchcancel', handlePointerUp);
      return () => {
        window.removeEventListener('mousemove', handlePointerMove);
        window.removeEventListener('mouseup', handlePointerUp);
        window.removeEventListener('touchmove', handlePointerMove);
        window.removeEventListener('touchend', handlePointerUp);
        window.removeEventListener('touchcancel', handlePointerUp);
      };
    }
  }, [listening, handlePointerMove, handlePointerUp]);

  // Cleanup rAF on unmount
  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return {
    containerRef,
    interaction: renderState,
    startInteraction,
    calculateNewDates
  };
}
