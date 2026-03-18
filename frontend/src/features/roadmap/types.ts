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

export const STAGE_CONFIG = {
  now: { label: "Maintenant", color: "bg-red-500/20 text-red-400 border-red-500/10", desc: "Priorités immédiates" },
  next: { label: "Bientôt", color: "bg-klando-gold/20 text-klando-gold border-klando-gold/10", desc: "1-2 prochains mois" },
  later: { label: "Plus tard", color: "bg-indigo-500/20 text-indigo-400 border-indigo-500/10", desc: "3-6 prochains mois" },
  backlog: { label: "Backlog", color: "bg-slate-500/20 text-slate-400 border-slate-500/10", desc: "Futur & Idées" }
};
