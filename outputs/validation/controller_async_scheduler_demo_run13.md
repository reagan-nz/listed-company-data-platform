# Async Scheduler Demo — Run 13

_性质：Mission Execution Engine v4 调度语义验证（非新能力波次）_  
_日期：2026-07-15_  
_CNINFO live：0（本 demo 不调用 CNINFO）_

---

## Purpose

Run 12 用 **Global Wave 同步屏障** 执行。本 demo 用同一批已验证任务的墙钟特征，按 v4 **ASYNC_MISSION_LOOP** 重放调度事件，证明：

1. 一轨完成即可 review → commit → refill → dispatch  
2. 短轨不必等待长轨（A live）结束  
3. 报告单位为 track-local wave，而非 Global Wave N  

**不**发明新的低价值任务；**不**重跑 live；**不**声称新的 capability gain。

---

## Inputs（Run 12 observed）

| Track | Wave-local tasks (Run 12 order) | Relative duration class |
|-------|----------------------------------|-------------------------|
| A | live s1 → live s2 → offline closure | LONG / LONG / SHORT |
| B | wrong_company → wrong_period → fixture → unrelated | SHORT ×4 |
| C | prep adapter → partial7 → mock dry-run | SHORT ×3 |
| D | S5 live → closure → boundary note | MEDIUM / SHORT / SHORT |

Run 12 实际行为：Wave 1 内 B/C 在 A live s1 完成前不得进入 Wave 2。

---

## v4 event log（counterfactual replay）

时间轴为逻辑时序（T0…），非墙钟秒。`parallel_peers` 仅报告，不阻塞。

```text
T0  dispatch A-wave-1 (live s1)     lifecycle=EXECUTING  peers=[]
T0  dispatch B-wave-1 (wrong_co)    lifecycle=EXECUTING  peers=[A]
T0  dispatch C-wave-1 (prep)        lifecycle=EXECUTING  peers=[A,B]
T0  dispatch D-wave-1 (S5 live)     lifecycle=EXECUTING  peers=[A,B,C]

T1  B completes → VALIDATING → evidence/regression/boundary → COMMIT
    B REFRESH_GAP → GENERATE_NEXT → dispatch B-wave-2 (wrong_period)
    # A still EXECUTING — B did NOT wait for Global Wave barrier

T2  C completes → … → COMMIT → dispatch C-wave-2 (partial7)
    # A still EXECUTING

T3  D completes S5 live → … → COMMIT → dispatch D-wave-2 (closure)
    # A still EXECUTING

T4  B-wave-2 completes → COMMIT → dispatch B-wave-3 (fixture)
T5  C-wave-2 completes → COMMIT → dispatch C-wave-3 (mock dry-run)
T6  D-wave-2 completes → COMMIT → dispatch D-wave-3 (boundary)

T7  A-wave-1 completes → COMMIT → dispatch A-wave-2 (live s2)
    # By T7, B already finished ≥2 track-local waves under v4
    # Under Run 12 sync, B would still be blocked until Wave 1 barrier

T8  B-wave-3 completes → COMMIT → dispatch B-wave-4 (unrelated)
T9  C-wave-3 completes → IDLE_NO_TASK (audit: no high-value autonomous next)
T10 D-wave-3 completes → IDLE_NO_TASK

T11 A-wave-2 completes → COMMIT → dispatch A-wave-3 (offline closure)
T12 B-wave-4 completes → IDLE_NO_TASK (§7 FP exhausted)
T13 A-wave-3 completes → IDLE_NO_TASK

T14 all_tracks_idle_and_audited_empty → stop NO_VALUABLE_SAFE_TASK
```

---

## Parallel efficiency（required v4 section）

```text
While A was EXECUTING (A-wave-1 live s1):
  B completed B-wave-1 and started B-wave-2
  C completed C-wave-1 and started C-wave-2
  D completed D-wave-1 and started D-wave-2

While A was EXECUTING (A-wave-2 live s2):
  B completed B-wave-3 / B-wave-4 path continued
  C reached IDLE_NO_TASK after C-wave-3
  D reached IDLE_NO_TASK after D-wave-3
```

**Sync tax removed:** Run 12 Global Wave 1 墙钟 ≈ max(A_s1, B1, C1, D1)。  
v4 墙钟推进 ≈ 各轨独立累加；短轨空等时间 → 0。

---

## Track-local wave counts（replay）

| Track | internal_wave_count | Timeline |
|-------|---------------------|----------|
| A | 3 | live s1 → review/commit → live s2 → review/commit → offline closure |
| B | 4 | wrong_company → wrong_period → fixture → unrelated |
| C | 3 | prep → partial7 → mock dry-run |
| D | 3 | S5 live → closure → boundary |

**total track waves:** 13（与 Run 12 任务包数量一致；调度形状不同）  
**total commits (model):** 同 Run 12 分包数（仍禁止 micro-commit）  
**CNINFO (this demo):** 0  

---

## Scheduler invariants checked

| Invariant | Result |
|-----------|--------|
| `blocked_by_other_tracks` always false | PASS |
| Review after each track task (not only global wave end) | PASS (modeled) |
| Stop only after full A/B/C/D audit empty | PASS (T14) |
| No fake idle-fill tasks | PASS |
| Long A live does not pause B/C/D | PASS (T1–T6) |

---

## Next real validation

启用 `mission_execution_engine_v4` 后的首次 live mission：在 A 长 CNINFO 仍 RUNNING 时，至少完成并 commit 一次 B 或 C 或 D 的真实 track-local wave（非本 counterfactual）。
