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

      if (format === "csv") {
        const csvContent = [
          headers.join(","),
          ...rows.map((row) => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
        ].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `klando-users-${new Date().toISOString().split('T')[0]}.csv`);
        link.click();
      } else {
        // Mode "Premium XLSX Style" - Using XML structure for perfect formatting
        const filterLabels = [];
        if (filters.role && filters.role !== "all") filterLabels.push(`Rôle: ${filters.role}`);
        if (filters.verified === "true") filterLabels.push("Vérifiés");
        if (filters.search) filterLabels.push(`Recherche: ${filters.search}`);
        const filterText = filterLabels.length > 0 ? filterLabels.join(" | ") : "Tous les utilisateurs";

        const styles = `
          <style>
            table { border-collapse: collapse; font-family: 'Helvetica', 'Arial', sans-serif; }
            .title { font-size: 24pt; color: #1a1a1a; font-weight: bold; padding: 20px 0; }
            .meta { font-size: 11pt; color: #4b5563; padding-bottom: 30px; }
            th { background-color: #eab308; color: white; border: 1.5pt solid #ca8a04; font-weight: bold; height: 40px; text-transform: uppercase; font-size: 10pt; }
            td { border: 0.5pt solid #d1d5db; height: 35px; padding: 5px; font-size: 11pt; color: #1f2937; }
            .zebra { background-color: #fffbeb; }
            .center { text-align: center; }
            .verified-yes { color: #166534; font-weight: bold; background-color: #f0fdf4; }
            .verified-no { color: #991b1b; font-weight: bold; background-color: #fef2f2; }
            .role-driver { color: #854d0e; font-weight: 700; }
            .rating { color: #ca8a04; font-weight: bold; }
            .email { color: #2563eb; text-decoration: underline; }
          </style>
        `;

        const htmlContent = `
          <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
          <head>
            <meta http-equiv="content-type" content="application/vnd.ms-excel; charset=UTF-8">
            ${styles}
          </head>
          <body>
            <table>
              <tr><td colspan="11" class="title">RAPPORT UTILISATEURS KLANDO</td></tr>
              <tr><td colspan="11" class="meta">
                Date : ${new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}<br>
                Filtres appliqués : ${filterText}<br>
                Export : ${users.length} utilisateurs extraits
              </td></tr>
              <tr style="height: 20px;"></tr>
              <thead>
                <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
              </thead>
              <tbody>
                ${rows.map((row, i) => `
                  <tr class="${i % 2 === 0 ? "" : "zebra"}">
                    <td>${row[0]}</td>
                    <td style="font-weight:bold">${row[1]}</td>
                    <td class="email">${row[2]}</td>
                    <td>${row[3]}</td>
                    <td class="${row[4] === 'driver' ? 'role-driver' : ''}">${row[4]}</td>
                    <td class="center">${row[5]}</td>
                    <td class="center rating">${row[6]}</td>
                    <td class="center ${row[7] === 'OUI' ? 'verified-yes' : 'verified-no'}">${row[7]}</td>
                    <td>${row[8]}</td>
                    <td>${row[9]}</td>
                    <td>${row[10]}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </body>
          </html>
        `;

        const blob = new Blob([htmlContent], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const filename = `klando-export-${new Date().toISOString().split('T')[0]}.xlsx`;
        
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        link.click();
        
        toast.success("Rapport XLSX généré avec un design premium !");
      }

      setIsDone(true);
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
            Choisissez le format et le nombre d&apos;utilisateurs à extraire.
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
                <SelectItem value="10000">10 000 utilisateurs</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button 
            variant="outline" 
            className="flex-1 gap-2" 
            onClick={() => handleExport("csv")}
            disabled={isExporting}
          >
            <FileSpreadsheet className="w-4 h-4 text-gray-500" />
            CSV Brut
          </Button>
          
          <Button 
            variant="default" 
            className="flex-1 gap-2 bg-green-700 hover:bg-green-800" 
            onClick={() => handleExport("google-sheets")}
            disabled={isExporting}
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="w-4 h-4" />
            )}
            Format XLSX (Stylisé)
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
