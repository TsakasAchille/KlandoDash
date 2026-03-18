import { RoadmapView } from "@/features/roadmap/roadmap-view";
import { Milestone } from "lucide-react";
import { getRoadmapItems, getDashMembers, getPlanningBoards } from "@/lib/queries/admin";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Roadmap Technique | KlandoDash",
  description: "Vision et planification des évolutions techniques de la plateforme Klando.",
};

export default async function RoadmapPage() {
  const [items, members, boards] = await Promise.all([getRoadmapItems(), getDashMembers(), getPlanningBoards()]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-klando-gold/10 text-klando-gold">
          <Milestone className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Roadmap Technique</h1>
          <p className="text-muted-foreground">Vision stratégique et planification des développements.</p>
        </div>
      </div>

      <RoadmapView items={items} members={members} boards={boards} />
    </div>
  );
}
