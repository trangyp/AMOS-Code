-- AXIOM ONE: MVP Database Schema
-- PostgreSQL 16+ with pgvector extension

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================
-- CORE TABLES
-- ============================================

-- Tenants (isolation boundary)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settings JSONB NOT NULL DEFAULT '{}'
);

-- People (human users)
CREATE TABLE people (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    theme VARCHAR(20) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

-- Teams
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    cost_center VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, slug)
);

-- Team memberships
CREATE TABLE team_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, person_id)
);

-- ============================================
-- CODE OBJECTS
-- ============================================

-- Repositories
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    team_id UUID REFERENCES teams(id),
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255),
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    language VARCHAR(50),
    languages JSONB DEFAULT '{}',
    health_score FLOAT,
    last_activity_at TIMESTAMPTZ,
    open_issues INT NOT NULL DEFAULT 0,
    open_prs INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    embedding VECTOR(1536),
    UNIQUE(tenant_id, full_name)
);

-- Files
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    language VARCHAR(50),
    size BIGINT NOT NULL DEFAULT 0,
    last_commit_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, repository_id, path)
);

-- Symbols (functions, classes, etc)
CREATE TABLE symbols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    symbol_type VARCHAR(50) NOT NULL,
    fully_qualified_name TEXT NOT NULL,
    line_start INT NOT NULL,
    line_end INT NOT NULL,
    column_start INT,
    column_end INT,
    signature TEXT,
    docstring TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Symbol relationships (calls, imports)
CREATE TABLE symbol_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    from_symbol_id UUID NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    to_symbol_id UUID NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- 'calls', 'imports', 'implements'
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tests
CREATE TABLE tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    line INT NOT NULL,
    flake_rate FLOAT,
    avg_duration_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Test runs
CREATE TABLE test_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    test_id UUID NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    duration_ms INT,
    output TEXT,
    commit_sha VARCHAR(100),
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- SERVICE OBJECTS
-- ============================================

-- Services
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES teams(id),
    repository_id UUID REFERENCES repositories(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    service_type VARCHAR(50) NOT NULL,
    current_availability FLOAT,
    current_latency_p99 INT,
    monthly_cost_cents BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, slug)
);

-- Endpoints
CREATE TABLE endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    symbol_id UUID REFERENCES symbols(id),
    path TEXT NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_schema JSONB,
    response_schema JSONB,
    request_rate FLOAT,
    error_rate FLOAT,
    latency_p50 INT,
    latency_p99 INT,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Service dependencies
CREATE TABLE service_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    depends_on_service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, service_id, depends_on_service_id)
);

-- ============================================
-- RUNTIME OBJECTS
-- ============================================

-- Environments
CREATE TABLE environments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    environment_type VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'healthy',
    health_score FLOAT,
    require_approval BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, slug)
);

-- Deployments
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    environment_id UUID NOT NULL REFERENCES environments(id) ON DELETE CASCADE,
    commit_sha VARCHAR(100) NOT NULL,
    image TEXT,
    image_digest VARCHAR(255),
    deployed_by_id UUID NOT NULL REFERENCES people(id),
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    replicas INT NOT NULL DEFAULT 0,
    healthy_replicas INT NOT NULL DEFAULT 0,
    hourly_cost_cents BIGINT,
    rollback_to_deployment_id UUID REFERENCES deployments(id),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- OPERATIONS OBJECTS
-- ============================================

-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    mitigated_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    detected_by_id UUID REFERENCES people(id),
    commander_id UUID REFERENCES people(id),
    root_cause TEXT,
    affected_customers INT,
    estimated_revenue_impact_cents BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Incident service mapping
CREATE TABLE incident_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    impact_level VARCHAR(50),
    UNIQUE(incident_id, service_id)
);

-- Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'firing',
    first_fired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_fired_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    acknowledged_by_id UUID REFERENCES people(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- AI OBJECTS
-- ============================================

-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    description TEXT,
    permitted_tools JSONB NOT NULL DEFAULT '[]',
    forbidden_paths JSONB NOT NULL DEFAULT '[]',
    budget_tokens_per_day INT,
    approval_threshold VARCHAR(50) NOT NULL DEFAULT 'risky',
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    execution_count INT NOT NULL DEFAULT 0,
    success_rate FLOAT,
    last_execution_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent executions
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    triggered_by_id UUID NOT NULL REFERENCES people(id),
    goal TEXT NOT NULL,
    observation TEXT,
    plan JSONB,
    steps_executed JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'observing',
    result JSONB,
    evidence_hash VARCHAR(255),
    rollback_available BOOLEAN NOT NULL DEFAULT FALSE,
    tokens_used INT NOT NULL DEFAULT 0,
    cost_cents INT,
    duration_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- BUSINESS OBJECTS
-- ============================================

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    external_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL,
    health_score FLOAT,
    churn_risk FLOAT,
    monthly_revenue_cents BIGINT,
    lifetime_value_cents BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cost tracking
CREATE TABLE cost_objects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id),
    environment_id UUID REFERENCES environments(id),
    category VARCHAR(50) NOT NULL,
    amount_cents BIGINT NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    compute_cents BIGINT,
    storage_cents BIGINT,
    network_cents BIGINT,
    ai_inference_cents BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- REPO AUTOPSY OBJECTS
