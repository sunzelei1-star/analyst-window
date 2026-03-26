from __future__ import annotations

import numpy as np
import pandas as pd


def summarize_statistics(cleaned_df: pd.DataFrame, stats_df: pd.DataFrame, corr_df: pd.DataFrame) -> list[str]:
    conclusions: list[str] = []
    conclusions.append(f"数据规模为 {cleaned_df.shape[0]} 行、{cleaned_df.shape[1]} 列。")

    if "missing_count" in stats_df.columns:
        top_missing = stats_df.sort_values("missing_count", ascending=False).head(1)
        if not top_missing.empty:
            conclusions.append(
                f"缺失值最多的字段是 {top_missing.iloc[0]['column']}（{int(top_missing.iloc[0]['missing_count'])} 个）。"
            )

    if not corr_df.empty and len(corr_df.columns) > 1:
        pair = corr_df.where(~np.eye(len(corr_df), dtype=bool)).abs().stack().sort_values(ascending=False)
        if not pair.empty:
            strongest = pair.index[0]
            conclusions.append(f"相关性最强的指标组合是 {strongest[0]} 与 {strongest[1]}。")

    return conclusions


def summarize_trend(trend_df: pd.DataFrame) -> list[str]:
    if trend_df is None or trend_df.empty:
        return ["暂无趋势结论：请先选择日期列和趋势值列。"]

    result: list[str] = []
    latest = trend_df.iloc[-1]
    result.append(f"最新周期值约为 {latest['value']:.2f}。")

    if "mom" in trend_df.columns and pd.notna(latest.get("mom")):
        direction = "上升" if latest["mom"] >= 0 else "下降"
        result.append(f"最近一个周期环比{direction} {abs(latest['mom']):.2%}。")

    if "rolling_avg" in trend_df.columns and pd.notna(latest.get("rolling_avg")):
        result.append(f"短期滚动均值约为 {latest['rolling_avg']:.2f}，可用于判断短期趋势。")

    return result


def summarize_top_bottom(top_df: pd.DataFrame, bottom_df: pd.DataFrame, target_col: str) -> list[str]:
    if top_df is None or top_df.empty or bottom_df is None or bottom_df.empty:
        return ["暂无 Top/Bottom 结论。"]

    top_mean = top_df[target_col].mean()
    bottom_mean = bottom_df[target_col].mean()
    ratio = top_mean / bottom_mean if bottom_mean else float("inf")
    return [
        f"Top 组平均 {target_col} 为 {top_mean:.2f}，Bottom 组平均为 {bottom_mean:.2f}。",
        f"两组均值差距约 {ratio:.2f} 倍，可作为业务分层或资源投放参考。",
    ]
