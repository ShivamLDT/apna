import json
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_job_id(value=None):
    if value is None:
        return str(uuid4())
    value = str(value).strip()
    return value or str(uuid4())


def _ensure_structured_file_handler(logger, log_path="every_logs/structured_events.log"):
    if getattr(logger, "_structured_file_handler_attached", False):
        return
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger._structured_file_handler_attached = True


def log_event(
    logger,
    level,
    job_id,
    operation_type,
    file_path=None,
    file_id=None,
    chunk_index=None,
    error_code=None,
    error_message=None,
    extra=None,
):
    _ensure_structured_file_handler(logger)
    payload = {
        "timestamp": _utc_timestamp(),
        "job_id": ensure_job_id(job_id),
        "operation_type": operation_type,
        "file_path": file_path,
        "file_id": file_id,
        "chunk_index": chunk_index,
        "error_code": error_code or "",
        "error_message": error_message or "",
    }
    if extra:
        payload.update(extra)
    logger.log(level, json.dumps(payload, ensure_ascii=True, separators=(",", ":")))


def log_chunk_event(
    logger,
    level,
    job_id,
    operation_type,
    file_path=None,
    file_id=None,
    chunk_index=None,
    error_code=None,
    error_message=None,
    extra=None,
    sample_n=10,
):
    if level != logging.DEBUG:
        log_event(
            logger,
            level,
            job_id,
            operation_type,
            file_path=file_path,
            file_id=file_id,
            chunk_index=chunk_index,
            error_code=error_code,
            error_message=error_message,
            extra=extra,
        )
        return
    if not logger.isEnabledFor(logging.DEBUG):
        return
    index = None
    if chunk_index is not None:
        try:
            index = int(chunk_index)
        except (TypeError, ValueError):
            index = None
    if index is None or sample_n <= 1 or (index % sample_n) == 0:
        log_event(
            logger,
            level,
            job_id,
            operation_type,
            file_path=file_path,
            file_id=file_id,
            chunk_index=chunk_index,
            error_code=error_code,
            error_message=error_message,
            extra=extra,
        )
