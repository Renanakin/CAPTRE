"""phase2 init

Revision ID: 20260515_01
Revises:
Create Date: 2026-05-15
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260515_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            document_hash TEXT NOT NULL,
            file_name TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            status TEXT NOT NULL,
            responsible TEXT,
            period TEXT,
            center_cost TEXT,
            storage_path TEXT,
            warnings_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(tenant_id, document_hash)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS document_extractions (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            document_type TEXT,
            country_code TEXT,
            confidence REAL,
            extraction_json TEXT NOT NULL,
            raw_extraction_json TEXT,
            extra_fields_json TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(document_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS document_template_mapping (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            header_fields_json TEXT NOT NULL,
            detail_fields_json TEXT NOT NULL,
            missing_fields_json TEXT NOT NULL,
            warnings_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(document_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS renditions (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            period TEXT NOT NULL,
            template_version TEXT NOT NULL,
            file_path TEXT,
            status TEXT NOT NULL,
            warnings_count INTEGER NOT NULL DEFAULT 0,
            summary_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS rendition_items (
            id TEXT PRIMARY KEY,
            rendition_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            row_number INTEGER NOT NULL,
            fields_json TEXT NOT NULL,
            warnings_json TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            actor_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS review_tasks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            reason TEXT,
            warnings_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS review_tasks")
    op.execute("DROP TABLE IF EXISTS audit_events")
    op.execute("DROP TABLE IF EXISTS rendition_items")
    op.execute("DROP TABLE IF EXISTS renditions")
    op.execute("DROP TABLE IF EXISTS document_template_mapping")
    op.execute("DROP TABLE IF EXISTS document_extractions")
    op.execute("DROP TABLE IF EXISTS documents")
