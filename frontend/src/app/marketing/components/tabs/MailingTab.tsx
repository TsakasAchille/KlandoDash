"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { 
  Sparkles, Loader2, Send, History, cn 
} from "lucide-react";
import { MarketingEmail } from "../../mailing-actions";

interface MailingTabProps {
  emails: MarketingEmail[];
  isScanning: boolean;
  sendingEmailId: string | null;
  onScan: () => void;
  onSendEmail: (id: string) => void;
}

export function MailingTab({ 
  emails, 
  isScanning, 
  sendingEmailId, 
  onScan, 
  onSendEmail 
}: MailingTabProps) {
  const drafts = emails.filter(e => e.status === 'DRAFT');
  const history = emails.filter(e => e.status !== 'DRAFT');

  return (
    <div className="outline-none space-y-8">
      {/* Drafts Section */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
            <div className="p-2 bg-purple-500/10 rounded-xl">
                <Sparkles className="w-4 h-4 text-purple-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Suggestions de Mailing IA</h3>
        </div>

        <div className="grid md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {drafts.length > 0 ? (
                drafts.map((email) => (
                    <Card key={email.id} className="bg-card/40 backdrop-blur-md border-white/5 hover:border-purple-500/30 transition-all duration-500 group relative overflow-hidden flex flex-col h-full">
                        <CardContent className="p-6 space-y-4 flex flex-col h-full">
                            <div className="flex justify-between items-start">
                                <span className="text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border bg-purple-500/10 text-purple-500 border-purple-500/20">
                                    {email.category}
                                </span>
                            </div>
                            <div>
                                <h4 className="font-black text-sm text-white uppercase tracking-tight group-hover:text-purple-400 transition-colors line-clamp-1">
                                    {email.subject}
                                </h4>
                                <p className="text-[10px] font-bold text-muted-foreground mt-1 uppercase">À: {email.recipient_name || email.recipient_email}</p>
                                <div className="text-[11px] text-muted-foreground mt-3 leading-relaxed line-clamp-4 bg-white/5 p-3 rounded-xl border border-white/5 italic">
                                    "{email.content}"
                                </div>
                            </div>
                            <div className="mt-auto pt-4 flex gap-2">
                                <Button 
                                    size="sm" 
                                    onClick={() => onSendEmail(email.id)}
                                    disabled={sendingEmailId === email.id}
                                    className="flex-1 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest h-9 shadow-lg shadow-purple-500/20"
                                >
                                    {sendingEmailId === email.id ? <Loader2 className="w-3.5 h-3.5 animate-spin mr-2" /> : <Send className="w-3.5 h-3.5 mr-2" />}
                                    Envoyer
                                </Button>
                                <Button 
                                    variant="ghost" 
                                    size="sm"
                                    className="rounded-xl text-muted-foreground hover:text-white font-black text-[10px] uppercase h-9"
                                >
                                    Ignorer
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))
            ) : (
                <div className="col-span-3 flex flex-col items-center justify-center py-16 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
                    <p className="text-[10px] font-black uppercase text-muted-foreground/40 tracking-widest italic">Aucun brouillon suggéré. Lancez un scan.</p>
                </div>
            )}
        </div>
      </div>

      {/* History Table */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
            <div className="p-2 bg-white/5 rounded-xl">
                <History className="w-4 h-4 text-muted-foreground" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white text-muted-foreground/60">Journal d&apos;envoi Mailing</h3>
        </div>

        <Card className="bg-card/30 border-white/5 overflow-hidden rounded-[2rem]">
            <Table>
                <TableHeader>
                    <TableRow className="border-white/5 hover:bg-transparent">
                        <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground py-5 pl-8">Date</TableHead>
                        <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Destinataire</TableHead>
                        <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Sujet</TableHead>
                        <TableHead className="text-right text-[10px] font-black uppercase tracking-widest text-muted-foreground pr-8">Status</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {history.length > 0 ? (
                        history.map((email) => (
                            <TableRow key={email.id} className="border-white/5 hover:bg-white/[0.02] transition-colors">
                                <TableCell className="text-[11px] font-medium text-muted-foreground py-4 tabular-nums pl-8">
                                    {new Date(email.sent_at || email.created_at).toLocaleString('fr-FR')}
                                </TableCell>
                                <TableCell>
                                    <div className="flex flex-col">
                                        <span className="text-xs font-bold text-white uppercase">{email.recipient_name || 'Inconnu'}</span>
                                        <span className="text-[10px] text-muted-foreground/60">{email.recipient_email}</span>
                                    </div>
                                </TableCell>
                                <TableCell className="text-xs font-medium text-white/80">{email.subject}</TableCell>
                                <TableCell className="text-right pr-8">
                                    <span className={cn(
                                        "text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-tighter border",
                                        email.status === 'SENT' ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-red-500/10 text-red-500 border-red-500/20"
                                    )}>
                                        {email.status}
                                    </span>
                                </TableCell>
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={4} className="h-24 text-center text-muted-foreground/30 font-black uppercase text-[10px] tracking-widest">Aucun historique d&apos;envoi</TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </Card>
      </div>
    </div>
  );
}
