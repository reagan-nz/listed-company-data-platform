# CNINFO D 类 restricted_shares_unlock First-Slice — Closure Decision

_生成时间：2026-07-10_

> **性质：** 离线 closure 决策 · **CNINFO = 0** · **无 live** · **不是 verified**

---

## 1. Primary Decision

**CLOSE the restricted_shares_unlock first-slice track with caveat — NOW.**

| 项 | 决策 |
|----|------|
| closure gate | `d_class_restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT` |
| effective acceptable | **5/5** |
| sparse-day semantics | **confirmed** across all 5 cases on `tdate=2026-06-08` |
| endpoint consistency | **yes** — 0 rows for every case after 3-probe exhaustion; no http_error / blocked |
| unresolved blocking cases | **0** |
| verified / production_ready | **no** |
| bare PASS | **no** |

---

## 2. Rationale

1. Execution gate **`PASS_WITH_CAVEAT`** met at isolated live（**5/5** acceptable）。
2. All five cases demonstrate legal **`empty_but_valid`** on a sparse anchor day — consistent endpoint behavior across chinext / szse_main / sse_main / star.
3. Expectation mix absorbed block_trade DBT002 lesson: **no sole `captured_normal_candidate`**; all cases acceptable under documented mix.
4. No per-case blocking unresolved cases. Sparse-day empty is **not** treated as failure.

---

## 3. Sparse-Day Disposition

| 项 | 值 |
|----|-----|
| failure_class | **none** — sparse-day legal empty |
| closure disposition | **accept_with_caveat** at track level |
| blocking closure | **no** |
| ledger | [final_caveat_ledger.csv](cninfo_d_class_restricted_shares_unlock_first_slice_final_caveat_ledger.csv) · CAV-RSU-002 / CAV-RSU-003 |

---

## 4. Optional Later Actions（NOT in this task）

以下选项 **不在本任务执行** · **不自动运行** · 需单独批准：

### a) Separate approved probe on known nonzero restricted_shares_unlock tdate

| 项 | 内容 |
|----|------|
| action | 在已知有 liftBan 记录的 tdate 上执行单独批准的小探针 |
| scope | 新 slice / 新 approval phrase · 非 first-slice rerun |
| prerequisite | 人工批准 · 独立 task |
| recommendation now | **deferred** — not required for first-slice closure |

**Closure decision:** optional denser-day / nonzero-tdate probe is **deferred**, not recommended as immediate blocker.

---

## 5. Frozen Tracks（保持 closed）

- known-event replacement / targeted probe
- block_trade first-slice（commit **`403472d`** · **NOT verified** · **NOT pushed**）
- margin_trading first-slice（commit **`116f875`**）
- disclosure_schedule first-slice（commit **`d37ce0a`**）
- A/B/C live roots

---

## 6. Gate Sign-Off

```text
d_class_restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_restricted_shares_unlock_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

---

## 7. Next Step

见 [post-closure next-step recommendation](cninfo_d_class_restricted_shares_unlock_first_slice_post_closure_next_step_recommendation.md)。
