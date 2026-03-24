from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_desc = df.describe(include="number").T
    missing = df.isna().sum().rename("missing_count")
    dtypes = df.dtypes.astype(str).rename("dtype")
    uniques = df.nunique(dropna=True).rename("unique_count")

    summary = pd.concat([dtypes, uniques, missing], axis=1)
    if not numeric_desc.empty:
        summary = summary.join(numeric_desc, how="left")
    summary = summary.reset_index().rename(columns={"index": "column"})
    return summary


def filter_table(df: pd.DataFrame, column: str, query: str) -> pd.DataFrame:
    if not query:
        return df
    return df[df[column].astype(str).str.contains(query, case=False, na=False)]


def build_visualization(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str | None = None,
):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.set_theme(style="whitegrid")

    if chart_type == "柱状图":
        if y_col and y_col in df.columns:
            agg = df.groupby(x_col, dropna=False)[y_col].mean().reset_index()
            sns.barplot(data=agg, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"{x_col} vs {y_col}（均值）")
        else:
            counts = df[x_col].value_counts().head(20)
            sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax)
            ax.set_title(f"{x_col} 频次")
            ax.set_ylabel("count")
    elif chart_type == "折线图" and y_col:
        sorted_df = df.sort_values(by=x_col)
        sns.lineplot(data=sorted_df, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"{x_col} - {y_col} 折线")
    elif chart_type == "散点图" and y_col:
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"{x_col} - {y_col} 散点")
    elif chart_type == "箱线图" and y_col:
        sns.boxplot(data=df, x=x_col, y=y_col, ax=ax)
        ax.set_title(f"{x_col} - {y_col} 箱线")
    elif chart_type == "直方图":
        target = y_col if y_col else x_col
        sns.histplot(df[target], kde=True, ax=ax)
        ax.set_title(f"{target} 分布")
    elif chart_type == "热力图":
        numeric_df = df.select_dtypes(include="number")
        if numeric_df.empty:
            plt.close(fig)
            return None
        try:
            corr = numeric_df.corr(numeric_only=True)
        except TypeError:
            corr = numeric_df.corr()
        sns.heatmap(corr, cmap="RdBu_r", center=0, ax=ax)
        ax.set_title("数值列相关性热力图")
    else:
        plt.close(fig)
        return None

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    return fig
