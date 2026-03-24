# 数据分析工具（增强版）

基于 **Python + Streamlit + pandas** 的本地分析工具，保留原有表格/文本分析能力，并新增金融财务分析、公式模块、自动关键发现摘要与更完整的数据清洗能力。

## 支持的数据类型与模式
- **普通表格分析模式**：CSV / Excel（销售、名单、问卷等）
- **文本分析模式**：TXT，或以文本列为主的 CSV / Excel
- **金融/财务分析模式**：包含价格、收益、收入/成本/利润等字段的 CSV / Excel（自动识别）

## 新增核心能力
1. **更完整的数据清洗**
   - 缺失值处理（数值中位数、文本空字符串）
   - 异常值检测（IQR）+ 异常值处理（截断/剔除）
   - 重复值处理
   - 日期识别与转换
   - 数据类型自动识别（数值列、日期列）
   - 标准化/归一化（z-score / min-max）

2. **更丰富的分析**
   - 描述统计
   - 分组汇总
   - 相关性分析
   - 趋势分析（按天/周/月/季/年）
   - 增长率、环比（MoM）、同比（YoY）
   - 滚动平均、累计和
   - Top/Bottom 分析

3. **更多图表类型**
   - 折线图、柱状图、散点图、箱线图、直方图、热力图

4. **公式模块（可扩展）**
   - 增长率
   - 利润率
   - 转化率
   - 加权平均

5. **金融/财务分析**
   - 收益率、累计收益率
   - 波动率
   - 最大回撤
   - 移动平均（MA5/MA20）
   - 收入/成本/利润趋势
   - 毛利率、净利率

6. **自动关键发现与摘要输出**
7. **导出能力**
   - 导出清洗后数据（CSV）
   - 导出分析结果（JSON）

---

## 项目结构

```bash
analyst-window/
├── app.py
├── requirements.txt
├── src/data_tool/
│   ├── processing/table_cleaner.py       # 增强数据清洗、异常值处理、标准化
│   ├── analysis/table_analysis.py         # 基础统计 + 多图表
│   ├── analysis/advanced_analysis.py      # 分组/相关性/趋势/环比同比/TopBottom
│   ├── analysis/formulas.py               # 公式模块（增长率/利润率/转化率/加权平均）
│   ├── analysis/finance_analysis.py       # 金融财务指标
│   ├── text/text_analysis.py              # 文本分类/关键词/聚类/总结
│   ├── utils/io.py                        # 文件读取与模式识别(table/text/finance)
│   └── reporting/
│       ├── exporter.py                    # JSON/CSV导出
│       └── insights.py                    # 自动关键发现摘要
└── README.md
```

---

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 测试建议
- 基础语法检查：
  - `python -m compileall app.py src`
- 手动验证：
  1. 上传普通销售表，确认进入 `table` 模式；验证清洗、分组、趋势、Top/Bottom 和导出。
  2. 上传客户反馈 txt，确认进入 `text` 模式；验证分类、聚类、摘要与导出。
  3. 上传带 `date/close/revenue/cost/profit` 的财务表，确认进入 `finance` 模式；验证收益率、回撤、波动率、毛利率/净利率。
