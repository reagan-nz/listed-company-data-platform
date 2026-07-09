# CNINFO B 类 Phase 2 Expansion Plan

_生成时间：2026-07-09_

> **性质：** Phase 1 tiny live 收口后的扩大样本规划；**离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

---

## 1. Phase 1 Recap

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| cases | **5**（TLC001–TLC005） |
| resolved | **5** |
| failed | **0** |
| schema | phase1_freeze_v1 · **15** required fields |
| validated endpoints | EP001 · EP002 · EP004 · EP005 |
| TLC002 | 初始 `network_error`（EP002 orgId）→ isolated retry → `found/pass/discovered` |
| PDF download / parse | **0** |
| DB / MinIO / RAG | **0** |
| verified | **false** |
| production_ready | **false** |

Phase 1 证明了 metadata-only live 路径在极小样本上可行，但样本量不足以支撑板块覆盖、失败率统计或 endpoint 稳定性结论。

---

## 2. Why Phase 2 Is Needed

1. **样本代表性不足：** Phase 1 仅 5 家，无法覆盖主板/创业板/科创板/金融/消费/制造等组合分布。
2. **失败模式未充分观测：** TLC002 表明 EP002 存在瞬时网络失败；需在更大样本上观察 transient error 频率与隔离 retry 策略是否足够。
3. **endpoint 组合未压测：** EP001+EP004 与 EP001+EP005 路径在 Phase 1 各覆盖有限；需扩大以验证检索窗口、orgId 辅助、category routing 的一致性。
4. **仍不进入 PDF 阶段：** Phase 2 继续 metadata + pdf URL lineage only，为后续 harvest/parse 提供更大证据基础，但不宣称 production readiness。

---

## 3. Expansion Objective

在 **phase1_freeze_v1 schema 不变** 的前提下，将 live metadata validation 样本从 5 扩大至人工批准的规模（见 §5），目标：

- 验证 EP001 / EP002 / EP004 / EP005 在更多公司与板块上的 metadata 检索稳定性
- 积累 `quality_status` / `lineage_status` 分布（pass · needs_review · caveat）
- 建立 Phase 2 专用输出隔离根与 resume/retry 运行纪律
- **不**下载 PDF · **不**解析 · **不**写 DB/MinIO/RAG · **不**标 verified

---

## 4. Scope Boundary

### In scope（允许）

- metadata retrieval（CNINFO 公告列表 API 响应）
- announcement lineage（id · title · time · date · category）
- pdf URL lineage（`adjunctUrl` → `pdf_url` / `adjunct_url` 登记；**不下载**）
- EP002 orgId 辅助解析（单次尝试；失败则 `needs_review`）
- quality flags：`pass` · `needs_review` · `caveat`

### Out of scope（禁止）

- PDF download / parse / OCR / text extraction
- harvest 写入 `outputs/harvest/`
- DB / MinIO / RAG / embeddings
- verified / testing_stable_sample 升级
- production registry 状态更新
- schema freeze v1 字段或 endpoint catalog 修改
- 触碰 `outputs/harvest/cninfo_c_class/` 及 C-class snapshot 产物
- BSE legacy universe
- ST / *ST / 退市 / manual identity review 样本

---

## 5. Sample Size Options

| Option | 公司数 | 说明 | 风险 |
|--------|--------|------|------|
| **A** | **20** | 最小有意义扩大；约 4× Phase 1；便于人工审阅 universe | low–medium |
| **B** | **50** | 中等扩大；可初步观察板块与 endpoint 失败率 | medium |
| **C** | **100** | 较大扩大；接近小规模压测 | medium–high |

**本回合不自动选定规模。** 须人工在批准包中勾选 Option A / B / C。

### Recommendation（非决定）

鉴于 Phase 1 出现 **1 次 EP002 瞬时网络错误**（TLC002，已通过 isolated retry 恢复），建议 **从 Option A（20）或 Option B（50）起步，暂不直接上 Option C（100）**。理由：

- transient network error 在更大并发/更长批次中可能复现
- 需先验证 Phase 2 runner 的 rate limit · resume · isolated retry 纪律
- 100 家在未观测 Phase 2 失败率前，retry 与人工 triage 成本偏高

已准备 **20 家公司** universe draft 供审阅；若批准 Option B/C，可在同 bucket 规则下扩展 CSV。

---

## 6. Endpoint Strategy

沿用 Phase 1 freeze v1 endpoint catalog，**不新增 endpoint**：

| ID | name | Phase 2 角色 |
|----|------|----------------|
| EP001 | hisAnnouncement/query | 主公告列表检索（periodic + general） |
| EP002 | topSearch/query | orgId 发现辅助（金融/大型样本优先覆盖） |
| EP004 | cninfo_periodic_report_pdf | 定期报告 metadata + pdf URL lineage |
| EP005 | cninfo_general_announcement_pdf | 一般公告 metadata + pdf URL lineage |

**排除：** EP003 removed · EP006/EP007 deferred

