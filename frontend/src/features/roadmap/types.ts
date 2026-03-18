import { 
  Globe, MessageSquare, LayoutDashboard, ShieldCheck, 
  Zap, Target, BarChart3, Rocket, Cpu, Star 
} from "lucide-react";

export type PlanningStage = 'now' | 'next' | 'later' | 'backlog';

export interface RoadmapItem {
  id: string;
  phase_name: string;
  timeline: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  progress: number;
  icon_name: string;
  order_index: number;
  is_planning: boolean;
  planning_stage: PlanningStage;
  start_date: string | null;
  target_date: string | null;
  custom_color: string | null;
  assigned_to: string[];
  planning_board_id: string | null;
  updated_at: string;
}

export interface PlanningBoard {
  id: string;
  name: string;
  description: string | null;
  color: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export const ICON_MAP: Record<string, any> = {
  Globe,
  MessageSquare,
  LayoutDashboard,
  ShieldCheck,
  Zap,
  Target,
  BarChart3,
  Rocket,
  Cpu,
  Star
};

export const COLOR_PRESETS = [
  { value: "#EF4444", label: "Rouge" },
  { value: "#F97316", label: "Orange" },
  { value: "#EBC33F", label: "Or" },
  { value: "#22C55E", label: "Vert" },
  { value: "#14B8A6", label: "Teal" },
  { value: "#3B82F6", label: "Bleu" },
  { value: "#8B5CF6", label: "Violet" },
  { value: "#EC4899", label: "Rose" },
  { value: "#7B1F2F", label: "Bordeaux" },
  { value: "#64748B", label: "Gris" },
];

export const STAGE_CONFIG = {
  now: { label: "Maintenant", color: "bg-red-500 text-black border-red-400", desc: "Priorités immédiates" },
  next: { label: "Bientôt", color: "bg-klando-gold text-black border-yellow-400", desc: "1-2 prochains mois" },
  later: { label: "Plus tard", color: "bg-indigo-400 text-black border-indigo-300", desc: "3-6 prochains mois" },
  backlog: { label: "Backlog", color: "bg-slate-400 text-black border-slate-300", desc: "Futur & Idées" }
};
