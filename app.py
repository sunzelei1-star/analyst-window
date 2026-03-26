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
from src.data_tool.analysis.table_analysis import build_summary_statistics, build_visualization
from src.data_tool.processing.table_cleaner import clean_table_data, detect_outliers
from src.data_tool.reporting.exporter import dataframe_to_download_link, export_analysis_bundle
from src.data_tool.reporting.insights import generate_finance_insights, generate_table_insights, generate_text_insights
from src.data_tool.text.text_analysis import classify_texts, cluster_texts, summarize_clusters
from src.data_tool.ui.auto_conclusions import summarize_stats, summarize_top_bottom, summarize_trend
from src.data_tool.ui.dashboard_style import apply_dashboard_style, render_hero, section_end, section_start
from src.data_tool.ui.sample_data import get_business_sample_data, get_finance_sample_data
from src.data_tool.utils.io import load_uploaded_file

st.set_page_config(page_title="数据分析工具", page_icon="📊", layout="wide")
apply_dashboard_style()

with st.sidebar:
    st.header("数据入口")
    data_entry = st.radio("选择数据来源", options=["上传文件", "示例数据"], horizontal=False)

loaded = None
if data_entry == "上传文件":
    uploaded = st.sidebar.file_uploader("上传 CSV / Excel / TXT", type=["csv", "xlsx", "xls", "txt"], accept_multiple_files=False)
    if uploaded:
        try:
            loaded = load_uploaded_file(uploaded)
        except Exception as exc:
            st.error(f"文件读取失败：{exc}")
            st.stop()
else:
    sample_mode = st.sidebar.selectbox("选择示例", options=["商业分析示例", "财务分析示例"])
    if sample_mode == "商业分析示例":
        loaded = {"mode": "table", "data": get_business_sample_data()}
    else:
        loaded = {"mode": "finance", "data": get_finance_sample_data()}

if not loaded:
    st.info("请在侧边栏选择并加载数据后开始分析。")
    st.stop()

mode = loaded["mode"]
render_hero("普通表格分析" if mode == "table" else "金融财务分析" if mode == "finance" else "文本分析")

