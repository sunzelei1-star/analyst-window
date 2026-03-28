from __future__ import annotations

import streamlit as st

from src.data_tool.analysis.advanced_analysis import (
    add_period_comparison,
    correlation_matrix,
    describe_dataframe,
    group_summary,
    top_bottom_analysis,
    trend_analysis,
)
from src.data_tool.analysis.finance_analysis import (
    add_financial_statement_metrics,
    add_return_metrics,
    summarize_finance_metrics,
)
from src.data_tool.analysis.formulas import conversion_rate, growth_rate, margin, weighted_average
from src.data_tool.analysis.table_analysis import (
    build_chart_presentation,
    build_summary_statistics,
    build_visualization,
    is_time_like_series,
    recommended_chart_type,
)
from src.data_tool.processing.table_cleaner import clean_table_data, detect_outliers
from src.data_tool.reporting.exporter import dataframe_to_download_link, export_analysis_bundle
from src.data_tool.reporting.insights import (
    generate_advanced_key_findings,
    generate_finance_insights,
    generate_table_insights,
    generate_text_insights,
    recommend_analysis_paths,
)
from src.data_tool.text.text_analysis import classify_texts, cluster_texts, summarize_clusters
from src.data_tool.ui.auto_conclusions import summarize_stats, summarize_top_bottom, summarize_trend
from src.data_tool.ui.dashboard_style import (
    apply_dashboard_style,
    render_bullet_cards,
    render_empty_state,
    render_hero,
    section_end,
    section_start,
)
from src.data_tool.ui.i18n import t
from src.data_tool.ui.sample_data import get_business_sample_data, get_finance_sample_data
from src.data_tool.utils.io import load_uploaded_file

st.set_page_config(page_title="数据分析工具", page_icon="📊", layout="wide")
apply_dashboard_style()

with st.sidebar:
    language = st.selectbox(t("zh", "lang_label"), options=["中文", "English"], index=0)
    lang = "zh" if language == "中文" else "en"
    st.header(t(lang, "data_entry"))
    data_entry = st.radio(t(lang, "source_choice"), options=[t(lang, "upload_file"), t(lang, "sample_data")], horizontal=False)

loaded = None
if data_entry == t(lang, "upload_file"):
    uploaded = st.sidebar.file_uploader(t(lang, "upload_hint"), type=["csv", "xlsx", "xls", "txt"], accept_multiple_files=False)
    if uploaded:
        try:
            loaded = load_uploaded_file(uploaded)
        except Exception as exc:
            st.error(t(lang, "load_error", error=exc))
            st.stop()
else:
    sample_mode = st.sidebar.selectbox(t(lang, "sample_choice"), options=[t(lang, "business_sample"), t(lang, "finance_sample")])
    if sample_mode == t(lang, "business_sample"):
        loaded = {"mode": "table", "data": get_business_sample_data()}
    else:
        loaded = {"mode": "finance", "data": get_finance_sample_data()}

if not loaded:
    render_empty_state(
        title=t(lang, "empty_title"),
        subtitle=t(lang, "empty_subtitle"),
        cards=[
            ("🧭", t(lang, "empty_intro"), t(lang, "empty_intro_desc")),
            ("📁", t(lang, "empty_types"), t(lang, "empty_types_desc")),
            ("🧪", t(lang, "empty_scenes"), t(lang, "empty_scenes_desc")),
            ("🚀", t(lang, "empty_sample"), t(lang, "empty_sample_desc")),
        ],
        steps_label=t(lang, "empty_steps"),
        steps_text=t(lang, "empty_step_list"),
    )
    st.info(t(lang, "wait_load"))
    st.stop()

mode = loaded["mode"]
mode_text = t(lang, "mode_table") if mode == "table" else t(lang, "mode_finance") if mode == "finance" else t(lang, "mode_text")
render_hero(t(lang, "hero_title"), t(lang, "hero_subtitle", mode=mode_text))

