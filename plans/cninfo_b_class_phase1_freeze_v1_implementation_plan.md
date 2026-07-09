# CNINFO B 类 Phase 1 Freeze v1 Implementation Plan

_最后更新：2026-07-09_

> **性质：** 未来实施计划 only；**本文件创建时不执行任何 implementation**；不修改 registry YAML；不 live。  
> **前置 signoff：** [cninfo_b_class_phase1_schema_freeze_approval_draft.md](cninfo_b_class_phase1_schema_freeze_approval_draft.md) · [signoff summary](../outputs/validation/cninfo_b_class_phase1_schema_freeze_signoff_summary.md)  
> **Gate：** `b_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION`

---

## 1. Purpose

将已 signoff 的 Phase 1 schema（15 required fields · 4 in-scope endpoints）落地为可离线验证的 artifacts：registry 修订、fixtures、schema catalog、lint、ready-case benchmark。

**不包含：** PDF 下载/解析、DB、MinIO、RAG、live CNINFO、verified。

---

## 2. Signoff Baseline（不再重新辩论）

### Frozen scope

- announcement metadata
- document metadata
- PDF URL lineage
- source lineage
- quality status

### In-scope endpoints

EP001 · EP002 · EP004 · EP005

### Deferred / removed

- Deferred: EP006 · EP007
- Removed: EP003

---

## 3. Implementation Steps（严格顺序）

### Step 1 — Update source registry YAML

**文件：** `config/cninfo_b_class_source_registry_draft.yaml`

| 动作 | 源 | 内容 |
|------|-----|------|
| keep | cninfo_periodic_report_pdf | 维持 EP001 映射 |
| revise | cninfo_general_announcement_pdf | 补 category 对齐注释；对齐 cninfo_announcement_categories.yaml |
| defer | cninfo_inquiry_reply_pdf | 补 `deferred_phase2: true` 注释；endpoint 暂填 EP001 预期或保持 null + 显式 defer 说明 |
| defer | cninfo_meeting_notice_pdf | 同上 |

**红线：** 不写 verified；不升级 testing_stable_sample。

### Step 2 — Generate fixtures

**目标目录：** `fixtures/b_class/phase1_freeze_v1/`

| 产物 | 说明 |
|------|------|
| `announcement_metadata_fixtures.jsonl` | 覆盖 15 required fields 的 offline 样本 |
| `pdf_reference_fixtures.jsonl` | adjunct_url + pdf_url + source_endpoint lineage |
| `negative_cases.jsonl` | not_found · missing adjunctUrl · title_excluded |

来源：复用既有 periodic/non-periodic fixtures + 手工构造 EP004/EP005 代表行；**不调用 CNINFO**。

### Step 3 — Create validation schema / freeze v1 catalog

| 产物 | 路径 |
|------|------|
| Freeze v1 field catalog | `outputs/validation/cninfo_b_class_phase1_freeze_v1_fields.csv` |
| Phase 1 JSON Schema patch notes | `plans/cninfo_b_class_phase1_freeze_v1_schema_notes.md` |

对照 signoff 15 required fields；可选生成 `schemas/b_class/b_phase1_metadata.schema.json` draft。

### Step 4 — Create offline schema lint

**脚本草案：** `lab/lint_cninfo_b_class_phase1_freeze_v1.py`

规则示例：

- R-P1-001：15 required fields 非空（fixture 模式）
- R-P1-002：download_status 必须为 not_attempted
- R-P1-003：无 PDF body / parse / embedding 字段
- R-P1-004：source_endpoint 必须匹配 in-scope endpoint 表
- R-P1-005：EP003/EP006/EP007 不得出现在 Phase1 fixture source_id

**无网络。**

### Step 5 — Create ready-case benchmark

**文件：** `fixtures/b_class/retrieval_validation/phase1_freeze_v1_ready_cases.yaml`

| 类型 | 数量建议 |
|------|----------|
| periodic known-document | 2–3 |
| general announcement known-document | 2–3 |
| guard（title_excluded 不误入 periodic） | 1 |

沿用既有 ready-case intake / review checklist 机制；**不 live 执行**。

### Step 6 — Request live validation approval（仅 Step 1–5 完成后）

前置条件：

- [ ] registry YAML 修订完成
- [ ] fixtures + lint PASS
- [ ] ready-case 人工 review 为 ready
- [ ] C-class Phase 3 live harvest 不与 B-class 并发
- [ ] 用户显式批准 tiny live metadata

产物：live approval plan + command draft（**NOT APPROVED YET**）

---

## 4. Explicit Non-Goals

- 不下载 PDF
- 不解析 PDF / OCR
- 不建 vector index / RAG
- 不接 DB / MinIO
- 不写 verified
- 不触碰 `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`

---

## 5. Success Criteria（implementation 回合）

| 项 | 目标 |
|----|------|
| freeze v1 catalog | 15 required fields 文档化 |
| registry YAML | EP004/EP005 对齐；EP006/EP007 defer 标注 |
| fixtures | ≥10 条 Phase1 metadata 行 |
| lint | 全规则 PASS（offline） |
| ready-case | ≥5 条 ready（设计目标） |
| live | **0** CNINFO 请求（本 plan 范围内） |

---

## 6. Gate Progression

```text
b_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION  (current)
b_class_phase1_freeze_v1_implementation_gate = NOT_STARTED
b_class_phase1_live_validation_gate = NOT_STARTED
```

Implementation 完成后可设 `b_class_phase1_freeze_v1_implementation_gate = READY_FOR_LIVE_APPROVAL`（仍不是 PASS）。

---

## 7. Recommended First Implementation Task

**Step 1：** 修订 registry YAML（offline diff only）并生成 registry revision notes — 仍在本 plan 的未来回合执行，**非本 signoff 回合**。
