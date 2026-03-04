"use export"; // This is not a real directive, I mean "use server"
"use server";

import { getExportUsers } from "@/lib/queries/users/export-users";

export async function exportUsersAction(
  limit: number,
  filters: {
    role?: string;
    verified?: string;
    gender?: string;
    minRating?: number;
    search?: string;
    isNew?: boolean;
  }
) {
  try {
    const users = await getExportUsers(limit, filters);
    return { success: true, users };
  } catch (error) {
    console.error("Export action error:", error);
    return { success: false, error: "Failed to fetch users for export" };
  }
}
