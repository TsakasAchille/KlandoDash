-- Migration: Setup Marketing Storage Bucket
-- Description: Creates the 'marketing' bucket and configures RLS policies for secure upload and public viewing.

-- 1. Create the bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('marketing', 'marketing', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Allow Public Access (SELECT)
-- This allows anyone to view images in emails or social posts.
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' AND policyname = 'Public Marketing Access'
    ) THEN
        CREATE POLICY "Public Marketing Access" ON storage.objects
        FOR SELECT USING (bucket_id = 'marketing');
    END IF;
END $$;

-- 3. Allow Authenticated Upload (INSERT)
-- Only dashboard users can upload files.
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' AND policyname = 'Admin Marketing Upload'
    ) THEN
        CREATE POLICY "Admin Marketing Upload" ON storage.objects
        FOR INSERT TO authenticated WITH CHECK (
            bucket_id = 'marketing'
        );
    END IF;
END $$;

-- 4. Allow Authenticated Manage (UPDATE, DELETE)
-- Only dashboard users can update or delete their files.
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' AND policyname = 'Admin Marketing Manage'
    ) THEN
        CREATE POLICY "Admin Marketing Manage" ON storage.objects
        FOR ALL TO authenticated USING (
            bucket_id = 'marketing'
        );
    END IF;
END $$;
