# CNINFO A 类 Tiny Live Metadata V2 Rerun Review

_生成时间：2026-07-09_

> **性质：** v2 rerun 人工 review 摘要；**不是 verified** · **不是 production_ready**

---

## Comparison with Previous Run (v1)

| 指标 | v1 | v2 |
|------|----|----|
| execution gate | `PASS_WITH_CAVEAT` | `PASS_WITH_CAVEAT` |
| CNINFO requests | 10 | **11** |
| success (found) | 5 | **5** |
| failure | 0 | **0** |
| wrong report-type match | **2** (ALM001/ALM005 semi) | **0** |
| English title slipped through | **1** (ALM004) | **0** |
| code/name mismatch in universe | **1** (ALM003) | **0** |
| PDF downloaded | 0 | **0** |
| PDF parsed | 0 | **0** |
| matching_logic | v1 (weak) | **v2** |
| universe | v1 | **v2 draft** |

---

## Caveat Fix Verification

### 1. Annual vs semi-annual mismatch (ALM001 / ALM005)

| case | v1 retrieved | v2 retrieved | Fixed? |
|------|--------------|--------------|--------|
| ALM001 | 2024年**半年度**报告 | 2024年**年度**报告 | **Yes** |
| ALM005 | 2024年**半年度**报告 | 2024年**年度**报告 | **Yes** |

**Root cause fixed：** v2 `match_title_for_report_type` 拒绝半年度标题；annual 搜索窗口扩展至次年 Q1。

### 2. ALM003 code/name mismatch

| 项 | v1 | v2 |
|----|----|----|
| universe name | 华熙生物 | **华兴源创** |
| retrieved title | 华兴源创：2025年第一季度报告 | 华兴源创：2025年第一季度报告 |
| consistency | mismatch | **aligned** |

**Fixed：** universe v2 Option A（`688001` = 华兴源创）。

### 3. English Q3 title (ALM004)

| 项 | v1 | v2 |
|----|----|----|
| retrieved | 2024年第三季度报告**（英文）** | 2024年**三季度**报告 |
| English exclusion | failed | **worked**（4 English titles skipped） |

**Fixed：** `ENGLISH_TITLE_REJECT` + v2 quarterly filters。

### 4. ALM002 (unchanged correct case)

v1/v2 both: `2024年半年度报告` · **correct**.

---

## V2 Case Results

| case_id | company | report_type | title | title_match | period_match |
|---------|---------|-------------|-------|-------------|--------------|
| ALM001 | 600000 浦发银行 | annual_report | 2024年年度报告 | pass | pass |
| ALM002 | 300001 特锐德 | semi_annual_report | 2024年半年度报告 | pass | pass |
| ALM003 | 688001 华兴源创 | quarterly_report_q1 | 2025年第一季度报告 | pass | pass |
| ALM004 | 000858 五粮液 | quarterly_report_q3 | 2024年三季度报告 | pass | pass |
| ALM005 | 600519 贵州茅台 | annual_report | 2024年年度报告 | pass | pass |

---

## Counts

| 指标 | 值 |
|------|-----|
| success | **5** |
| failed | **0** |
| wrong report-type match | **0** |
| English titles rejected (skipped) | **4** |
| CNINFO requests | **11** |
| PDF downloaded | **0** |
| PDF parsed | **0** |

---

## Remaining Caveats

- tiny sample only（**5** 家）；不可外推全市场
- `quality_status=pass` 仅表示 metadata 字段齐全 + title/period 对齐；**不是 verified**
- annual 报告披露窗口依赖次年 Q1 扩展；其他 edge case 未覆盖
- registry `live_validation_status` **未更新**（仍 design-only）
- prior v1 gate **`PASS_WITH_CAVEAT`** 保留为历史记录

---

## Gate Decision

```text
a_class_tiny_live_metadata_v2_execution_gate = PASS_WITH_CAVEAT
```

**理由：**

- **5/5** correct report-type metadata
- **0** wrong report-type matches
- **0** red-line violations（无 PDF · 无 DB · 无 verified）
- 仍 **不是 PASS**（tiny live only · 非 production_ready）

```text
a_class_tiny_live_metadata_fix_gate = RERUN_COMPLETE
```

（fix 包已执行；prior `READY_FOR_RERUN_APPROVAL` 已满足）

---

## Parallel Safety

- C-class: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）
- B-class / D-class outputs: **unchanged**

---

## Next Recommended Task

1. 人工 signoff v2 rerun review
2. 可选：将 universe v2 draft 提升为正式 tiny universe
3. 可选：registry draft `live_validation_status` 文档更新（**不写 verified**）
4. 扩大样本前须新 approval 包（仍 metadata-only · 无 PDF）
