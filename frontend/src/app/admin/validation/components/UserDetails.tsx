"use client";

import { UserListItem } from "@/types/user";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Mail, Phone, CheckCircle, XCircle, User, Split, ChevronLeft } from "lucide-react";
import Image from "next/image";
import { DocumentCard } from "./DocumentCard";
import { ImageComparisonDialog } from "./ImageComparisonDialog";

interface UserDetailsProps {
  selectedUser: UserListItem | null;
  onValidate: () => void;
  onBack?: () => void;
}

export function UserDetails({ selectedUser, onValidate, onBack }: UserDetailsProps) {
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  if (!selectedUser) {
    return (
      <div className="h-[400px] flex items-center justify-center rounded-xl border border-dashed border-muted-foreground/20 bg-muted/5">
        <p className="text-muted-foreground text-sm">Sélectionnez un utilisateur pour voir ses documents</p>
      </div>
    );
  }

  return (
    <>
      <div className="lg:hidden mb-4">
        <Button variant="ghost" onClick={onBack} className="gap-2 text-muted-foreground font-black uppercase text-[10px] tracking-widest">
          <ChevronLeft className="w-4 h-4" /> Retour à la liste
        </Button>
      </div>

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
            <div className="flex flex-col items-end gap-2">
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
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsCompareOpen(true)}
                className="h-8 gap-2 text-[10px] font-black uppercase tracking-widest border-klando-gold/30 text-klando-gold hover:bg-klando-gold/10"
              >
                <Split className="w-3 h-3" />
                Comparer
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <DocumentCard 
              title="Permis de conduire" 
              url={selectedUser.driver_license_url} 
              type="license" 
            />
            <DocumentCard 
              title="Carte d'identité" 
              url={selectedUser.id_card_url} 
              type="id" 
            />
          </div>

          <div className="mt-8 flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onValidate}
              className={cn(
                "flex-1 font-bold text-white h-12",
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

      <ImageComparisonDialog 
        isOpen={isCompareOpen}
        onClose={() => setIsCompareOpen(false)}
        image1={selectedUser.driver_license_url || null}
        image2={selectedUser.id_card_url || null}
        label1="Permis de conduire"
        label2="Carte d'identité"
        userName={selectedUser.display_name || "Utilisateur"}
      />
    </>
  );
}
