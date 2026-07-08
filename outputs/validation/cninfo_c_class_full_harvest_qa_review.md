# CNINFO C-Class Full Harvest QA Review

_生成时间：2026-07-08_

> 离线 QA：仅读取现有 harvest 输出。**无 CNINFO** · **无 live 重跑** · **无 raw/normalized 修改** · **无 verified** · **无 DB/MinIO/RAG**

## QA Conclusion

**PASS_WITH_CAVEAT**

- harvest_full_gate: **PASS_WITH_RESUME**

## 1. Full harvest gate

| 检查项 | 值 | 期望 | 判定 |
|--------|-----|------|------|
| harvest_full_gate | PASS_WITH_RESUME | PASS_WITH_RESUME | **PASS** |
| blocked | 0 | 0 | **PASS** |
| http_error | 0 | 0 | **PASS** |

## 2. 文件计数 & universe

| 指标 | 实际 | 期望 |
|------|------|------|
| raw total | **6041** | 6041 |
| normalized total | **8630** | 8630 |
| completed companies | **863** | 863 |
| hold_overlap | **0** | 0 |
| total_harvest_universe | **863** | 863 |
| resume_smoke_only_disk | **10** | 10（resume 跳过 smoke） |

## 3. Per-source reachability（863 家 · 含磁盘 smoke 补齐）

| source | endpoint_found | derived_from_basic | empty_but_valid_response | valid_empty | other |
|--------|----------------|--------------------|--------------------------|-------------|-------|
| basic | 863 | 0 | 0 | 0 | 0 |
| executive | 854 | 0 | 9 | 0 | 0 |
| share_capital | 853 | 0 | 10 | 0 | 0 |
| top_shareholders | 847 | 0 | 16 | 0 | 0 |
| top_float | 844 | 0 | 19 | 0 | 0 |
| dividend_history | 825 | 0 | 0 | 38 | 0 |
| security_observe _(observe_only)_ | 863 | 0 | 0 | 0 | 0 |
| contact | 0 | 863 | 0 | 0 | 0 |
| business_scope | 0 | 863 | 0 | 0 | 0 |
| industry | 0 | 863 | 0 | 0 | 0 |

## 4. company_harvest_status 分布（863 家重建）

- `complete`: **863**

## 5. retrieval_status 分布（8630 rows）

- `blocked`: **0**
- `derived_from_basic`: **2589**
- `empty_but_valid_response`: **54**
- `endpoint_found`: **5949**
- `http_error`: **0**
- `valid_empty`: **38**

## 6. dividend_parse_status 分布（company 级 · 863 家）

_dividend_history ≠ financing；自 normalized/dividend_history jsonl 聚合。_

- `empty_but_valid`: **38**
- `parsed`: **293**
- `partial`: **532**

_补充：事件级 `needs_review` 共 **12** 条，分布于 **12** 家公司（company 级聚合为 `partial`）。_


## 7. Review flags 摘要

- 总 flags: **72**
- `dividend_parse`: **12**
- `missing_normalized_core`: **6**
- `source_caveat`: **54**

详见 [cninfo_c_class_full_harvest_qa_flags.csv](cninfo_c_class_full_harvest_qa_flags.csv)。

## 8. 判定说明

| 级别 | 条件 |
|------|------|
| **PASS** | gate 通过 · 计数正确 · 无 review flags |
| **PASS_WITH_CAVEAT** | gate 通过 · 存在 source_partial / empty_but_valid / dividend parse / fill gap 等待人工 review |
| **FAIL** | gate 失败 · hold_overlap · 计数不符 · blocked/http_error · company failed |

**政策：** `source_partial` / `empty_but_valid` **不自动判 FAIL**；`security_observe` **observe_only**，不进入主 company snapshot。

### Caveat notes

- resume_smoke_batch=10 家仅磁盘覆盖、无 full report 行
- dividend_parse partial=532
- dividend_parse empty_but_valid=38
- dividend needs_review 事件涉及 12 家
- source_caveat flags=54 (empty_but_valid on partial/caveat sources)
- normalized_core fill gaps: 55 家有缺口

## 9. 输入文件

- `outputs/harvest/cninfo_c_class/quality/harvest_summary.md`
- `outputs/validation/cninfo_c_class_harvest_full_summary.md`
- `outputs/validation/cninfo_c_class_harvest_full_report.csv` (8530 rows)
- `outputs/harvest/cninfo_c_class/quality/source_quality.csv`
- `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv`
- `outputs/harvest/cninfo_c_class/quality/field_fill_rate.csv`
- sample: `lab/eval_companies_c_class_harvest_863_non_bse.yaml`

## 10. 红线确认

- 未请求 CNINFO
- 未重跑 live harvest
- 未修改 raw / normalized 数据
- 未写 verified / 未升级 testing_stable_sample
- 未入库 / MinIO / RAG / YAML backfill
