# CNINFO A 类 Phase 2 Metadata Expansion Plan

_生成时间：2026-07-09_

> **性质：** Phase 1 boundary 收口后的 20 家公司 metadata 扩大规划；**离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 1 boundary commit：** `2f1f342` — Close A-class Phase 1 metadata validation with caveat

---

## 1. Phase 1 Recap

| 项 | 值 |
|----|-----|
| boundary gate | `a_class_phase1_boundary_gate = PASS_WITH_CAVEAT` |
| freeze v1 gate | `a_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE` |
| ready-case benchmark | `a_class_ready_case_benchmark_gate = READY_FOR_REVIEW` · **5/5 PASS** |
| tiny live v2 | `a_class_tiny_live_metadata_v2_execution_gate = PASS_WITH_CAVEAT` |
| v2 closure | `a_class_phase1_tiny_live_metadata_v2_closure_gate = PASS_WITH_CAVEAT` |
| cases / success / failed | **5 / 5 / 0** |
| wrong_report_type | **0** |
| title_match_pass / period_match_pass | **5 / 5** |
| PDF download / parse | **0 / 0** |
| DB / MinIO / RAG | **0** |
| verified / production_ready | **false / false** |

Phase 1 在极小样本（5 家）上验证了 A-class 定期报告 metadata 检索路径、v2 标题/期间匹配策略与输出隔离纪律，但样本量不足以支撑板块分布、失败率统计或 report-type 交叉覆盖结论。

---

## 2. v1 Caveats and v2 Fix Recap

### v1 caveats（已记录）

| case | 问题 |
|------|------|
| ALM001 / ALM005 | annual 请求匹配到 semi-annual 标题 |
| ALM003 | company_code 与 company_name 不一致（688001 ≠ 华熙生物） |
| ALM004 | 英文 Q3 标题未被拒绝 |

### v2 fix（已离线完成并 rerun）

| 项 | 内容 |
|----|------|
| universe v2 | ALM003 → **华兴源创** |
| matching v2 | report-type 专用 `match_title_for_report_type()` · `ENGLISH_TITLE_REJECT` |
| matching tests | **10/10 PASS** |
| v2 rerun | **5/5** correct · wrong_report_type=**0** |

**Phase 2 必须沿用 v2 matching policy**，不得回退 v1 宽松标题匹配。

---

## 3. Why Phase 2 Is Needed

1. **样本代表性不足：** Phase 1 仅 5 家，无法覆盖 SSE/SZSE 主板、创业板、科创板及金融/消费/制造/科技等行业组合。
2. **report-type 交叉覆盖不足：** Phase 1 各类型仅 1–2 家；需在更大样本上验证 annual / semi-annual / Q1 / Q3 四类 metadata 路径。
3. **v2 matching 未在多样本压测：** v2 修复仅在 5 家验证；20 家可观察 English 标题拒绝、report-type 互斥过滤在更多板块上的稳定性。
4. **失败模式未充分观测：** 需在更大批次观察 CNINFO 瞬时错误、空响应、标题歧义等分布，但不进入 PDF 阶段。
5. **仍不进入 PDF 层：** Phase 2 继续 metadata-only，为后续 harvest/parse 提供更大证据基础，但不宣称 production readiness。

---

## 4. Expansion Objective

在 **phase1_freeze_v1 schema 不变** 的前提下，将 live metadata validation 样本从 5 扩大至 **20 家公司**（A2M001–A2M020），目标：

- 验证 v2 标题/期间匹配在更多公司与板块上的稳定性
- 积累 annual / semi-annual / Q1 / Q3 四类 report-type 的 metadata 检索分布
- 建立 Phase 2 专用输出隔离根与 rate limit / resume 运行纪律
- **不**下载 PDF · **不**解析 · **不**写 DB/MinIO/RAG · **不**标 verified

---

## 5. Recommended Phase 2 Size

| Option | 公司数 | 说明 | 本回合 |
|--------|--------|------|--------|
| **A（推荐）** | **20** | 最小有意义扩大；约 4× Phase 1；便于人工审阅 universe | **已准备 draft** |
| B | 50 | 中等扩大；可初步观察板块失败率 | **本回合不推荐** |
| C | 100 | 较大扩大；接近小规模压测 | **本回合不推荐** |

**推荐从 Option A（20）起步。** 理由：

- Phase 1 v2 虽 5/5 成功，但 matching 逻辑变更后需在多样本上再观测
- 20 家足以覆盖 12 个 bucket 组合，人工 triage 成本可控
- 50 家在未观测 Phase 2 失败率前，retry 与人工审阅成本偏高

---

## 6. Report-type Coverage Strategy

| report_type | 目标 case 数 | 说明 |
|-------------|-------------|------|
| `annual_report` | **~8** | SSE/SZSE 主板蓝筹 + 金融 + 消费；验证「年度报告」专用过滤 |
| `semi_annual_report` | **~4** | 主板/创业板；验证「半年度报告」专用过滤 |
| `quarterly_report_q1` | **~4** | 科创板/主板；验证 Q1 标题变体（一季度/第一季度/Q1） |
| `quarterly_report_q3` | **~4** | 创业板/科创板/主板；验证 Q3 标题变体；重点观测 English 拒绝 |

**合计：20 家，每家公司仅 1 个 report_type case。**

---

## 7. Title / Period Matching Policy

沿用 Phase 1 v2 matching logic（`MATCHING_LOGIC_VERSION = "v2"`）：

### annual_report

