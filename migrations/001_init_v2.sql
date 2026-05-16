-- V2 initial schema bootstrap

CREATE TABLE IF NOT EXISTS documents (
	id UUID PRIMARY KEY,
	tenant_id VARCHAR(64) NOT NULL,
	document_hash CHAR(64) NOT NULL,
	file_name VARCHAR(255) NOT NULL,
	mime_type VARCHAR(64) NOT NULL,
	status VARCHAR(32) NOT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE (tenant_id, document_hash)
);

CREATE INDEX IF NOT EXISTS idx_documents_tenant_status
	ON documents (tenant_id, status);

CREATE TABLE IF NOT EXISTS document_extractions (
	id UUID PRIMARY KEY,
	document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
	provider VARCHAR(64) NOT NULL,
	document_type VARCHAR(32),
	country_code VARCHAR(8),
	confidence NUMERIC(5,4),
	extraction JSONB NOT NULL,
	raw_extraction JSONB,
	extra_fields JSONB,
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_document_extractions_document
	ON document_extractions (document_id);

CREATE TABLE IF NOT EXISTS audit_events (
	id UUID PRIMARY KEY,
	entity_type VARCHAR(32) NOT NULL,
	entity_id UUID NOT NULL,
	event_type VARCHAR(64) NOT NULL,
	payload JSONB NOT NULL,
	actor_id VARCHAR(64),
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_template_mapping (
	id UUID PRIMARY KEY,
	document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
	header_fields JSONB NOT NULL,
	detail_fields JSONB NOT NULL,
	missing_fields JSONB NOT NULL,
	warnings_count INT NOT NULL DEFAULT 0,
	created_at TIMESTAMP NOT NULL DEFAULT NOW(),
	UNIQUE (document_id)
);

CREATE TABLE IF NOT EXISTS renditions (
	id UUID PRIMARY KEY,
	tenant_id VARCHAR(64) NOT NULL,
	period VARCHAR(7) NOT NULL,
	template_version VARCHAR(64) NOT NULL,
	file_url TEXT,
	status VARCHAR(32) NOT NULL,
	warnings_count INT NOT NULL DEFAULT 0,
	summary JSONB NOT NULL,
	generated_at TIMESTAMP,
	created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rendition_items (
	id UUID PRIMARY KEY,
	rendition_id UUID NOT NULL REFERENCES renditions(id) ON DELETE CASCADE,
	document_id UUID NOT NULL REFERENCES documents(id),
	row_number INT NOT NULL,
	fields JSONB NOT NULL,
	warnings JSONB
);
