# CNINFO A 类 Phase 3 50-Company Expansion Plan

_生成时间：2026-07-10_

> **性质：** Phase 2（20/20 effective）收口 commit 后的 50 家 metadata 扩大规划；**离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 2 commit：** `cad5ed1` — A-class Phase 2 metadata final closure: 20/20 effective accepted after retry_v3 recovery

**Recommendation source：** [cninfo_a_class_phase2_post_retry_v3_next_step_recommendation.md](cninfo_a_class_phase2_post_retry_v3_next_step_recommendation.md) · **Option B only**

---

## 1. Objective

在 **a_class_phase1_freeze_v1 schema 不变** 的前提下，将 A-class live metadata validation 规划扩大至 **50** 家公司（A3M001–A3M050）：

- **metadata + pdf URL lineage only**
- 沿用 Phase 1 v2 标题/期间匹配策略（`MATCHING_LOGIC_VERSION = "v2"`）
- 使用 **独立输出根** `outputs/validation/cninfo_a_class_phase3_50_company_expansion/`
- **不**标 verified · **不**宣称 production_ready · **不**升级 testing_stable_sample

---

## 2. Why Phase 3 Is Planning-Only Now

1. **Phase 2 刚完成 explicit-path commit**（`cad5ed1`）：effective **20/20**（12 original + 8 retry_v3 recovered）；需先完成离线 universe 设计与批准包，再进入 runner 扩展与 live。
2. **50 家规模风险上升**：Phase 2 已观测 network/orgId 瞬时失败与 ChiNext residual risk（A2M010 precheck unreachable）；50 家需更严格 bucket 设计与 rate limit 预案。
3. **runner 尚未支持 `--phase3-50`**：当前 `run_cninfo_a_class_phase2_metadata_expansion.py` 仅支持 Phase 2 expansion 与 retry v1/v2/v3/precheck 模式。
4. **红线约束**：本任务 **不调用 CNINFO**、**不 live**、**不 PDF/OCR/extraction/DB/MinIO/RAG**。

---

## 3. Phase 1 / Phase 2 Evidence Recap

### Phase 1 Tiny Live v2

| 项 | 值 |
|----|-----|
| boundary gate | `a_class_phase1_boundary_gate = PASS_WITH_CAVEAT` |
| cases | **5** · ALM001–ALM005 |
| v2 matching | wrong_report_type=**0** |
| PDF / DB / MinIO / RAG | **0** |

### Phase 2 Expansion + Retries

| 项 | 值 |
|----|-----|
| original execution gate | `a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED` |
| failed retry execution gate | `a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED` |
| retry v3 execution gate | `a_class_phase2_retry_v3_execution_gate = PASS_WITH_CAVEAT` |
| final closure gate | `a_class_phase2_metadata_final_closure_gate = PASS_WITH_CAVEAT` |
| **effective final** | **20/20** · unresolved **0** |
| accepted_original_success | **12** |
| accepted_retry_v3_recovered | **8** |
| CNINFO（Phase 2 全轨合计） | original + retry_v1 + retry_v2 + precheck + retry_v3 |
| PDF download / parse / OCR / extraction / DB / MinIO / RAG | **0** |

Phase 2 证明 20 家 pilot 可在 metadata-only 边界内达到 **100% effective coverage**（含 isolated retry_v3）；仍不足以支撑全市场失败率统计，但为 Phase 3 50 家提供了可复用 playbook。

**Phase 2 20 家不重跑。** retry_v3 recovered 8 不重跑。

---

## 4. Scope

| 项 | 值 |
|----|-----|
| sample size | **50** |
| case ID | **A3M001–A3M050** |
| schema | a_class_phase1_freeze_v1 · **不变** |
| objects | `report_document` · `report_period_snapshot` · `document_lineage` |
| matching | v2 · **不变** |
| retrieval | CNINFO announcement metadata · orgId resolution |
| lineage | pdf_url / adjunct_url **登记 only** |

### 明确禁止

- PDF download · PDF parse · OCR · section/table extraction
- DB · MinIO · RAG / embeddings
- verified · production_ready · testing_stable_sample 升级
- 触碰 Phase 1 / Phase 2 / retry / precheck 既有输出根
- 重跑 Phase 2 effective accepted 20

---

## 5. Report-type Coverage Strategy

| report_type | 目标 case 数 | 说明 |
|-------------|-------------|------|
| `annual_report` | **20** | SSE/SZSE 主板蓝筹 + 金融；验证年度报告专用过滤 |
| `semi_annual_report` | **10** | 主板/创业板；验证半年度报告专用过滤 |
| `quarterly_report_q1` | **10** | 科创板/主板；验证 Q1 标题变体 |
| `quarterly_report_q3` | **10** | 创业板/科创板/主板；验证 Q3 标题变体；观测 English 拒绝 |

