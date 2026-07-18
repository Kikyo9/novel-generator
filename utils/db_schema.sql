-- Supabase database schema for 网文生成工坊
-- Run this in Supabase SQL Editor to set up tables

-- Novels table
CREATE TABLE IF NOT EXISTS novels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT '未命名',
    categories TEXT[] DEFAULT '{}',
    protagonist TEXT DEFAULT '',
    length TEXT DEFAULT '',
    styles TEXT[] DEFAULT '{}',
    synopsis TEXT DEFAULT '',
    outline TEXT DEFAULT '[]',
    chapters TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster user queries
CREATE INDEX IF NOT EXISTS idx_novels_user_id ON novels(user_id);
CREATE INDEX IF NOT EXISTS idx_novels_updated ON novels(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE novels ENABLE ROW LEVEL SECURITY;

-- Users can only read their own novels
CREATE POLICY "Users can read own novels"
    ON novels FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own novels
CREATE POLICY "Users can insert own novels"
    ON novels FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own novels
CREATE POLICY "Users can update own novels"
    ON novels FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can delete their own novels
CREATE POLICY "Users can delete own novels"
    ON novels FOR DELETE
    USING (auth.uid() = user_id);
