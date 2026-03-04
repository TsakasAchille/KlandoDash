"use client";

import { useState } from "react";
import { Download, FileSpreadsheet, FileJson, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { exportUsersAction } from "@/lib/actions/users";
import { toast } from "sonner";

interface UserExportButtonProps {
  filters: {
    role?: string;
    verified?: string;
    gender?: string;
    minRating?: number;
    search?: string;
    isNew?: boolean;
  };
}

export function UserExportButton({ filters }: UserExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [limit, setLimit] = useState("100");
  const [isExporting, setIsExporting] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const handleExport = async (format: "csv" | "google-sheets") => {
    setIsExporting(true);
    setIsDone(false);

    try {
      const result = await exportUsersAction(parseInt(limit), filters);

      if (!result.success || !result.users) {
        throw new Error(result.error || "Erreur lors de l'exportation");
      }

      const users = result.users;
      
      if (users.length === 0) {
        toast.error("Aucun utilisateur trouvé pour ces critères");
        setIsExporting(false);
        return;
      }

      // Headers for CSV
      const headers = [
        "ID",
        "Nom d'affichage",
        "Email",
        "Téléphone",
        "Rôle",
        "Genre",
        "Note",
        "Vérifié",
        "Date d'inscription",
        "N° Carte ID",
        "N° Permis",
      ];

      // Format data rows
      const rows = users.map((u) => [
        u.uid,
        u.display_name || "",
        u.email || "",
        u.phone_number || "",
        u.role || "passenger",
        u.gender || "",
        u.rating || 0,
        u.is_driver_doc_validated ? "OUI" : "NON",
        u.created_at ? new Date(u.created_at).toLocaleDateString() : "",
        u.id_card_number || "",
        u.driver_license_number || "",
      ]);

      // Create CSV string
      // Note: Use semicolon for Excel/Google Sheets compatibility in some locales, or comma
      const csvContent = [
        headers.join(","),
        ...rows.map((row) => row.map(cell => {
          const content = String(cell).replace(/"/g, '""');
          return `"${content}"`;
        }).join(","))
      ].join("\n");

      // Create blob and download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const filename = `klando-users-export-${new Date().toISOString().split('T')[0]}.csv`;
      
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setIsDone(true);
      toast.success(`${users.length} utilisateurs exportés avec succès`);
      
      if (format === "google-sheets") {
        toast.info("Importez ce fichier CSV dans Google Sheets (Fichier > Importer)");
      }

      // Fermer après un court délai
      setTimeout(() => {
        setIsOpen(false);
        setIsDone(false);
        setIsExporting(false);
      }, 1500);

    } catch (error) {
      console.error("Export error:", error);
      toast.error("Échec de l'exportation");
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Download className="w-4 h-4" />
          <span>Exporter</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Exporter les utilisateurs</DialogTitle>
          <DialogDescription>
            Choisissez le nombre d&apos;utilisateurs à exporter. Les filtres actuels seront appliqués.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium">Limite d&apos;extraction</label>
            <Select value={limit} onValueChange={setLimit}>
              <SelectTrigger>
                <SelectValue placeholder="Choisir une limite" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="100">100 utilisateurs</SelectItem>
                <SelectItem value="500">500 utilisateurs</SelectItem>
                <SelectItem value="1000">1 000 utilisateurs</SelectItem>
                <SelectItem value="5000">5 000 utilisateurs</SelectItem>
                <SelectItem value="10000">10 000 utilisateurs (Maximum)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-[10px] text-muted-foreground">
              Note: Les exports volumineux peuvent prendre quelques secondes.
            </p>
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button 
            variant="default" 
            className="flex-1 gap-2" 
            onClick={() => handleExport("csv")}
            disabled={isExporting}
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isDone ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : (
              <FileSpreadsheet className="w-4 h-4" />
            )}
            {isExporting ? "Exportation..." : "Format CSV / Excel"}
          </Button>
          
          <Button 
            variant="secondary" 
            className="flex-1 gap-2" 
            onClick={() => handleExport("google-sheets")}
            disabled={isExporting}
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isDone ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : (
              <FileSpreadsheet className="w-4 h-4 text-green-600" />
            )}
            Google Sheets
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
