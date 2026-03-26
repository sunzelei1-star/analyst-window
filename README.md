# 商业分析与财务洞察平台（Streamlit）

这是一个本地可运行的 **Python + Streamlit + pandas** 数据分析网站，提供更接近商业 dashboard 的体验。

## 本次重点增强

1. **公式模块输入校验**
   - 相同字段不能同时作为分子/分母或当前值/对比值
   - 分母为 0 时给出友好提示并安全返回空值

2. **示例数据入口**
   - 商业分析示例数据（销售/成本/利润/访问/订单）
   - 财务分析示例数据（收盘价/收益/收入/成本/净利润/成交量）

3. **自动分析结论**
   - 自动输出统计结论
   - 自动输出趋势解释与 Top/Bottom 业务解释

4. **页面视觉升级**
   - 统一的现代简洁商业风格
   - 分区更清晰：上传区、清洗区、分析区、结论区、导出区
   - 信息卡片、按钮和表格区域样式优化

---

## 项目结构（核心）

```bash
app.py
src/data_tool/
├── analysis/
│   ├── advanced_analysis.py
│   ├── finance_analysis.py
│   ├── formulas.py
│   └── table_analysis.py
├── processing/table_cleaner.py
├── reporting/
│   ├── auto_summary.py
│   ├── exporter.py
│   └── insights.py
├── text/text_analysis.py
└── utils/
    ├── io.py
    └── sample_data.py
```

---

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 测试建议

1. 在左侧切换“示例数据”：
   - 选择“商业分析示例”验证统计/趋势/TopBottom/公式
   - 选择“财务分析示例”验证收益率/回撤/财务指标

2. 重点验证公式输入校验：
   - 选择相同字段作为分子和分母，确认出现警告
   - 选择分母含 0 的字段，确认出现友好提示且不报错

3. 验证导出：
   - JSON 导出包含 insights 与 quick_conclusions
   - CSV 导出为清洗后数据