-- ============================================

-- Autopsy jobs
CREATE TABLE repo_autopsy_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    total_issues INT NOT NULL DEFAULT 0,
    fixable_issues INT NOT NULL DEFAULT 0,
    report JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Autopsy issues
CREATE TABLE repo_autopsy_issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES repo_autopsy_jobs(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    file_path TEXT,
    line_number INT,
    fix_available BOOLEAN NOT NULL DEFAULT FALSE,
    fix_diff TEXT,
    applied BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- EVENT STORE
-- ============================================

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    version INT NOT NULL,
    payload JSONB NOT NULL,
    actor_id UUID REFERENCES people(id),
    actor_type VARCHAR(50) NOT NULL DEFAULT 'system',
    correlation_id UUID,
    causation_id UUID REFERENCES events(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    policy_checks JSONB DEFAULT '[]'
);

CREATE INDEX idx_events_tenant ON events(tenant_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_aggregate ON events(aggregate_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_correlation ON events(correlation_id);

-- ============================================
-- INDICES
-- ============================================

CREATE INDEX idx_people_tenant ON people(tenant_id);
CREATE INDEX idx_repositories_tenant ON repositories(tenant_id);
CREATE INDEX idx_repositories_team ON repositories(team_id);
CREATE INDEX idx_repositories_embedding ON repositories USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_symbols_repo ON symbols(repository_id);
CREATE INDEX idx_symbols_file ON symbols(file_id);
CREATE INDEX idx_symbols_type ON symbols(symbol_type);
CREATE INDEX idx_symbols_embedding ON symbols USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_services_tenant ON services(tenant_id);
CREATE INDEX idx_services_team ON services(team_id);

CREATE INDEX idx_endpoints_service ON endpoints(service_id);

CREATE INDEX idx_deployments_service ON deployments(service_id);
CREATE INDEX idx_deployments_env ON deployments(environment_id);
CREATE INDEX idx_deployments_status ON deployments(status);

CREATE INDEX idx_incidents_tenant ON incidents(tenant_id);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);

CREATE INDEX idx_alerts_tenant ON alerts(tenant_id);
CREATE INDEX idx_alerts_service ON alerts(service_id);
CREATE INDEX idx_alerts_status ON alerts(status);

CREATE INDEX idx_agent_exec_agent ON agent_executions(agent_id);
CREATE INDEX idx_agent_exec_status ON agent_executions(status);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Update modified_at trigger
CREATE OR REPLACE FUNCTION update_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with modified_at
CREATE TRIGGER update_tenants_modified_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

CREATE TRIGGER update_people_modified_at BEFORE UPDATE ON people
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

CREATE TRIGGER update_repositories_modified_at BEFORE UPDATE ON repositories
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

CREATE TRIGGER update_services_modified_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

CREATE TRIGGER update_incidents_modified_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

CREATE TRIGGER update_agents_modified_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_modified_at();

-- Semantic search function
CREATE OR REPLACE FUNCTION search_symbols_semantic(
    query_embedding VECTOR(1536),
    tenant_id UUID,
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE(
    id UUID,
    name VARCHAR,
    symbol_type VARCHAR,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.symbol_type,
        1 - (s.embedding <=> query_embedding) AS similarity
    FROM symbols s
    WHERE s.tenant_id = search_symbols_semantic.tenant_id
        AND s.embedding IS NOT NULL
        AND 1 - (s.embedding <=> query_embedding) > match_threshold
    ORDER BY s.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Graph path query function
CREATE OR REPLACE FUNCTION find_symbol_callers(
    symbol_id UUID,
    max_depth INT DEFAULT 5
)
RETURNS TABLE(
    caller_id UUID,
    caller_name VARCHAR,
    depth INT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE call_tree AS (
        -- Base case: direct callers
        SELECT
            s.id AS caller_id,
            s.name AS caller_name,
            1 AS depth
        FROM symbol_relationships sr
        JOIN symbols s ON sr.from_symbol_id = s.id
        WHERE sr.to_symbol_id = symbol_id
            AND sr.relationship_type = 'calls'

        UNION ALL

        -- Recursive: callers of callers
        SELECT
            s.id,
            s.name,
            ct.depth + 1
        FROM call_tree ct
        JOIN symbol_relationships sr ON sr.to_symbol_id = ct.caller_id
        JOIN symbols s ON sr.from_symbol_id = s.id
        WHERE sr.relationship_type = 'calls'
            AND ct.depth < max_depth
    )
    SELECT DISTINCT ON (caller_id) caller_id, caller_name, depth
    FROM call_tree
    ORDER BY caller_id, depth;
END;
$$ LANGUAGE plpgsql;
