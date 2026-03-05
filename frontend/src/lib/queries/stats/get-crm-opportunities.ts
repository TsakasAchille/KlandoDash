import { createServerClient } from "../../supabase";

export async function getCRMOpportunities() {
  const supabase = createServerClient();
  const { data, error } = await supabase.rpc("get_crm_opportunities");

  if (error) {
    console.error("Error fetching CRM opportunities:", {
      message: error.message,
      code: error.code,
      details: error.details
    });
    return null;
  }

  return data;
}
