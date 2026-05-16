import importlib.util
import os
import sqlite3
from pathlib import Path


def _prepare_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute("INSERT INTO documents (id, status, created_at) VALUES (?, ?, ?)", ("doc-1", "RECEIVED", "2026-05-13T00:00:00Z"))
    conn.execute("INSERT INTO documents (id, status, created_at) VALUES (?, ?, ?)", ("doc-2", "COMPLETED", "2026-05-13T00:00:01Z"))
    conn.commit()
    conn.close()


def _load_worker_module():
    worker_path = Path("g:/PROYECTOS/capturador_datos_v2/apps/worker/app/main.py")
    spec = importlib.util.spec_from_file_location("worker_main", worker_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pending_document_ids(tmp_path):
    db_path = str(tmp_path / "worker.db")
    _prepare_db(db_path)

    os.environ["APP_DB_PATH"] = db_path

    worker_main = _load_worker_module()

    pending = worker_main._pending_document_ids(limit=10)
    assert pending == ["doc-1"]


def test_run_once_processes_pending(monkeypatch, tmp_path):
    db_path = str(tmp_path / "worker.db")
    _prepare_db(db_path)

    os.environ["APP_DB_PATH"] = db_path

    worker_main = _load_worker_module()

    monkeypatch.setattr(worker_main, "_process_document", lambda document_id: (True, "ok"))
    processed = worker_main.run_once()
    assert processed == 1
