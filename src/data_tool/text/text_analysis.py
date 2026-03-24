from __future__ import annotations

from collections import Counter

import jieba
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_LABEL_RULES = {
    "投诉": ["差", "慢", "问题", "故障", "投诉", "不满", "退款"],
    "表扬": ["好", "满意", "感谢", "优秀", "推荐", "喜欢"],
    "咨询": ["请问", "如何", "是否", "可以", "咨询", "了解"],
}


def classify_texts(texts: list[str]) -> pd.DataFrame:
    records = []
    for text in texts:
        label = "其他"
        for candidate, keywords in DEFAULT_LABEL_RULES.items():
            if any(k in text for k in keywords):
                label = candidate
                break
        keywords = extract_keywords(text, top_k=5)
        records.append({"text": text, "category": label, "keywords": ", ".join(keywords)})
    return pd.DataFrame(records)


def extract_keywords(text: str, top_k: int = 10) -> list[str]:
    words = [w.strip() for w in jieba.cut(text) if len(w.strip()) > 1]
    filtered = [w for w in words if w not in {"我们", "你们", "这个", "那个", "然后", "但是"}]
    return [item for item, _ in Counter(filtered).most_common(top_k)]


def cluster_texts(classified_df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    df = classified_df.copy()
    if df.empty:
        df["cluster"] = []
        return df

    vectorizer = TfidfVectorizer(max_features=800, token_pattern=r"(?u)\b\w+\b")
    features = vectorizer.fit_transform(df["text"])

    n_clusters = max(1, min(n_clusters, len(df)))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    df["cluster"] = kmeans.fit_predict(features)

    terms = vectorizer.get_feature_names_out()
    centers = kmeans.cluster_centers_
    cluster_terms = []
    for idx in df["cluster"]:
        top_ids = centers[idx].argsort()[-5:][::-1]
        cluster_terms.append(", ".join(terms[top_ids]))
    df["cluster_keywords"] = cluster_terms
    return df


def summarize_clusters(clustered_df: pd.DataFrame) -> pd.DataFrame:
    if clustered_df.empty:
        return pd.DataFrame(columns=["cluster", "count", "top_categories", "sample_summary"])

    summary_rows = []
    for cluster_id, group in clustered_df.groupby("cluster"):
        top_categories = group["category"].value_counts().head(3).to_dict()
        sample_text = "；".join(group["text"].head(3).tolist())
        summary_rows.append(
            {
                "cluster": int(cluster_id),
                "count": int(len(group)),
                "top_categories": str(top_categories),
                "sample_summary": sample_text[:180],
            }
        )
    return pd.DataFrame(summary_rows).sort_values("count", ascending=False)
