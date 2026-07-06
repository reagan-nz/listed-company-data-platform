# 宁德时代（300750）2024 年报 — 年度公司属性案例

> **性质说明**：本文档为 **annual company snapshot**（单一年度、单份年报抽取结果的可读汇总），**不是**完整 company master table，也不代表已接入 PostgreSQL / MinIO 生产库。
>
> **生成方式**：离线整理既有 Era B 全市场 2024 年报抽取产物；未联网、未重新下载 PDF、未接数据库。

---

## 1. 案例标识

| 字段 | 值 |
|------|-----|
| company_code | `300750` |
| company_name | `宁德时代`（全称：宁德时代新能源科技股份有限公司，见 PDF 正文） |
| report_year | `2024` |
| exchange | `SZSE`（创业板） |
| schema_profile | `industrial`（工业 11 字段模板） |

---

## 2. 报告元数据

| 字段 | 值 | 来源 |
|------|-----|------|
| report_title | `2024年年度报告` | `chinext/300750/company_profile.json` → `source.report_title` |
| publish_time | `2025-03-15`（CNINFO `finalpage` 路径日期；审计报告签署日为 2025-03-13） | `source.source_url`；`.cache/*.pages.json` 审计报告签署日期 |
| pdf_url | http://static.cninfo.com.cn/finalpage/2025-03-15/1222806982.PDF | `company_profile.json` → `source.source_url` |
| pdf_sha256 | `b4f1713d7b821eb076c102711d177fe942ccc2bc8dd171ae5d7a95799a65b0ad` | `company_profile.json` |
| page_count | `229` | `company_profile.json` / `eval_results.json` |

---

## 3. 核心财务与经营属性（用户关注字段）

| 字段 | 值 | 单位 / 备注 | 来源 |
|------|-----|-------------|------|
| **main_business** | 主要从事动力电池、储能电池的研发、生产、销售；全球新能源创新科技公司，覆盖动力电池与储能电池产业链 | 摘要自「主营业务/业务板块」抽取片段 | `company_profile.json` → `fields[main_business_segments].value` |
| **revenue** | `362,012,554` | **千元**（≈ 3,620.13 亿元） | `.cache/b4f1713….pages.json` 主要会计数据表「营业收入（千元）」；**非** 11 字段 schema 独立字段 |
| **net_profit** | `50,744,682` | **千元**（归属于上市公司股东的净利润） | `.cache/b4f1713….pages.json` 主要会计数据表；**非** 11 字段 schema 独立字段 |
| **r_and_d_expense** | `18,606,756` | **千元** | `company_profile.json` → `fields[rnd_investment].value.labeled[研发投入金额]`；与 `rnd_refresh_changes.csv` 一致 |
| **r_and_d_ratio** | `5.14%` | 研发投入占营业收入比例（2024 年） | `company_profile.json` → `fields[rnd_investment].value.context` |
| **employee_count** | `131,988` | **人**（报告期末在职员工的数量合计） | `.cache/b4f1713….pages.json`；母公司在职 32,510 + 主要子公司 99,478；**非** 11 字段 schema 独立字段 |
| **audit_opinion** | `标准的无保留意见` | 2024 年度财务报告审计 | `.cache/b4f1713….pages.json`（审计报告元数据表）；年报重要提示亦载「非标准审计意见提示：不适用」 |

---

## 4. 抽取与质量状态

| 字段 | 值 | 说明 |
|------|-----|------|
| extraction_status | `ok` | `eval_results.json`：`status=ok`，`found=11/11`，`partial=0`，`not_found=0` |
| audit_flag | `11/11 found, 11 plausible` | 工业 schema 11 字段全部 `found` 且 `plausible=true`；R&D 刷新后仍为 `usable`（`rnd_refresh_changes.csv`） |
| field_coverage | `11 found / 0 partial / 0 not_found` | `company_profile.json` → `field_counts` |

---

## 5. 年报还能提供哪些年度属性（11 字段全景）

以下为 `company_profile.json` 已结构化抽取的字段（均有页码与 evidence_sentence）：

