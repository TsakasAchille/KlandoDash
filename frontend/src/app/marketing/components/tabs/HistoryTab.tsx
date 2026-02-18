"use client";

import { Card } from "@/components/ui/card";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { CheckCircle2, cn } from "@/lib/utils";
import { AIRecommendation } from "../../types";

interface HistoryTabProps {
  recommendations: AIRecommendation[];
}

export function HistoryTab({ recommendations }: HistoryTabProps) {
  const history = recommendations
    .filter(r => r.status === 'APPLIED')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <Card className="bg-card/30 border-white/5 overflow-hidden rounded-[2rem]">
      <Table>
        <TableHeader>
          <TableRow className="border-white/5 hover:bg-transparent">
            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground py-5 pl-8">Date</TableHead>
            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Type</TableHead>
            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Action</TableHead>
            <TableHead className="text-right text-[10px] font-black uppercase tracking-widest text-muted-foreground pr-8">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {history.length > 0 ? (
            history.map((reco) => (
              <TableRow key={reco.id} className="border-white/5 hover:bg-white/[0.02] transition-colors">
                <TableCell className="text-[11px] font-medium text-muted-foreground py-4 tabular-nums pl-8">
                  {new Date(reco.created_at).toLocaleString('fr-FR')}
                </TableCell>
                <TableCell>
                  <span className={cn(
                    "text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter border",
                    reco.type === 'TRACTION' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                    reco.type === 'STRATEGIC' ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
                    reco.type === 'ENGAGEMENT' ? "bg-klando-gold/10 text-klando-gold border-klando-gold/20" :
                    "bg-red-500/10 text-red-500 border-red-500/20"
                  )}>
                    {reco.type}
                  </span>
                </TableCell>
                <TableCell className="text-xs font-bold text-white uppercase">{reco.title}</TableCell>
                <TableCell className="text-right pr-8">
                  <div className="flex items-center justify-end gap-2 text-green-500 font-black text-[10px] uppercase">
                    <span className="w-3.5 h-3.5 border-2 border-green-500 rounded-full flex items-center justify-center text-[8px]">✓</span> Validé
                  </div>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} className="h-40 text-center text-muted-foreground/30 font-black uppercase text-[10px] tracking-widest">
                Aucun historique
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </Card>
  );
}
