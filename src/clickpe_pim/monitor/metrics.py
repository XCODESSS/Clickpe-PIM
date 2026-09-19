def weighted_completeness(group_fractions: dict[str, float], weights: dict[str, float]) -> float:
    if not weights or any(not 0 <= value <= 1 for value in group_fractions.values()) or any(value < 0 for value in weights.values()):
        raise ValueError("fractions and weights must be valid")
    denominator = sum(weights.values())
    if denominator <= 0:
        raise ValueError("weight sum must be positive")
    return 100 * sum(weights[group] * group_fractions.get(group, 0) for group in weights) / denominator


def ratio(numerator: int, denominator: int) -> float | None:
    if numerator < 0 or denominator < 0 or numerator > denominator:
        raise ValueError("invalid ratio")
    return numerator / denominator if denominator else None

