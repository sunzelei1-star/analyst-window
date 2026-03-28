from __future__ import annotations

import numpy as np
import pandas as pd

BUSINESS_KEYWORDS = {
    "sales": ["sales", "sale", "gmv"],
    "cost": ["cost", "expense"],
    "profit": ["profit", "net_income", "earning"],
    "revenue": ["revenue", "income"],
    "orders": ["orders", "order", "qty", "quantity"],
    "visitors": ["visitors", "traffic", "uv", "pv"],
    "price": ["close", "price", "nav"],
}


def _find_columns(df: pd.DataFrame, keys: list[str]) -> list[str]:
    cols = []
    for col in df.columns:
        low = str(col).lower()
        if any(k in low for k in keys):
            cols.append(col)
    return cols


def recommend_analysis_paths(df: pd.DataFrame, lang: str = "zh") -> list[str]:
    recommendations: list[str] = []
    date_cols = [c for c in df.columns if "datetime" in str(df[c].dtype) or "date" in str(c).lower() or "time" in str(c).lower()]
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = [c for c in df.columns if str(df[c].dtype) == "object" or str(df[c].dtype).startswith("category")]

    if date_cols and numeric_cols:
        recommendations.append("已检测到时间字段，建议先看趋势变化与环比增长。" if lang == "zh" else "Time fields detected: start with trend tracking and period-over-period growth.")
    if cat_cols and numeric_cols:
        recommendations.append("存在分类字段，建议做分组汇总，快速定位高贡献与低表现类别。" if lang == "zh" else "Category fields found: run grouped summaries to spot high and low performers.")

    sales_cols = _find_columns(df, BUSINESS_KEYWORDS["sales"])
    cost_cols = _find_columns(df, BUSINESS_KEYWORDS["cost"])
    profit_cols = _find_columns(df, BUSINESS_KEYWORDS["profit"])
    if (sales_cols or _find_columns(df, BUSINESS_KEYWORDS["revenue"])) and (cost_cols or profit_cols):
        recommendations.append("检测到销售/成本/利润相关字段，建议做利润率与成本效率分析。" if lang == "zh" else "Sales/cost/profit signals found: evaluate margin and cost efficiency.")

    price_cols = _find_columns(df, BUSINESS_KEYWORDS["price"])
    if price_cols:
        recommendations.append("检测到价格/收盘字段，可进一步做收益率、波动率和回撤分析。" if lang == "zh" else "Price/close fields detected: proceed with return, volatility, and drawdown analysis.")

    if _find_columns(df, BUSINESS_KEYWORDS["orders"]) and _find_columns(df, BUSINESS_KEYWORDS["visitors"]):
        recommendations.append("具备流量与订单字段，推荐做转化率漏斗与异常波动排查。" if lang == "zh" else "Traffic and order fields available: analyze conversion funnel and anomaly spikes.")

    if not recommendations:
        recommendations.append("建议先从基础统计与可视化入手，确认数据质量后再深入分析。" if lang == "zh" else "Start with baseline statistics and charts, then deep-dive after quality checks.")

    return recommendations[:4]


def generate_advanced_key_findings(
    df: pd.DataFrame,
    trend_df: pd.DataFrame | None = None,
    trend_target: str = "",
    top_df: pd.DataFrame | None = None,
    bottom_df: pd.DataFrame | None = None,
    top_target: str = "",
    lang: str = "zh",
) -> list[str]:
    findings: list[str] = []

    miss_ratio = (df.isna().mean() * 100).sort_values(ascending=False)
    high_missing = miss_ratio[miss_ratio >= 20].head(2)
    for col, ratio in high_missing.items():
        findings.append(
            f"字段 {col} 缺失率约 {ratio:.1f}%，建议优先补齐或在建模前剔除。"
            if lang == "zh"
            else f"Column {col} has ~{ratio:.1f}% missing values; fill or exclude before modeling."
        )

    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) < 8:
            continue
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            continue
        outlier_ratio = ((series < (q1 - 1.5 * iqr)) | (series > (q3 + 1.5 * iqr))).mean()
        if outlier_ratio >= 0.05:
            findings.append(
                f"字段 {col} 可能存在异常值（约 {outlier_ratio:.1%}），建议核查极端记录。"
                if lang == "zh"
                else f"Potential outliers in {col} (~{outlier_ratio:.1%}); review extreme records."
            )
            break

    if trend_df is not None and not trend_df.empty and trend_target in trend_df.columns:
        ts = trend_df[trend_target].dropna()
        if len(ts) >= 6 and float(np.abs(ts.mean())) > 1e-9:
            cv = float(ts.std() / np.abs(ts.mean()))
            if cv >= 0.35:
                findings.append(
                    f"{trend_target} 在时间序列中波动较明显（变异系数约 {cv:.2f}），建议拆分阶段复盘。"
                    if lang == "zh"
                    else f"{trend_target} shows visible volatility (CV ~{cv:.2f}); review by period segments."
                )

    if top_df is not None and bottom_df is not None and not top_df.empty and not bottom_df.empty and top_target:
        top_value = float(top_df.iloc[0][top_target])
        bottom_value = float(bottom_df.iloc[0][top_target])
        if bottom_value != 0 and abs(top_value / bottom_value) >= 2:
            findings.append(
                f"Top 与 Bottom 在 {top_target} 上差异显著（约 {top_value / bottom_value:.1f} 倍），可复用头部策略优化尾部。"
                if lang == "zh"
                else f"Top vs Bottom gap on {top_target} is large (~{top_value / bottom_value:.1f}x); replicate winning patterns."
            )

    visitors = _find_columns(df, BUSINESS_KEYWORDS["visitors"])
    orders = _find_columns(df, BUSINESS_KEYWORDS["orders"])
    if visitors and orders:
        v_col, o_col = visitors[0], orders[0]
        denom = df[v_col].replace(0, np.nan)
        if pd.api.types.is_numeric_dtype(df[o_col]) and pd.api.types.is_numeric_dtype(df[v_col]):
            cvt = (df[o_col] / denom).dropna()
            if not cvt.empty and cvt.mean() < 0.02:
                findings.append(
                    f"{o_col}/{v_col} 平均转化率约 {cvt.mean():.2%}，整体偏低，建议先排查流量质量与落地页转化。"
                    if lang == "zh"
                    else f"Average conversion ({o_col}/{v_col}) is {cvt.mean():.2%}, relatively low; inspect traffic quality and funnel steps."
                )

    revenue = _find_columns(df, BUSINESS_KEYWORDS["revenue"] + BUSINESS_KEYWORDS["sales"])
    profit = _find_columns(df, BUSINESS_KEYWORDS["profit"])
    if revenue and profit and pd.api.types.is_numeric_dtype(df[revenue[0]]) and pd.api.types.is_numeric_dtype(df[profit[0]]):
        margin = (df[profit[0]] / df[revenue[0]].replace(0, np.nan)).dropna()
        if not margin.empty and margin.mean() < 0.1:
            findings.append(
                f"{profit[0]}/{revenue[0]} 平均利润率约 {margin.mean():.2%}，偏低，建议关注成本结构与定价策略。"
                if lang == "zh"
                else f"Average margin ({profit[0]}/{revenue[0]}) is {margin.mean():.2%}, relatively low; review cost structure and pricing."
            )

    if not findings:
        findings.append("当前未发现显著异常，建议持续监控趋势与关键指标阈值。" if lang == "zh" else "No major anomalies detected yet; keep monitoring trends and KPI thresholds.")

    return findings[:6]


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
