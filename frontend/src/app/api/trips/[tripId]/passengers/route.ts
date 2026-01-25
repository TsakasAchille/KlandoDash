import { NextRequest } from "next/server";
import { getPassengersForTrip } from "@/lib/queries/trips";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ tripId: string }> }
) {
  const { tripId } = await params;

  try {
    const passengers = await getPassengersForTrip(tripId);
    return Response.json(passengers);
  } catch (error) {
    console.error("Error fetching passengers:", error);
    return Response.json(
      { error: "Failed to fetch passengers" },
      { status: 500 }
    );
  }
}
