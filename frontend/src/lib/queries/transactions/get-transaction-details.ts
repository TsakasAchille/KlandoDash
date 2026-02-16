import { createServerClient } from "../../supabase";
import { TransactionWithBooking } from "@/types/transaction";

/**
 * Détail d'une transaction par ID (avec booking + trip si lié)
 */
export async function getTransactionById(id: string): Promise<TransactionWithBooking | null> {
  const supabase = createServerClient();

  const { data: txn, error: txnError } = await supabase
    .from("transactions")
    .select("*")
    .eq("id", id)
    .single();

  if (txnError || !txn) {
    console.error("Erreur getTransactionById:", txnError?.message);
    return null;
  }

  let user = null;
  if (txn.user_id) {
    const { data: userData } = await supabase
      .from("users")
      .select("display_name, phone_number, email")
      .eq("uid", txn.user_id)
      .maybeSingle();
    user = userData ? {
      display_name: userData.display_name,
      phone: userData.phone_number,
      email: userData.email,
    } : null;
  }

  const { data: booking } = await supabase
    .from("bookings")
    .select(`
      id,
      trip_id,
      user_id,
      trip:trips!trip_id (
        trip_id,
        departure_name,
        destination_name,
        driver_price,
        passenger_price
      )
    `)
    .eq("transaction_id", id)
    .maybeSingle();

  return {
    ...txn,
    user,
    booking: booking ?? null,
  } as unknown as TransactionWithBooking;
}
