"use server";

import { validateUser } from "@/lib/queries/users";
import { revalidatePath } from "next/cache";

export async function validateUserAction(uid: string, isValidated: boolean) {
  try {
    const success = await validateUser(uid, isValidated);
    
    if (success) {
      revalidatePath("/validation");
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
