// Type complet depuis Supabase
export interface TransactionRow {
  id: string;
  user_id: string;
  intech_transaction_id: string | null;
  msg: string | null;
  amount: number | null;
  status: string | null;
  phone: string | null;
  code_service: string | null;
  created_at: string | null;
  updated_at: string | null;
  type: string | null;
}

// Type pour la liste (colonnes minimales)
export interface TransactionListItem {
  id: string;
  user_id: string;
  amount: number | null;
  status: string | null;
  type: string | null;
  code_service: string | null;
  phone: string | null;
  created_at: string | null;
}

// Type avec infos utilisateur (join)
export interface TransactionWithUser extends TransactionListItem {
  user: {
    display_name: string | null;
    phone: string | null;
  } | null;
}

// Type avec booking + trip (pour calcul marge)
// booking peut être null (top-up, pénalité, remboursement…)
export interface TransactionWithBooking extends TransactionRow {
  user: {
    display_name: string | null;
    phone: string | null;
    email: string | null;
  } | null;
  booking: {
    id: string;
    trip_id: string;
    user_id: string;
    trip: {
      trip_id: string;
      departure_name: string | null;
      destination_name: string | null;
      driver_price: number | null;
      passenger_price: number | null;
    } | null;
  } | null;
}

// Direction du flux financier (logique Intech inversée)
// CASH_IN = argent qui SORT pour Klando
// CASH_OUT = argent qui RENTRE pour Klando
export type CashDirection = "CASH_IN" | "CASH_OUT" | "UNKNOWN";

export function getCashDirection(codeService: string | null): CashDirection {
  if (!codeService) return "UNKNOWN";
  if (codeService.includes("CASH_IN")) return "CASH_IN";
  if (codeService.includes("CASH_OUT")) return "CASH_OUT";
  return "UNKNOWN";
}

// Stats agrégées
export interface TransactionStats {
  total: number;
  totalAmount: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
}

// Stats cash flow
export interface CashFlowStats {
  totalIn: number;    // CASH_OUT Intech = entrées Klando
  totalOut: number;   // CASH_IN Intech = sorties Klando
  solde: number;      // totalIn - totalOut
  countIn: number;
  countOut: number;
}

// Stats revenus (basé sur transactions SUCCESS liées à des bookings)
export interface RevenueStats {
  totalPassengerPaid: number;   // sum transactions.amount
  totalDriverPrice: number;     // sum trips.driver_price
  klandoMargin: number;         // différence (inclut 15% TVA)
  transactionCount: number;
}
