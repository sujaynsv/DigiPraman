-- ====================
-- EXTENSIONS (Enable only once)
-- ====================
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;


-- ====================
-- ENUM TYPES
-- ====================

CREATE TYPE role_type AS ENUM ('beneficiary', 'officer', 'admin');
CREATE TYPE verification_status AS ENUM (
    'pending','submitted','scored','routed','needs_more','approved','rejected','video_pending','video_done'
);
CREATE TYPE requirement_type AS ENUM ('photo', 'video', 'doc');
CREATE TYPE requirement_status AS ENUM ('not_started', 'in_progress', 'completed');
CREATE TYPE decision_type AS ENUM ('approve', 'reject', 'request_more', 'video_required');
CREATE TYPE notification_channel AS ENUM ('sms','email','whatsapp','push');


-- ====================
-- TABLES & INDEXES
-- ====================

-- organizations
CREATE TABLE organizations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    type        TEXT,
    config      JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- schemes
CREATE TABLE schemes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _org_id           UUID NOT NULL,
    code              TEXT UNIQUE NOT NULL,
    name              TEXT NOT NULL,
    evidence_template JSONB,
    default_thresholds JSONB,
    locale_options    JSONB,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_schemes_org FOREIGN KEY (_org_id)
        REFERENCES organizations (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_schemes_org ON schemes (_org_id);

-- users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _org_id     UUID NOT NULL,
    role        role_type NOT NULL,
    name        TEXT NOT NULL,
    mobile      VARCHAR(15) UNIQUE NOT NULL,
    email       TEXT,
    locale      VARCHAR(8),
    status      TEXT NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_users_org FOREIGN KEY (_org_id)
        REFERENCES organizations (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_users_org ON users (_org_id);

-- devices
CREATE TABLE devices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _user_id            UUID NOT NULL,
    device_fingerprint  TEXT UNIQUE NOT NULL,
    last_seen           TIMESTAMPTZ,
    trust_score         NUMERIC(3,2),
    metadata            JSONB,
    CONSTRAINT fk_devices_user FOREIGN KEY (_user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_devices_user ON devices (_user_id);

-- loan_applications
CREATE TABLE loan_applications (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _org_id           UUID NOT NULL,
    _scheme_id        UUID NOT NULL,
    _beneficiary_id   UUID NOT NULL,
    loan_ref_no       TEXT UNIQUE NOT NULL,
    loan_type         TEXT,
    sanctioned_amount NUMERIC(12,2),
    disbursed_amount  NUMERIC(12,2),
    emi_due_date      DATE,
    next_emi_date     DATE,
    purpose           TEXT,
    declared_asset    JSONB,
    lifecycle_status  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_loans_org FOREIGN KEY (_org_id)
        REFERENCES organizations (id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_loans_scheme FOREIGN KEY (_scheme_id)
        REFERENCES schemes (id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_loans_beneficiary FOREIGN KEY (_beneficiary_id)
        REFERENCES users (id)
        ON DELETE RESTRICT
);
CREATE INDEX idx_loans_org          ON loan_applications (_org_id);
CREATE INDEX idx_loans_scheme       ON loan_applications (_scheme_id);
CREATE INDEX idx_loans_beneficiary  ON loan_applications (_beneficiary_id);

-- loan_status_history
CREATE TABLE loan_status_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _loan_id    UUID NOT NULL,
    status_from TEXT,
    status_to   TEXT NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_lsh_loan FOREIGN KEY (_loan_id)
        REFERENCES loan_applications (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_lsh_loan           ON loan_status_history (_loan_id);
CREATE INDEX idx_lsh_loan_created   ON loan_status_history (_loan_id, created_at);

-- verification_requests
CREATE TABLE verification_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _loan_id        UUID NOT NULL,
    initiated_by    UUID NOT NULL,
    status          verification_status NOT NULL DEFAULT 'pending',
    current_tier    TEXT,
    thresholds_ref  JSONB,
    due_date        DATE,
    submitted_at    TIMESTAMPTZ,
    scored_at       TIMESTAMPTZ,
    routed_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_verif_loan FOREIGN KEY (_loan_id)
        REFERENCES loan_applications (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_verif_initiator FOREIGN KEY (initiated_by)
        REFERENCES users (id)
        ON DELETE RESTRICT
);
CREATE INDEX idx_verif_loan   ON verification_requests (_loan_id);
CREATE INDEX idx_verif_status ON verification_requests (status);

-- verification_requirements
CREATE TABLE verification_requirements (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _verification_id UUID NOT NULL,
    label           TEXT NOT NULL,
    type            requirement_type NOT NULL,
    required        BOOLEAN NOT NULL DEFAULT true,
    instructions    TEXT,
    status          requirement_status NOT NULL DEFAULT 'not_started',
    sort_order      INTEGER,
    CONSTRAINT fk_vreq_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_vreq_verif               ON verification_requirements (_verification_id);
CREATE INDEX idx_vreq_verif_sort_order    ON verification_requirements (_verification_id, sort_order);

-- evidence_items
CREATE TABLE evidence_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _verification_id UUID NOT NULL,
    _requirement_id UUID,
    type            requirement_type NOT NULL,
    storage_url     TEXT,
    file_key        TEXT,
    gps             GEOGRAPHY(POINT, 4326),
    captured_at     TIMESTAMPTZ,
    uploaded_at     TIMESTAMPTZ,
    metadata        JSONB,
    CONSTRAINT fk_evi_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evi_req FOREIGN KEY (_requirement_id)
        REFERENCES verification_requirements (id)
        ON DELETE SET NULL
);
CREATE INDEX idx_evi_verif      ON evidence_items (_verification_id);
CREATE INDEX idx_evi_req        ON evidence_items (_requirement_id);
CREATE INDEX idx_evi_gps_gist   ON evidence_items USING GIST (gps);

-- sync_queue
CREATE TABLE sync_queue (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _device_id      UUID NOT NULL,
    _evidence_id    UUID NOT NULL,
    sync_status     TEXT NOT NULL,
    retries         INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    error_message   TEXT,
    CONSTRAINT fk_sync_device FOREIGN KEY (_device_id)
        REFERENCES devices (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_sync_evidence FOREIGN KEY (_evidence_id)
        REFERENCES evidence_items (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_sync_device    ON sync_queue (_device_id);
CREATE INDEX idx_sync_status    ON sync_queue (sync_status);

-- risk_analyses
CREATE TABLE risk_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _verification_id UUID NOT NULL UNIQUE,
    version         TEXT,
    scores          JSONB,
    risk_score      NUMERIC(5,2),
    risk_tier       TEXT,
    recommended_action TEXT,
    flags           JSONB,
    explanation     JSONB,
    model_metadata  JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_risk_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_risk_tier ON risk_analyses (risk_tier);

-- decisions
CREATE TABLE decisions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _verification_id UUID NOT NULL,
    _officer_id     UUID NOT NULL,
    decision        decision_type NOT NULL,
    notes           TEXT,
    attachments     JSONB,
    decided_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT fk_decision_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_decision_officer FOREIGN KEY (_officer_id)
        REFERENCES users (id)
        ON DELETE RESTRICT
);
CREATE INDEX idx_decision_verif   ON decisions (_verification_id);
CREATE INDEX idx_decision_officer ON decisions (_officer_id);

-- video_sessions
CREATE TABLE video_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _verification_id UUID NOT NULL,
    session_token   TEXT,
    status          TEXT,
    provider        TEXT,
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    CONSTRAINT fk_video_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE CASCADE
);
CREATE INDEX idx_video_verif  ON video_sessions (_verification_id);
CREATE INDEX idx_video_status ON video_sessions (status);

-- notifications
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _user_id        UUID NOT NULL,
    _verification_id UUID,
    channel         notification_channel NOT NULL,
    template_id     TEXT,
    payload         JSONB,
    status          TEXT,
    sent_at         TIMESTAMPTZ,
    delivery_receipt JSONB,
    CONSTRAINT fk_notif_user FOREIGN KEY (_user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_notif_verif FOREIGN KEY (_verification_id)
        REFERENCES verification_requests (id)
        ON DELETE SET NULL
);
CREATE INDEX idx_notif_user   ON notifications (_user_id);
CREATE INDEX idx_notif_verif  ON notifications (_verification_id);
CREATE INDEX idx_notif_status ON notifications (status);

-- audit_entries
CREATE TABLE audit_entries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    _actor_id   UUID NOT NULL,
    action      TEXT NOT NULL,
    entity      TEXT NOT NULL,
    entity_id   UUID,
    delta       JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    trace_id    TEXT,
    CONSTRAINT fk_audit_actor FOREIGN KEY (_actor_id)
        REFERENCES users (id)
        ON DELETE SET NULL
);
CREATE INDEX idx_audit_actor      ON audit_entries (_actor_id);
CREATE INDEX idx_audit_entity     ON audit_entries (entity);
CREATE INDEX idx_audit_entity_id  ON audit_entries (entity_id);
