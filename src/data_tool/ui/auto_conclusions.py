from __future__ import annotations

import pandas as pd


def summarize_stats(stats_df: pd.DataFrame) -> str:
    if stats_df.empty:
        return "统计分析：当前数据暂无可计算的数值指标。"

    if "std" not in stats_df.columns:
        return "统计分析：当前字段以非数值类型为主，建议先补充数值指标。"

    row = stats_df.sort_values(by="std", ascending=False, na_position="last").head(1)
    if row.empty:
        return "统计分析：已完成基础统计，但暂无明显波动指标。"

    metric = row.iloc[0]
    return (
        f"统计分析：字段 {metric['column']} 波动性最高（标准差约 {metric['std']:.2f}），"
        f"均值约 {metric['mean']:.2f}，建议优先跟踪该指标。"
    )


def summarize_trend(trend_df: pd.DataFrame, value_col: str) -> str:
    if trend_df is None or trend_df.empty or value_col not in trend_df.columns:
        return "趋势分析：暂无可用趋势数据。"

    first_val = trend_df[value_col].iloc[0]
    last_val = trend_df[value_col].iloc[-1]
    change = last_val - first_val
    direction = "上升" if change > 0 else "下降" if change < 0 else "持平"
    return f"趋势分析：{value_col} 从 {first_val:.2f} 变化到 {last_val:.2f}，整体呈{direction}趋势。"


def summarize_top_bottom(top_df: pd.DataFrame, bottom_df: pd.DataFrame, target: str) -> str:
    if top_df is None or bottom_df is None or top_df.empty or bottom_df.empty:
        return "Top/Bottom：暂无足够数据生成排名解释。"

    top_name = str(top_df.iloc[0, 0])
    top_value = top_df.iloc[0][target]
    bottom_name = str(bottom_df.iloc[0, 0])
    bottom_value = bottom_df.iloc[0][target]
    return (
        f"业务排名：{top_name} 在 {target} 指标上表现最佳（{top_value:.2f}），"
        f"{bottom_name} 相对较弱（{bottom_value:.2f}），可聚焦资源复用与改进。"
    )
