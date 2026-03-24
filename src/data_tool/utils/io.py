from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd

FINANCE_KEYWORDS = {
    "price",
    "close",
    "open",
    "high",
    "low",
    "volume",
    "return",
    "nav",
    "revenue",
    "income",
    "cost",
    "profit",
    "expense",
    "资产",
    "负债",
    "收入",
    "成本",
    "利润",
    "收盘",
    "开盘",
}


def load_uploaded_file(uploaded_file) -> dict[str, Any]:
    """Load CSV / Excel / TXT and infer analysis mode (table/text/finance)."""
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        texts = [line.strip() for line in content.splitlines() if line.strip()]
        return {"mode": "text", "data": texts}

    if name.endswith(".csv"):
        raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        df = pd.read_csv(StringIO(raw))
        return _infer_mode_from_dataframe(df)

    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
        return _infer_mode_from_dataframe(df)

    raise ValueError("不支持的文件格式")


def _infer_mode_from_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"mode": "table", "data": df}

    text_like_cols = [c for c in df.columns if df[c].dtype == "object"]
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if _is_finance_dataframe(df):
        return {"mode": "finance", "data": df}

    # Heuristic: predominantly text with <= 2 columns is treated as text samples.
    if text_like_cols and len(numeric_cols) == 0 and len(df.columns) <= 2:
        text_series = df[text_like_cols[0]].dropna().astype(str).str.strip()
        texts = [v for v in text_series.tolist() if v]
        return {"mode": "text", "data": texts}

    return {"mode": "table", "data": df}


def _is_finance_dataframe(df: pd.DataFrame) -> bool:
    cols = [str(c).strip().lower() for c in df.columns]
    keyword_hit = any(any(keyword in col for keyword in FINANCE_KEYWORDS) for col in cols)
    numeric_ratio = len(df.select_dtypes(include="number").columns) / max(len(df.columns), 1)

    has_datetime_like = False
    for col in df.columns:
        if df[col].dtype == "object":
            sample = pd.to_datetime(df[col].dropna().astype(str).head(20), errors="coerce")
            if sample.notna().mean() >= 0.6:
                has_datetime_like = True
                break

    return keyword_hit and (numeric_ratio >= 0.4 or has_datetime_like)
