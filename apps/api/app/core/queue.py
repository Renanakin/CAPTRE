import os


def enqueue_document_processing(document_id: str) -> bool:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    queue_name = os.getenv("REDIS_QUEUE_NAME", "document-processing")

    try:
        import redis
    except ModuleNotFoundError:
        return False

    try:
        client = redis.from_url(redis_url)
        client.rpush(queue_name, document_id)
        return True
    except Exception:
        return False
