import os
import uuid

from dataclasses import dataclass
from typing import Any, Optional
from langfuse.langchain import CallbackHandler
import logging
from config.settings import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)

@dataclass
class Observability:
    run_id: uuid.UUID
    handler: Optional [Any] = None

def build_observability() -> Observability:
    """Return a Langfuse CallbackHandler if the SDK is installed, else None."""
    handler = CallbackHandler()
    return Observability(run_id=uuid.uuid4(), handler=handler)

def resolve_trace_id(observability: Observability) -> str:
    """Best-effort trace id: Langfuse handler's id if available, else the run id."""
    if observability.handler is not None:
        get_trace_id_fn = getattr(observability.handler, "get_trace_id", None)
        if callable(get_trace_id_fn):
            try:
                langfuse_trace_id = get_trace_id_fn()
                if langfuse_trace_id:
                    return str(langfuse_trace_id)
            except Exception:
                pass

        langfuse_trace_id = getattr(observability.handler, "trace_id", None)

        if langfuse_trace_id:
            return str(langfuse_trace_id)
    return str(observability.run_id)

def flush(observability: Observability) -> None:
    """Flush the tracer so spans are sent before the process exits."""
    if observability.handler is not None:
        flush_fn = getattr(observability.handler, "flush", None)
        if callable(flush_fn):
            try:
                flush_fn()
            except Exception:
                pass