from __future__ import annotations

import pandas as pd

from src.data_tool.analysis.formulas import growth_rate


def describe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe(include="all", datetime_is_numeric=True).T.fillna("")


def group_summary(df: pd.DataFrame, group_col: str, value_col: str, agg: str = "sum") -> pd.DataFrame:
    return df.groupby(group_col, dropna=False)[value_col].agg(agg).reset_index(name=f"{value_col}_{agg}")


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr(numeric_only=True)


def trend_analysis(df: pd.DataFrame, date_col: str, value_col: str, freq: str = "M") -> pd.DataFrame:
    tmp = df[[date_col, value_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna().sort_values(date_col)
    if tmp.empty:
        return pd.DataFrame(columns=["period", "value", "growth_rate", "rolling_avg", "cumulative_sum"])

    series = tmp.set_index(date_col)[value_col].resample(freq).sum()
    result = series.rename("value").to_frame()
    result["growth_rate"] = growth_rate(result["value"], result["value"].shift(1))
    result["rolling_avg"] = result["value"].rolling(3, min_periods=1).mean()
    result["cumulative_sum"] = result["value"].cumsum()
    return result.reset_index(names="period")


def add_period_comparison(trend_df: pd.DataFrame, date_col: str = "period", value_col: str = "value") -> pd.DataFrame:
    if trend_df.empty:
        return trend_df
    result = trend_df.copy().sort_values(date_col)
    result["mom"] = growth_rate(result[value_col], result[value_col].shift(1))
    result["yoy"] = growth_rate(result[value_col], result[value_col].shift(12))
    return result


def top_bottom_analysis(df: pd.DataFrame, value_col: str, n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    sorted_df = df.sort_values(value_col)
    return sorted_df.tail(n), sorted_df.head(n)