**执行顺序（每 case）：** EP002（若 universe 要求）→ EP001 → EP004 或 EP005（按 `announcement_type`）

---

## 7. Quality Policy

对齐 Phase 1 freeze v1 与 tiny live 执行口径：

| 场景 | quality_status | lineage_status |
|------|----------------|----------------|
| 必填字段齐全 · 单条明确匹配 | `pass` | `discovered` |
| pdf_url 缺失 | `needs_review` | `needs_review` |
| 多候选 announcement_id | `needs_review` | `discovered`（`dedup_decision_required=true`） |
| unknown category | `caveat` | `discovered`（`category_status=review_later`） |
| network_error / http_429 | `needs_review` | `needs_review` |
| orgId 缺失且 EP002 失败 | `needs_review` | `needs_review` |

**禁止：** 将任何 case 标为 `verified` 或升级 `testing_stable_sample`。

---

## 8. Failure Handling

| 失败类型 | 处理 |
|----------|------|
| `empty_response` | 记录 `needs_review`；继续下一 case |
| `network_error` | 停止当前 case；写入报告；**不**全局 retry storm |
| `http_429` | **全局停止**；报告 `rate_limited` |
| `org_id_missing` | EP002 单次；失败则 `needs_review`（不猜测 orgId） |
| `pdf_url_missing` | `needs_review`（对齐 RC003） |
| `duplicate_announcement_id` | 保留多候选 · `dedup_decision_required=true`（对齐 RC004） |
| `unknown_category` | `review_later`（对齐 RC005） |

批次结束后产出 failure summary；按 case 分类决定是否 **isolated retry**（见 §9）。

---

## 9. Retry Policy

1. **默认：** Phase 2 主批次 **不**自动 inline retry；失败 case 写入 `run_status.csv`。
2. **isolated retry：** 仅对 triage 判定为 `transient_network_error` 的 case，经 **人工批准** 后，使用独立输出根（类似 TLC002 retry），**禁止**覆盖主批次 baseline。
3. **禁止：** 失败后立即全量重跑；禁止与 C-class live harvest 并发。
4. **TLC002 教训：** EP002 orgId 阶段 network_error 可恢复；Phase 2 须记录 failure stage（EP002 vs EP001 vs EP004/EP005）。

---

## 10. Output Isolation

**Phase 2 专用输出根（强制）：**

```text
outputs/validation/cninfo_b_class_phase2_expansion/
```

建议结构：

```text
outputs/validation/cninfo_b_class_phase2_expansion/
  raw_metadata/
  quality/
  reports/
  run_status.csv
```

**隔离要求：**

- **禁止**写入 Phase 1 tiny live 根 `cninfo_b_class_tiny_live_validation/`
- **禁止**写入 TLC002 retry 根 `cninfo_b_class_tlc002_retry/`
- **禁止**写入 `outputs/harvest/`
- isolated retry（若未来批准）使用 `cninfo_b_class_phase2_expansion_retry/` 或 case 级子目录

---

## 11. Approval Requirements

执行 Phase 2 live expansion 前须满足：

| # | 要求 |
|---|------|
| 1 | Phase 1 closure gate = `PASS_WITH_CAVEAT` 已审阅 |
| 2 | TLC002 failure + isolated retry 已理解 |
| 3 | 样本规模（Option A/B/C）**人工批准** |
| 4 | [universe draft](../outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv) 已审阅 |
| 5 | [approval checklist](../outputs/validation/cninfo_b_class_phase2_expansion_approval_checklist.md) 全勾选 |
| 6 | runner 扩展 + `--approve-b-class-phase2-expansion` 已实现（未来回合） |
| 7 | C-class Phase 3 harvest **未并发** |
| 8 | 用户显式批准 live execution |

**当前 gate：**

```text
b_class_phase2_expansion_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 12. Related Artifacts

| 文档 | 路径 |
|------|------|
| candidate universe design | [cninfo_b_class_phase2_candidate_universe_design.csv](../outputs/validation/cninfo_b_class_phase2_candidate_universe_design.csv) |
| 20-company universe draft | [cninfo_b_class_phase2_expansion_universe_draft.csv](../outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv) |
| command draft | [cninfo_b_class_phase2_expansion_command_draft.md](cninfo_b_class_phase2_expansion_command_draft.md) |
| approval checklist | [cninfo_b_class_phase2_expansion_approval_checklist.md](../outputs/validation/cninfo_b_class_phase2_expansion_approval_checklist.md) |
| approval summary | [cninfo_b_class_phase2_expansion_approval_summary.md](../outputs/validation/cninfo_b_class_phase2_expansion_approval_summary.md) |
| Phase 1 closure review | [cninfo_b_class_phase1_tiny_live_closure_review.md](cninfo_b_class_phase1_tiny_live_closure_review.md) |

---

## 13. Red Lines

- No CNINFO in this planning round
- No live execution in this planning round
- No TLC002 retry in this planning round
- No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No C-class / A-class / D-class output modification
