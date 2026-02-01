"""
Unified UNC/SMB Logging Module for Client-Side Operations.
Provides consistent logging for all UNC/SMB operations including:
- Connection attempts and results
- Path normalization
- Browse operations
- File transfers with throughput stats
- Error tracking
"""
import logging
import logging.handlers
import os
import time
from functools import wraps

# Ensure logs folder exists
os.makedirs("every_logs", exist_ok=True)

UNC_LOG_FILE = "every_logs/unc.log"

# Create dedicated UNC logger
unc_logger = logging.getLogger("UNC_SMB")
unc_logger.setLevel(logging.DEBUG)
unc_logger.propagate = False  # Prevent duplicate logs

# Formatter with timestamp, level, and context
_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler - writes to unc.log
if not any(isinstance(h, logging.FileHandler) and 
           getattr(h, 'baseFilename', '').endswith('unc.log') 
           for h in unc_logger.handlers):
    _file_handler = logging.FileHandler(UNC_LOG_FILE, mode='a', encoding='utf-8')
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(_formatter)
    unc_logger.addHandler(_file_handler)


def mask_credentials(username, password=None):
    """Mask credentials for safe logging - shows first 2 chars only."""
    masked_user = f"{username[:2]}***" if username and len(username) > 2 else "***"
    masked_pass = "****" if password else None
    return masked_user, masked_pass


def log_connection_attempt(host, username, port=445, protocol="SMB3"):
    """Log SMB/UNC connection attempt with masked credentials."""
    masked_user, _ = mask_credentials(username)
    unc_logger.info(
        f"CONNECTION_ATTEMPT | host={host} | port={port} | "
        f"protocol={protocol} | user={masked_user}"
    )


def log_connection_result(host, success, error=None, duration_ms=None):
    """Log connection result with timing."""
    status = "SUCCESS" if success else "FAILED"
    msg = f"CONNECTION_{status} | host={host}"
    if duration_ms:
        msg += f" | duration={duration_ms:.0f}ms"
    if error:
        msg += f" | error={str(error)[:100]}"
    
    if success:
        unc_logger.info(msg)
    else:
        unc_logger.error(msg)


def log_path_normalization(original_path, normalized_path):
    """Log UNC path normalization for debugging."""
    if original_path != normalized_path:
        unc_logger.debug(
            f"PATH_NORMALIZE | original={original_path} | normalized={normalized_path}"
        )


def log_browse_start(host, path, method="browse"):
    """Log browse operation start."""
    unc_logger.info(f"BROWSE_START | host={host} | path={path} | method={method}")


def log_browse_result(host, path, item_count=0, error=None):
    """Log browse operation result."""
    if error:
        unc_logger.error(f"BROWSE_FAILED | host={host} | path={path} | error={str(error)[:100]}")
    else:
        unc_logger.info(f"BROWSE_SUCCESS | host={host} | path={path} | items={item_count}")


def log_transfer_start(operation, source_path, dest_path=None, file_size=None):
    """Log file transfer start (copy/upload/download)."""
    msg = f"TRANSFER_START | op={operation} | source={source_path}"
    if dest_path:
        msg += f" | dest={dest_path}"
    if file_size:
        msg += f" | size={_format_size(file_size)}"
    unc_logger.info(msg)


def log_transfer_complete(operation, path, file_size, duration_seconds, error=None):
    """Log file transfer completion with throughput stats."""
    if error:
        unc_logger.error(
            f"TRANSFER_FAILED | op={operation} | path={path} | error={str(error)[:100]}"
        )
    else:
        throughput = file_size / duration_seconds if duration_seconds > 0 else 0
        unc_logger.info(
            f"TRANSFER_COMPLETE | op={operation} | path={path} | "
            f"size={_format_size(file_size)} | duration={duration_seconds:.2f}s | "
            f"throughput={_format_size(throughput)}/s"
        )


def log_share_list(host, shares, error=None):
    """Log share listing operation."""
    if error:
        unc_logger.error(f"SHARE_LIST_FAILED | host={host} | error={str(error)[:100]}")
    else:
        share_names = [s.get('path', s) if isinstance(s, dict) else str(s) for s in shares[:10]]
        unc_logger.info(
            f"SHARE_LIST_SUCCESS | host={host} | count={len(shares)} | "
            f"shares={share_names}{'...' if len(shares) > 10 else ''}"
        )


def log_error(operation, error, context=None):
    """Log generic UNC/SMB error."""
    msg = f"ERROR | op={operation} | error={str(error)}"
    if context:
        msg += f" | context={context}"
    unc_logger.error(msg)


def log_debug(message):
    """Log debug message."""
    unc_logger.debug(message)


def log_info(message):
    """Log info message."""
    unc_logger.info(message)


def _format_size(size_bytes):
    """Format byte size to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f}MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f}GB"


def timed_operation(operation_name):
    """Decorator to time and log operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                unc_logger.debug(f"TIMING | op={operation_name} | duration={duration_ms:.0f}ms | status=success")
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                unc_logger.error(f"TIMING | op={operation_name} | duration={duration_ms:.0f}ms | status=failed | error={str(e)[:50]}")
                raise
        return wrapper
    return decorator


# Expose logger for direct access if needed
logger = unc_logger
