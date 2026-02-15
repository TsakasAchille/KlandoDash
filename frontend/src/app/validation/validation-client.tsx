"use client";

import { useState, useTransition } from "react";
import { UserListItem } from "@/types/user";
import { validateUserAction } from "./actions";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  CheckCircle, 
  XCircle, 
  FileText, 
  CreditCard, 
  User, 
  Mail, 
  Phone,
  ExternalLink,
  Loader2,
  ShieldAlert
} from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface ValidationClientProps {
  pendingUsers: UserListItem[];
}

export function ValidationClient({ pendingUsers: initialUsers }: ValidationClientProps) {
  const [users, setUsers] = useState<UserListItem[]>(initialUsers);
  const [selectedUser, setSelectedUser] = useState<UserListItem | null>(
    initialUsers.length > 0 ? initialUsers[0] : null
  );
  const [isPending, startTransition] = useTransition();

  const handleValidate = (uid: string, isValidated: boolean) => {
    toast.error("Option non disponible pour l'instant");
    return;
    
    // Logic temporarily disabled
    /*
    startTransition(async () => {
      const result = await validateUserAction(uid, isValidated);
      if (result.success) {
        toast.success(isValidated ? "Conducteur validé !" : "Validation annulée");
        const updatedUsers = users.filter(u => u.uid !== uid);
        setUsers(updatedUsers);
        if (selectedUser?.uid === uid) {
          setSelectedUser(updatedUsers.length > 0 ? updatedUsers[0] : null);
        }
      } else {
        toast.error(result.message || "Une erreur est survenue");
      }
    });
    */
  };

  if (users.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-muted/20 rounded-xl border border-dashed">
        <div className="bg-green-100 p-4 rounded-full mb-4">
          <CheckCircle className="w-10 h-10 text-green-600" />
        </div>
        <h3 className="text-xl font-bold">Tout est en ordre !</h3>
        <p className="text-muted-foreground">Aucun conducteur n&apos;est en attente de validation.</p>
      </div>
    );
  }

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Liste des conducteurs en attente */}
      <div className="lg:col-span-1 space-y-4">
        <h3 className="font-bold flex items-center gap-2 px-2">
          <ShieldAlert className="w-5 h-5 text-klando-gold" />
          En attente ({users.length})
        </h3>
        <div className="space-y-2 overflow-auto max-h-[calc(100vh-250px)] pr-2 scrollbar-thin">
          {users.map((user) => (
            <button
              key={user.uid}
              onClick={() => setSelectedUser(user)}
              className={cn(
                "w-full text-left p-4 rounded-xl border transition-all flex items-center gap-4",
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
            </button>
          ))}
        </div>
      </div>

      {/* Détails et documents */}
      <div className="lg:col-span-2 space-y-6">
        {selectedUser && (
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
                  <Badge variant="outline" className="bg-yellow-500/10 text-yellow-600 border-yellow-500/20">
                    ATTENTE VALIDATION
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
                    onClick={() => handleValidate(selectedUser.uid, true)}
                    disabled={isPending}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold"
                  >
                    {isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <CheckCircle className="w-4 h-4 mr-2" />}
                    Approuver le conducteur
                  </Button>
                  <Button
                    onClick={() => handleValidate(selectedUser.uid, false)}
                    disabled={isPending}
                    variant="outline"
                    className="border-red-200 text-red-600 hover:bg-red-50"
                  >
                    Refuser / Demander correction
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex gap-3 items-start">
              <User className="w-5 h-5 text-blue-500 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-blue-900">Conseil de validation</h4>
                <p className="text-xs text-blue-700 leading-relaxed mt-1">
                  Vérifiez la validité des dates d&apos;expiration et la correspondance des noms avec le profil utilisateur.
                  Une fois validé, l&apos;utilisateur pourra publier des trajets en tant que conducteur.
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
