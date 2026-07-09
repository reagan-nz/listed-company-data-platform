# CNINFO A 类 Phase 1 Freeze v1 Implementation Plan

_最后更新：2026-07-09_

> **性质：** 未来实施计划 only；**本文件创建时不执行任何 implementation**；不调用 CNINFO；不 live；不下载 PDF。  
> **前置 signoff：** [cninfo_a_class_phase1_schema_freeze_approval_checklist.md](../outputs/validation/cninfo_a_class_phase1_schema_freeze_approval_checklist.md) · [approval summary](../outputs/validation/cninfo_a_class_phase1_schema_freeze_approval_summary.md)  
> **Gate 前提：** `a_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL` → 人工批准后 → `READY_FOR_IMPLEMENTATION`

---

## 1. Purpose

将已批准的 A-class Phase 1 freeze v1 schema（22 required · 13 recommended · 4 future · 2 removed）落地为可离线验证的 artifacts：

- A-class source registry draft 更新
- freeze v1 field catalog
- 扩展 offline fixtures
- benchmark validation 骨架

**不包含：** CNINFO live、PDF 下载/解析、extractor、embeddings、RAG、DB、MinIO、verified、testing_stable_sample。

---

## 2. Signoff Baseline（批准后不再重新辩论）

### Frozen scope

- `report_document` — 定期报告 metadata
- `report_period_snapshot` — company × report_type × expected_period 覆盖
- `document_lineage` — PDF URL 谱系（`storage_status=not_attempted`）

### In-scope report types

`annual_report` · `semi_annual_report` · `quarterly_report_q1` · `quarterly_report_q3`

### In-scope endpoint（metadata only）

`POST https://www.cninfo.com.cn/new/hisAnnouncement/query`（继承 A-class Phase1）

辅助：`POST https://www.cninfo.com.cn/new/information/topSearch/query`（orgId linkage）

### Removed from Phase1 contract

- `notes`（report_document）
- `mime_type`（document_lineage）

### Deferred

- `available_sections` · `download_time` · `file_hash` · `file_size`

---

## 3. Implementation Steps（严格顺序 · 批准后执行）

### Step 1 — Create freeze v1 field catalog

**产物：** `outputs/validation/cninfo_a_class_phase1_freeze_v1_field_catalog.csv`

| 列 | 说明 |
|----|------|
| field_name | 字段名 |
| object | report_document / report_period_snapshot / document_lineage |
| required_level | required / recommended / future / removed |
| source | CNINFO 或 derived 来源 |
| enum_values | 若有枚举则列出 |
| notes | 审计备注 |

对照已批准 decision matrix **40** 行；required 行数必须为 **22**。

**红线：** 不修改原始 [cninfo_a_class_phase1_minimum_fields.csv](../outputs/validation/cninfo_a_class_phase1_minimum_fields.csv)。

### Step 2 — Update A-class registry draft

**产物：** `config/cninfo_a_class_source_registry_draft.yaml`（新建草案）

| source_id | 说明 |
|-----------|------|
| `cninfo_periodic_report_annual` | 年报 metadata |
| `cninfo_periodic_report_semi_annual` | 半年报 metadata |
| `cninfo_periodic_report_quarterly` | 季报 metadata（q1/q3 子类型由 report_type 区分） |

内容：

- `query_endpoint` → hisAnnouncement/query
- `url_field` → adjunctUrl
- `phase1_status` → phase1_in_scope
- `status.recommended_status` → candidate 或 testing（**不写 verified / testing_stable_sample**）

对齐既有 B-class registry 中 `cninfo_periodic_report_pdf` 字段映射；A-class 独立 registry，不修改 B-class YAML。

### Step 3 — Expand offline fixtures

**目标目录：** `fixtures/a_class/phase1_freeze_v1/`

