import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@/lib/supabase";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ uid: string }> }
) {
  const { uid } = await params;
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "5");
  const offset = (page - 1) * limit;

  const supabase = createServerClient();

  // Get total count
  const { count } = await supabase
    .from("transactions")
    .select("*", { count: "exact", head: true })
    .eq("user_id", uid);

  // Get paginated transactions
  const { data: transactions, error } = await supabase
    .from("transactions")
    .select(`
      id,
      amount,
      status,
      type,
      code_service,
      created_at
    `)
    .eq("user_id", uid)
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({
    transactions: transactions || [],
    total: count || 0,
    page,
    totalPages: Math.ceil((count || 0) / limit),
  });
}
