from __future__ import annotations

import pandas as pd


def get_business_sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=12, freq="MS"),
            "region": ["华东", "华南", "华北", "西南"] * 3,
            "channel": ["电商", "直营", "代理", "电商"] * 3,
            "revenue": [120, 140, 110, 98, 135, 152, 125, 105, 148, 160, 132, 119],
            "cost": [70, 78, 66, 62, 76, 84, 72, 64, 82, 88, 75, 70],
            "orders": [860, 920, 780, 730, 900, 980, 840, 760, 970, 1030, 890, 810],
        }
    )


def get_finance_sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=16, freq="W"),
            "asset": ["组合A"] * 8 + ["组合B"] * 8,
            "price": [100, 101, 102, 103, 105, 104, 106, 108, 96, 97, 99, 100, 101, 100, 102, 104],
            "revenue": [50, 51, 52, 53, 54, 53, 55, 56, 47, 48, 50, 51, 52, 51, 53, 54],
            "cost": [31, 31.5, 32, 33, 34, 33.5, 34.5, 35, 29, 29.5, 30.2, 30.8, 31.1, 30.9, 31.6, 32],
            "net_profit": [12, 12.3, 12.9, 13.1, 13.8, 13.3, 14.1, 14.5, 10.2, 10.4, 10.9, 11.2, 11.4, 11.1, 11.8, 12.1],
        }
    )
