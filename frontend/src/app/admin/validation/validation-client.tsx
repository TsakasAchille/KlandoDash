"use client";

import { useState, useEffect } from "react";
import { UserListItem } from "@/types/user";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  CheckCircle, 
  XCircle, 
  FileText, 
  CreditCard, 
  User, 
  Mail, 
  Phone,
  ExternalLink,
  ShieldAlert,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { useRouter, useSearchParams } from "next/navigation";

interface ValidationClientProps {
  pendingUsers: UserListItem[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  currentStatus: string;
}

export function ValidationClient({ 
  pendingUsers, 
  totalCount, 
  currentPage, 
  pageSize,
  currentStatus 
}: ValidationClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(
    pendingUsers.length > 0 ? pendingUsers[0] : null
  );

  // Reset selected user when the list changes
  useEffect(() => {
    if (pendingUsers.length > 0) {
      if (!selectedUser || !pendingUsers.some(u => u.uid === selectedUser.uid)) {
        setSelectedUser(pendingUsers[0]);
      }
    } else {
      setSelectedUser(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingUsers]);

  const updateFilters = (newStatus: string, newPage: number = 1) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("status", newStatus);
    params.set("page", newPage.toString());
    router.push(`?${params.toString()}`);
  };

  const handleValidate = () => {
    toast.error("Option non disponible pour l'instant");
    return;
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      {/* Filtres de statut */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-muted/30 p-2 rounded-xl border border-border/50">
        <Tabs value={currentStatus} onValueChange={(val) => updateFilters(val)} className="w-full md:w-auto">
          <TabsList className="bg-background/50 grid grid-cols-3 w-full md:w-[400px]">
            <TabsTrigger value="pending" className="data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark">
              En attente
            </TabsTrigger>
            <TabsTrigger value="true" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              Validés
            </TabsTrigger>
            <TabsTrigger value="all" className="data-[state=active]:bg-klando-burgundy data-[state=active]:text-white">
              Tous
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Pagination compacte */}
        {totalPages > 1 && (
          <div className="flex items-center gap-2 px-2">
            <span className="text-[10px] uppercase font-black tracking-widest text-muted-foreground mr-2">
              Page {currentPage} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={currentPage <= 1}
              onClick={() => updateFilters(currentStatus, currentPage - 1)}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={currentPage >= totalPages}
              onClick={() => updateFilters(currentStatus, currentPage + 1)}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Liste des conducteurs */}
        <div className="lg:col-span-1 space-y-4">
          <h3 className="font-bold flex items-center gap-2 px-2 text-sm uppercase tracking-wider">
            {currentStatus === "pending" ? (
              <ShieldAlert className="w-4 h-4 text-klando-gold" />
            ) : currentStatus === "true" ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <User className="w-4 h-4 text-muted-foreground" />
            )}
            Résultats ({totalCount})
          </h3>
          
          {pendingUsers.length === 0 ? (
            <div className="py-10 text-center bg-muted/10 rounded-xl border border-dashed">
              <p className="text-sm text-muted-foreground italic">Aucun utilisateur trouvé</p>
            </div>
          ) : (
            <div className="space-y-2 overflow-auto max-h-[calc(100vh-320px)] pr-2 scrollbar-thin">
              {pendingUsers.map((user) => (
                <button
                  key={user.uid}
                  onClick={() => setSelectedUser(user)}
                  className={cn(
                    "w-full text-left p-4 rounded-xl border transition-all flex items-center gap-4 relative overflow-hidden group",
                    selectedUser?.uid === user.uid
                      ? "bg-klando-burgundy text-white border-klando-burgundy shadow-md scale-[1.02]"
                      : "bg-card hover:bg-accent border-border"
                  )}
                >
                  {user.photo_url ? (
                    <div className="relative w-10 h-10 flex-shrink-0">
                      <Image
                        src={user.photo_url}
                        alt=""
                        fill
                        className="rounded-lg object-cover"
                      />
                    </div>
                  ) : (
                    <div className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center font-bold",
                      selectedUser?.uid === user.uid ? "bg-white/20" : "bg-muted"
                    )}>
                      {(user.display_name || "?").charAt(0).toUpperCase()}
                    </div>
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="font-bold truncate text-sm">
                      {user.display_name || "Utilisateur sans nom"}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      {user.driver_license_url && <FileText className="w-3 h-3 opacity-70" />}
                      {user.id_card_url && <CreditCard className="w-3 h-3 opacity-70" />}
                      <span className={cn(
                        "text-[10px] font-mono",
                        selectedUser?.uid === user.uid ? "text-white/60" : "text-muted-foreground"
                      )}>
                        {user.uid.slice(0, 8)}...
                      </span>
                    </div>
                  </div>
                  {user.is_driver_doc_validated && (
                    <div className="absolute top-1 right-1">
                      <CheckCircle className="w-3 h-3 text-green-500 fill-white" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Détails et documents */}
        <div className="lg:col-span-2 space-y-6">
          {selectedUser ? (
            <>
              <Card className="border-klando-gold/20 overflow-hidden">
                <CardHeader className="bg-muted/30 pb-4">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-4">
                      {selectedUser.photo_url ? (
                        <div className="relative w-16 h-16 rounded-xl overflow-hidden border-2 border-white shadow-sm">
                          <Image
                            src={selectedUser.photo_url}
                            alt=""
                            fill
                            className="object-cover"
                          />
                        </div>
                      ) : (
                        <div className="w-16 h-16 rounded-xl bg-klando-burgundy text-white flex items-center justify-center text-2xl font-black">
                          {(selectedUser.display_name || "?").charAt(0).toUpperCase()}
                        </div>
                      )}
                      <div>
                        <CardTitle className="text-xl font-black uppercase tracking-tight">
                          {selectedUser.display_name}
                        </CardTitle>
                        <div className="flex flex-wrap gap-3 mt-1 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1.5">
                            <Mail className="w-3.5 h-3.5" />
                            {selectedUser.email}
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Phone className="w-3.5 h-3.5" />
                            {selectedUser.phone_number}
                          </div>
                        </div>
                      </div>
                    </div>
                    <Badge 
                      variant="outline" 
                      className={cn(
                        selectedUser.is_driver_doc_validated 
                          ? "bg-green-500/10 text-green-600 border-green-500/20"
                          : "bg-yellow-500/10 text-yellow-600 border-yellow-500/20"
                      )}
                    >
                      {selectedUser.is_driver_doc_validated ? "VALIDÉ" : "EN ATTENTE"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Permis de conduire */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold flex items-center gap-2">
                        <FileText className="w-4 h-4 text-klando-gold" />
                        Permis de conduire
                      </h4>
                      {selectedUser.driver_license_url ? (
                        <div className="relative group aspect-[4/3] rounded-xl overflow-hidden bg-muted border">
                          <Image
                            src={selectedUser.driver_license_url}
                            alt="Permis de conduire"
                            fill
                            className="object-contain"
                          />
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                            <Button size="sm" variant="secondary" asChild>
                              <a href={selectedUser.driver_license_url} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Agrandir
                              </a>
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="aspect-[4/3] rounded-xl bg-muted/50 border border-dashed flex flex-col items-center justify-center text-muted-foreground">
                          <XCircle className="w-8 h-8 mb-2 opacity-20" />
                          <p className="text-xs italic">Document non fourni</p>
                        </div>
                      )}
                    </div>

                    {/* Carte d'identité */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold flex items-center gap-2">
                        <CreditCard className="w-4 h-4 text-klando-gold" />
                        Carte d&apos;identité
                      </h4>
                      {selectedUser.id_card_url ? (
                        <div className="relative group aspect-[4/3] rounded-xl overflow-hidden bg-muted border">
                          <Image
                            src={selectedUser.id_card_url}
                            alt="Carte d'identité"
                            fill
                            className="object-contain"
                          />
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                            <Button size="sm" variant="secondary" asChild>
                              <a href={selectedUser.id_card_url} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="w-4 h-4 mr-2" />
                                Agrandir
                              </a>
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="aspect-[4/3] rounded-xl bg-muted/50 border border-dashed flex flex-col items-center justify-center text-muted-foreground">
                          <XCircle className="w-8 h-8 mb-2 opacity-20" />
                          <p className="text-xs italic">Document non fourni</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mt-8 flex gap-3">
                    <Button
                      onClick={() => handleValidate()}
                      className={cn(
                        "flex-1 font-bold text-white",
                        selectedUser.is_driver_doc_validated 
                          ? "bg-red-600 hover:bg-red-700" 
                          : "bg-green-600 hover:bg-green-700"
                      )}
                    >
                      {selectedUser.is_driver_doc_validated ? (
                        <XCircle className="w-4 h-4 mr-2" />
                      ) : (
                        <CheckCircle className="w-4 h-4 mr-2" />
                      )}
                      {selectedUser.is_driver_doc_validated ? "Invalider le conducteur" : "Approuver le conducteur"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex gap-3 items-start">
                <User className="w-5 h-5 text-blue-500 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold text-blue-900">Information Validation</h4>
                  <p className="text-xs text-blue-700 leading-relaxed mt-1">
                    {selectedUser.is_driver_doc_validated 
                      ? "Ce conducteur a été validé. Vous pouvez révoquer son accès si les documents sont obsolètes."
                      : "Vérifiez la validité des dates d'expiration avant d'approuver. Une fois validé, il pourra publier des trajets."}
                  </p>
                </div>
              </div>
            </>
          ) : (
            <div className="h-[400px] flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/20 bg-muted/5">
              <p className="text-muted-foreground text-sm">Sélectionnez un utilisateur pour voir ses documents</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
