import { redirect } from "next/navigation";

export default async function MarketingPage() {
  redirect("/admin/pilotage?tab=prospects");
}
