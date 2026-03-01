"use client";

import { useState, useMemo } from "react";
import { AuditLog } from "@/lib/queries/admin";
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
import { Shield, Mail, Send, Sparkles, User, FileText, Database, Trash2, Edit3, Plus, Filter, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface LogsClientProps {
  initialLogs: AuditLog[];
  admins: string[];
}

export function LogsClient({ initialLogs, admins }: LogsClientProps) {
  const [adminFilter, setAdminFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const actionTypes = useMemo(() => {
    const types = new Set(initialLogs.map(log => log.action_type));
    return Array.from(types).sort();
  }, [initialLogs]);

  const filteredLogs = useMemo(() => {
    return initialLogs.filter(log => {
      const matchesAdmin = adminFilter === "ALL" || log.admin_email === adminFilter;
      const matchesType = typeFilter === "ALL" || log.action_type === typeFilter;
      const matchesSearch = searchTerm === "" || 
        log.admin_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(log.details).toLowerCase().includes(searchTerm.toLowerCase());
      
      return matchesAdmin && matchesType && matchesSearch;
    });
  }, [initialLogs, adminFilter, typeFilter, searchTerm]);

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
    <div className="space-y-6">
      {/* FILTERS BAR */}
      <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-sm flex flex-col md:flex-row gap-4 items-center">
        <div className="flex items-center gap-3 flex-1 w-full min-w-0">
            <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input 
                    placeholder="Rechercher par email ou contenu..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-10 bg-slate-50 border-slate-200 rounded-xl text-xs font-bold"
                />
            </div>
        </div>

        <div className="flex gap-3 w-full md:w-auto shrink-0">
            <Select value={adminFilter} onValueChange={setAdminFilter}>
                <SelectTrigger className="w-full md:w-[200px] h-10 bg-slate-50 border-slate-200 rounded-xl text-xs font-black uppercase">
                    <div className="flex items-center gap-2">
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        <SelectValue placeholder="Administrateur" />
                    </div>
                </SelectTrigger>
                <SelectContent className="rounded-xl">
                    <SelectItem value="ALL" className="text-xs font-bold uppercase tracking-tight">Tous les admins</SelectItem>
                    {admins.map(email => (
                        <SelectItem key={email} value={email} className="text-xs">{email}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-full md:w-[180px] h-10 bg-slate-50 border-slate-200 rounded-xl text-xs font-black uppercase">
                    <div className="flex items-center gap-2">
                        <Filter className="w-3.5 h-3.5 text-slate-400" />
                        <SelectValue placeholder="Type d'action" />
                    </div>
                </SelectTrigger>
                <SelectContent className="rounded-xl">
                    <SelectItem value="ALL" className="text-xs font-bold uppercase tracking-tight">Toutes les actions</SelectItem>
                    {actionTypes.map(type => (
                        <SelectItem key={type} value={type} className="text-xs uppercase">{type.replace('_', ' ')}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
      </div>

      {/* TABLE */}
      <div className="bg-white border border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden min-h-[400px]">
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
            {filteredLogs.map((log) => (
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
        
        {filteredLogs.length === 0 && (
          <div className="p-20 text-center space-y-4">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto">
              <Database className="w-8 h-8 text-slate-200" />
            </div>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Aucun journal correspondant à vos filtres</p>
          </div>
        )}
      </div>
    </div>
  );
}
