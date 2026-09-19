import re
import unicodedata

from rapidfuzz import fuzz


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def suggest_alias(name: str, aliases: dict[str, str]) -> list[tuple[str, float]]:
    needle = normalize_name(name)
    return sorted(((entity_id, fuzz.token_set_ratio(needle, normalize_name(alias)) / 100) for alias, entity_id in aliases.items()), key=lambda item: (-item[1], item[0]))