| 产物 | 说明 |
|------|------|
| `report_document_fixtures.jsonl` | 覆盖 4 report_type + not_found 负例 |
| `report_period_snapshot_fixtures.jsonl` | found / not_found / caveat 覆盖样例 |
| `document_lineage_fixtures.jsonl` | lineage 与 document_id 链接 |
| `negative_cases.jsonl` | title_excluded · missing adjunctUrl · unknown report_period |

来源：

- 从 `outputs/validation/cninfo_report_p1_coverage_validation.csv` 离线派生（**不调用 CNINFO**）
- 补充合成负例（company_code 999xxx）
- 保留 `fixtures/a_class/phase1/` 骨架为 schema 参考

**红线：** `_fixture_meta.cninfo_called = false`；URL 合成占位符。

### Step 4 — Extend offline lint

**脚本：** 扩展 `lab/lint_cninfo_a_class_phase1_freeze_v1.py` 或新建 `lab/lint_cninfo_a_class_phase1_freeze_v1_catalog.py`

新增规则示例：

- R-A1-011：freeze v1 catalog required count = 22
- R-A1-012：registry draft 无 verified / testing_stable_sample
- R-A1-013：expanded fixtures 全部 storage_status = not_attempted
- R-A1-014：无 removed 字段出现在 normalized fixture 输出

**无网络。**

### Step 5 — Create benchmark validation skeleton

**产物：**

| 文件 | 说明 |
|------|------|
| `fixtures/a_class/phase1_freeze_v1/ready_cases.yaml` | 3–5 家 known-company offline benchmark 定义 |
| `lab/run_cninfo_a_class_phase1_ready_case_benchmark.py` | 离线 runner（读 fixture · 不请求 CNINFO） |
| `outputs/validation/cninfo_a_class_phase1_ready_case_benchmark.csv` | benchmark case 表 |

建议 case 矩阵（offline only）：

| case_id | company_code | report_type | 预期 |
|---------|--------------|-------------|------|
| ARC001 | 600000 | annual_report | found |
| ARC002 | 300001 | semi_annual_report | found |
| ARC003 | 688001 | quarterly_report_q1 | found |
| ARC004 | 999002 | quarterly_report_q3 | not_found |
| ARC005 | guard | title_excluded | 不误入 periodic |

**不 live 执行。**

---

## 4. Not Included（明确排除）

| 项 | 状态 |
|----|------|
| CNINFO live metadata harvest | deferred |
| PDF download | deferred |
| PDF parser / extractor | deferred |
| OCR / embeddings / RAG | deferred |
| PostgreSQL / MinIO / MongoDB | deferred |
| verified | **不写** |
| testing_stable_sample | **不升级** |
| C-class / B-class output 修改 | **禁止** |

---

## 5. Expected Gates（implementation 完成后）

| Gate | 目标值 |
|------|--------|
| `a_class_phase1_freeze_v1_implementation_gate` | `PASS_OFFLINE` |
| `a_class_phase1_ready_case_benchmark_execution_gate` | `PASS_OFFLINE` |
| `a_class_phase1_schema_freeze_review_gate` | 保持 `READY_FOR_APPROVAL` 直至人工 signoff；signoff 后 → `READY_FOR_IMPLEMENTATION` |

---

## 6. Implementation Entry Condition

仅当以下全部满足时启动 implementation：

1. 人工完成 [approval checklist](../outputs/validation/cninfo_a_class_phase1_schema_freeze_approval_checklist.md) 并勾选 **APPROVE**
2. `a_class_phase1_freeze_v1_lint_gate = PASS_OFFLINE`（当前已满足）
3. C-class 状态仍为 `SNAPSHOT_GENERATED_QA_REVIEW`；不触碰 C/B-class 既有 harvest 输出

---

## 7. Red Lines

- **No CNINFO**
- **No live**
- **No PDF**
- **No parser**
- **No DB**
- **No MinIO**
- **No RAG**
- **No verified**
- **No testing_stable_sample**
