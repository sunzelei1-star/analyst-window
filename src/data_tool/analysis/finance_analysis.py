from __future__ import annotations

import pandas as pd


def add_return_metrics(df: pd.DataFrame, price_col: str) -> pd.DataFrame:
    result = df.copy()
    result = result.sort_values(by=result.columns[0])
    result["return"] = result[price_col].pct_change()
    result["cum_return"] = (1 + result["return"].fillna(0)).cumprod() - 1
    result["volatility"] = result["return"].rolling(20, min_periods=5).std() * (252**0.5)
    result["ma_5"] = result[price_col].rolling(5, min_periods=1).mean()
    result["ma_20"] = result[price_col].rolling(20, min_periods=1).mean()

    running_max = result[price_col].cummax()
    drawdown = result[price_col] / running_max - 1
    result["drawdown"] = drawdown
    return result


def summarize_finance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "return" not in df.columns:
        return pd.DataFrame()
    max_drawdown = df["drawdown"].min()
    total_return = df["cum_return"].iloc[-1]
    annual_vol = df["return"].std() * (252**0.5)
    return pd.DataFrame(
        [
            {"metric": "total_return", "value": total_return},
            {"metric": "annual_volatility", "value": annual_vol},
            {"metric": "max_drawdown", "value": max_drawdown},
        ]
    )


def add_financial_statement_metrics(
    df: pd.DataFrame,
    revenue_col: str,
    cost_col: str,
    net_profit_col: str | None = None,
) -> pd.DataFrame:
    result = df.copy()
    result["gross_profit"] = result[revenue_col] - result[cost_col]
    result["gross_margin"] = result["gross_profit"] / result[revenue_col].replace(0, pd.NA)

    if net_profit_col and net_profit_col in result.columns:
        result["net_margin"] = result[net_profit_col] / result[revenue_col].replace(0, pd.NA)
    return result
