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
from src.data_tool.reporting.auto_summary import summarize_statistics, summarize_top_bottom, summarize_trend
from src.data_tool.reporting.exporter import dataframe_to_download_link, export_analysis_bundle
from src.data_tool.reporting.insights import generate_finance_insights, generate_table_insights, generate_text_insights
from src.data_tool.text.text_analysis import cluster_texts, classify_texts, summarize_clusters
from src.data_tool.utils.io import load_uploaded_file
from src.data_tool.utils.sample_data import load_business_sample_data, load_finance_sample_data

st.set_page_config(page_title="商业分析与财务洞察平台", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f5f7fb; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2.6rem; max-width: 1200px; }
    .hero-card { background: linear-gradient(120deg, #102a43 0%, #1f4f8a 100%); color: #ffffff;
        border-radius: 14px; padding: 1.1rem 1.3rem; margin-bottom: 0.9rem; }
    .section-card { background: white; border: 1px solid #e8edf3; border-radius: 12px; padding: 0.9rem 1rem; margin-bottom: 0.8rem; }
    .soft-title { font-size: 1.1rem; font-weight: 700; color: #102a43; margin-bottom: 0.35rem; }
    .kpi { background:#edf4ff; border-radius:10px; padding:0.6rem 0.8rem; border:1px solid #d4e2ff; }
    div.stDownloadButton > button { background: #184e9c; color: white; border-radius: 8px; border: none; }
    div.stDownloadButton > button:hover { background: #123f80; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
      <h2 style="margin:0;">📈 商业分析与财务洞察平台</h2>
      <p style="margin:0.35rem 0 0 0;opacity:0.95;">面向业务与财务团队的本地分析工作台：数据清洗、统计洞察、趋势判断、公式计算与报告导出。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 数据入口")
    source_type = st.radio("选择数据来源", options=["上传文件", "示例数据"], index=0)

loaded = None
if source_type == "上传文件":
    uploaded = st.file_uploader("上传 CSV / Excel / TXT 文件", type=["csv", "xlsx", "xls", "txt"])
    if uploaded is None:
        st.info("请上传文件，或在左侧切换到示例数据进行演示。")
        st.stop()
    try:
        loaded = load_uploaded_file(uploaded)
    except Exception as exc:
        st.error(f"文件读取失败：{exc}")
        st.stop()
else:
    sample_kind = st.sidebar.selectbox("选择示例数据", options=["商业分析示例", "财务分析示例"])
    if sample_kind == "商业分析示例":
        loaded = {"mode": "table", "data": load_business_sample_data()}
    else:
        loaded = {"mode": "finance", "data": load_finance_sample_data()}

mode = loaded["mode"]
raw_data = loaded["data"]

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='kpi'><b>分析模式</b><br>{mode}</div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi'><b>样本行数</b><br>{len(raw_data) if hasattr(raw_data, '__len__') else 0}</div>", unsafe_allow_html=True)
c3.markdown(
    f"<div class='kpi'><b>字段数量</b><br>{raw_data.shape[1] if hasattr(raw_data, 'shape') else '-'}</div>",
    unsafe_allow_html=True,
)

if mode in {"table", "finance"}:
    raw_df = raw_data

    st.markdown("<div class='section-card'><div class='soft-title'>1) 上传区与原始数据</div>", unsafe_allow_html=True)
    st.dataframe(raw_df.head(30), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><div class='soft-title'>2) 数据清洗区</div>", unsafe_allow_html=True)
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
    st.dataframe(cleaned_df.head(30), use_container_width=True)
    st.markdown("**清洗日志**")
    st.write(clean_log)
    outlier_df = detect_outliers(cleaned_df)
    st.dataframe(outlier_df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><div class='soft-title'>3) 分析区</div>", unsafe_allow_html=True)
    tabs = st.tabs(["基础统计", "描述统计", "分组汇总", "相关性", "趋势与增长", "Top/Bottom", "图表", "公式模块"])
    stats_df = build_summary_statistics(cleaned_df)

    corr_df = correlation_matrix(cleaned_df)
    trend_df = None
    top_df = None
    bottom_df = None
    top_target = None

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
            freq = st.selectbox("周期", options=["D", "W", "M", "Q", "Y"], index=2)
            trend_df = add_period_comparison(trend_analysis(cleaned_df, d_col, v_col, freq=freq))
            st.dataframe(trend_df, use_container_width=True)
        else:
            st.info("请确保存在日期列与数值列。")

    with tabs[5]:
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            top_target = st.selectbox("排序字段", options=num_cols)
            top_df, bottom_df = top_bottom_analysis(cleaned_df, top_target, n=10)
            a, b = st.columns(2)
            a.markdown("**Top 10**")
            a.dataframe(top_df, use_container_width=True)
            b.markdown("**Bottom 10**")
            b.dataframe(bottom_df, use_container_width=True)

    with tabs[6]:
        numeric_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        all_cols = cleaned_df.columns.tolist()
        chart_type = st.radio("图表类型", options=["柱状图", "折线图", "散点图", "箱线图", "直方图", "热力图"], horizontal=True)
        x_col = st.selectbox("X 轴", options=all_cols)
        y_col = st.selectbox("Y 轴（若适用）", options=[""] + numeric_cols)
        fig = build_visualization(cleaned_df, chart_type, x_col, y_col or None)
        if fig is not None:
            st.pyplot(fig, clear_figure=True)

    with tabs[7]:
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        formula_tab = st.tabs(["增长率", "利润率", "转化率", "加权平均"])

        if not num_cols:
            st.info("没有可用于公式计算的数值列。")
        else:
            with formula_tab[0]:
                cur = st.selectbox("当前值列", options=num_cols, key="g_cur")
                prev = st.selectbox("对比值列", options=num_cols, key="g_prev")
                if cur == prev:
                    st.warning("当前值列与对比值列不能相同，请选择不同字段。")
                else:
                    tmp = cleaned_df[[cur, prev]].copy()
                    zero_count = (tmp[prev] == 0).sum()
                    if zero_count:
                        st.info(f"检测到 {zero_count} 行对比值为 0，增长率将显示为空值（已安全处理）。")
                    tmp["growth_rate"] = growth_rate(tmp[cur], tmp[prev])
                    st.dataframe(tmp.head(50), use_container_width=True)

            with formula_tab[1]:
                numerator = st.selectbox("利润列", options=num_cols, key="m_num")
                denominator = st.selectbox("收入列", options=num_cols, key="m_den")
                if numerator == denominator:
                    st.warning("分子与分母字段不能相同，请重新选择。")
                else:
                    tmp = cleaned_df[[numerator, denominator]].copy()
                    zero_count = (tmp[denominator] == 0).sum()
                    if zero_count:
                        st.info(f"检测到 {zero_count} 行分母为 0，利润率将显示为空值（已安全处理）。")
                    tmp["margin"] = margin(tmp[numerator], tmp[denominator])
                    st.dataframe(tmp.head(50), use_container_width=True)

            with formula_tab[2]:
                success_col = st.selectbox("成功数列", options=num_cols, key="c_s")
                total_col = st.selectbox("总数列", options=num_cols, key="c_t")
                if success_col == total_col:
                    st.warning("分子与分母字段不能相同，请重新选择。")
                else:
                    tmp = cleaned_df[[success_col, total_col]].copy()
                    zero_count = (tmp[total_col] == 0).sum()
                    if zero_count:
                        st.info(f"检测到 {zero_count} 行分母为 0，转化率将显示为空值（已安全处理）。")
                    tmp["conversion_rate"] = conversion_rate(tmp[success_col], tmp[total_col])
                    st.dataframe(tmp.head(50), use_container_width=True)

            with formula_tab[3]:
                value_col = st.selectbox("值列", options=num_cols, key="w_v")
                weight_col = st.selectbox("权重列", options=num_cols, key="w_w")
                if value_col == weight_col:
                    st.warning("值列与权重列不能相同，请重新选择。")
                else:
                    if (cleaned_df[weight_col] == 0).all():
                        st.info("权重全为 0，无法计算加权平均。")
                    else:
                        wavg = weighted_average(cleaned_df[value_col], cleaned_df[weight_col])
                        st.metric("加权平均", f"{wavg:.4f}" if wavg == wavg else "NaN")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><div class='soft-title'>4) 自动分析结论</div>", unsafe_allow_html=True)
    quick_conclusions = summarize_statistics(cleaned_df, stats_df, corr_df)
    for idx, text in enumerate(quick_conclusions, start=1):
        st.write(f"{idx}. {text}")

    st.markdown("**趋势解释**")
    for text in summarize_trend(trend_df):
        st.write(f"- {text}")

    st.markdown("**Top/Bottom 解释**")
    for text in summarize_top_bottom(top_df, bottom_df, top_target) if top_target else ["请在 Top/Bottom 页签选择排序字段后查看结论。"]:
        st.write(f"- {text}")

    if mode == "finance":
        st.markdown("**金融关键发现**")
        num_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            price_col = st.selectbox("价格/净值列", options=num_cols)
            fin_df = add_return_metrics(cleaned_df, price_col)
            st.dataframe(summarize_finance_metrics(fin_df), use_container_width=True)

            if len(num_cols) >= 2:
                revenue_col = st.selectbox("收入列", options=num_cols, index=0)
                cost_col = st.selectbox("成本列", options=num_cols, index=min(1, len(num_cols) - 1))
                net_col = st.selectbox("净利润列（可选）", options=[""] + num_cols)
                st.dataframe(
                    add_financial_statement_metrics(
                        cleaned_df,
                        revenue_col=revenue_col,
                        cost_col=cost_col,
                        net_profit_col=net_col or None,
                    ).head(60),
                    use_container_width=True,
                )

            insights = generate_finance_insights(fin_df)
        else:
            insights = ["当前金融数据缺少数值列，无法计算金融指标。"]
    else:
        insights = generate_table_insights(cleaned_df, stats_df)

    for i, insight in enumerate(insights, start=1):
        st.write(f"{i}. {insight}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'><div class='soft-title'>5) 导出区</div>", unsafe_allow_html=True)
    bundle = export_analysis_bundle(
        mode=mode,
        cleaned_df=cleaned_df,
        stats_df=stats_df,
        outlier_df=outlier_df,
        insights=insights,
        quick_conclusions=quick_conclusions,
    )
    st.download_button("下载分析结果（JSON）", data=bundle, file_name=f"{mode}_analysis_result.json", mime="application/json")
    st.markdown(dataframe_to_download_link(cleaned_df, f"{mode}_cleaned.csv"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    texts = raw_data
    st.markdown("<div class='section-card'><div class='soft-title'>文本分析区</div>", unsafe_allow_html=True)
    st.write(texts[:20])
    classified_df = classify_texts(texts)
    clustered_df = cluster_texts(classified_df, n_clusters=st.slider("聚类数量", min_value=2, max_value=8, value=3))
    summary_df = summarize_clusters(clustered_df)

    st.dataframe(classified_df.head(40), use_container_width=True)
    st.dataframe(clustered_df.head(40), use_container_width=True)
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
    st.markdown("</div>", unsafe_allow_html=True)
