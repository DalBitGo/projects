-- Create tables for StoreBridge

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domeggook_item_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),
    category VARCHAR(200),
    images TEXT[],
    options JSONB,
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_domeggook_id ON products(domeggook_item_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    config JSONB NOT NULL,
    total_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    error_summary JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(type);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

CREATE TABLE IF NOT EXISTS product_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    job_id UUID,
    state VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    naver_product_id VARCHAR(100),
    seller_product_code VARCHAR(100) UNIQUE,
    retry_count INTEGER DEFAULT 0,
    error_code VARCHAR(100),
    error_message TEXT,
    registration_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_registrations_product_id ON product_registrations(product_id);
CREATE INDEX IF NOT EXISTS idx_registrations_state ON product_registrations(state);
CREATE INDEX IF NOT EXISTS idx_registrations_job_id ON product_registrations(job_id);

CREATE TABLE IF NOT EXISTS category_mappings (
    id SERIAL PRIMARY KEY,
    domeggook_category VARCHAR(200) NOT NULL,
    naver_leaf_category_id VARCHAR(50) NOT NULL,
    required_attributes JSONB,
    default_attributes JSONB,
    confidence REAL DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_category_mappings_domeggook ON category_mappings(domeggook_category);
CREATE INDEX IF NOT EXISTS idx_category_mappings_active ON category_mappings(is_active, domeggook_category);
