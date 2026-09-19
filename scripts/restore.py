from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts and not (path.parts and ":" in path.parts[0])


def restore_backup(archive: Path, destination: Path) -> Path:
    archive, destination = archive.resolve(), destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("restore destination must be new or empty")
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if any(not _safe(name) for name in names):
            raise ValueError("archive contains an unsafe path")
        if "backup-manifest.json" not in names:
            raise ValueError("backup manifest is missing")
        manifest = json.loads(bundle.read("backup-manifest.json"))
        if manifest.pop("_schema_version", None) != 1:
            raise ValueError("unsupported backup schema")
        if set(manifest) != set(names) - {"backup-manifest.json"}:
            raise ValueError("archive contents do not match manifest")
        for name, expected in manifest.items():
            payload = bundle.read(name)
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f"hash mismatch: {name}")
            target = destination / PurePosixPath(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    database = destination / "database/monitor.sqlite"
    if not database.exists():
        raise ValueError("restored database is missing")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(restore_backup(args.archive, args.destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

