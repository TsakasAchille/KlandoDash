"use client";

import { useState, useMemo, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AuditLog } from "@/lib/queries/admin";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { 
  Shield, Mail, Send, Sparkles, User, FileText, Database, 
  Trash2, Edit3, Plus, Filter, Search, ChevronLeft, ChevronRight 
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface LogsClientProps {
  initialLogs: AuditLog[];
  admins: string[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
}

export function LogsClient({ initialLogs, admins, totalCount, currentPage, pageSize }: LogsClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const adminFilter = searchParams.get("admin") || "ALL";
  const typeFilter = searchParams.get("action") || "ALL";
  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");

  const totalPages = Math.ceil(totalCount / pageSize);

  // Common actions based on AuditAction type
  const actionTypes = [
    'USER_CREATE', 'USER_UPDATE', 'USER_DELETE',
    'USER_VALIDATED', 'USER_INVALIDATED', 'USER_AI_ANALYZED',
    'EMAIL_SENT', 'EMAIL_DRAFT_CREATED', 'EMAIL_TRASHED',
    'POST_CREATED', 'POST_UPDATED', 'POST_TRASHED', 'POST_DELETED',
    'TRIP_VALIDATED', 'TRIP_CANCELLED',
    'IA_DATA_INGESTION', 'LOGIN_SUCCESS'
  ].sort();

  const updateFilters = (updates: Record<string, string | number | null>) => {
    const params = new URLSearchParams(searchParams.toString());
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === "ALL" || value === "") {
        params.delete(key);
      } else {
        params.set(key, String(value));
      }
    });
    // Reset to page 1 on filter change, unless we are explicitly changing the page
    if (updates.page === undefined) {
      params.delete("page");
    }
    router.push(`?${params.toString()}`);
  };

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (searchParams.get("search") || "")) {
        updateFilters({ search: searchTerm });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const getActionIcon = (type: string) => {
    if (type.includes('USER')) return <User className="w-4 h-4 text-blue-500" />;
    if (type.includes('EMAIL')) return <Mail className="w-4 h-4 text-purple-500" />;
    if (type.includes('POST')) return <Send className="w-4 h-4 text-emerald-500" />;
    if (type.includes('IA')) return <Sparkles className="w-4 h-4 text-klando-gold" />;
    if (type.includes('TRIP')) return <Database className="w-4 h-4 text-orange-500" />;
    return <FileText className="w-4 h-4 text-slate-400" />;
  };

  const getActionBadge = (type: string) => {
    const isCreate = type.includes('CREATE') || type.includes('SENT') || type.includes('SUCCESS');
    const isDelete = type.includes('DELETE') || type.includes('TRASH') || type.includes('CANCELLED') || type.includes('INVALIDATED');
    const isUpdate = type.includes('UPDATE') || type.includes('VALIDATED');
    
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
        <div className="flex items-center gap-3 flex-1 w-full min-w-0 text-left">
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
            <Select value={adminFilter} onValueChange={(val) => updateFilters({ admin: val })}>
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

            <Select value={typeFilter} onValueChange={(val) => updateFilters({ action: val })}>
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
        <div className="p-6 bg-slate-50/50 border-b border-slate-200 flex justify-between items-center">
            <div className="flex flex-col">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-burgundy">Audit Transparence</span>
                <span className="text-sm font-black text-slate-900">{totalCount} actions enregistrées</span>
            </div>
            
            {totalPages > 1 && (
                <div className="flex items-center gap-3">
                    <Button 
                        variant="outline" 
                        size="icon" 
                        className="h-8 w-8 rounded-lg"
                        disabled={currentPage <= 1}
                        onClick={() => updateFilters({ page: currentPage - 1 })}
                    >
                        <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Page {currentPage} / {totalPages}</span>
                    <Button 
                        variant="outline" 
                        size="icon" 
                        className="h-8 w-8 rounded-lg"
                        disabled={currentPage >= totalPages}
                        onClick={() => updateFilters({ page: currentPage + 1 })}
                    >
                        <ChevronRight className="w-4 h-4" />
                    </Button>
                </div>
            )}
        </div>

        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
              <TableHead className="w-[180px] text-[10px] font-black uppercase tracking-widest py-5 pl-8 text-left">Date</TableHead>
              <TableHead className="w-[200px] text-[10px] font-black uppercase tracking-widest text-left">Administrateur</TableHead>
              <TableHead className="w-[180px] text-[10px] font-black uppercase tracking-widest text-left">Action</TableHead>
              <TableHead className="w-[120px] text-[10px] font-black uppercase tracking-widest text-left">Entité</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-left">Détails</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {initialLogs.map((log) => (
              <TableRow key={log.id} className="hover:bg-slate-50 transition-colors group">
                <TableCell className="text-[11px] font-bold text-slate-500 tabular-nums pl-8 text-left">
                  {format(new Date(log.created_at), 'dd MMM yyyy • HH:mm:ss', { locale: fr })}
                </TableCell>
                <TableCell className="text-xs font-black text-slate-900 truncate max-w-[200px] text-left">
                  {log.admin_email}
                </TableCell>
                <TableCell className="text-left">
                  {getActionBadge(log.action_type)}
                </TableCell>
                <TableCell className="text-left">
                  <div className="flex items-center gap-2">
                    {getActionIcon(log.action_type)}
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{log.entity_type}</span>
                  </div>
                </TableCell>
                <TableCell className="text-[11px] text-slate-600 font-medium text-left">
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
        
        {initialLogs.length === 0 && (
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
