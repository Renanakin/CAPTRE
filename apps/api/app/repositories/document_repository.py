import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.engine import Engine, Result

_ENGINE_CACHE: dict[str, Engine] = {}


def _database_url() -> str:
    configured = os.getenv("DATABASE_URL")
    if configured:
        return configured

    app_db_path = os.getenv("APP_DB_PATH")
    if app_db_path:
        return f"sqlite:///{Path(app_db_path).as_posix()}"

    return "sqlite:////tmp/capturador_v2.db"


def _engine() -> Engine:
    db_url = _database_url()
    cached = _ENGINE_CACHE.get(db_url)
    if cached is not None:
        return cached

    engine = create_engine(db_url, future=True)
    _ENGINE_CACHE[db_url] = engine
    return engine


@dataclass
class _RowCompat:
    _data: dict[str, Any]

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            return list(self._data.values())[key]
        return self._data[key]


class _ResultCompat:
    def __init__(self, result: Result):
        try:
            self._rows = [_RowCompat(dict(row)) for row in result.mappings().all()]
        except ResourceClosedError:
            self._rows = []

    def fetchone(self):
        if not self._rows:
            return None
        return self._rows[0]

    def fetchall(self):
        return self._rows


class DbConnection:
    def __init__(self) -> None:
        self._conn = _engine().connect()
        self._tx = self._conn.begin()

    def _convert_query(self, sql: str, params: tuple[Any, ...] | list[Any] | None) -> tuple[str, dict[str, Any]]:
        if not params:
            return sql, {}

        values = list(params)
        index = 0

        def replace_qmark(_: re.Match[str]) -> str:
            nonlocal index
            placeholder = f"p{index}"
            index += 1
            return f":{placeholder}"

        converted = re.sub(r"\?", replace_qmark, sql)
        bind_params = {f"p{i}": value for i, value in enumerate(values)}
        return converted, bind_params

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] | None = None) -> _ResultCompat:
        converted_sql, bind_params = self._convert_query(sql, params)
        result = self._conn.execute(text(converted_sql), bind_params)
        return _ResultCompat(result)

    def commit(self) -> None:
        if self._tx.is_active:
            self._tx.commit()
        self._tx = self._conn.begin()

    def close(self) -> None:
        if self._tx.is_active:
            self._tx.rollback()
        self._conn.close()


def get_db_connection() -> DbConnection:
    return DbConnection()


def init_database() -> None:
    conn = get_db_connection()
    try:
        conn.execute(
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
        conn.execute(
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
        conn.execute(
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
        conn.execute(
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
        conn.execute(
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
        conn.execute(
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_tasks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                reason TEXT,
                decision TEXT,
                reviewer_id TEXT,
                resolution_reason TEXT,
                resolved_at TEXT,
                warnings_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_accounts (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                company_id TEXT NOT NULL,
                is_bootstrap INTEGER NOT NULL DEFAULT 0,
                must_change_password INTEGER NOT NULL DEFAULT 0,
                password_changed_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_id TEXT NOT NULL UNIQUE,
                revoked INTEGER NOT NULL DEFAULT 0,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        review_columns = [
            ("decision", "TEXT"),
            ("reviewer_id", "TEXT"),
            ("resolution_reason", "TEXT"),
            ("resolved_at", "TEXT"),
        ]
        user_account_columns = [
            ("is_bootstrap", "INTEGER NOT NULL DEFAULT 0"),
            ("must_change_password", "INTEGER NOT NULL DEFAULT 0"),
            ("password_changed_at", "TEXT"),
        ]
        if _database_url().startswith("sqlite"):
            existing = {row["name"] for row in conn.execute("PRAGMA table_info(review_tasks)").fetchall()}
            for column_name, column_type in review_columns:
                if column_name not in existing:
                    conn.execute(f"ALTER TABLE review_tasks ADD COLUMN {column_name} {column_type}")
            existing_users = {row["name"] for row in conn.execute("PRAGMA table_info(user_accounts)").fetchall()}
            for column_name, column_type in user_account_columns:
                if column_name not in existing_users:
                    conn.execute(f"ALTER TABLE user_accounts ADD COLUMN {column_name} {column_type}")
        else:
            for column_name, column_type in review_columns:
                conn.execute(f"ALTER TABLE review_tasks ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
            for column_name, column_type in user_account_columns:
                conn.execute(f"ALTER TABLE user_accounts ADD COLUMN IF NOT EXISTS {column_name} {column_type}")

        _seed_auth_users(conn)
        conn.commit()
    finally:
        conn.close()


def _seed_auth_users(conn: DbConnection) -> None:
    if not _seed_users_enabled():
        return

    try:
        from app.services.auth_service import hash_password_for_seed
    except Exception:
        return

    default_password = os.getenv("DEFAULT_SEED_PASSWORD", "change_me_123")
    created_at = datetime.now(timezone.utc).isoformat()
    seeds = [
        ("admin", "admin", "*"),
        ("contador", "contador", "real-go-nogo"),
        ("ejecutivo", "ejecutivo", "real-go-nogo"),
        ("auditor", "auditor", "real-go-nogo"),
    ]

    for username, role, company_id in seeds:
        existing = conn.execute("SELECT id FROM user_accounts WHERE username = ?", (username,)).fetchone()
        if existing:
            continue
        conn.execute(
            """
            INSERT INTO user_accounts (id, username, password_hash, role, company_id, is_bootstrap, must_change_password, password_changed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                username,
                hash_password_for_seed(default_password),
                role,
                company_id,
                1,
                1,
                None,
                created_at,
            ),
        )


def _seed_users_enabled() -> bool:
    env = (os.getenv("ENV", "dev") or "dev").strip().lower()
    if env in {"prod", "production", "staging"}:
        return False

    configured = os.getenv("AUTH_SEED_USERS")
    if configured is None:
        return True
    return configured.lower() in {"1", "true", "yes", "on"}
