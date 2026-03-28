from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


@dataclass(frozen=True)
class ChartPresentation:
    chart_type: str
    title: str
    subtitle: str
    x_label: str
    y_label: str
    is_time_axis: bool


def build_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_desc = df.describe(include="number").T
    missing = df.isna().sum().rename("missing_count")
    dtypes = df.dtypes.astype(str).rename("dtype")
    uniques = df.nunique(dropna=True).rename("unique_count")

    summary = pd.concat([dtypes, uniques, missing], axis=1)
    if not numeric_desc.empty:
        summary = summary.join(numeric_desc, how="left")
    return summary.reset_index(names="column")


def filter_table(df: pd.DataFrame, column: str, query: str) -> pd.DataFrame:
    if not query:
        return df
    return df[df[column].astype(str).str.contains(query, case=False, na=False)]


def is_time_like_series(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if pd.api.types.is_numeric_dtype(series):
        return False
    if series.dropna().empty:
        return False
    parsed = pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
    return parsed.notna().mean() >= 0.8


def _format_time_axis(ax: plt.Axes, series: pd.Series) -> None:
    parsed = pd.to_datetime(series, errors="coerce")
    parsed = parsed.dropna()
    if parsed.empty:
        return
    time_span_days = (parsed.max() - parsed.min()).days
    tick_count = min(8, max(4, ceil(len(parsed.unique()) / 10)))

    if time_span_days >= 365 * 2:
        locator = mdates.AutoDateLocator(minticks=4, maxticks=tick_count)
        formatter = mdates.DateFormatter("%Y-%m")
    elif time_span_days >= 45:
        locator = mdates.AutoDateLocator(minticks=4, maxticks=tick_count)
        formatter = mdates.DateFormatter("%m-%d")
    else:
        locator = mdates.AutoDateLocator(minticks=4, maxticks=tick_count)
        formatter = mdates.DateFormatter("%m-%d")

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.tick_params(axis="x", labelrotation=25, labelsize=9, pad=6)


def recommended_chart_type(default_chart_type: str, is_time_axis: bool, y_col: str | None = None) -> str:
    if is_time_axis and y_col and default_chart_type in {"柱状图", "折线图"}:
        return "折线图"
    return default_chart_type


def _auto_axis_label(lang: str, x_col: str, y_col: str | None) -> tuple[str, str]:
    if lang == "zh":
        return x_col, y_col if y_col else "数量"
    return x_col, y_col if y_col else "Count"


def build_chart_presentation(
    lang: str,
    x_col: str,
    y_col: str | None,
    chart_type: str,
    is_time_axis: bool,
) -> ChartPresentation:
    x_label, y_label = _auto_axis_label(lang, x_col, y_col)

    if is_time_axis and y_col:
        if lang == "zh":
            title = f"{y_col} 随时间变化趋势"
            subtitle = f"当前展示的是 {y_col} 随时间变化趋势，用于观察周期波动和整体走向。"
        else:
            title = f"{y_col} Trend Over Time"
            subtitle = f"This chart shows how {y_col} changes over time for trend and seasonality reading."
    elif y_col:
        if lang == "zh":
            title = f"{x_col} 与 {y_col} 对比分析"
            subtitle = f"当前展示的是不同 {x_col} 维度下的 {y_col} 对比。"
        else:
            title = f"{y_col} Comparison by {x_col}"
            subtitle = f"This chart compares {y_col} across different {x_col} categories."
    else:
        if lang == "zh":
            title = f"{x_col} 分布概览"
            subtitle = f"当前展示的是 {x_col} 的分布情况。"
        else:
            title = f"{x_col} Distribution Overview"
            subtitle = f"This chart summarizes the distribution of {x_col}."

    return ChartPresentation(
        chart_type=chart_type,
        title=title,
        subtitle=subtitle,
        x_label=x_label,
        y_label=y_label,
        is_time_axis=is_time_axis,
    )


def build_visualization(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str | None = None,
    presentation: ChartPresentation | None = None,
    dark_mode: bool = False,
):
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    sns.set_theme(style="whitegrid")
    if presentation:
        chart_type = presentation.chart_type

    plot_df = df.copy()
    if presentation and presentation.is_time_axis:
        plot_df[x_col] = pd.to_datetime(plot_df[x_col], errors="coerce")
        plot_df = plot_df.dropna(subset=[x_col])

    if dark_mode:
        fig.patch.set_facecolor("#0f172a")
        ax.set_facecolor("#111827")
        text_color = "#e5e7eb"
        grid_color = "#334155"
    else:
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")
        text_color = "#1f2937"
        grid_color = "#d1d5db"

    default_title = ""
    if chart_type == "柱状图":
        if y_col and y_col in plot_df.columns:
            agg = plot_df.groupby(x_col, dropna=False)[y_col].mean().reset_index()
            sns.barplot(data=agg, x=x_col, y=y_col, ax=ax)
            default_title = f"{x_col} vs {y_col} (avg)"
        else:
            counts = plot_df[x_col].value_counts().head(20)
            sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax)
            default_title = f"{x_col} Count"
            ax.set_ylabel("count")
    elif chart_type == "折线图" and y_col:
        sorted_df = plot_df.sort_values(by=x_col)
        sns.lineplot(data=sorted_df, x=x_col, y=y_col, ax=ax)
        default_title = f"{x_col} - {y_col} Trend"
    elif chart_type == "散点图" and y_col:
        sns.scatterplot(data=plot_df, x=x_col, y=y_col, ax=ax)
        default_title = f"{x_col} - {y_col} Scatter"
    elif chart_type == "箱线图" and y_col:
        sns.boxplot(data=plot_df, x=x_col, y=y_col, ax=ax)
        default_title = f"{x_col} - {y_col} Box"
    elif chart_type == "直方图":
        target = y_col if y_col else x_col
        sns.histplot(plot_df[target], kde=True, ax=ax)
        default_title = f"{target} Distribution"
    elif chart_type == "热力图":
        corr = plot_df.select_dtypes(include="number").corr(numeric_only=True)
        if corr.empty:
            plt.close(fig)
            return None
        sns.heatmap(corr, cmap="RdBu_r", center=0, ax=ax)
        default_title = "Correlation Heatmap"
    else:
        plt.close(fig)
        return None

    if presentation:
        ax.set_title(presentation.title, loc="left", pad=16, fontsize=14, fontweight="bold")
        ax.set_xlabel(presentation.x_label, fontsize=10, labelpad=10)
        ax.set_ylabel(presentation.y_label, fontsize=10, labelpad=8)
    elif default_title:
        ax.set_title(default_title, loc="left", pad=16, fontsize=14, fontweight="bold")

    if presentation and presentation.is_time_axis:
        _format_time_axis(ax, plot_df[x_col])
    else:
        plt.xticks(rotation=18, ha="right", fontsize=9)

    ax.tick_params(colors=text_color, labelcolor=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    for spine in ax.spines.values():
        spine.set_color(grid_color)
    ax.grid(color=grid_color, alpha=0.35, linestyle="--", linewidth=0.7)

    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.2)
    return fig
