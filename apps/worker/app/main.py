import os
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine, text

APP_DB_PATH = os.getenv("APP_DB_PATH", "/tmp/capturador_v2.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{Path(APP_DB_PATH).as_posix()}")
WORKER_MODE = os.getenv("WORKER_MODE", "once")
POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "5"))
BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "20"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME", "document-processing")


def _db_engine():
    return create_engine(DATABASE_URL, future=True)


def _pending_document_ids(limit: int) -> list[str]:
    try:
        with _db_engine().connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT id
                    FROM documents
                    WHERE status = 'RECEIVED'
                    ORDER BY created_at ASC
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            ).mappings().all()
            return [str(row["id"]) for row in rows]
    except Exception:
        return []


def _import_api_processor():
    configured = os.getenv("API_CODE_PATH")
    if configured:
        api_dir = Path(configured)
    else:
        repo_root = Path(__file__).resolve().parents[3]
        api_dir = repo_root / "apps" / "api"
        if not api_dir.exists():
            api_dir = Path("/opt/api")

    api_path = str(api_dir)
    if api_path not in sys.path:
        sys.path.insert(0, api_path)

    from app.services.document_service import process_document  # type: ignore

    return process_document


def _process_document(document_id: str) -> tuple[bool, str]:
    try:
        process_document = _import_api_processor()
        payload = process_document(document_id)
        return True, f"status={payload.get('status', 'unknown')}"
    except Exception as exc:  # noqa: BLE001
        return False, f"error={type(exc).__name__}: {exc}"


def _pop_from_queue(limit: int) -> list[str]:
    try:
        import redis
    except ModuleNotFoundError:
        return []

    try:
        client = redis.from_url(REDIS_URL)
        ids: list[str] = []
        for _ in range(limit):
            value = client.lpop(REDIS_QUEUE_NAME)
            if value is None:
                break
            if isinstance(value, bytes):
                ids.append(value.decode("utf-8"))
            else:
                ids.append(str(value))
        return ids
    except Exception:
        return []


def run_once() -> int:
    doc_ids = _pop_from_queue(BATCH_SIZE)
    if not doc_ids:
        doc_ids = _pending_document_ids(BATCH_SIZE)

    if not doc_ids:
        print("worker: no pending documents")
        return 0

    processed = 0
    for doc_id in doc_ids:
        ok, detail = _process_document(doc_id)
        if ok:
            processed += 1
            print(f"worker: processed {doc_id} ({detail})")
        else:
            print(f"worker: failed {doc_id} ({detail})")

    return processed


def run_loop() -> None:
    print(f"worker: loop mode started, poll={POLL_SECONDS}s")
    while True:
        run_once()
        time.sleep(POLL_SECONDS)


def main() -> None:
    if WORKER_MODE == "loop":
        run_loop()
    else:
        processed = run_once()
        print(f"worker: finished once mode processed={processed}")


if __name__ == "__main__":
    main()
