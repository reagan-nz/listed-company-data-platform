# CNINFO A 类 Phase 2 Post-Retry v2 Next Step Recommendation

_生成时间：2026-07-09_

> **性质：** retry_v2 closure 后路径建议；**未执行** · **不是 verified**

**Current closure gate：** `a_class_phase2_retry_v2_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**Effective state：** 12 accepted · 8 unresolved (`unresolved_network_orgid_failure`)

---

## Context

| 轮次 | 结果 |
|------|------|
| original Phase 2 | 12/20 accepted |
| retry v1 | 0/8 · CNINFO 0 |
| retry v2 | 0/8 · CNINFO 0 |
| wrong_report_type | 0 |

Schema / matching：**unchanged** · **no change recommended**

---

## Option A: Network Recovery + retry_v3 Package

网络恢复后，为相同 **8 case** 准备 isolated retry_v3 包（新输出根）。

| 项 | 内容 |
|----|------|
| universe | 同 8 unresolved cases |
| scope | metadata only · 无 PDF |
| successful 12 | **不重跑** |

**前提：** Option B precheck 通过

---

## Option B: CNINFO Reachability Precheck（推荐优先）

在任意 retry_v3 live 之前，增加人工/脚本 CNINFO reachability precheck：

- topSearch endpoint 可达
- orgId resolution 对 1–2 probe company 成功
- 记录 precheck 时间戳与结果

| 项 | 内容 |
|----|------|
| 目的 | 避免 v1/v2 类零 CNINFO 空跑 |
| 时机 | **before** retry_v3 approval |

**推荐：Option B before Option A**

---

## Option C: Formal Permanent Network Caveat Signoff

人工 signoff 接受 8 case 为 permanent `unresolved_network_orgid_failure`。

| 项 | 内容 |
|----|------|
| effective accepted | 12/20 固定 |
| expansion | 仍不建议 50-company 直至 signoff 文档化 |

---

## Option D: Hold A-class Expansion

维持当前 closure gate，暂停一切 A-class expansion，直至基础设施稳定。

---

## Recommendation

1. **Option B** — CNINFO reachability precheck（**先于** retry_v3）
2. **Option A** — retry_v3 isolated package（8 case only）
3. 若多次 retry 仍失败 → 考虑 **Option C** signoff

**不推荐：**
- 50-company expansion
- schema / matching changes without new contradictory evidence

---

## Red Lines

- No successful 12 rerun
- No PDF / DB / MinIO / RAG
- No verified / production_ready
- No overwrite of original / v1 / v2 execution reports
