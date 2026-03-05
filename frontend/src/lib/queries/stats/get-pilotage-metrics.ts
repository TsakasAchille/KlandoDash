import { createServerClient } from "../../supabase";

export async function getPilotageMetrics() {
  const supabase = createServerClient();
  const { data, error } = await supabase.rpc("get_pilotage_metrics");

  if (error) {
    console.error("Error fetching pilotage metrics:", JSON.stringify({
      message: error.message,
      code: error.code,
      details: error.details,
      hint: error.hint,
      fullError: error
    }, null, 2));
    return null;
  }

  return data;
}
