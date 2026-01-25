import { NextRequest, NextResponse } from "next/server";
import { getTripsByDriver } from "@/lib/queries/trips";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ uid: string }> }
) {
  const { uid } = await params;
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "5");
  const offset = (page - 1) * limit;

  const { trips, total } = await getTripsByDriver(uid, { limit, offset });

  return NextResponse.json({
    trips,
    total,
    page,
    totalPages: Math.ceil(total / limit),
  });
}
