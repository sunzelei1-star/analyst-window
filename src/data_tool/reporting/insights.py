from __future__ import annotations

import pandas as pd


def generate_table_insights(df: pd.DataFrame, stats_df: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    insights.append(f"数据共 {len(df)} 行、{df.shape[1]} 列。")

    missing_total = int(df.isna().sum().sum())
    insights.append(f"全表缺失值总数：{missing_total}。")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        variances = df[numeric_cols].var().sort_values(ascending=False)
        insights.append(f"波动最大的数值字段：{variances.index[0]}。")

    if "missing_count" in stats_df.columns:
        top_missing = stats_df.sort_values("missing_count", ascending=False).head(1)
        if not top_missing.empty:
            insights.append(
                f"缺失最多字段：{top_missing.iloc[0]['column']}（{int(top_missing.iloc[0]['missing_count'])}）。"
            )

    return insights


def generate_finance_insights(finance_df: pd.DataFrame) -> list[str]:
    if finance_df.empty:
        return ["金融分析数据为空，无法生成关键发现。"]

    insights: list[str] = []
    if "cum_return" in finance_df.columns:
        insights.append(f"累计收益率：{finance_df['cum_return'].iloc[-1]:.2%}。")
    if "volatility" in finance_df.columns:
        insights.append(f"近窗口年化波动率均值：{finance_df['volatility'].dropna().mean():.2%}。")
    if "drawdown" in finance_df.columns:
        insights.append(f"最大回撤：{finance_df['drawdown'].min():.2%}。")
    return insights


def generate_text_insights(clustered_df: pd.DataFrame) -> list[str]:
    if clustered_df.empty:
        return ["文本数据为空，无法生成关键发现。"]

    insights: list[str] = []
    category_dist = clustered_df["category"].value_counts().to_dict()
    insights.append(f"文本分类分布：{category_dist}。")

    if "cluster" in clustered_df.columns:
        cluster_size = clustered_df["cluster"].value_counts().to_dict()
        insights.append(f"聚类规模分布：{cluster_size}。")

    return insights
