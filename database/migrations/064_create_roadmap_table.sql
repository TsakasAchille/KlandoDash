-- Migration 064: Create roadmap table
CREATE TABLE IF NOT EXISTS public.roadmap_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phase_name TEXT NOT NULL,
    timeline TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo' CHECK (status IN ('todo', 'in-progress', 'done')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    icon_name TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Active RLS
ALTER TABLE public.roadmap_items ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Roadmap items are viewable by everyone" ON public.roadmap_items
    FOR SELECT USING (true);

CREATE POLICY "Roadmap items are editable by admins only" ON public.roadmap_items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.dash_authorized_users
            WHERE email = auth.jwt()->>'email' AND role = 'admin'
        )
    );

-- Insert initial data
INSERT INTO public.roadmap_items (phase_name, timeline, title, description, status, progress, icon_name, order_index)
VALUES 
-- Phase 0
('Phase 0: Réalisations Récentes', 'Terminé (Q1 2026)', 'Plateforme Web (klando-sn.com)', 'Lancement du site vitrine klando-sn.com et de capture d''intentions de trajets.', 'done', 100, 'Globe', 0),
('Phase 0: Réalisations Récentes', 'Terminé (Q1 2026)', 'Messagerie Unifiée (v1)', 'Intégration du Centre Éditorial avec support Email (SMTP) et WhatsApp Business.', 'done', 100, 'MessageSquare', 1),
('Phase 0: Réalisations Récentes', 'Terminé (Q1 2026)', 'Cockpit de Pilotage Growth', 'Interface de suivi des KPIs: Activation, Rétention et Liquidité.', 'done', 100, 'LayoutDashboard', 2),
-- Phase 1
('Phase 1: Automatisation & Temps Réel', 'Court Terme (1-2 mois)', 'WhatsApp Business API Pro', 'Passage à l''API officielle pour l''envoi automatisé de notifications.', 'in-progress', 20, 'Zap', 3),
('Phase 1: Automatisation & Temps Réel', 'Court Terme (1-2 mois)', 'Notifications Push Desktop', 'Alertes instantanées pour les nouveaux tickets et messages critiques.', 'todo', 0, 'Target', 4),
('Phase 1: Automatisation & Temps Réel', 'Court Terme (1-2 mois)', 'Optimisation du Radar PostGIS', 'Affinage des algorithmes de matching pour les trajets transversaux.', 'todo', 10, 'Globe', 5),
-- Phase 2
('Phase 2: Intelligence & Reporting', 'Moyen Terme (3-4 mois)', 'Module Finance & Revenus', 'Dashboard dédié aux flux financiers: Commissions Klando vs Revenus Conducteurs.', 'todo', 0, 'BarChart3', 6),
('Phase 2: Intelligence & Reporting', 'Moyen Terme (3-4 mois)', 'Export Reporting Engine', 'Génération automatique de rapports PDF pour les bilans.', 'todo', 0, 'Rocket', 7),
('Phase 2: Intelligence & Reporting', 'Moyen Terme (3-4 mois)', 'Predictive Analytics (Gemini)', 'Prédiction des zones de forte demande basée sur l''historique.', 'todo', 0, 'Cpu', 8);
