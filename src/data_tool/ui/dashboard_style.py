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
        .stApp {
            background: linear-gradient(180deg, color-mix(in srgb, var(--app-bg) 75%, white) 0%, var(--app-bg) 100%);
            color: var(--text-main);
        }
        @media (prefers-color-scheme: dark) {
            .stApp {
                background: linear-gradient(180deg, color-mix(in srgb, var(--app-bg) 85%, black) 0%, var(--app-bg) 100%);
            }
        }
        .hero-wrap {
            border-radius: 20px;
            padding: 1.5rem 1.7rem;
            background: linear-gradient(130deg, #1e3a8a 0%, #1d4ed8 55%, #0ea5e9 100%);
            color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 14px 28px rgba(30, 64, 175, 0.28);
            border: 1px solid rgba(255,255,255,0.15);
        }
        .hero-title { font-size: 1.62rem; font-weight: 800; margin: 0; }
        .hero-subtitle { margin-top: 0.45rem; color: rgba(241,245,249,0.95); font-size: 0.98rem; }

        .section-card {
            background: var(--surface-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1rem 0.7rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 20px var(--shadow);
        }
        .section-title { color: var(--text-main); font-size: 1.04rem; font-weight: 700; margin-bottom: 0.75rem; }

        div[data-testid="stMetric"] {
            background: var(--surface-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.8rem 1rem;
            box-shadow: 0 4px 18px var(--shadow);
        }
        div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
        .stTabs [data-baseweb="tab"] { font-weight: 600; color: var(--text-main); }
        .stButton button, .stDownloadButton button {
            border-radius: 10px;
            font-weight: 700;
            border: 1px solid var(--btn-border);
            background: var(--btn-bg);
            color: var(--btn-text);
        }

        .feature-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:0.65rem; margin:0.4rem 0 0.8rem; }
        .feature-card {
            background: var(--surface-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.85rem 0.9rem;
            min-height: 108px;
        }
        .feature-card h4 { margin: 0 0 0.45rem; font-size: 0.96rem; }
        .feature-card p { margin: 0; font-size: 0.88rem; color: var(--text-muted); line-height: 1.45; }
        .pill-item {
            border-left: 4px solid color-mix(in srgb, var(--primary-color) 70%, transparent);
            background: color-mix(in srgb, var(--primary-color) 11%, var(--surface-bg));
            border-radius: 10px;
            padding: 0.55rem 0.75rem;
            margin-bottom: 0.45rem;
        }
        section[data-testid="stSidebar"] * { color: var(--text-main); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(mode_text: str) -> None:
    st.markdown(
        f"""
        <div class="hero-wrap">
            <p class="hero-title">📊 Business Intelligence Dashboard</p>
            <p class="hero-subtitle">当前数据模式：{mode_text} ｜ 支持清洗、趋势、Top/Bottom 解释与一键导出</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, subtitle: str, cards: list[tuple[str, str, str]], steps_label: str, steps_text: str) -> None:
    st.markdown(
        f"""
        <div class="hero-wrap">
            <p class="hero-title">{title}</p>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        <div class="feature-grid">
            {''.join([f'<div class="feature-card"><h4>{icon} {h}</h4><p>{d}</p></div>' for icon, h, d in cards])}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"**{steps_label}**")
    st.markdown(f"<div class='pill-item'>{steps_text}</div>", unsafe_allow_html=True)


def render_bullet_cards(items: list[str]) -> None:
    for item in items:
        st.markdown(f"<div class='pill-item'>• {item}</div>", unsafe_allow_html=True)


def section_start(title: str) -> None:
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
