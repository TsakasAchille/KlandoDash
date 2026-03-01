import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getAuditLogs } from "@/lib/queries/admin";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { Shield, Mail, Send, Sparkles, User, FileText, Database, Trash2, Edit3, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function AuditLogsPage() {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    redirect("/login");
  }

  const logs = await getAuditLogs(200);

  const getActionIcon = (type: string) => {
    if (type.includes('USER')) return <User className="w-4 h-4 text-blue-500" />;
    if (type.includes('EMAIL')) return <Mail className="w-4 h-4 text-purple-500" />;
    if (type.includes('POST')) return <Send className="w-4 h-4 text-emerald-500" />;
    if (type.includes('IA')) return <Sparkles className="w-4 h-4 text-klando-gold" />;
    if (type.includes('TRIP')) return <Database className="w-4 h-4 text-orange-500" />;
    return <FileText className="w-4 h-4 text-slate-400" />;
  };

  const getActionBadge = (type: string) => {
    const isCreate = type.includes('CREATE');
    const isDelete = type.includes('DELETE') || type.includes('TRASH');
    const isUpdate = type.includes('UPDATE');
    
    return (
      <span className={cn(
        "px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-tighter flex items-center gap-1 w-fit",
        isCreate ? "bg-green-50 text-green-700 border border-green-100" :
        isDelete ? "bg-red-50 text-red-700 border border-red-100" :
        isUpdate ? "bg-blue-50 text-blue-700 border border-blue-100" :
        "bg-slate-50 text-slate-700 border border-slate-100"
      )}>
        {isCreate && <Plus className="w-2.5 h-2.5" />}
        {isDelete && <Trash2 className="w-2.5 h-2.5" />}
        {isUpdate && <Edit3 className="w-2.5 h-2.5" />}
        {type.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-center border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-2xl font-black text-slate-900 uppercase tracking-tight flex items-center gap-3">
            <Shield className="w-7 h-7 text-klando-gold" />
            Journaux d&apos;Audit
          </h1>
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Historique des actions administratives</p>
        </div>
      </header>

      <div className="bg-white border border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
              <TableHead className="w-[180px] text-[10px] font-black uppercase tracking-widest">Date</TableHead>
              <TableHead className="w-[200px] text-[10px] font-black uppercase tracking-widest">Administrateur</TableHead>
              <TableHead className="w-[180px] text-[10px] font-black uppercase tracking-widest">Action</TableHead>
              <TableHead className="w-[120px] text-[10px] font-black uppercase tracking-widest">Entité</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest">Détails</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id} className="hover:bg-slate-50 transition-colors group">
                <TableCell className="text-[11px] font-bold text-slate-500 tabular-nums">
                  {format(new Date(log.created_at), 'dd MMM yyyy • HH:mm:ss', { locale: fr })}
                </TableCell>
                <TableCell className="text-xs font-black text-slate-900 truncate max-w-[200px]">
                  {log.admin_email}
                </TableCell>
                <TableCell>
                  {getActionBadge(log.action_type)}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {getActionIcon(log.action_type)}
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{log.entity_type}</span>
                  </div>
                </TableCell>
                <TableCell className="text-[11px] text-slate-600 font-medium">
                  <div className="max-w-md truncate group-hover:whitespace-normal group-hover:overflow-visible transition-all">
                    {Object.entries(log.details || {}).map(([key, val]) => (
                      <span key={key} className="mr-3">
                        <span className="text-[9px] font-black uppercase text-slate-400 mr-1">{key}:</span>
                        <span className="text-slate-900">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
                      </span>
                    ))}
                    {!Object.keys(log.details || {}).length && <span className="italic text-slate-300">Aucun détail supplémentaire</span>}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        
        {logs.length === 0 && (
          <div className="p-20 text-center space-y-4">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto">
              <Database className="w-8 h-8 text-slate-200" />
            </div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Aucun journal trouvé</p>
          </div>
        )}
      </div>
    </div>
  );
}
