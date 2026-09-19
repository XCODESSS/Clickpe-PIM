SEVERITY = {"low": .2, "medium": .5, "high": .8, "critical": 1.0}


def priority(severity: str, importance: float, confidence: float, days: int | None) -> int:
    if severity not in SEVERITY or not 0 <= importance <= 1 or not 0 <= confidence <= 1:
        raise ValueError("invalid priority input")
    factor = 1.0 if days is None or days <= 30 else 1.15 if days <= 90 else 1.25
    return min(100, round(100 * SEVERITY[severity] * importance * confidence * factor))

