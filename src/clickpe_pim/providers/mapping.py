from pathlib import Path

import yaml

from clickpe_pim.contracts import Mapping


def load_mappings(path: Path) -> list[Mapping]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [Mapping.model_validate(item) for item in payload.get("mappings", [])]

