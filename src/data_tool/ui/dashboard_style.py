from __future__ import annotations

import streamlit as st


def apply_dashboard_style() -> None:
    """Apply a cleaner business dashboard style."""
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #f4f7fb;
            --card-bg: #ffffff;
            --accent: #2563eb;
            --accent-soft: #dbeafe;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border: #dbe3ef;
        }
        .stApp {
            background: linear-gradient(180deg, #f8fbff 0%, var(--bg-main) 100%);
        }
        div[data-testid="stMetric"] {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 18px rgba(15, 23, 42, 0.06);
        }
        .hero-wrap {
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            background: linear-gradient(135deg, #1d4ed8, #2563eb 45%, #0ea5e9 100%);
            color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.28);
        }
        .hero-title {
            font-size: 1.5rem;
            font-weight: 800;
            margin: 0;
        }
        .hero-subtitle {
            margin-top: 0.4rem;
            color: #e2e8f0;
            font-size: 0.95rem;
        }
        .section-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1rem 0.6rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
        }
        .section-title {
            color: var(--text-main);
            font-size: 1.02rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid #bfdbfe;
            background: #eff6ff;
            color: #1e40af;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(mode_text: str) -> None:
    st.markdown(
        f"""
        <div class="hero-wrap">
            <p class="hero-title">商业数据智能分析 Dashboard</p>
            <p class="hero-subtitle">当前数据模式：{mode_text} ｜ 支持清洗、趋势、Top/Bottom 解释与一键导出</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_start(title: str) -> None:
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
