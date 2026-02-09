"use server";

import { revalidatePath } from "next/cache";
import { updateSiteTripRequest as updateRequest } from "@/lib/queries/site-requests";
import { SiteTripRequestStatus } from "@/types/site-request";

export async function updateRequestStatusAction(id: string, status: SiteTripRequestStatus) {
  const success = await updateRequest(id, { status });

  if (success) {
    revalidatePath("/site-requests");
    return { success: true, message: "Statut mis à jour." };
  }

  return { success: false, message: "Erreur lors de la mise à jour." };
}
