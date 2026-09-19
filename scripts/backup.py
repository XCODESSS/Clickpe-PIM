from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_backup(db_path: Path, data_root: Path, archive: Path) -> Path:
    db_path, data_root, archive = db_path.resolve(), data_root.resolve(), archive.resolve()
    if not db_path.exists():
        raise ValueError("database does not exist")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="clickpe-pim-backup-") as temporary:
        standalone = Path(temporary) / "monitor.sqlite"
        source = sqlite3.connect(db_path)
        destination = sqlite3.connect(standalone)
        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()
        con = sqlite3.connect(standalone)
        try:
            run_ids = [row[0] for row in con.execute("SELECT run_id FROM scrape_runs WHERE status IN ('complete','partial')")]
            raw_paths = [row[0] for row in con.execute("SELECT DISTINCT c.raw_path FROM captures c JOIN scrape_runs r ON r.run_id=c.run_id WHERE r.status IN ('complete','partial') AND c.raw_path IS NOT NULL")]
        finally:
            con.close()
        files: dict[str, Path] = {"database/monitor.sqlite": standalone}
        for raw in raw_paths:
            candidate = (data_root / "raw" / raw).resolve()
            if data_root not in candidate.parents or not candidate.is_file():
                raise ValueError(f"referenced evidence is missing or unsafe: {raw}")
            files[f"data/raw/{Path(raw).as_posix()}"] = candidate
        for run_id in run_ids:
            for relative in (Path("manifests") / f"{run_id}.json", Path("snapshots") / run_id):
                candidate = data_root / relative
                if candidate.is_file():
                    files[f"data/{relative.as_posix()}"] = candidate
                elif candidate.is_dir() and not candidate.name.endswith(".pending"):
                    for item in candidate.rglob("*"):
                        if item.is_file():
                            files[f"data/{item.relative_to(data_root).as_posix()}"] = item
        manifest = {name: _hash(path) for name, path in sorted(files.items())}
        manifest["_schema_version"] = 1
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name, path in sorted(files.items()):
                bundle.write(path, name)
            bundle.writestr("backup-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    print(create_backup(args.db, args.data_root, args.archive))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
