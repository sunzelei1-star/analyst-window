from __future__ import annotations

import pandas as pd


def growth_rate(current: pd.Series, previous: pd.Series) -> pd.Series:
    return (current - previous) / previous.replace(0, pd.NA)


def margin(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace(0, pd.NA)


def conversion_rate(success: pd.Series, total: pd.Series) -> pd.Series:
    return success / total.replace(0, pd.NA)


def weighted_average(values: pd.Series, weights: pd.Series) -> float:
    total_weight = weights.sum()
    if total_weight == 0:
        return float("nan")
    return float((values * weights).sum() / total_weight)
