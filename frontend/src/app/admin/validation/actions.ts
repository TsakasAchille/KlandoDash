"use server";

import { validateUser } from "@/lib/queries/users";
import { revalidatePath } from "next/cache";
import { createAdminClient } from "@/lib/supabase";
import { analyzeDocument, DocumentAnalysisReport } from "@/lib/gemini";
import { recordAuditLog } from "@/lib/audit";

export async function validateUserAction(uid: string, isValidated: boolean) {
  try {
    const success = await validateUser(uid, isValidated);
    
    if (success) {
      await recordAuditLog({
        action: isValidated ? 'USER_VALIDATED' : 'USER_INVALIDATED',
        entityType: 'USER',
        entityId: uid
      });
      revalidatePath("/admin/validation");
      revalidatePath("/users");
      revalidatePath(`/users/${uid}`);
      return { success: true };
    } else {
      return { success: false, message: "Erreur lors de la mise à jour en base de données." };
    }
  } catch (error) {
    console.error("Action validateUserAction error:", error);
    return { success: false, message: "Une erreur inattendue est survenue." };
  }
}

export async function analyzeDocumentsAction(uid: string) {
  const supabase = createAdminClient();
  
  try {
    // 1. Récupérer les documents et le nom de l'utilisateur
    const { data: user, error: fetchError } = await supabase
      .from('users')
      .select('uid, display_name, id_card_url, driver_license_url')
      .eq('uid', uid)
      .single();

    if (fetchError || !user) throw new Error("Utilisateur non trouvé");

    const reports: Record<string, any> = {};
    let idCardNumber = null;
    let idCardName = null;
    let idCardFirstName = null;
    let idCardLastName = null;
    let idCardExpiry = null;
    
    let licenseNumber = null;
    let licenseName = null;
    let licenseFirstName = null;
    let licenseLastName = null;
    let licenseExpiry = null;
    
    const warnings: string[] = [];

    // 2. Analyser la carte d'identité
    if (user.id_card_url) {
      try {
        const report = await analyzeDocument(user.id_card_url, 'ID_CARD', user.display_name);
        reports.id_card = report;
        idCardNumber = report.documentNumber;
        idCardName = report.fullName;
        idCardFirstName = report.firstName;
        idCardLastName = report.lastName;
        idCardExpiry = report.expirationDate;
        
        if (!report.isSenegalese) warnings.push("La carte d'identité ne semble pas être sénégalaise.");
        if (!report.isLegible) warnings.push("La carte d'identité est difficile à lire.");
        if (report.nameMatchesProfile === false) warnings.push(`Divergence de nom (ID) : Trouvé "${report.fullName}" vs Profil "${user.display_name}"`);
      } catch (e) {
        console.error("ID Analysis failed", e);
      }
    }

    // 3. Analyser le permis de conduire
    if (user.driver_license_url) {
      try {
        const report = await analyzeDocument(user.driver_license_url, 'DRIVER_LICENSE', user.display_name);
        reports.driver_license = report;
        licenseNumber = report.documentNumber;
        licenseName = report.fullName;
        licenseFirstName = report.firstName;
        licenseLastName = report.lastName;
        licenseExpiry = report.expirationDate;
        
        if (!report.isSenegalese) warnings.push("Le permis ne semble pas être sénégalais.");
        if (!report.isLegible) warnings.push("Le permis est difficile à lire.");
        if (report.nameMatchesProfile === false) warnings.push(`Divergence de nom (Permis) : Trouvé "${report.fullName}" vs Profil "${user.display_name}"`);
      } catch (e) {
        console.error("License Analysis failed", e);
      }
    }

    // 4. Vérifier les doublons (Fraude)
    
    // Check par Numéro CNI
    if (idCardNumber && reports.id_card) {
      const { count } = await supabase.from('users').select('uid', { count: 'exact', head: true }).eq('id_card_number', idCardNumber).neq('uid', uid);
      reports.id_card.isUnique = count === 0;
      if (count && count > 0) warnings.push(`ALERTE FRAUDE : Ce numéro de CNI est déjà utilisé par ${count} autre(s) compte(s).`);
    }

    // Check par Numéro Permis
    if (licenseNumber && reports.driver_license) {
      const { count } = await supabase.from('users').select('uid', { count: 'exact', head: true }).eq('driver_license_number', licenseNumber).neq('uid', uid);
      reports.driver_license.isUnique = count === 0;
      if (count && count > 0) warnings.push(`ALERTE FRAUDE : Ce numéro de permis est déjà utilisé par ${count} autre(s) compte(s).`);
    }

    // Check par Nom/Prénom Extrait (Détection de fraude par identité identique)
    if (idCardFirstName && idCardLastName) {
        const { count } = await supabase.from('users')
            .select('uid', { count: 'exact', head: true })
            .eq('id_card_first_name_ai', idCardFirstName)
            .eq('id_card_last_name_ai', idCardLastName)
            .neq('uid', uid);
        
        if (count && count > 0) {
            warnings.push(`ALERTE IDENTITÉ : "${idCardFirstName} ${idCardLastName}" est déjà validé sur ${count} autre(s) compte(s).`);
        }
    }

    // 5. Déterminer le statut final
    let status: 'SUCCESS' | 'FAILED' | 'WARNING' = 'SUCCESS';
    if (warnings.some(w => w.includes("ALERTE FRAUDE") || w.includes("ALERTE IDENTITÉ"))) {
      status = 'FAILED';
    } else if (warnings.length > 0) {
      status = 'WARNING';
    }

    // 6. Mettre à jour l'utilisateur avec toutes les infos extraites
    const { error: updateError } = await supabase
      .from('users')
      .update({
        id_card_number: idCardNumber,
        id_card_name_ai: idCardName,
        id_card_first_name_ai: idCardFirstName,
        id_card_last_name_ai: idCardLastName,
        id_card_expiry_ai: idCardExpiry,
        driver_license_number: licenseNumber,
        driver_license_name_ai: licenseName,
        driver_license_first_name_ai: licenseFirstName,
        driver_license_last_name_ai: licenseLastName,
        driver_license_expiry_ai: licenseExpiry,
        ai_validation_status: status,
        ai_validation_report: {
          analyzed_at: new Date().toISOString(),
          reports,
          warnings
        }
      })
      .eq('uid', uid);

    if (updateError) {
      if (updateError.code === '42703') {
        throw new Error("Les colonnes IA manquent en base de données. Veuillez appliquer la migration 051.");
      }
      throw updateError;
    }

    await recordAuditLog({
      action: 'USER_AI_ANALYZED',
      entityType: 'USER',
      entityId: uid,
      details: { status, warningsCount: warnings.length }
    });

    revalidatePath("/admin/validation");
    return { success: true, status, warnings };

  } catch (error: any) {
    console.error("analyzeDocumentsAction error:", error);
    return { success: false, message: error.message || "Erreur lors de l'analyse IA" };
  }
}
