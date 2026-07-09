# CNINFO B 类 Phase 1 Ready-case Benchmark Summary

_生成时间：2026-07-09_

> **性质：** 离线 benchmark 设计快照；**未执行 live**；无 CNINFO 请求。  
> **明细表：** [cninfo_b_class_phase1_ready_case_benchmark.csv](cninfo_b_class_phase1_ready_case_benchmark.csv)

---

## Current Cases（5）

| case_id | fixture | status |
|---------|---------|--------|
| RC001 | [announcement_metadata_fixture.json](../../fixtures/b_class/phase1/announcement_metadata_fixture.json) | not_run |
| RC002 | [announcement_metadata_fixture.json](../../fixtures/b_class/phase1/announcement_metadata_fixture.json) | not_run |
| RC003 | [RC003_missing_pdf_url_case.json](../../fixtures/b_class/phase1/ready_cases/RC003_missing_pdf_url_case.json) | not_run |
| RC004 | [RC004_duplicate_announcement_case.json](../../fixtures/b_class/phase1/ready_cases/RC004_duplicate_announcement_case.json) | not_run |
| RC005 | [RC005_unknown_category_case.json](../../fixtures/b_class/phase1/ready_cases/RC005_unknown_category_case.json) | not_run |

---

## RC001 — periodic_report_metadata

**Purpose:** 验证定期报告 metadata 路径下 15 个 required 字段与 PDF URL lineage 均可登记。

**Expected behavior:**

- 所有 signoff required 字段存在
- `pdf_url` 与 `adjunct_url` 有值
- `quality_status = pass`
- `lineage_status = discovered`

**Failure mode tested:** 若 periodic source 检索成功但缺 required 字段，应 fail lint/QA 而非 silent pass。

---

## RC002 — general_announcement_metadata

**Purpose:** 验证非定期公告源（`cninfo_general_announcement_pdf`）可复用同一 metadata 形状。

**Expected behavior:**

- required 字段齐全
- PDF URL lineage 存在
- `quality_status = pass`（fixture 级）

**Failure mode tested:** general source 与 periodic source 字段形状不一致导致 mapper 断裂。

---

## RC003 — missing_pdf_url

**Purpose:** 公告 metadata 存在但 PDF lineage 缺失。

**Expected behavior:**

- `announcement_id` 存在
- `announcement_title` 存在
- `pdf_url` 缺失（null）
- `adjunct_url` 缺失（null）
- `quality_status = needs_review`
- **不得**标记为 `verified`

**Failure mode tested:** 将无 PDF URL 的公告误标为 pass/verified。

---

## RC004 — duplicate_announcement_id

**Purpose:** 同一 `announcement_id` 出现多个 metadata 候选。

**Expected behavior:**

- 两个 candidate 共享 `announcement_id`
- metadata 内容不同（标题/时间/pdf_url）
- `dedup_decision_required = true`
- **无** automatic merge

**Failure mode tested:** 静默覆盖或自动合并重复公告导致 lineage 丢失。

---

## RC005 — unknown_category

**Purpose:** 无法可靠路由的公告类别。

**Expected behavior:**

- announcement metadata 被接受
- `announcement_category = unknown` 或 `category_status = review_later`
- **不**强制 taxonomy 映射
- `quality_status = needs_review`

**Failure mode tested:** 未知标题被硬编码映射到错误 category 并标 pass。

---

## Gate

```text
b_class_ready_case_benchmark_gate = READY_FOR_REVIEW
```

**不是 PASS** — benchmark 尚未 offline 执行或 live 验证。

---

## Next Step

人工 review 本 summary + fixtures → 批准后进入 [live validation approval plan](../../plans/cninfo_b_class_phase1_live_validation_approval_plan.md) 审阅（仍 **NOT APPROVED**）。

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**