if mode in {"table", "finance"}:
    raw_df = loaded["data"]
    section_start("一、数据总览与清洗")
    st.dataframe(raw_df.head(30), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总记录数", f"{len(raw_df):,}")
    c2.metric("字段数", f"{raw_df.shape[1]}")
    numeric_cnt = len(raw_df.select_dtypes(include="number").columns)
    c3.metric("数值字段", f"{numeric_cnt}")
    c4.metric("缺失值总数", f"{int(raw_df.isna().sum().sum())}")

    with st.expander("清洗设置", expanded=True):
        drop_duplicates = st.checkbox("去重", value=True)
        strip_strings = st.checkbox("清除文本首尾空格", value=True)
        fill_numeric_na = st.checkbox("数值缺失填充（中位数）", value=True)
        fill_text_na = st.checkbox("文本缺失填充为空字符串", value=True)
        normalize_columns = st.checkbox("标准化列名", value=True)
        detect_dates = st.checkbox("自动识别日期列", value=True)
        infer_numeric = st.checkbox("自动识别数值列", value=True)
        handle_outliers = st.checkbox("异常值处理", value=True)
        outlier_method = st.selectbox("异常值策略", options=["iqr_clip", "remove"])
        scale_method = st.selectbox("标准化/归一化", options=["none", "zscore", "minmax"])

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

    st.markdown("**清洗后数据**")
    st.dataframe(cleaned_df.head(30), use_container_width=True)
    st.markdown("**清洗日志**")
    st.write(clean_log)
    outlier_df = detect_outliers(cleaned_df)
    st.markdown("**异常值检测（IQR）**")
    st.dataframe(outlier_df, use_container_width=True)
    section_end()

    section_start("二、统计分析与可视化")
    tabs = st.tabs(["基础统计", "描述统计", "分组汇总", "相关性", "趋势与增长", "Top/Bottom", "图表"])

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
            g_col = st.selectbox("分组字段", options=cols)
            v_col = st.selectbox("汇总值字段", options=num_cols)
            agg = st.selectbox("聚合方式", options=["sum", "mean", "median", "count", "max", "min"])
            st.dataframe(group_summary(cleaned_df, g_col, v_col, agg), use_container_width=True)

    with tabs[3]:
        corr_df = correlation_matrix(cleaned_df)
        if corr_df.empty:
            st.warning("没有可用于相关性分析的数值列。")
        else:
            st.dataframe(corr_df, use_container_width=True)
            heatmap = build_visualization(cleaned_df, "热力图", x_col=cleaned_df.columns[0])
            if heatmap is not None:
                st.pyplot(heatmap, clear_figure=True)

    with tabs[4]:
        date_candidates = [c for c in cleaned_df.columns if "datetime" in str(cleaned_df[c].dtype) or "date" in c.lower()]
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if date_candidates and num_cols:
            d_col = st.selectbox("日期字段", options=date_candidates)
            v_col = st.selectbox("趋势值字段", options=num_cols)
            trend_target = v_col
            freq = st.selectbox("周期", options=["D", "W", "M", "Q", "Y"], index=2)
            trend_df = trend_analysis(cleaned_df, d_col, v_col, freq=freq)
            trend_df = add_period_comparison(trend_df)
            st.dataframe(trend_df, use_container_width=True)
        else:
            st.info("请确保存在日期列与数值列。")

    with tabs[5]:
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            top_target = st.selectbox("排序字段", options=num_cols)
            top_df, bottom_df = top_bottom_analysis(cleaned_df, top_target, n=10)
            c1, c2 = st.columns(2)
            c1.markdown("**Top 10**")
            c1.dataframe(top_df, use_container_width=True)
            c2.markdown("**Bottom 10**")
            c2.dataframe(bottom_df, use_container_width=True)

    with tabs[6]:
        numeric_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        all_cols = cleaned_df.columns.tolist()
        chart_type = st.radio("图表类型", options=["柱状图", "折线图", "散点图", "箱线图", "直方图", "热力图"], horizontal=True)
        x_col = st.selectbox("X 轴", options=all_cols)
        y_col = st.selectbox("Y 轴（若适用）", options=[""] + numeric_cols)
        fig = build_visualization(cleaned_df, chart_type, x_col, y_col or None)
        if fig is not None:
            st.pyplot(fig, clear_figure=True)
    section_end()

    section_start("三、自动分析结论")
    auto_insights = [
        summarize_stats(stats_df),
        summarize_trend(trend_df, trend_target),
        summarize_top_bottom(top_df, bottom_df, top_target) if top_target else "Top/Bottom：未选择排序指标。",
    ]
    for i, insight in enumerate(auto_insights, start=1):
        st.write(f"{i}. {insight}")
    section_end()

    section_start("四、公式模块与导出")
    formula_tab = st.tabs(["增长率", "利润率", "转化率", "加权平均"])
    num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()

    if num_cols:
        with formula_tab[0]:
            cur = st.selectbox("当前值列", options=num_cols, key="g_cur")
            prev = st.selectbox("对比值列", options=num_cols, key="g_prev")
            tmp = cleaned_df[[cur, prev]].copy()
            tmp["growth_rate"] = growth_rate(tmp[cur], tmp[prev])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tab[1]:
            numerator = st.selectbox("利润列", options=num_cols, key="m_num")
            denominator = st.selectbox("收入列", options=num_cols, key="m_den")
            tmp = cleaned_df[[numerator, denominator]].copy()
            tmp["margin"] = margin(tmp[numerator], tmp[denominator])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tab[2]:
            success_col = st.selectbox("成功数列", options=num_cols, key="c_s")
            total_col = st.selectbox("总数列", options=num_cols, key="c_t")
            tmp = cleaned_df[[success_col, total_col]].copy()
            tmp["conversion_rate"] = conversion_rate(tmp[success_col], tmp[total_col])
            st.dataframe(tmp.head(50), use_container_width=True)

        with formula_tab[3]:
            value_col = st.selectbox("值列", options=num_cols, key="w_v")
            weight_col = st.selectbox("权重列", options=num_cols, key="w_w")
            wavg = weighted_average(cleaned_df[value_col], cleaned_df[weight_col])
            st.metric("加权平均", f"{wavg:.4f}" if wavg == wavg else "NaN")

    if mode == "finance":
        st.markdown("**金融/财务分析**")
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            price_col = st.selectbox("价格/净值列", options=num_cols)
            fin_df = add_return_metrics(cleaned_df, price_col)
            st.dataframe(fin_df.head(100), use_container_width=True)
            st.dataframe(summarize_finance_metrics(fin_df), use_container_width=True)

            if len(num_cols) >= 2:
                revenue_col = st.selectbox("收入列", options=num_cols, index=0)
                cost_col = st.selectbox("成本列", options=num_cols, index=min(1, len(num_cols) - 1))
                net_col = st.selectbox("净利润列（可选）", options=[""] + num_cols)
                fin_stmt_df = add_financial_statement_metrics(
                    cleaned_df,
                    revenue_col=revenue_col,
                    cost_col=cost_col,
                    net_profit_col=net_col or None,
                )
                st.dataframe(fin_stmt_df.head(100), use_container_width=True)

            insights = generate_finance_insights(fin_df)
        else:
            insights = ["当前金融数据缺少数值列，无法计算金融指标。"]
    else:
        insights = generate_table_insights(cleaned_df, stats_df)

    st.markdown("**关键发现（规则摘要）**")
    for i, insight in enumerate(insights, start=1):
        st.write(f"{i}. {insight}")

    bundle = export_analysis_bundle(
        mode=mode,
        cleaned_df=cleaned_df,
        stats_df=stats_df,
        outlier_df=outlier_df,
        insights=insights + auto_insights,
    )
    st.download_button("下载分析结果（JSON）", data=bundle, file_name=f"{mode}_analysis_result.json", mime="application/json")
    st.markdown(dataframe_to_download_link(cleaned_df, f"{mode}_cleaned.csv"), unsafe_allow_html=True)
    section_end()

else:
    texts = loaded["data"]
    section_start("文本分析")
    st.write(texts[:20])
    classified_df = classify_texts(texts)
    st.dataframe(classified_df, use_container_width=True)

    cluster_count = st.slider("聚类数量", min_value=2, max_value=8, value=3)
    clustered_df = cluster_texts(classified_df, n_clusters=cluster_count)
    st.dataframe(clustered_df, use_container_width=True)

    summary_df = summarize_clusters(clustered_df)
    st.dataframe(summary_df, use_container_width=True)

    insights = generate_text_insights(clustered_df)
    for i, insight in enumerate(insights, start=1):
        st.write(f"{i}. {insight}")

    bundle = export_analysis_bundle(
        mode="text",
        classified_df=classified_df,
        clustered_df=clustered_df,
        summary_df=summary_df,
        insights=insights,
    )
    st.download_button("下载文本分析结果（JSON）", data=bundle, file_name="text_analysis_result.json", mime="application/json")
    section_end()
