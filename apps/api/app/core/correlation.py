import contextvars

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    return correlation_id_ctx.get() or ""