- **must include：** `年度报告`
- **must reject：** `半年度报告` · `一季度报告` · `三季度报告` · `英文` · `English`

### semi_annual_report

- **must include：** `半年度报告`
- **must reject：** `英文` · `English`

### quarterly_report_q1

- **must include：** `一季度报告` OR `第一季度报告` OR `Q1`
- **must reject：** `英文` · `English`

### quarterly_report_q3

- **must include：** `三季度报告` OR `第三季度报告` OR `Q3`
- **must reject：** `英文` · `English`

### period matching

- `expected_period` 与公告 `announcementTime` 派生期间比对
- 年报 → `YYYY-12-31`；半年报 → `YYYY-06-30`；Q1 → `YYYY-03-31`；Q3 → `YYYY-09-30`

### company code / name validation

- 执行前 `validate_universe_code_name()` 校验 code↔name 一致性
- 禁止人工 identity review 占位 case

---

## 8. Quality Policy

| 维度 | 规则 |
|------|------|
| title_match_status | `pass` · `fail` · `not_found` |
| period_match_status | `pass` · `fail` · `not_found` |
| wrong_report_type | 匹配到错误 report-type 标题 → **hard fail** |
| English title | 含 English/英文 → **reject** |
| quality_status | `pass` · `needs_review` · `caveat` |
| acceptable threshold（规划） | wrong_report_type=**0** 为硬门槛；其余 caveat 可记录但不自动 PASS |

**不写 verified。** **不升级 testing_stable_sample。**

---

## 9. Failure Handling

| 失败类型 | 处理 |
|----------|------|
| CNINFO 瞬时网络错误 | 单 case 隔离 retry（最多 1 次）；失败记 `network_error` |
| empty_response | 记 `not_found`；不自动换公司 |
| wrong_report_type | 记 hard fail；纳入 quality report |
| title_match fail | 记 `needs_review`；不阻断批次 |
| period_match fail | 记 `needs_review` |
| rate limit | runner 内置 sleep；不并发轰炸 CNINFO |

**不发明 company code。** **不覆盖 Phase 1 产物。**

---

## 10. Output Isolation

**专用输出根（强制）：**

```text
outputs/validation/cninfo_a_class_phase2_metadata_expansion/
```

建议子路径：

```text
outputs/validation/cninfo_a_class_phase2_metadata_expansion/
  reports/
    a_class_phase2_metadata_expansion_report.csv
    a_class_phase2_metadata_expansion_summary.md
    a_class_phase2_metadata_expansion_quality_report.csv
  raw_metadata/
    A2M001.json … A2M020.json
```

**禁止写入：**

- `outputs/validation/cninfo_a_class_tiny_live_metadata/`（Phase 1）
- `outputs/harvest/cninfo_c_class/`
- `outputs/snapshot/`

---

## 11. Approval Requirements

| 项 | 要求 |
|----|------|
| Phase 1 boundary | 已 review（`PASS_WITH_CAVEAT`） |
| v2 matching policy | 已 review |
| 20-company universe | 人工审阅 CSV |
| report-type mix | 人工确认 ~8/4/4/4 |
| output root | 确认隔离 |
| explicit user approval | **`--approve-a-class-phase2-metadata-expansion`** |
| runner extension | Phase 2 runner 扩展 **未实现**（本回合仅规划） |

**Gate（本回合）：** `a_class_phase2_metadata_planning_gate = READY_FOR_APPROVAL`

**不是 PASS。** **不是 live_ready。** **不是 verified。**

---

## 12. Risks

| 风险 | 级别 | 缓解 |
|------|------|------|
| v2 matching 在多样本失效 | medium | 20 家分类型覆盖；quality report 分 report-type 统计 |
| English 标题漏拒 | medium | 沿用 `ENGLISH_TITLE_REJECT`；Q3 bucket 重点观测 |
| CNINFO rate limit | low–medium | sleep + 串行执行 |
| company code/name 错误 | low | `validate_universe_code_name()` 预检 |
| 与 Phase 1 样本重复 | low | universe draft 避开 ALM001–ALM005 公司代码 |
| 过早扩大至 50 | medium | 本回合仅推荐 20；50 待 Phase 2 结果后再议 |

---

## 13. Scope Boundary

### In scope

- metadata retrieval（CNINFO 公告列表 API）
- report_document · report_period_snapshot · document_lineage 字段登记
- v2 title/period matching
- pdf URL lineage 登记（**不下载**）

### Out of scope

- PDF download / parse / OCR / section extraction
- DB / MinIO / RAG / embeddings
- verified / production_ready / testing_stable_sample
- schema freeze v1 修改
- BSE legacy · ST / *ST · 退市 · manual identity review

---

## 14. Artifacts（本回合）

| 项 | 路径 |
|----|------|
| expansion plan | 本文档 |
| candidate universe design | [cninfo_a_class_phase2_candidate_universe_design.csv](../outputs/validation/cninfo_a_class_phase2_candidate_universe_design.csv) |
| universe draft | [cninfo_a_class_phase2_metadata_universe_draft.csv](../outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv) |
| command draft | [cninfo_a_class_phase2_metadata_command_draft.md](cninfo_a_class_phase2_metadata_command_draft.md) |
| approval checklist | [cninfo_a_class_phase2_metadata_approval_checklist.md](../outputs/validation/cninfo_a_class_phase2_metadata_approval_checklist.md) |
| approval summary | [cninfo_a_class_phase2_metadata_approval_summary.md](../outputs/validation/cninfo_a_class_phase2_metadata_approval_summary.md) |

**CNINFO calls（本回合）：** **0**
