import { createServerClient } from "../../supabase";

/**
 * Valide ou invalide les documents d'un conducteur
 */
export async function validateUser(uid: string, isValidated: boolean): Promise<boolean> {
  const supabase = createServerClient();

  const { error } = await supabase
    .from("users")
    .update({ 
      is_driver_doc_validated: isValidated,
      updated_at: new Date().toISOString()
    })
    .eq("uid", uid);

  if (error) {
    console.error("validateUser error:", error);
    return false;
  }

  return true;
}
