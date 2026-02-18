-- Migration: Fix Marketing Storage Permissions
-- Description: Forces the 'marketing' bucket to be public and resets RLS policies to ensure visibility.

-- 1. Force bucket to be public (Critical for image display)
UPDATE storage.buckets 
SET public = true 
WHERE id = 'marketing';

-- 2. Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Public Marketing Access" ON storage.objects;
DROP POLICY IF EXISTS "Admin Marketing Upload" ON storage.objects;
DROP POLICY IF EXISTS "Admin Marketing Manage" ON storage.objects;

-- 3. Re-create: Allow Public Access (SELECT)
-- This allows anyone to view images via the public URL.
CREATE POLICY "Public Marketing Access" ON storage.objects
FOR SELECT USING (bucket_id = 'marketing');

-- 4. Re-create: Allow Authenticated Upload (INSERT)
CREATE POLICY "Admin Marketing Upload" ON storage.objects
FOR INSERT TO authenticated WITH CHECK (
    bucket_id = 'marketing'
);

-- 5. Re-create: Allow Authenticated Manage (UPDATE, DELETE)
CREATE POLICY "Admin Marketing Manage" ON storage.objects
FOR ALL TO authenticated USING (
    bucket_id = 'marketing'
);
