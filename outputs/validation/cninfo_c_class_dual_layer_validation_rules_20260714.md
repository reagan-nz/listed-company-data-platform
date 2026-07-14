# CNINFO C 类 — 双层语义校验规则（Status-Ledger vs Resume-Audit）

_生成时间：2026-07-14 · offline rules only · CNINFO=0_

> **offline only** · **no live** · **no snapshot** · **no harvest mutation** · **no commit/push** · **approved_for_snapshot_rebuild=false（保持不变）**

---

## 任务范围

为 slice1 universe 200 建立 **双层语义校验规则** 文档：明确 status-ledger（`company_harvest_status.csv`）与 offline resume-audit 两层对同一 harvest 产物的不同判定语义，覆盖 **partial7** 与 **empty-dividend-3** caveat 家族，以及二者对齐/分歧时的离线处置。

**任务 ID：** C-GEN-20260714-05

**不重复：** caveat10 registry（C-GEN-20260714-04）索引；本任务仅新增规则文档与规则矩阵。

---

## 来源（只读）

| 文件 | 用途 |
|------|------|
| `cninfo_c_class_caveat10_registry_20260714.md` / `.csv` | 10 家 caveat 统一索引 |
| `cninfo_c_class_partial7_evidence_completeness_20260714.md` | partial7 证据完备性 |
| `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` | partial7 离线矩阵（7 行） |
| `cninfo_c_class_empty_dividend_evidence_20260714.md` | empty-dividend 证据完备性 |
| `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv` | empty-dividend 离线矩阵（3 行） |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` | closure 权威计数与 case_id |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` | 闭合指标 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` | 10 行 caveat 明细 |
| `lab/run_cninfo_c_class_harvest_resume_audit.py` | resume-audit 判定实现（只读引用） |

---

## 双层模型定义

### Layer 1 — Status-Ledger（检索层）

**数据源：** `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv`

**语义：** 按 normalized 目录下 **文件存在性** 计数（共 10 源），与 harvest runner 对齐。

| 条件 | `harvest_status` |
|------|------------------|
| normalized 源目录数 ≥ 10 | **complete** |
| 1 ≤ 源目录数 ≤ 9 | **partial** |
| 源目录数 = 0 | **missing** |

**关键语义：** 0 字节 `dividend_history.jsonl` **计入** sources_present（文件存在即算）。

### Layer 2 — Resume-Audit（质量层）

**数据源：** `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv`

**语义：** 在 ledger 基础上，对 normalized 内容做 **非空校验**（`.jsonl` 须至少一行非空；`.json` 须 size>2），并映射 `resume_state`。

| `resume_state` | 触发条件（摘要） |
|----------------|------------------|
| **complete** | ledger=complete 且 audit sources_present ≥ 10 |
| **partial** | ledger=partial/failed；或源缺口但有部分文件 |
| **needs_review** | ledger=complete 但 audit sources_present < 10；或无 status 行但有磁盘文件 |
| **missing** | 无 status 且无 normalized 文件 |

**关键语义：** 0 字节 `dividend_history.jsonl` 在 audit 层 **不计入** present → 可产生 ledger=complete / audit=needs_review **合法分歧**。

---

## 闭合指标（slice1 · 引用 closure）

| 指标 | 值 |
|------|-----|
| universe | 200 |
| ledger complete | 193 |
| ledger partial | 7 |
| ledger missing | 0 |
| audit complete | 190 |
| audit partial | 7 |
| audit needs_review | 3 |
| caveat 总数 | 10 |
| QA gate | `PASS_WITH_CAVEAT` |
| `approved_for_snapshot_rebuild` | **false** |
| CNINFO 调用 | **0** |

---

## 规则族 A — 通用阈值（applies_to: both）

### DLVR-001 · Ledger 完整门槛

- **ledger_expectation：** `harvest_status=complete` 当且仅当 normalized 源文件数 ≥ 10（存在性，含 0 字节）
- **audit_expectation：** 不单独判定；须与 DLVR-004/005 联立
- **offline_action：** 自磁盘 `normalized/<source_type>/` 计数；与 `company_harvest_status.csv` 交叉核验
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-002 · Ledger 部分门槛

- **ledger_expectation：** `harvest_status=partial` 当 1 ≤ normalized 源数 ≤ 9
- **audit_expectation：** 通常 `resume_state=partial`（`status_csv_partial`）
- **offline_action：** 列出 missing normalized 源；与 raw `retrieval_status` 对账
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-003 · Ledger 缺失门槛

- **ledger_expectation：** `harvest_status=missing` 当 normalized 源数 = 0
- **audit_expectation：** 通常 `resume_state=missing`
- **offline_action：** 确认无 status 行且无磁盘产物；标记 universe 缺口
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-004 · Audit 源 present 内容门槛

- **ledger_expectation：** N/A（ledger 不看内容）
- **audit_expectation：** `.jsonl` present 须 ≥1 非空行；`.json` present 须 size>2；否则 audit 计 missing
- **offline_action：** 逐源 `_source_present` 等价离线复算；写入 source_ledger
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-005 · 双层对齐 — 标准 complete

- **ledger_expectation：** complete（10/10 文件存在）
- **audit_expectation：** complete（`status_csv_complete_sources_ok`）
- **offline_action：** 无 caveat；计入 audit complete 190 家
- **requires_snapshot：** false（snapshot 仍 blocked）
- **requires_live：** false

---

## 规则族 B — Partial7（applies_to: partial）

**case_id：** CE1E002, CE1E003, CE1E034, CE1E061, CE1E067, CE1E070, CE1E071

**caveat_class：** `delisted_or_merged_partial_normalized`

### DLVR-P01 · Partial 双层一致

- **ledger_expectation：** `partial`（4/10 normalized）
- **audit_expectation：** `partial`（`status_csv_partial`）
- **offline_action：** 打包 raw 6×`http_error`/500 + security_observe `delisted=true`；引用 partial7 offline matrix
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-P02 · 退市/合并 HTTP 失败可接受

- **ledger_expectation：** partial 不因 raw 500 自动升为 missing
- **audit_expectation：** partial；live 建议 `deferred_targeted_live_after_approval`
- **offline_action：** 记录 `business_code=9240002`；disposition=`accept_with_caveat`；**不**建议 re-live
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-P03 · Partial 不得冒充 complete

- **ledger_expectation：** 禁止将 4/10 标为 complete
- **audit_expectation：** 禁止将 partial 标为 complete
- **offline_action：** 校验 ledger/audit/reconcile 三处一致；违规标 `FAIL_REVIEW_REQUIRED`
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-P04 · Partial snapshot 排除

- **ledger_expectation：** partial 不计入 snapshot complete 候选
- **audit_expectation：** partial 保持 `deferred_targeted_live_after_approval` 或 hold
- **offline_action：** 在 snapshot planning 清单中显式排除 7 家；`approved_for_snapshot_rebuild=false`
- **requires_snapshot：** false（规则本身不要求 snapshot；snapshot 仍 blocked）
- **requires_live：** false

---

## 规则族 C — Empty-Dividend（applies_to: empty_dividend）

**case_id：** CE1E176, CE1E188, CE1E193

**caveat_class：** `empty_but_valid_dividend_normalized_zero_byte`

### DLVR-E01 · 合法双层分歧（核心规则）

- **ledger_expectation：** `complete`（10/10 文件存在，含 0 字节 dividend）
- **audit_expectation：** `needs_review`（`status_csv_complete_but_source_gap`；audit 仅 9/10 present）
- **offline_action：** 文档化分歧为 **质量层 caveat**，**禁止** 因 audit needs_review 翻转 ledger harvest_status
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-E02 · Raw valid_empty 旁证

- **ledger_expectation：** complete 维持；raw dividend `retrieval_status=valid_empty` · `http_status=200` · `raw_records=[]`
- **audit_expectation：** needs_review 维持；source_ledger dividend_history=no/missing（按内容判定）
- **offline_action：** 打包 raw valid_empty JSON + 零字节 normalized 路径 + audit/ledger 交叉引用
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-E03 · 活跃 STAR 标的区分

- **ledger_expectation：** complete；`security_observe.delisted=false`
- **audit_expectation：** needs_review（非退市 partial 模式）
- **offline_action：** 与 partial7 `delisted=true` 模式区分；disposition=`accept_with_caveat`
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-E04 · 禁止 live retry

- **ledger_expectation：** complete 不因 audit 降为 partial
- **audit_expectation：** needs_review；live 建议 `offline_review_first`
- **offline_action：** 引用 caveat_ledger「no re-live」；无 Controller 批准不得 CNINFO
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-E05 · Audit 语义分歧登记

- **ledger_expectation：** dividend 文件存在（0 字节）→ sources_present
- **audit_expectation：** dividend 无有效行 → missing
- **offline_action：** 在规则矩阵与 evidence 包中显式登记「audit vs ledger 语义不一致」为已知 caveat，非数据错误
- **requires_snapshot：** false
- **requires_live：** false

---

## 规则族 D — 跨家族治理（applies_to: both）

### DLVR-G01 · Caveat disposition 统一

- **ledger_expectation：** 保持 closure 重建结果（193 complete / 7 partial / 0 missing）
- **audit_expectation：** 保持 closure audit 结果（190 complete / 7 partial / 3 needs_review）
- **offline_action：** 10 家 caveat 全部 `disposition=accept_with_caveat`；gate=`PASS_WITH_CAVEAT`
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-G02 · 禁止 bare PASS 升级

- **ledger_expectation：** 不因 complete 计数高而消除 caveat
- **audit_expectation：** needs_review/partial 不得静默忽略
- **offline_action：** 禁止标 `verified` / `production_ready` / bare `PASS`
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-G03 · Snapshot 审批隔离

- **ledger_expectation：** N/A
- **audit_expectation：** N/A
- **offline_action：** `approved_for_snapshot_rebuild=false` 保持不变；本规则包不触发 snapshot rebuild
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-G04 · Harvest success ≠ production readiness

- **ledger_expectation：** complete/partial 仅表检索结果
- **audit_expectation：** resume_state 表质量/eligibility
- **offline_action：** 下游须同时读取两层；单层 complete 不得单独用于 production bundle
- **requires_snapshot：** false
- **requires_live：** false

### DLVR-G05 · 未映射 status 兜底

- **ledger_expectation：** 未知 `harvest_status` 值
- **audit_expectation：** `needs_review`（`unmapped_status_csv=...`）
- **offline_action：** 人工复核；不自动 live
- **requires_snapshot：** false
- **requires_live：** false

---

## 分歧判定速查

| 模式 | ledger | audit | 合法？ | disposition |
|------|--------|-------|--------|-------------|
| 标准 complete | complete | complete | 是 | 无 caveat |
| partial7 | partial | partial | 是 | accept_with_caveat |
| empty-dividend | complete | needs_review | **是（预期分歧）** | accept_with_caveat |
| complete→audit gap（非 valid_empty） | complete | needs_review | 需复核 | 待 Evidence Auditor |
| partial 标 complete | partial | complete | **否** | FAIL_REVIEW_REQUIRED |
| complete 标 partial（10/10 存在） | complete | partial | **否** | FAIL_REVIEW_REQUIRED |

---

## 机器可读规则矩阵

[cninfo_c_class_dual_layer_rule_matrix_20260714.csv](cninfo_c_class_dual_layer_rule_matrix_20260714.csv)

---

## 影响说明

本规则包 **不改变** closure gate、harvest 产物、`company_harvest_status.csv` 或 snapshot 审批状态。其核心贡献是：**正式文档化** status-ledger 与 resume-audit 的双层语义边界，尤其 empty-dividend 三案中 ledger `complete` 与 audit `needs_review` 的 **合法、不可互翻** 分歧；以及 partial7 七案中双层 `partial` 的 **一致对齐**。10 家 caveat 仍计入 slice1 `PASS_WITH_CAVEAT`；`approved_for_snapshot_rebuild` **保持 false**。下游（Evidence Auditor、Controller、snapshot planning）应联立读取两层状态，禁止以单层 complete 冒充 production readiness。可选后续（需另批）：runner/audit 对 zero-byte normalized 的 present 语义对齐实现。

---

## Gates

```
c_class_erad_fuller_market_slice1_qa_closure_gate = PASS_WITH_CAVEAT（未变）
approved_for_snapshot_rebuild = false（未变）
dual_layer_validation_rules_gate = RULES_COMPLETE
```

**NOT verified** · **NOT production_ready** · snapshot **blocked**

---

## 安全确认

| 项 | 状态 |
|----|------|
| CNINFO 调用 | **0** |
| live 执行 | **未执行** |
| harvest root 变更 | **无** |
| caveat10 registry 重做 | **无** |
| snapshot | **未创建** |
| 其他 track | **未触碰** |

---

## 产出物

| 文件 | 说明 |
|------|------|
| `cninfo_c_class_dual_layer_validation_rules_20260714.md` | 本规则文档 |
| `cninfo_c_class_dual_layer_rule_matrix_20260714.csv` | 规则矩阵（机器可读） |

---

## 下一步建议

Evidence Auditor 核验规则矩阵行与 closure 计数、partial7/empty-dividend 矩阵一致后，Controller 可将双层规则登记入 PROJECT_CONTROL；snapshot rebuild 仍须单独批准。
