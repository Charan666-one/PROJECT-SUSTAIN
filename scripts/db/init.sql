-- Homoeo CDSS initial DB setup
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text similarity search

-- Audit log table (immutable append-only)
CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type      VARCHAR(100) NOT NULL,
    actor_id        UUID NOT NULL,
    target_id       UUID,
    target_type     VARCHAR(100),
    payload         JSONB,
    ip_address      VARCHAR(45),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- DPDP consent log (immutable)
CREATE TABLE IF NOT EXISTS consent_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL,
    consent_version VARCHAR(10) NOT NULL,
    consented_at    TIMESTAMP DEFAULT NOW(),
    ip_address      VARCHAR(45),
    revoked_at      TIMESTAMP
);