| 字段 key | 中文标签 | status | 要点摘要 |
|----------|----------|--------|----------|
| main_business_segments | 主营业务/业务板块 | found | 动力电池、储能电池研发产销；六大研发中心、十三大基地 |
| major_products | 主要产品及服务 | found | 电芯/模组/电池包；磷酸铁锂、三元、钠离子、M3P、凝聚态等 |
| revenue_by_segment | 营业收入-分产品/行业 | found | 动力电池 253,041,337 千元；储能 57,290,460；材料及回收 28,699,935 等（千元） |
| revenue_by_region | 营业收入-分地区 | found | 境内 251,677,045；境外 110,335,509（千元） |
| top_customers | 前五名客户 | found | 前五合计占年度销售 37.03% |
| top_suppliers | 前五名供应商 | found | 前五合计占年度采购 16.33% |
| rnd_investment | 研发投入 | found | 金额 18,606,756 千元；占营收 5.14% |
| major_subsidiaries | 主要控股参股公司 | found | 报告期无应当披露的重要控股参股公司信息 |
| risk_factors | 风险因素 | found | 宏观经济、市场竞争加剧等 |
| industry_discussion | 所处行业情况 | found | 新能源产业化→产业新能源化；电动化与储能需求 |
| mda | 管理层讨论与分析 | found | 行业分类 C3841 锂离子电池制造；行业趋势与战略 |

更完整的 evidence 与表格预览见：`outputs/generalization/full_market_2024/chinext/300750/company_brief.md`

---

## 6. 未纳入 11 字段模板、但年报中存在的属性

| 属性 | 是否在抽取产物中 | 说明 |
|------|------------------|------|
| 营业收入合计 | 有（pages cache） | 见 §3 `revenue` |
| 归母净利润 | 有（pages cache） | 见 §3 `net_profit` |
| 员工人数 | 有（pages cache） | 见 §3 `employee_count` |
| 审计意见 | 有（pages cache） | 见 §3 `audit_opinion` |
| 现金流量表科目 | unknown（未作独立字段） | 年报有「经营活动现金流」等，未进入 industrial 11 字段 |
| 资产负债率 / EPS 等 | unknown（未作独立字段） | 存在于主要会计数据表，未结构化入库 |

---

## 7. 数据来源文件清单

| 路径 | 用途 |
|------|------|
| `outputs/generalization/full_market_2024/chinext/300750/company_profile.json` | **主数据源**：11 字段结构化值、PDF URL、字段 status |
| `outputs/generalization/full_market_2024/chinext/300750/company_brief.md` | 人类可读 brief，与 profile 同源 |
| `outputs/generalization/full_market_2024/chinext/300750/meta.json` | 检索元数据（`picked_title`、`orgid`） |
| `outputs/generalization/full_market_2024/chinext/300750/.cache/b4f1713d….pages.json` | PDF 分页文本缓存；补充 revenue / net_profit / employee / audit_opinion |
| `outputs/generalization/full_market_2024/eval_results.json`（`stock_code=300750`） | 全市场评估：`status`、字段 found 计数、PDF 体量 |
| `outputs/generalization/full_market_2024/eval_summary.md` | 汇总表：宁德时代 229 页、11/11 |
| `outputs/generalization/full_market_2024/rnd_refresh_changes.csv` | R&D 字段刷新记录：`usable`、无回归 |
| `outputs/generalization/generalization_report.md` | CATL 作为调参参考样本的说明 |

---

## 8. 边界与局限

- 本文档 **不** 修改任何已有 CSV / JSON 抽取产物，仅为 validation 层案例说明。
- `revenue`、`net_profit`、`employee_count`、`audit_opinion` 来自 **pages 文本缓存**，尚未作为 Era B industrial schema 的独立持久字段；若字段在 profile 中不存在，已标注来源而非编造。
- `recommended_status`：**未写 verified**；仅代表 2024 单份年报、单管道抽取快照。
- 数值单位以年报原文为准（表中金额多为 **千元**）；引用时请保留单位，避免与「元」混淆。

---

## 9. 一句话结论

宁德时代 2024 年报在现有抽取管道中 **11/11 工业字段全部 found**，可作为「年报能提供哪些年度公司属性」的**高质量正面案例**；主营业务、分产品/分地区收入、研发、客户供应商集中度、风险与行业讨论均已结构化；合并报表级 revenue / 归母净利润 / 员工总数 / 审计意见可从同次抽取的 pages 缓存中补读，但尚未纳入 11 字段标准 schema。
