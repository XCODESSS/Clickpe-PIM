from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def save_bytes(root: Path, run_id: str, source_id: str, payload: bytes, suffix: str) -> tuple[Path, str]:
    if not SAFE_ID.fullmatch(run_id) or not SAFE_ID.fullmatch(source_id):
        raise ValueError("run_id and source_id must contain only letters, digits, underscore, or dash")
    if not suffix.startswith(".") or "/" in suffix or "\\" in suffix:
        raise ValueError("suffix must be a simple extension")
    digest = hashlib.sha256(payload).hexdigest()
    relative = Path(run_id) / f"{source_id}{suffix}"
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() == payload:
            return relative, digest
        raise FileExistsError(f"immutable capture already exists: {target}")
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        target.unlink(missing_ok=True)
        raise
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise OSError("capture verification failed")
    return relative, digest

