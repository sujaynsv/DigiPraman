BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

DO $$ BEGIN
    CREATE TYPE role_type AS ENUM ('beneficiary', 'officer', 'admin');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE verification_status AS ENUM (
        'pending','submitted','scored','routed','needs_more','approved','rejected','video_pending','video_done'
    );
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE requirement_type AS ENUM ('photo','video','doc');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE requirement_status AS ENUM ('not_started','in_progress','completed');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE decision_type AS ENUM ('approve','reject','request_more','video_required');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE notification_channel AS ENUM ('sms','email','whatsapp','push');
EXCEPTION WHEN duplicate_object THEN null; END $$;

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    type TEXT,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS schemes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    evidence_template JSONB DEFAULT '{}'::jsonb,
    default_thresholds JSONB DEFAULT '{}'::jsonb,
    locale_options JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    role role_type NOT NULL,
    name TEXT NOT NULL,
    mobile VARCHAR(15) NOT NULL UNIQUE,
    email TEXT UNIQUE,
    locale VARCHAR(8) DEFAULT 'en',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_fingerprint TEXT NOT NULL UNIQUE,
    last_seen TIMESTAMPTZ,
    trust_score NUMERIC(3,2),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS loan_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    scheme_id UUID REFERENCES schemes(id) ON DELETE SET NULL,
    beneficiary_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    loan_ref_no TEXT NOT NULL UNIQUE,
    loan_type TEXT,
    sanctioned_amount NUMERIC(12,2) NOT NULL,
    disbursed_amount NUMERIC(12,2),
    emi_due_date DATE,
    next_emi_date DATE,
    purpose TEXT,
    declared_asset JSONB,
    lifecycle_status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS loan_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    status_from TEXT,
    status_to TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verification_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    initiated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status verification_status NOT NULL DEFAULT 'pending',
    current_tier TEXT,
    thresholds_ref JSONB,
    due_date DATE,
    submitted_at TIMESTAMPTZ,
    scored_at TIMESTAMPTZ,
    routed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verification_requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    type requirement_type NOT NULL,
    required BOOLEAN NOT NULL DEFAULT true,
    instructions TEXT,
    status requirement_status NOT NULL DEFAULT 'not_started',
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    requirement_id UUID REFERENCES verification_requirements(id) ON DELETE SET NULL,
    type requirement_type NOT NULL,
    storage_url TEXT NOT NULL,
    file_key TEXT NOT NULL,
    gps GEOGRAPHY(Point, 4326),
    captured_at TIMESTAMPTZ,
    uploaded_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    evidence_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    sync_status TEXT NOT NULL DEFAULT 'pending',
    retries INT NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS risk_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    scores JSONB NOT NULL,
    risk_score NUMERIC(5,2) NOT NULL,
    risk_tier TEXT NOT NULL,
    recommended_action TEXT,
    flags JSONB,
    explanation JSONB,
    model_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS risk_analyses_verification_unique ON risk_analyses (verification_id);

CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    officer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    decision decision_type NOT NULL,
    notes TEXT,
    attachments JSONB,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS video_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    verification_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL,
    status TEXT NOT NULL,
    provider TEXT,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_id UUID REFERENCES verification_requests(id) ON DELETE SET NULL,
    channel notification_channel NOT NULL,
    template_id TEXT,
    payload JSONB,
    status TEXT NOT NULL,
    sent_at TIMESTAMPTZ,
    delivery_receipt JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id UUID,
    delta JSONB,
    trace_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_schemes_org ON schemes (org_id);
CREATE INDEX IF NOT EXISTS idx_users_org ON users (org_id);
CREATE INDEX IF NOT EXISTS idx_devices_user ON devices (user_id);
CREATE INDEX IF NOT EXISTS idx_loans_org ON loan_applications (org_id);
CREATE INDEX IF NOT EXISTS idx_loans_scheme ON loan_applications (scheme_id);
CREATE INDEX IF NOT EXISTS idx_loans_beneficiary ON loan_applications (beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_loan_history_loan ON loan_status_history (loan_id);
CREATE INDEX IF NOT EXISTS idx_verifications_loan ON verification_requests (loan_id);
CREATE INDEX IF NOT EXISTS idx_verifications_status ON verification_requests (status);
CREATE INDEX IF NOT EXISTS idx_requirements_verification ON verification_requirements (verification_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_evidence_verification ON evidence_items (verification_id);
CREATE INDEX IF NOT EXISTS idx_evidence_requirement ON evidence_items (requirement_id);
CREATE INDEX IF NOT EXISTS idx_evidence_gps ON evidence_items USING GIST (gps);
CREATE INDEX IF NOT EXISTS idx_sync_device ON sync_queue (device_id);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_queue (sync_status);
CREATE INDEX IF NOT EXISTS idx_decisions_verification ON decisions (verification_id);
CREATE INDEX IF NOT EXISTS idx_decisions_officer ON decisions (officer_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_verification ON notifications (verification_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_entries (actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_entries (entity, entity_id);

COMMIT;
