"use client";

import { useState } from "react";
import { Plus, Pencil, Trash2, LayoutGrid } from "lucide-react";
import { PlanningBoard } from "../types";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { createPlanningBoard, updatePlanningBoard, deletePlanningBoard } from "@/app/admin/roadmap/actions";
import { toast } from "sonner";

interface BoardSelectorProps {
  boards: PlanningBoard[];
  selectedBoardId: string | null;
  onBoardChange: (boardId: string | null) => void;
}

export function BoardSelector({ boards, selectedBoardId, onBoardChange }: BoardSelectorProps) {
  const [createOpen, setCreateOpen] = useState(false);
  const [editBoard, setEditBoard] = useState<PlanningBoard | null>(null);
  const [deleteBoard, setDeleteBoard] = useState<PlanningBoard | null>(null);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    const result = await createPlanningBoard({ name: name.trim() });
    if (result.success) {
      toast.success("Planning créé");
      setCreateOpen(false);
      setName("");
      if (result.board) onBoardChange(result.board.id);
    } else toast.error("Erreur");
    setLoading(false);
  };

  const handleRename = async () => {
    if (!editBoard || !name.trim()) return;
    setLoading(true);
    const result = await updatePlanningBoard(editBoard.id, { name: name.trim() });
    if (result.success) {
      toast.success("Renommé");
      setEditBoard(null);
      setName("");
    } else toast.error("Erreur");
    setLoading(false);
  };

  const handleDelete = async () => {
    if (!deleteBoard) return;
    setLoading(true);
    const result = await deletePlanningBoard(deleteBoard.id);
    if (result.success) {
      toast.success("Supprimé");
      if (selectedBoardId === deleteBoard.id) onBoardChange(null);
      setDeleteBoard(null);
    } else toast.error("Erreur");
    setLoading(false);
  };

  return (
    <>
      <div className="flex items-center gap-1.5 flex-wrap">
        {/* All items */}
        <button
          className={cn(
            "px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all border",
            selectedBoardId === null
              ? "bg-klando-gold text-black border-klando-gold"
              : "bg-white/5 text-slate-400 border-white/10 hover:text-white hover:border-white/20"
          )}
          onClick={() => onBoardChange(null)}
        >
          <LayoutGrid className="w-3 h-3 inline mr-1" />
          Tous
        </button>

        {boards.map(board => (
          <div key={board.id} className="group relative">
            <button
              className={cn(
                "px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all border flex items-center gap-1.5",
                selectedBoardId === board.id
                  ? "bg-klando-gold text-black border-klando-gold"
                  : "bg-white/5 text-slate-400 border-white/10 hover:text-white hover:border-white/20"
              )}
              onClick={() => onBoardChange(board.id)}
            >
              {board.color && <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: board.color }} />}
              {board.name}
            </button>

            {/* Edit/Delete on hover */}
            <div className="absolute -top-1 -right-1 hidden group-hover:flex gap-0.5 z-30">
              <button
                className="w-4 h-4 rounded-full bg-slate-700 border border-white/20 flex items-center justify-center hover:bg-slate-600"
                onClick={(e) => { e.stopPropagation(); setName(board.name); setEditBoard(board); }}
              >
                <Pencil className="w-2 h-2 text-white" />
              </button>
              <button
                className="w-4 h-4 rounded-full bg-red-900 border border-red-500/30 flex items-center justify-center hover:bg-red-800"
                onClick={(e) => { e.stopPropagation(); setDeleteBoard(board); }}
              >
                <Trash2 className="w-2 h-2 text-red-400" />
              </button>
            </div>
          </div>
        ))}

        <button
          className="px-2 py-1.5 rounded-lg text-[11px] font-bold bg-white/5 text-slate-500 border border-dashed border-white/10 hover:text-klando-gold hover:border-klando-gold/30 transition-all"
          onClick={() => { setName(""); setCreateOpen(true); }}
        >
          <Plus className="w-3 h-3 inline" />
        </button>
      </div>

      {/* Create dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[350px]">
          <DialogHeader>
            <DialogTitle>Nouveau Planning</DialogTitle>
            <DialogDescription>Créer un tableau de planification.</DialogDescription>
          </DialogHeader>
          <Input
            placeholder="Nom du planning"
            className="bg-white/5 border-white/10"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Annuler</Button>
            <Button className="bg-klando-gold text-black" onClick={handleCreate} disabled={loading || !name.trim()}>Créer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rename dialog */}
      <Dialog open={!!editBoard} onOpenChange={() => setEditBoard(null)}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[350px]">
          <DialogHeader>
            <DialogTitle>Renommer</DialogTitle>
            <DialogDescription>Modifier le nom du planning.</DialogDescription>
          </DialogHeader>
          <Input
            className="bg-white/5 border-white/10"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleRename()}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditBoard(null)}>Annuler</Button>
            <Button className="bg-klando-gold text-black" onClick={handleRename} disabled={loading || !name.trim()}>Enregistrer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog open={!!deleteBoard} onOpenChange={() => setDeleteBoard(null)}>
        <DialogContent className="bg-slate-900 border-white/10 text-white sm:max-w-[350px]">
          <DialogHeader>
            <DialogTitle>Supprimer "{deleteBoard?.name}" ?</DialogTitle>
            <DialogDescription>Les tâches de ce planning seront déplacées vers le backlog général.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteBoard(null)}>Annuler</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={loading}>Supprimer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
