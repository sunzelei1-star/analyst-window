from __future__ import annotations

import streamlit as st


def apply_dashboard_style() -> None:
    """Apply a cleaner business dashboard style."""
    st.markdown(
        """
        <style>
        :root {
            --app-bg: var(--background-color);
            --surface-bg: var(--secondary-background-color);
            --text-main: var(--text-color);
            --text-muted: color-mix(in srgb, var(--text-color) 72%, transparent);
            --border: color-mix(in srgb, var(--text-color) 22%, transparent);
            --shadow: color-mix(in srgb, var(--text-color) 14%, transparent);
            --btn-bg: color-mix(in srgb, var(--primary-color) 18%, var(--surface-bg));
            --btn-border: color-mix(in srgb, var(--primary-color) 45%, transparent);
            --btn-text: color-mix(in srgb, var(--primary-color) 74%, var(--text-main));
        }

        @supports not (color: color-mix(in srgb, white, black)) {
            :root {
                --text-muted: #64748b;
                --border: rgba(100, 116, 139, 0.35);
                --shadow: rgba(15, 23, 42, 0.14);
                --btn-bg: rgba(37, 99, 235, 0.12);
                --btn-border: rgba(37, 99, 235, 0.35);
                --btn-text: var(--text-main);
            }
        }

        .stApp {
            background: linear-gradient(
                180deg,
                color-mix(in srgb, var(--app-bg) 75%, white) 0%,
                var(--app-bg) 100%
            );
            color: var(--text-main);
        }
        @media (prefers-color-scheme: dark) {
            .stApp {
                background: linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--app-bg) 85%, black) 0%,
                    var(--app-bg) 100%
                );
            }
        }
        div[data-testid="stMetric"] {
            background: var(--surface-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 18px var(--shadow);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: var(--text-main) !important;
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
            color: rgba(241, 245, 249, 0.95);
            font-size: 0.95rem;
        }
        .section-card {
            background: var(--surface-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1rem 0.6rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 6px 16px var(--shadow);
        }
        .section-title {
            color: var(--text-main);
            font-size: 1.02rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }
        .section-card p,
        .section-card li,
        .section-card span,
        .section-card label,
        .section-card .stMarkdown,
        .section-card .stCaption {
            color: var(--text-main);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
            color: var(--text-main);
        }
        .stButton button, .stDownloadButton button {
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid var(--btn-border);
            background: var(--btn-bg);
            color: var(--btn-text);
        }

        section[data-testid="stSidebar"] * {
            color: var(--text-main);
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
