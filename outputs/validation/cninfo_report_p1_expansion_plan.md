# CNINFO A 类报告 P1 扩展样本验证计划

- Era：C Phase 1 延伸（P1 扩展样本）
- 权威口径：[plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md)（A 类）
- P0 最终总结：[cninfo_report_coverage_final_summary.md](cninfo_report_coverage_final_summary.md)
- 样本清单：[cninfo_report_p1_sample_companies.csv](cninfo_report_p1_sample_companies.csv)
- 构建脚本：`lab/build_cninfo_report_p1_sample_companies.py`
- Coverage 入口：`lab/validate_cninfo_report_coverage.py`（`--input-mapping` / `--output-prefix`）

---

## 1. 为什么需要 P1 扩展

| 事实 | 含义 |
|------|------|
| P0 coverage **113/120 = 94.17%** | 仅是 **30 家 mapped** 小样本结果 |
| P0 样本来源 | 40 家 P0 公司（10 家 SZSE 主板无 orgId → skipped） |
| P0 能证明什么 | **Mechanism passed**：`hisAnnouncement/query` + 参数修复后，在已知 mapped 身份下可检索 A 类报告 PDF 链接 |
| P0 不能证明什么 | **Full-market stable**：不能代表 6000+ 上市公司全市场稳定 |
| 剩余 7 条 not_found | 全部 **SZSE 创业板 Q1/Q3**，`empty_response` |
| 板块分布不均 | P0 每板块仅 7–10 家 mapped，SSE/BSE 100% 可能受小样本偏差影响 |

**结论**：在宣布 A 类 retrieval 可工程化推广前，需要 **更平衡、更大样本** 的扩展验证，检验跨 exchange / board 稳定性——但 **仍不直接全市场**。

---

## 2. P1 验证目标

| 目标 | 说明 |
|------|------|
| 跨板块稳定性 | 检查 A 类 report retrieval 在 SSE 主板、SZSE 主板、创业板、科创板、北交所是否均可运行 |
| 样本规模 | **扩展样本**（目标 200 家），非全市场 |
| Coverage 口径 | 继续 **company × report_type × expected_period**（与 P0 一致） |
| 不写 verified | P1 仍是验证阶段结论 |
| 不宣称全市场 | P1 结果 **不得** 写成「全市场 94%」或「CNINFO A 类已 verified」 |

### 2.1 Coverage 阈值（与 P0 一致）

| coverage | recommended_status |
|----------|-------------------|
| < 80% | partial / not acceptable |
| 80–90% | partial |
| 90–95% | **testing / usable candidate** |
| 95%+ | stable pipeline candidate |

---

## 3. 样本设计

### 3.1 目标样本量

**200 家公司**（5 层 × 每层 **40** 家）。

| sample_layer | exchange | board | 目标数 |
|--------------|----------|-------|--------|
| sse_main | SSE | 主板 | 40 |
| szse_main | SZSE | 主板 | 40 |
| chinext | SZSE | 创业板 | 40 |
| star | SSE | 科创板 | 40 |
| bse | BSE | 北交所 | 40 |

### 3.2 公司全集来源

优先使用本地已有全市场列表（**不联网**）：

1. `lab/eval_companies_full_market_2024.yaml`（约 6124 家，含 `stock_code` / `short_name` / `exchange` / `board` / `orgid`）
2. 辅助：`outputs/generalization/full_market_2024/eval_results.json`

若某层不足 40 家可用公司，取 **最大可得样本** 并在 `cninfo_report_p1_sample_companies_summary.md` 说明。

### 3.3 抽样规则

- 优先 **A 股上市公司**（YAML 全市场列表已过滤）
- **尽量覆盖不同代码段**：层内按 `stock_code` 排序后等距抽取
- **尽量避免** ST / 退市 / 异常简称（简称含 `ST`、`*ST`、`退` 等排除）
- 输出字段：`company_code`、`company_name`、`exchange`、`board`、`sample_layer`、`sample_reason`、`source_file`
- **不伪造 orgId**：样本 CSV 仅标识公司；orgId 由后续 **identity mapping 扩展** 单独完成

### 3.4 与 P0 关系

- P1 样本 **可包含** P0 公司（用于对照稳定性）
- P1 **不等于** P0 超集替换；以分层新抽样为主，重叠在 summary 中统计

---

## 4. 验证口径

与 Phase 1 P0 **完全相同**：

| 项 | 定义 |
|----|------|
| 一行 | `company × report_type × expected_period` |
| report_type / period | `annual_report:2024`、`semi_annual_report:2024H1`、`quarterly_report_q1:2024Q1`、`quarterly_report_q3:2024Q3` |
| 分母 expected | `mapping_status=mapped` 的公司 × 4 |
| 分子 found | `found=yes` 且标题匹配、`parsed_report_period == expected_period`、`pdf_url` 非空 |
| skipped | `needs_orgid_mapping` 不计入分母 |
| strategy | 仅内部 fallback，不拆行 |

---

## 5. 预期输出

P1 coverage 本地运行（待 identity mapping 完成后）：

```bash
python lab/validate_cninfo_report_coverage.py \
  --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \
  --output-prefix outputs/validation/cninfo_report_p1_coverage \
  --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv
```

产出：

| 文件 | 内容 |
|------|------|
| `cninfo_report_p1_coverage_validation.csv` | 逐行 coverage |
| `cninfo_report_p1_coverage_validation_summary.md` | P1 摘要 + **与 P0 对比** |

Summary 必须包含：

- P0 baseline：113/120 = 94.17%
- P1 overall / 按 report_type / exchange / board
- `failure_reason` 分布
- remaining gaps（not_found 公司列表）
- mapped vs skipped 统计

---

## 6. 实施步骤（当前状态）

| 步骤 | 状态 | 产物 |
|------|------|------|
| P1 设计文档 | ✅ 本文档 | `cninfo_report_p1_expansion_plan.md` |
| P1 样本构建 | ✅ 脚本 + CSV | `build_cninfo_report_p1_sample_companies.py`、`cninfo_report_p1_sample_companies.csv` |
| Coverage 脚本 P1 入口 | ✅ 参数化 | `--input-mapping`、`--output-prefix`、`--sample-csv` |
| P1 identity mapping | ⏳ 待做 | 从 YAML `orgid` + P0 规则扩展，**不伪造** |
| P1 coverage 运行 | ⏳ 待做 | 需 mapping 完成后本地执行 |
| P1 最终总结 | ⏳ 待做 | 跑完后写 `cninfo_report_p1_coverage_final_summary.md`（可选） |

---

## 7. 边界

- 不下载 PDF 正文；不解析 PDF；不计算 hash
- 不接 PostgreSQL / MinIO / MongoDB
- 不使用 BrowserUser；不绕过登录 / 验证码 / 权限
- 请求间 sleep
- **不写 verified**
- P1 结果仅代表 **P1 样本集**，不代表全市场

---

## 8. 风险与关注

| 风险 | 缓解 |
|------|------|
| P1 大部分公司尚无 orgId mapping | 先扩展 `cninfo_report_p1_identity_mapping.csv`，再跑 coverage |
| 创业板季报 residual（P0 7 条） | P1 含 40 家创业板，可观察问题是否系统性 |
| SZSE 主板 orgId 规则 | P1 含 40 家 SZSE 主板，需批量 mapping（YAML 有 `gssz*` orgId 可参考） |
| 样本构建不联网 | orgId 来自已有 YAML，不 topSearch 批量补全（coverage 时再按需解析） |
