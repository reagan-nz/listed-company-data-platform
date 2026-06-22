# 年报抽取流程

## 流程概览

```
公司代码/名称
    │
    ▼
查询年报公告 (CNINFO API)
    │
    ▼
筛选全文年报 (pick_full_report)
    │
    ▼
下载 PDF
    │
    ▼
解析文本和表格 (PyMuPDF + pdfplumber)
    │
    ▼
计算文档区域 (MD&A / 附注)
    │
    ▼
逐字段定位章节 (锚点 + region + avoid)
    │
    ▼
按类型抽取 (snippet / table / numeric / concentration)
    │
    ▼
输出结构化结果 (company_profile.json)
```

## 详细步骤

### 1. 查询年报

```python
# lab/probe_cninfo.py
resolve_org_id(session, stock_code)          # 获取 orgId
query_announcements(session, code, org, ...)   # 查询 2024-2025 公告
pick_full_report(announcements)               # 筛选全文（排除摘要/H股）
```

关键筛选规则：
- 标题含「年度报告」且不含「摘要」「取消」「更正」「英文」
- A+H 双上市优先 A 股版本（不含「H股」「境外」「GDR」）

### 2. 下载 PDF

```python
url = STATIC_HOST + pick["adjunctUrl"]
session.get(url) → outputs/<code>/<code>.pdf
```

缓存机制：PDF ≥ 10KB + `meta.json` 存在 → 跳过后续网络请求。

### 3. 解析 PDF

```python
# lab/extract_annual_report.py
pages, meta = parse_pages(pdf_path, cache_dir)   # PyMuPDF 文本层
regions = compute_regions(pages)                  # MD&A / 附注页范围
```

- 文本层：`page.get_text()` → 按页字符串列表
- 表格层：`pdfplumber.extract_tables()` → 结构化行列（抽取 table 类字段时使用）
- 缓存：按 PDF SHA256 缓存 parsed pages（`.cache/*.pages.json`）

### 4. 字段定位

对每个字段（`field_schema.py` 中的 `FieldSpec`）：

```python
loc = locate_section(pages, spec.anchors, preferred_pages, spec.avoid)
```

评分因素（按优先级）：
1. 在 preferred region（MD&A / 附注）内 → +200
2. 非 TOC 页 → 避免 -1000
3. avoid 负上下文（如「在职员工」） → -130
4. 锚点优先级（越靠前越具体） → +8×index
5. heading boundary（行首） → +15

特殊机制：
- `fallback_anchors`：主锚点未命中时，尝试 sibling section（如 major_products → 业务概述）
- `_is_heading`：带编号前缀的标题（「（三）面临的风险」）也算 heading

### 5. 字段抽取

| 抽取类型 | 适用字段 | 方法 |
|---|---|---|
| `section_snippet` | mda, industry, segments, products, subsidiaries, risk | 锚点后 320 字符文本 |
| `table` | revenue_by_segment, revenue_by_region | pdfplumber 表格 + header 匹配 + preview 切片 |
| `numeric` | rnd_investment | 标签后数字提取（研发投入合计/金额） |
| `concentration` | top_customers, top_suppliers | 正则提取「前五名…占…%」句子 |

### 6. 输出

每个公司产出：

```
outputs/generalization/<code>/
  <code>.pdf              # 原始 PDF（不提交 Git）
  meta.json               # source_url, picked_title, orgid
  company_profile.json    # 结构化字段 + 证据
  company_brief.md        # 人类可读摘要
```

`company_profile.json` 结构：

```json
{
  "company": {"short_name": "...", "stock_code": "...", "exchange": "..."},
  "source": {"report_title": "...", "source_url": "...", "pdf_sha256": "...", "page_count": 282},
  "field_counts": {"found": 10, "partial": 1, "not_found": 0, "total": 11},
  "fields": [
    {
      "field": "mda",
      "label_cn": "管理层讨论与分析",
      "status": "found",
      "in_region": true,
      "value": "...",
      "evidence_sentence": "...",
      "page": 10,
      "anchor_matched": "管理层讨论与分析",
      "source_url": "..."
    }
  ]
}
```

## 单公司运行

```bash
python lab/extract_annual_report.py \
  --pdf outputs/generalization/600031/600031.pdf \
  --stock-code 600031 \
  --company-name "三一重工" \
  --source-url "https://static.cninfo.com.cn/finalpage/..." \
  --report-title "2024年年度报告"
```

## 批量评估

```bash
python lab/eval_generalize.py \
  --companies lab/eval_companies_1000.yaml \
  --out outputs/generalization/eval1000 \
  --throttle 1.0
```

特性：
- 逐公司顺序执行，1 req/s 限速
- 已缓存 PDF 自动跳过网络（断点续跑）
- 输出 `eval_results.json` + `eval_summary.md`
- 非金融/金融分开统计

## 关键设计决策

1. **不使用 LLM 抽取**：当前 pipeline 完全确定性，LLM 客户端为 stub
2. **工业 schema 为默认**：金融公司 auto-detect 仅记录 `suggested_profile`，不改变抽取
3. **evidence 优先**：每个字段必须能指向 PDF 具体页码和原文句子
4. **not_found 是有效结果**：银行无「前五名供应商」→ 正确返回 not_found，不编造

## 相关文档

- [字段 schema](database_schema.md)
- [评估方法](evaluation_method.md)
- [数据来源](data_sources.md)
