-- Migration: Add GLOBAL_STATS Category to Insight Category Enum
-- Description: Allows storing AI Assistant analyses for the Statistics page.

ALTER TYPE insight_category ADD VALUE IF NOT EXISTS 'GLOBAL_STATS';
