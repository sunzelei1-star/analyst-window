from __future__ import annotations

import base64
import json
from typing import Any

import pandas as pd


def export_analysis_bundle(mode: str, **kwargs: Any) -> str:
    payload: dict[str, Any] = {"mode": mode}
    for key, value in kwargs.items():
        if isinstance(value, pd.DataFrame):
            payload[key] = value.to_dict(orient="records")
        else:
            payload[key] = value
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def dataframe_to_download_link(df: pd.DataFrame, filename: str) -> str:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    b64 = base64.b64encode(csv_bytes).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">下载清洗后表格（CSV）</a>'