**合计：50 家，每家公司仅 1 个 report_type case。**

**universe draft：** [cninfo_a_class_phase3_50_company_universe_draft.csv](../outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv)

---

## 6. Overlap / Exclusion Policy

### 硬排除（universe draft 已离线校验）

1. **Phase 1 tiny live universe（5 codes）：** 600000 · 300001 · 688001 · 000858 · 600519
2. **Phase 2 effective accepted universe（20 codes）：** A2M001–A2M020 全部 company_code
3. **Phase 2 retry 子集：** 已含于 Phase 2 20，不单独纳入
4. ST / *ST / 退市公司（short_name 含 ST 或 退）
5. BSE（北交所）board — 默认排除
6. universe 内 `company_code` 不得重复

### 重叠策略

| 维度 | 策略 |
|------|------|
| Phase 1 overlap | **0** — 硬排除 ALM001–ALM005 codes |
| Phase 2 overlap | **0** — 硬排除 A2M001–A2M020 codes |
| Phase 2 effective 20 rerun | **禁止** — 12 original success + 8 retry_v3 recovered 均 hold |
| 同一 company 不同 report_type | Phase 3 每公司 1 case；不与 Phase 2 重复 company |

### 候选池来源

`lab/eval_companies_full_market_2024.yaml`（`full_market_2024` registry）

---

## 7. Title / Period Matching Policy

沿用 Phase 1 v2 matching logic（与 Phase 2 相同）：

- **annual_report：** must include `年度报告` · reject 半年度/一季/三季/英文
- **semi_annual_report：** must include `半年度报告` · reject 英文
- **quarterly_report_q1：** must include Q1 变体 · reject 英文
- **quarterly_report_q3：** must include Q3 变体 · reject 英文
- **period matching：** expected_period 与 announcementTime 派生期间比对

**不写 verified。** **不升级 testing_stable_sample。**

---

## 8. Output Root Isolation Proposal

**专用输出根（强制）：**

```text
outputs/validation/cninfo_a_class_phase3_50_company_expansion/
```

建议子路径：

```text
outputs/validation/cninfo_a_class_phase3_50_company_expansion/
  reports/
    a_class_phase3_50_company_expansion_report.csv
    a_class_phase3_50_company_expansion_summary.md
    a_class_phase3_50_company_expansion_quality_report.csv
  raw_metadata/
    A3M001.json … A3M050.json
```

**禁止写入：**

- `outputs/validation/cninfo_a_class_tiny_live_metadata/`（Phase 1）
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/`（Phase 2 original）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/`（retry v1）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/`（retry v2）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v3/`（retry v3）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/`（precheck）
- `outputs/harvest/` · `outputs/snapshot/`

---

## 9. Risk Controls

| 风险 | 控制措施 |
|------|----------|
| network transient error | 沿用 Phase 2 retry playbook；50 家需预留 isolated retry budget |
| ChiNext orgId unreachable | Phase 2 precheck 已记录 A2M010 residual risk；Phase 3 ChiNext 样本控制在 **4** 家 |
| rate limit / HTTP 429 | `--sleep-seconds 0.6`；并发 **1**；429 全局停止 |
| output root 污染 | 强制 `cninfo_a_class_phase3_50_company_expansion/` |
| scope creep | metadata only；PDF/OCR/extraction/DB/MinIO/RAG 红线 |
| prior-phase overlap | universe draft 离线校验 **0 overlap** |
| runner 误用 | 需 `--approve-a-class-phase3-50-company-expansion` + `--phase3-50`（未来实现） |

---

## 10. Expected Outputs（未来 live 回合）

| 输出 | 路径 |
|------|------|
| dry-run report | `outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/` |
| live expansion report | 同上 |
| quality report | 同上 |
| closure metrics | `outputs/validation/` |

**本回合仅产出规划包，不创建上述 live 输出。**

---

## 11. Approval Requirements

| 门槛 | 要求 |
|------|------|
| Phase 2 prerequisite | effective **20/20** · commit **`cad5ed1`** reviewed |
| universe review | 50-row draft 人工审阅 · overlap **0** |
| output isolation | 独立 Phase 3 根确认 |
| metadata-only | PDF/OCR/extraction/DB/MinIO/RAG 禁用确认 |
| explicit approval | `--approve-a-class-phase3-50-company-expansion`（未来 flag） |
| runner extension | dry-run + tests（未来回合） |
| live execution | **NOT APPROVED** until separate gate |

---

## 12. Gate（本回合）

```text
a_class_phase3_50_company_planning_gate = READY_FOR_APPROVAL
```

**不是 PASS。** **不是 live_ready。** **不是 verified。** **不是 production_ready。**

---

## 13. Next Immediate Task

人工审阅批准包 → runner extension + dry-run（**offline · separate approval · NOT APPROVED live**）。
