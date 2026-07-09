# CNINFO A 类 Phase 2 Network Recovery Retry Recommendation

_生成时间：2026-07-09_

> **性质：** Phase 2 closure 后未来路径建议；**未执行** · **不是 verified**

**Current closure gate：** `a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**Unresolved cases：** A2M005 · A2M010 · A2M011 · A2M012 · A2M013 · A2M018 · A2M019 · A2M020

---

## Context

- Phase 2 original live: **12/20** accepted
- Isolated retry: **0/8** — all orgId network_error
- wrong_report_type: **0** on all retrievable cases
- Schema / matching: **unchanged**

---

## Option A: Network Recovery Retry（推荐）

等待网络恢复后，仅 rerun **8 unresolved cases**。

| 项 | 内容 |
|----|------|
| universe | [cninfo_a_class_phase2_failed_retry_universe.csv](../outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv)（不变） |
| output root | `outputs/validation/cninfo_a_class_phase2_metadata_retry/` 或新 v2 根 |
| approval | `--approve-a-class-phase2-failed-retry` |
| scope | metadata only · 无 PDF |
| successful 12 | **不重跑** |

**优点：** 最小增量 · 保留 12 accepted baseline

---

## Option B: Retry v2 Isolated Output Root

网络恢复后使用新隔离根：

```text
outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/
```

| 项 | 内容 |
|----|------|
| universe | 同上 8 cases |
| 目的 | 与 retry v1（network outage）报告并存 · 审计清晰 |
| approval | 新 flag 或复用 `--approve-a-class-phase2-failed-retry` + v2 path |

**优点：** 不覆盖 v1 retry 产物 · 便于对比 network outage vs recovery

---

## Option C: Hold Closure with Network Caveat

接受 closure gate `PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`，暂不 rerun 8 cases，不进入 Phase 3 expansion。

| 项 | 内容 |
|----|------|
| accepted | 12/20 metadata validated |
| caveat | 8/20 network unresolved |
| expansion | **hold** |

**优点：** 无额外 CNINFO · 文档边界清晰

**缺点：** 8 cases 永久 unresolved 直至未来决策

---

## Recommendation

**推荐 Option A 或 B** 于网络恢复后执行，**在 Phase 3 任何 expansion 之前**。

**不推荐** 50-company expansion 直至：

1. 8 unresolved cases 重试成功，或
2. 人工正式接受 8/20 为 permanent network caveat

---

## Red Lines（所有 Option）

- No successful 12 rerun
- No PDF download / parse
- No DB / MinIO / RAG
- No verified / production_ready
- No schema / matching change without new evidence

---

## Gate After Future Retry（规划）

若 recovery retry ≥6/8 correct 且无 red-line：

```text
a_class_phase2_network_recovery_retry_execution_gate = PASS_WITH_CAVEAT
```

合并后可能更新 closure gate — **本回合不执行**。