if mode in {"table", "finance"}:
    raw_df = loaded["data"]
    section_start(t(lang, "section_overview"))
    st.dataframe(raw_df.head(30), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t(lang, "records"), f"{len(raw_df):,}")
    c2.metric(t(lang, "columns"), f"{raw_df.shape[1]}")
    numeric_cnt = len(raw_df.select_dtypes(include="number").columns)
    c3.metric(t(lang, "numeric_columns"), f"{numeric_cnt}")
    c4.metric(t(lang, "missing_total"), f"{int(raw_df.isna().sum().sum())}")

    with st.expander(t(lang, "cleaning_settings"), expanded=True):
        drop_duplicates = st.checkbox("去重 / Drop duplicates", value=True)
        strip_strings = st.checkbox("清除文本首尾空格 / Trim strings", value=True)
        fill_numeric_na = st.checkbox("数值缺失填充（中位数）/ Fill numeric NA", value=True)
        fill_text_na = st.checkbox("文本缺失填充为空字符串 / Fill text NA", value=True)
        normalize_columns = st.checkbox("标准化列名 / Normalize columns", value=True)
        detect_dates = st.checkbox("自动识别日期列 / Detect dates", value=True)
        infer_numeric = st.checkbox("自动识别数值列 / Infer numeric", value=True)
        handle_outliers = st.checkbox("异常值处理 / Handle outliers", value=True)
        outlier_method = st.selectbox("异常值策略 / Outlier strategy", options=["iqr_clip", "remove"])
        scale_method = st.selectbox("标准化/归一化 / Scaling", options=["none", "zscore", "minmax"])

    cleaned_df, clean_log = clean_table_data(
        raw_df,
        drop_duplicates=drop_duplicates,
        strip_strings=strip_strings,
        fill_numeric_na=fill_numeric_na,
        fill_text_na=fill_text_na,
        normalize_columns=normalize_columns,
        detect_dates=detect_dates,
        infer_numeric=infer_numeric,
        handle_outliers=handle_outliers,
        outlier_method=outlier_method,
        scale_method=scale_method,
    )

    st.markdown(f"**{t(lang, 'cleaned_data')}**")
    st.dataframe(cleaned_df.head(30), use_container_width=True)
    st.markdown(f"**{t(lang, 'clean_log')}**")
    st.write(clean_log)
    outlier_df = detect_outliers(cleaned_df)
    st.markdown(f"**{t(lang, 'outlier_check')}**")
    st.dataframe(outlier_df, use_container_width=True)

    st.markdown(f"**🧠 {t(lang, 'recommend_path')}**")
    render_bullet_cards(recommend_analysis_paths(cleaned_df, lang=lang))
    section_end()

    section_start(t(lang, "section_analysis"))
    tab_labels = ["基础统计", "描述统计", "分组汇总", "相关性", "趋势与增长", "Top/Bottom", "图表"] if lang == "zh" else ["Summary", "Describe", "Group", "Correlation", "Trend", "Top/Bottom", "Charts"]
    tabs = st.tabs(tab_labels)

    stats_df = build_summary_statistics(cleaned_df)
    trend_df = None
    top_df = None
    bottom_df = None
    top_target = ""
    trend_target = ""

    with tabs[0]:
        st.dataframe(stats_df, use_container_width=True)

    with tabs[1]:
        st.dataframe(describe_dataframe(cleaned_df), use_container_width=True)

    with tabs[2]:
        cols = cleaned_df.columns.tolist()
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if cols and num_cols:
            g_col = st.selectbox("分组字段 / Group column", options=cols)
            v_col = st.selectbox("汇总值字段 / Value column", options=num_cols)
            agg = st.selectbox("聚合方式 / Agg", options=["sum", "mean", "median", "count", "max", "min"])
            st.dataframe(group_summary(cleaned_df, g_col, v_col, agg), use_container_width=True)

    with tabs[3]:
        corr_df = correlation_matrix(cleaned_df)
        if corr_df.empty:
            st.warning("没有可用于相关性分析的数值列。" if lang == "zh" else "No numeric columns for correlation analysis.")
        else:
            st.dataframe(corr_df, use_container_width=True)
            heatmap = build_visualization(cleaned_df, "热力图", x_col=cleaned_df.columns[0])
            if heatmap is not None:
                st.pyplot(heatmap, clear_figure=True)

    with tabs[4]:
        date_candidates = [c for c in cleaned_df.columns if "datetime" in str(cleaned_df[c].dtype) or "date" in c.lower()]
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if date_candidates and num_cols:
            d_col = st.selectbox("日期字段 / Date", options=date_candidates)
            v_col = st.selectbox("趋势值字段 / Metric", options=num_cols)
            trend_target = v_col
            freq = st.selectbox("周期 / Frequency", options=["D", "W", "M", "Q", "Y"], index=2)
            trend_df = trend_analysis(cleaned_df, d_col, v_col, freq=freq)
            trend_df = add_period_comparison(trend_df)
            st.dataframe(trend_df, use_container_width=True)
        else:
            st.info("请确保存在日期列与数值列。" if lang == "zh" else "Please ensure date and numeric columns exist.")

    with tabs[5]:
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            top_target = st.selectbox("排序字段 / Sort by", options=num_cols)
            top_df, bottom_df = top_bottom_analysis(cleaned_df, top_target, n=10)
            c1, c2 = st.columns(2)
            c1.markdown("**Top 10**")
            c1.dataframe(top_df, use_container_width=True)
            c2.markdown("**Bottom 10**")
            c2.dataframe(bottom_df, use_container_width=True)

    with tabs[6]:
        numeric_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        all_cols = cleaned_df.columns.tolist()
        chart_options = ["柱状图", "折线图", "散点图", "箱线图", "直方图", "热力图"]
        chart_type = st.radio("图表类型 / Chart", options=chart_options, horizontal=True)
        x_col = st.selectbox("X 轴 / X", options=all_cols)
        y_col = st.selectbox("Y 轴（若适用）/ Y", options=[""] + numeric_cols)
        is_time_axis = is_time_like_series(cleaned_df[x_col])
        smart_chart_type = recommended_chart_type(chart_type, is_time_axis, y_col or None)
        dark_mode = st.get_option("theme.base") == "dark"
        presentation = build_chart_presentation(
            lang=lang,
            x_col=x_col,
            y_col=y_col or None,
            chart_type=smart_chart_type,
            is_time_axis=is_time_axis,
        )
        st.markdown(f"#### {presentation.title}")
        st.caption(presentation.subtitle)
        if smart_chart_type != chart_type and is_time_axis:
            st.info(t(lang, "chart_auto_switched"))

        fig = build_visualization(
            cleaned_df,
            smart_chart_type,
            x_col,
            y_col or None,
            presentation=presentation,
            dark_mode=dark_mode,
        )
        if fig is not None:
            st.pyplot(fig, clear_figure=True)
    section_end()

    section_start(t(lang, "section_auto"))
    auto_insights = [
        summarize_stats(stats_df),
        summarize_trend(trend_df, trend_target),
        summarize_top_bottom(top_df, bottom_df, top_target) if top_target else ("Top/Bottom：未选择排序指标。" if lang == "zh" else "Top/Bottom: no ranking metric selected."),
    ]
    for i, insight in enumerate(auto_insights, start=1):
        st.write(f"{i}. {insight}")
    section_end()

    section_start(t(lang, "section_key_findings"))
    advanced_findings = generate_advanced_key_findings(
        cleaned_df,
        trend_df=trend_df,
        trend_target=trend_target,
        top_df=top_df,
        bottom_df=bottom_df,
        top_target=top_target,
        lang=lang,
    )
    for i, insight in enumerate(advanced_findings, start=1):
        st.write(f"{i}. {insight}")
    section_end()

    section_start(t(lang, "section_formula"))
    formula_tabs = st.tabs(["增长率" if lang == "zh" else "Growth", "利润率" if lang == "zh" else "Margin", "转化率" if lang == "zh" else "Conversion", "加权平均" if lang == "zh" else "Weighted Avg"])
    num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()

    if num_cols:
        with formula_tabs[0]:
            cur = st.selectbox("当前值列 / Current", options=num_cols, key="g_cur")
            prev = st.selectbox("对比值列 / Previous", options=num_cols, key="g_prev")
            tmp = cleaned_df[[cur, prev]].copy()
            tmp["growth_rate"] = growth_rate(tmp[cur], tmp[prev])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tabs[1]:
            numerator = st.selectbox("利润列 / Profit", options=num_cols, key="m_num")
            denominator = st.selectbox("收入列 / Revenue", options=num_cols, key="m_den")
            tmp = cleaned_df[[numerator, denominator]].copy()
            tmp["margin"] = margin(tmp[numerator], tmp[denominator])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tabs[2]:
            success_col = st.selectbox("成功数列 / Success", options=num_cols, key="c_s")
            total_col = st.selectbox("总数列 / Total", options=num_cols, key="c_t")
            tmp = cleaned_df[[success_col, total_col]].copy()
            tmp["conversion_rate"] = conversion_rate(tmp[success_col], tmp[total_col])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tabs[3]:
            value_col = st.selectbox("值列 / Value", options=num_cols, key="w_v")
            weight_col = st.selectbox("权重列 / Weight", options=num_cols, key="w_w")
            wavg = weighted_average(cleaned_df[value_col], cleaned_df[weight_col])
            st.metric("加权平均 / Weighted Average", f"{wavg:.4f}" if wavg == wavg else "NaN")

    if mode == "finance":
        st.markdown(f"**{t(lang, 'finance_panel')}**")
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            price_col = st.selectbox("价格/净值列 / Price", options=num_cols)
            fin_df = add_return_metrics(cleaned_df, price_col)
            st.dataframe(fin_df.head(100), use_container_width=True)
            st.dataframe(summarize_finance_metrics(fin_df), use_container_width=True)

            if len(num_cols) >= 2:
                revenue_col = st.selectbox("收入列 / Revenue", options=num_cols, index=0)
                cost_col = st.selectbox("成本列 / Cost", options=num_cols, index=min(1, len(num_cols) - 1))
                net_col = st.selectbox("净利润列（可选）/ Net Profit", options=[""] + num_cols)
                fin_stmt_df = add_financial_statement_metrics(
                    cleaned_df,
                    revenue_col=revenue_col,
                    cost_col=cost_col,
                    net_profit_col=net_col or None,
                )
                st.dataframe(fin_stmt_df.head(100), use_container_width=True)

            insights = generate_finance_insights(fin_df)
        else:
            insights = ["当前金融数据缺少数值列，无法计算金融指标。"] if lang == "zh" else ["No numeric columns available for finance metrics."]
    else:
        insights = generate_table_insights(cleaned_df, stats_df)

    st.markdown(f"**{t(lang, 'key_findings_rule')}**")
    for i, insight in enumerate(insights, start=1):
        st.write(f"{i}. {insight}")

    bundle = export_analysis_bundle(
        mode=mode,
        cleaned_df=cleaned_df,
        stats_df=stats_df,
        outlier_df=outlier_df,
        insights=insights + auto_insights + advanced_findings,
    )
    st.download_button(t(lang, "download_json"), data=bundle, file_name=f"{mode}_analysis_result.json", mime="application/json")
    st.markdown(dataframe_to_download_link(cleaned_df, f"{mode}_cleaned.csv"), unsafe_allow_html=True)
    section_end()
else:
    texts = loaded["data"]
    st.dataframe(texts.head(100), use_container_width=True)
    if "text" in texts.columns:
        cls_df = classify_texts(texts, "text")
        clu_df = cluster_texts(cls_df, "text")
        st.dataframe(summarize_clusters(clu_df), use_container_width=True)
        for row in generate_text_insights(clu_df):
            st.write(f"- {row}")
