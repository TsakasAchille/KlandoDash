-- Migration: Add Feedback to Marketing Insights
-- Description: Adds columns to store admin feedback and likes for strategic insights.

ALTER TABLE public.dash_marketing_insights 
ADD COLUMN IF NOT EXISTS is_liked boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS admin_feedback text;
