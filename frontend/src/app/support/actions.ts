'use server';

import { revalidatePath } from 'next/cache';
import { updateTicketStatus } from '@/lib/queries/support';
import type { TicketStatus } from '@/types/support';

export async function updateTicketStatusAction(
  ticketId: string,
  status: TicketStatus
) {
  if (!ticketId || !status) {
    return { success: false, error: 'ID de ticket ou statut manquant.' };
  }

  const result = await updateTicketStatus(ticketId, status);

  if (result.success) {
    // Invalide le cache pour la page de support, ce qui forcera le re-fetch des données
    revalidatePath('/support');
  }

  return result;
}
