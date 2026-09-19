from datetime import datetime, timezone


def age_days(last_verified: datetime | None, now: datetime) -> int | None:
    if last_verified is None:
        return None
    if last_verified.tzinfo is None or now.tzinfo is None:
        raise ValueError("timestamps must be aware")
    seconds = (now.astimezone(timezone.utc) - last_verified.astimezone(timezone.utc)).total_seconds()
    if seconds < 0:
        raise ValueError("last_verified cannot be in the future")
    return int(seconds // 86400)


def freshness_band(days: int | None) -> str:
    if days is None:
        return "Unknown"
    if days < 0:
        raise ValueError("days cannot be negative")
    if days <= 7:
        return "Fresh"
    if days <= 30:
        return "Monitor"
    if days <= 90:
        return "Stale"
    return "High priority"

