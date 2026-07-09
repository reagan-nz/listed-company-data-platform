# CNINFO A 类 Tiny Live Metadata Caveat Fix Review

_生成时间：2026-07-09_

> **性质：** 离线 caveat 分析与修复规划；**无 CNINFO** · **无 live rerun** · **无 PDF**

---

## Result Recap

| 指标 | 值 |
|------|-----|
| execution gate | `a_class_tiny_live_metadata_execution_gate = PASS_WITH_CAVEAT` |
| CNINFO requests | **10** |
| success (found) | **5** |
| failed | **0** |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| universe size | **5** (ALM001–ALM005) |

输入报告：[a_class_tiny_live_metadata_report.csv](cninfo_a_class_tiny_live_metadata/reports/a_class_tiny_live_metadata_report.csv)

---

## Caveat 1 — ALM001 annual vs semi-annual mismatch

| 项 | 内容 |
|----|------|
| case | ALM001 · 600000 浦发银行 |
| expected | `annual_report` · `expected_period=2024-12-31` |
| retrieved | 上海浦东发展银行股份有限公司**2024年半年度报告** |
| problem | annual vs semi-annual mismatch |

**Root cause：** v1 `_pick_best_record` 仅用宽泛 `REPORT_TYPE_KEYWORDS`（含「年报」子串），且按 `announcementTime` 取最新；半年报发布时间晚于年报检索窗口内候选，导致误选。

**Required fix：** runner `match_title_for_report_type` v2 — `annual_report` 必须含「年度报告」、拒绝「半年度报告」及季报标题。

**Schema change：** **No**

**Registry change：** **No**

**Live rerun needed：** **Yes**（批准后，使用 v2 matching + v2 universe）

---

## Caveat 2 — ALM005 annual vs semi-annual mismatch

| 项 | 内容 |
|----|------|
| case | ALM005 · 600519 贵州茅台 |
| expected | `annual_report` · `expected_period=2024-12-31` |
| retrieved | 贵州茅台**2024年半年度报告** |
| problem | annual vs semi-annual mismatch |

**Root cause：** 同 Caveat 1。

**Required fix：** 同 Caveat 1 v2 annual 专用 reject 规则。

**Schema change：** **No**

**Registry change：** **No**

**Live rerun needed：** **Yes**

---

## Caveat 3 — ALM003 code/name mismatch

| 项 | 内容 |
|----|------|
| case | ALM003 |
| universe v1 | `688001` · **华熙生物** |
| actual listing | `688001` = **华兴源创**（华熙生物 = `688363`） |
| retrieved title | 华兴源创：2025年第一季度报告 |
| problem | universe 公司名与代码不一致 |

**Root cause：** universe CSV 人工录入错误；metadata 实际按 `688001` 检索正确，但 universe 标注误导 QA。

**Required fix：** **Option A** — 将 ALM003 `company_name` 改为 **华兴源创**（采用）；新增 `validate_universe_code_name` 校验。

**Schema change：** **No**

**Registry change：** **No**（minor：无 registry YAML 修改）

**Live rerun needed：** **Optional**（universe 标注修正；检索路径不变）

---

## Caveat 4 — ALM004 English Q3 report

| 项 | 内容 |
|----|------|
| case | ALM004 · 000858 五粮液 |
| expected | `quarterly_report_q3` |
| retrieved | 2024年第三季度报告**（英文）** |
| problem | English title slipped through exclusion |

**Root cause：** v1 `TITLE_EXCLUSIONS` 仅含「英文版」，未覆盖「（英文）」/ `English` 变体。

**Required fix：** `ENGLISH_TITLE_REJECT` + quarterly/annual/semi 统一拒绝英文标题。

**Schema change：** **No**

**Registry change：** **No**（minor：可将 `phase1_report_title_exclusions` 同步补充「英文」— 可选、非必须）

**Live rerun needed：** **Yes**

---

## Caveat 5 — ALM002 (no caveat)

| 项 | 内容 |
|----|------|
| case | ALM002 · 300001 特锐德 |
| result | `semi_annual_report` · 2024年半年度报告 · **correct** |

无需修复。

---

## Overall Conclusion

| 维度 | 结论 |
|------|------|
| Schema change | **No** |
| Registry change | **No** or **minor only**（title exclusion 文档同步可选） |
| Runner matching logic | **Yes**（v2） |
| Universe correction | **Yes**（v2 draft · ALM003 公司名） |
| Live rerun | **Yes**（须 `READY_FOR_RERUN_APPROVAL` 后显式批准） |

---

## Fix Artifacts（本轮）

| 产物 | 路径 |
|------|------|
| universe v2 draft | [cninfo_a_class_phase1_tiny_live_metadata_universe_v2_draft.csv](cninfo_a_class_phase1_tiny_live_metadata_universe_v2_draft.csv) |
| runner v2 matching | [lab/run_cninfo_a_class_tiny_live_metadata_validation.py](../../lab/run_cninfo_a_class_tiny_live_metadata_validation.py) |
| matching tests | [lab/test_cninfo_a_class_tiny_live_metadata_matching_logic.py](../../lab/test_cninfo_a_class_tiny_live_metadata_matching_logic.py) |
| v2 dry-run report | [a_class_tiny_live_metadata_v2_dryrun_report.csv](cninfo_a_class_tiny_live_metadata/reports/a_class_tiny_live_metadata_v2_dryrun_report.csv) |
| fix summary | [cninfo_a_class_tiny_live_metadata_fix_summary.md](cninfo_a_class_tiny_live_metadata_fix_summary.md) |

**Prior execution gate 保持 `PASS_WITH_CAVEAT` 不变。**
