# CNINFO D 类 Known Event Replacement — Live Failure Review

_生成时间：2026-07-09_

> **性质：** 离线 failure review only · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified**

**关联 gate：** `d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED`

---

## 1. Objective

评审 isolated replacement live 执行结果，说明为何 DLC003R/DLC006R 在人工披露证据存在的情况下仍返回 `empty_but_valid_after_budget`，并为是否设计 event-date targeted probe extension 准备决策包。

**本评审不：** 将人工披露等同于 live `captured_normal` · 升级 execution gate · 标记 verified。

---

## 2. Candidate Recap

| slot | replaces | company | component | expected_behavior |
|------|----------|---------|-----------|-------------------|
| DLC003R | DLC003 | 688671 碧兴物联 | restricted_shares_unlock | captured_normal |
| DLC006R | DLC006 | 301259 艾布鲁 | shareholder_change | captured_normal |

Intake：`HUMAN_CANDIDATE_VALIDATED` · intake **24/24 PASS**

---

## 3. Human Disclosure Evidence Recap

### DLC003R

| 项 | 值 |
|----|-----|
| event_date | **2024-02-19** |
| evidence_type | `unlock_schedule_record`（原始：CNINFO 限售股上市流通公告） |
| description | 碧兴物联披露《首次公开发行网下配售限售股上市流通公告》，上市流通总数 1,096,372 股 |
| source_reference | CNINFO finalpage 2024-02-01 / 1219054224.PDF |
| human_provided | true |

### DLC006R

| 项 | 值 |
|----|-----|
| event_date | **2024-07-16** |
| evidence_type | `shareholder_change_announcement`（原始：CNINFO 简式权益变动报告书） |
| description | 艾布鲁披露《简式权益变动报告书（一）》，正诚2号持股变动，不再是 5% 以上股东 |
| source_reference | CNINFO finalpage 2024-07-16 / 1220653628.PDF |
| human_provided | true |

**性质：** 人工内部披露记录 · **非** live metadata 探针命中 · **非** web 抓取

---

## 4. Live Execution Recap

| 项 | 值 |
|----|-----|
| command mode | `--known-event-replacement --live` |
| approval flag | `--approve-d-class-known-event-replacement-validation`（人工已提供） |
| universe | [filled replacement universe](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv) |
| output root | `cninfo_d_class_known_event_replacement_validation/` |
| probe strategy | v2-style bounded probe（`build_bounded_probe_plan_dlc003` / `build_bounded_probe_plan_dlc006`） |
| total CNINFO | **40** |
| baseline CNINFO | **0**（DLC001/002/004/005/007 reference_only） |
| PDF/OCR/extraction | **0** |
| DB/MinIO/RAG | **0** |

---

## 5. Per-Case Result

| case | requests | retrieval | records | acceptable | failure_type |
|------|----------|-----------|---------|------------|--------------|
| DLC003R | 21 | empty_but_valid | 0 | **no** | empty_but_valid_after_budget |
| DLC006R | 19 | empty_but_valid | 0 | **no** | empty_but_valid_after_budget |

Endpoints used：

- DLC003R：`liftBan/detail`（restricted_shares_unlock）
- DLC006R：`shareholeder/detail`（shareholder_change）

---

## 6. Why Both Cases Are Not Acceptable

Replacement live 可接受标准（实现契约）：

- `captured_normal`：`found` + `record_count ≥ 1`，或
- caveat：`needs_review` + 明确记录证据

实际结果：

- 两 case 均在预算内耗尽探针后 **company-level 零行**
- `acceptable = no` · `failure_type = empty_but_valid_after_budget`
- **2/2 replacement probe cases failed**

因此 execution gate 保持 **`FAIL_REVIEW_REQUIRED`** — **不得**升级为 `PASS_WITH_CAVEAT`。

---

## 7. Why `empty_but_valid_after_budget` Is Not Schema Failure

| 事实 | 含义 |
|------|------|
| HTTP 响应可解析 | 非 `schema_error` |
| `quality_status = pass` | 质量策略口径正确 |
| `lineage_status = discovered` | 端点可达 |
| `record_count = 0` | 公司级过滤后零行 — **合法空态** |

这是 **metadata/event 探针与已知事件日未对齐** 或 **端点索引行为不包含该事件形态** 的问题，**不是** schema freeze 缺陷。

---

## 8. Why Human Evidence ≠ Component-Level `captured_normal`

| 证据类型 | 可证明什么 | 不可证明什么 |
|----------|------------|--------------|
| 人工披露（PDF finalpage 记录） | 该公司历史上存在披露事件 | D-class metadata 端点可返回结构化行 |
| Live metadata probe | 端点在公司级过滤下可捕获行 | 披露 PDF 内容本身 |

**规则：** 人工披露证据 **不得** 推断 `component_level_captured_normal = yes` · **不得** 将 execution gate 标为 PASS。

组件级 `captured_normal` live 证据对 `restricted_shares_unlock` · `shareholder_change` **仍 outstanding**。

---

## 9. Why Old DLC003/DLC006 Should Not Be Rerun

| case | 状态 | 依据 |
|------|------|------|
| DLC003 (300009) | `empty_but_valid` · human_signed_off | v1+v2 bounded probe 已耗尽 |
| DLC006 (000550) | `empty_but_valid` · human_signed_off | v1+v2 bounded probe 已耗尽 |

Rerun 旧 case **不解决** replacement 轨道问题，且违反 Option A 校准 signoff 边界。

---

## 10. Why Full Tiny-Live Should Not Be Rerun

- Phase 1 tiny-live 已收口（`PASS_WITH_CAVEAT`）
- Replacement 轨道是 **并行补证**，非全 universe 重跑
- Full rerun 引入 scope creep · 可能 mutate v1 执行叙事

---

## 11. Red-Line Confirmations

| 项 | 本回合 |
|----|--------|
| CNINFO calls | **0** |
| live / rerun | **0** |
| old DLC003/DLC006 rerun | **no** |
| replacement live reports mutation | **no** |
| original / calibrated universe | **untouched** |
| v1/v2 execution reports | **untouched** |
| PDF/OCR/extraction/DB/MinIO/RAG | **0** |
| verified / production_ready | **no** |

---

## 12. Next Decision Options

| 选项 | 说明 | 推荐阶段 |
|------|------|----------|
| **Option A** | Event-date targeted probe extension 规划包 | **推荐优先** |
| **Option B** | 接受组件级证据缺口 + 人工 signoff | 需显式人工决策 |
| **Option C** | Hold replacement 轨道直至端点行为更清晰 | 保守 |

**推荐：** Option A planning package first — **not live** · **not implementation**

---

## 13. Gate

```text
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
d_class_known_event_replacement_live_failure_review_gate = READY_FOR_HUMAN_DECISION
```

**不是 PASS** · **不是 verified** · **不是 production_ready**
