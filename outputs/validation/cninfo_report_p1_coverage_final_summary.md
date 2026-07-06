# CNINFO A 类报告 coverage — Era C Phase 1 P1 最终总结

- 生成时间：2026-07-05（离线整理，最终 rerun 收口）
- **Phase 1 完整收口文档**：[cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md) ← **权威总结**
- 脚本：`lab/validate_cninfo_report_coverage.py`
- 跑次摘要：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- 逐行结果：[cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv)
- P1 样本与 mapping：[cninfo_report_p1_sample_companies_summary.md](cninfo_report_p1_sample_companies_summary.md)、[cninfo_report_p1_identity_mapping_summary.md](cninfo_report_p1_identity_mapping_summary.md)

---

## 1. P1 扩展样本最终结果（title-filter 后最终 rerun）

| 指标 | 数值 |
|------|------|
| 样本公司数 | 200 |
| mapped 公司数 | 199 |
| skipped（needs_orgid_mapping） | 1 家（000001），4 行 |
| **expected rows（分母）** | **796** |
| **found / effective found** | **749** |
| **not_found** | **47** |
| **overall effective coverage** | **749/796 = 94.10%** |
| **recommended_status** | **testing / usable candidate** |

### 按 report_type

| report_type | found / expected | coverage |
|-------------|------------------|----------|
| annual_report | 193/199 | 96.98% |
| semi_annual_report | 185/199 | 92.96% |
| quarterly_report_q1 | 184/199 | 92.46% |
| quarterly_report_q3 | 187/199 | 93.97% |

### 按 exchange

| exchange | found / expected | coverage |
|----------|------------------|----------|
| SSE | 304/320 | 95.00% |
| SZSE | 305/316 | 96.52% |
| BSE | 140/160 | 87.50% |

### not_found 构成

| failure_reason | 行数 |
|----------------|------|
| empty_response | 39 |
| period_mismatch | 8 |

### 与 P0 对比

- P0（30 mapped）：113/120 = **94.17%**
- P1（199 mapped）：749/796 = **94.10%** — 机制在更大分层样本上 **与 P0 同量级**，但 **不代表全市场**

### 修正轨迹（P1）

```
初跑（无 title filter / 无完整季报 fallback）：620/796 = 77.89%
    ↓ 参数修复 + 季报策略 + title filter
750/796 = 94.22%（含假阳性；一轮 audit pass 78%）
    ↓ audit-driven official title exclusion（全 report_type）
749/796 = 94.10%（effective found，最终 rerun）
```

---

## 2. Quality audit 收口

| 轮次 | found pass rate | 要点 |
|------|-----------------|------|
| 一轮（seed=42） | **78%**（78/100） | 旧 94.22% 含大量披露提示性公告假阳性；粗算有效 ~73.5% |
| 二轮（seed=43） | **97.5%**（39/40） | title-filter 后可信度高；not_found 10/10 合理；唯一 fail = 延期披露（已补 exclusion） |

- 一轮：[cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)
- 二轮：[cninfo_report_p1_quality_audit_round2_results.md](cninfo_report_p1_quality_audit_round2_results.md)
- audit 外推有效 coverage：**~91.7%**（抽样，非全量人工 accuracy）

---

## 3. 当前 coverage 的解释边界

- **94.10%** 是 **effective retrieval coverage**，**不是**全量人工 PDF accuracy。
- **found** = `pdf_url` 非空 + 报告期匹配 + 标题匹配 report_type + 未命中 official title exclusion。
- **recommended_status：testing / usable candidate**；**不写 verified**；**不写 full-market stable**。

---

## 4. 剩余问题与下一步

- **47 行 not_found**：主因 BSE `empty_response`（39）+ `period_mismatch`（8）
- BSE **87.50%** 为最低层；参数侧已确认 `column=bj`、stock 920/430 — 问题更可能在 mapping / 样本状态
- **Phase 1 A 类主线可收口**；下一步：**BSE residual diagnostics**（单独）→ **Phase 2 D 类表格**
- 详见 [cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md) §10–12

---

## 5. 边界

- 未下载 / 解析 PDF；未计算 hash；未接数据库 / MinIO
- 仅代表 **P1 分层 200 家样本（199 mapped）**
- **不写 verified**；**不代表全市场稳定**

### P1 一句话

**P1 在 audit-driven title filter 后达 749/796 = 94.10%，二轮 audit 97.5% found pass，评为 testing/usable candidate；Phase 1 可 close，BSE residual 与 Phase 2 分列推进。**

---

## 6. 相关产物索引

| 文件 | 用途 |
|------|------|
| [cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md) | **Phase 1 完整收口（P0+P1+audit）** |
| [cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv) | P1 逐行 coverage |
| [cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md) | 跑次摘要 + remaining gaps |
| [cninfo_report_p1_coverage_final_rerun.log](cninfo_report_p1_coverage_final_rerun.log) | 最终 rerun 日志 |
| [cninfo_report_p1_coverage_parameter_diagnostics.md](cninfo_report_p1_coverage_parameter_diagnostics.md) | BSE/SZSE/SSE 参数诊断 |
| [cninfo_report_coverage_final_summary.md](cninfo_report_coverage_final_summary.md) | P0 小样本最终总结 |
| [cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md) | P1 样本设计 |
