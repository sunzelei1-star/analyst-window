from __future__ import annotations

import numpy as np
import pandas as pd


def load_business_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2025-01-01", periods=120, freq="D")
    regions = ["华东", "华北", "华南", "西南"]
    channels = ["线上", "门店", "代理"]

    data = pd.DataFrame(
        {
            "date": dates,
            "region": rng.choice(regions, size=len(dates)),
            "channel": rng.choice(channels, size=len(dates)),
            "sales": rng.normal(22000, 4500, size=len(dates)).clip(8000, 45000).round(0),
            "cost": rng.normal(15000, 3500, size=len(dates)).clip(6000, 30000).round(0),
            "visitors": rng.integers(600, 2600, size=len(dates)),
            "orders": rng.integers(80, 550, size=len(dates)),
        }
    )
    data["profit"] = data["sales"] - data["cost"]
    return data


def load_finance_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    dates = pd.date_range("2024-01-01", periods=260, freq="B")
    returns = rng.normal(0.0006, 0.016, size=len(dates))
    close = 100 * (1 + pd.Series(returns)).cumprod()

    revenue = rng.normal(500000, 70000, size=len(dates)).clip(300000, 750000)
    cost = revenue * rng.uniform(0.52, 0.76, size=len(dates))
    net_profit = revenue * rng.uniform(0.08, 0.19, size=len(dates))

    return pd.DataFrame(
        {
            "date": dates,
            "close": close.round(2),
            "revenue": revenue.round(0),
            "cost": cost.round(0),
            "net_profit": net_profit.round(0),
            "volume": rng.integers(100000, 700000, size=len(dates)),
        }
    )
