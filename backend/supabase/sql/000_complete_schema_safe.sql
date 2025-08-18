-- Complete Database Schema Migration (Safe Version)
-- This script creates all tables for the Arrakis AI-Powered Brand Intelligence System
-- It handles existing types and tables gracefully

-- Create enums only if they don't exist
DO $$ BEGIN
    CREATE TYPE sentiment_tone AS ENUM ('positive', 'neutral', 'negative', 'mixed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE confidence_level AS ENUM ('low', 'medium', 'high');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE run_status AS ENUM ('queued', 'running', 'done', 'error');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Drop existing tables if they exist (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS competitor_mentions CASCADE;
DROP TABLE IF EXISTS url_analysis_results CASCADE;
DROP TABLE IF EXISTS deep_research_analysis CASCADE;
DROP TABLE IF EXISTS insights CASCADE;
DROP TABLE IF EXISTS judgments CASCADE;
DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS runs CASCADE;
DROP TABLE IF EXISTS prompts CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

-- Create brands table
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    industry TEXT,
    website TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create runs table
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id UUID REFERENCES prompts(id) ON DELETE CASCADE,
    status run_status NOT NULL DEFAULT 'queued',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create sources table
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    relevance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create judgments table
CREATE TABLE judgments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    judgment_type TEXT NOT NULL,
    judgment_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create insights table
CREATE TABLE insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL,
    insight_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the main deep research analysis table
CREATE TABLE deep_research_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic identification
    brand_name TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    
    -- Analysis summary
    total_urls_analyzed INTEGER NOT NULL DEFAULT 0,
    
    -- Sentiment Analysis
    overall_sentiment_tone sentiment_tone NOT NULL DEFAULT 'neutral',
    positive_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    neutral_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    negative_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    
    -- Brand Mention Tracking
    total_mention_count INTEGER NOT NULL DEFAULT 0,
    average_mentions_per_url DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    
    -- Trust/Authority Score
    overall_trust_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    confidence_level confidence_level NOT NULL DEFAULT 'low',
    
    -- Metadata
    model_used TEXT NOT NULL DEFAULT 'sonar-deep-research',
    total_tokens_used INTEGER NOT NULL DEFAULT 0,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Raw data storage
    analysis_summary JSONB NOT NULL DEFAULT '{}',
    detailed_analyses JSONB NOT NULL DEFAULT '[]',
    crawled_urls JSONB NOT NULL DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create table for individual URL analysis results
CREATE TABLE url_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to main analysis
    deep_research_analysis_id UUID NOT NULL REFERENCES deep_research_analysis(id) ON DELETE CASCADE,
    
    -- URL information
    url TEXT NOT NULL,
    title TEXT,
    query_text TEXT NOT NULL,
    query_index INTEGER NOT NULL,
    
    -- Sentiment Analysis
    sentiment_tone sentiment_tone NOT NULL DEFAULT 'neutral',
    positive_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    neutral_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    negative_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    sentiment_reasoning TEXT,
    
    -- Brand Mention Tracking
    mention_count INTEGER NOT NULL DEFAULT 0,
    frequency_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    context_diversity_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    mention_contexts TEXT[] DEFAULT '{}',
    mention_reasoning TEXT,
    
    -- Competitor Analysis
    competitors_mentioned TEXT[] DEFAULT '{}',
    competitor_favorability_scores JSONB NOT NULL DEFAULT '{}',
    competitor_reasoning TEXT,
    
    -- Trust/Authority Score
    ai_recommendation_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    vs_others_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    trust_reasoning TEXT,
    
    -- Raw response data
    raw_response TEXT,
    usage_data JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create table for competitor mentions across all analyses
CREATE TABLE competitor_mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference to main analysis
    deep_research_analysis_id UUID NOT NULL REFERENCES deep_research_analysis(id) ON DELETE CASCADE,
    
    -- Competitor information
    competitor_name TEXT NOT NULL,
    total_mentions INTEGER NOT NULL DEFAULT 0,
    average_favorability_score DECIMAL(3,2) NOT NULL DEFAULT 0.0, -- -1.0 to 1.0
    
    -- Aggregated data
    favorability_scores JSONB NOT NULL DEFAULT '[]', -- Array of individual scores
    mention_urls TEXT[] DEFAULT '{}', -- URLs where competitor was mentioned
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_brands_name ON brands(name);
CREATE INDEX idx_brands_industry ON brands(industry);

CREATE INDEX idx_prompts_text ON prompts(text);
CREATE INDEX idx_prompts_category ON prompts(category);

CREATE INDEX idx_runs_prompt_id ON runs(prompt_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created_at ON runs(created_at);

CREATE INDEX idx_sources_run_id ON sources(run_id);
CREATE INDEX idx_sources_url ON sources(url);
CREATE INDEX idx_sources_relevance ON sources(relevance_score);

CREATE INDEX idx_judgments_run_id ON judgments(run_id);
CREATE INDEX idx_judgments_source_id ON judgments(source_id);
CREATE INDEX idx_judgments_type ON judgments(judgment_type);

CREATE INDEX idx_insights_run_id ON insights(run_id);
CREATE INDEX idx_insights_type ON insights(insight_type);

CREATE INDEX idx_deep_research_analysis_brand_name ON deep_research_analysis(brand_name);
CREATE INDEX idx_deep_research_analysis_run_id ON deep_research_analysis(run_id);
CREATE INDEX idx_deep_research_analysis_created_at ON deep_research_analysis(created_at);
CREATE INDEX idx_deep_research_analysis_sentiment ON deep_research_analysis(overall_sentiment_tone);

CREATE INDEX idx_url_analysis_analysis_id ON url_analysis_results(deep_research_analysis_id);
CREATE INDEX idx_url_analysis_url ON url_analysis_results(url);
CREATE INDEX idx_url_analysis_sentiment ON url_analysis_results(sentiment_tone);

CREATE INDEX idx_competitor_mentions_analysis_id ON competitor_mentions(deep_research_analysis_id);
CREATE INDEX idx_competitor_mentions_name ON competitor_mentions(competitor_name);
CREATE INDEX idx_competitor_mentions_favorability ON competitor_mentions(average_favorability_score);

-- Create updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_brands_updated_at 
    BEFORE UPDATE ON brands
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompts_updated_at 
    BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_runs_updated_at 
    BEFORE UPDATE ON runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at 
    BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_judgments_updated_at 
    BEFORE UPDATE ON judgments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insights_updated_at 
    BEFORE UPDATE ON insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deep_research_analysis_updated_at 
    BEFORE UPDATE ON deep_research_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_url_analysis_results_updated_at 
    BEFORE UPDATE ON url_analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_mentions_updated_at 
    BEFORE UPDATE ON competitor_mentions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE brands IS 'Stores brand information and metadata';
COMMENT ON TABLE prompts IS 'Stores analysis prompts and queries';
COMMENT ON TABLE runs IS 'Tracks analysis execution runs and their status';
COMMENT ON TABLE sources IS 'Stores web sources and their content for analysis';
COMMENT ON TABLE judgments IS 'Stores AI judgments and analysis results';
COMMENT ON TABLE insights IS 'Stores derived insights and conclusions';
COMMENT ON TABLE deep_research_analysis IS 'Stores comprehensive brand analysis results from Perplexity AI deep research';
COMMENT ON TABLE url_analysis_results IS 'Stores individual URL analysis results from deep research';
COMMENT ON TABLE competitor_mentions IS 'Stores aggregated competitor mention data across all analyses';

-- Insert sample data for testing
INSERT INTO brands (name, description, industry, website) VALUES
('Tesla', 'Electric vehicle and clean energy company', 'Automotive', 'https://tesla.com'),
('Apple', 'Technology company specializing in consumer electronics', 'Technology', 'https://apple.com'),
('Nike', 'Athletic footwear and apparel company', 'Retail', 'https://nike.com');

INSERT INTO prompts (text, category) VALUES
('Analyze Tesla brand visibility and market presence', 'brand_analysis'),
('Evaluate Apple customer sentiment and brand perception', 'sentiment_analysis'),
('Assess Nike competitive positioning in athletic wear', 'competitive_analysis');

-- Grant necessary permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
