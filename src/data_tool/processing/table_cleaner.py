from __future__ import annotations

import pandas as pd


def clean_table_data(
    df: pd.DataFrame,
    drop_duplicates: bool = True,
    strip_strings: bool = True,
    fill_numeric_na: bool = True,
    fill_text_na: bool = True,
    normalize_columns: bool = True,
    detect_dates: bool = True,
    infer_numeric: bool = True,
    handle_outliers: bool = True,
    outlier_method: str = "iqr_clip",
    scale_method: str = "none",
) -> tuple[pd.DataFrame, list[str]]:
    """Clean tabular data with configurable preprocessing steps."""
    cleaned = df.copy()
    logs: list[str] = []

    if normalize_columns:
        old_cols = cleaned.columns.tolist()
        cleaned.columns = [str(c).strip().lower().replace(" ", "_") for c in cleaned.columns]
        logs.append(f"标准化列名：{old_cols} -> {cleaned.columns.tolist()}")

    if strip_strings:
        obj_cols = cleaned.select_dtypes(include="object").columns
        for col in obj_cols:
            cleaned[col] = cleaned[col].astype(str).str.strip()
        logs.append(f"清理文本列首尾空格：{len(obj_cols)} 列")

    if infer_numeric:
        converted = 0
        for col in cleaned.columns:
            if cleaned[col].dtype == "object":
                converted_series = pd.to_numeric(cleaned[col], errors="coerce")
                if converted_series.notna().mean() >= 0.8:
                    cleaned[col] = converted_series
                    converted += 1
        logs.append(f"自动识别并转换数值列：{converted} 列")

    if detect_dates:
        converted = 0
        for col in cleaned.columns:
            if cleaned[col].dtype == "object" and _looks_like_date_column(cleaned[col]):
                cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
                converted += 1
        logs.append(f"自动识别并转换日期列：{converted} 列")

    if drop_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        logs.append(f"去重：删除 {before - len(cleaned)} 行")

    if fill_numeric_na:
        numeric_cols = cleaned.select_dtypes(include="number").columns
        for col in numeric_cols:
            if cleaned[col].isna().any():
                cleaned[col] = cleaned[col].fillna(cleaned[col].median())
        logs.append(f"数值缺失值填充（中位数）：{len(numeric_cols)} 列")

    if fill_text_na:
        text_cols = cleaned.select_dtypes(include="object").columns
        for col in text_cols:
            cleaned[col] = cleaned[col].replace("nan", "").fillna("")
        logs.append(f"文本缺失值填充：{len(text_cols)} 列")

    if handle_outliers:
        outlier_report = detect_outliers(cleaned)
        clipped = apply_outlier_strategy(cleaned, outlier_report, method=outlier_method)
        cleaned = clipped
        outlier_cols = (outlier_report["outlier_count"] > 0).sum()
        logs.append(f"异常值处理({outlier_method})：{outlier_cols} 列存在异常值")

    if scale_method != "none":
        cleaned = apply_scaling(cleaned, method=scale_method)
        logs.append(f"数值标准化/归一化：{scale_method}")

    logs.append(f"最终数据维度：{cleaned.shape[0]} 行 x {cleaned.shape[1]} 列")
    return cleaned, logs


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()
        rows.append(
            {
                "column": col,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_count": int(outlier_count),
            }
        )
    return pd.DataFrame(rows)


def apply_outlier_strategy(df: pd.DataFrame, outlier_df: pd.DataFrame, method: str = "iqr_clip") -> pd.DataFrame:
    if outlier_df.empty:
        return df

    result = df.copy()
    for _, row in outlier_df.iterrows():
        col = row["column"]
        lower = row["lower_bound"]
        upper = row["upper_bound"]

        if method == "iqr_clip":
            result[col] = result[col].clip(lower=lower, upper=upper)
        elif method == "remove":
            result = result[(result[col] >= lower) & (result[col] <= upper)]
    return result


def apply_scaling(df: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
    scaled = df.copy()
    for col in scaled.select_dtypes(include="number").columns:
        s = scaled[col]
        if method == "zscore":
            std = s.std(ddof=0)
            if std and std > 0:
                scaled[col] = (s - s.mean()) / std
        elif method == "minmax":
            min_v, max_v = s.min(), s.max()
            if max_v > min_v:
                scaled[col] = (s - min_v) / (max_v - min_v)
    return scaled


def _looks_like_date_column(series: pd.Series) -> bool:
    sample = series.dropna().astype(str).head(30)
    if sample.empty:
        return False
    parsed = pd.to_datetime(sample, errors="coerce")
    return parsed.notna().mean() >= 0.6
