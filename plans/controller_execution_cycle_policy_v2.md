# Controller Execution Cycle Policy v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md) · [controller_commit_autonomy_policy_v2.md](controller_commit_autonomy_policy_v2.md)_


## 1. Purpose


Daily Autonomous Loop v2 在**同一次日运行（one daily run）**内，不得在完成单次 queue 执行后立即结束。


本政策定义 **Execution Cycle**：任务完成后更新状态、重新评估队列，并在同一 daily run 内继续自主工作，直到合法停机条件触发。


### Problem this solves


| Before（单次 queue） | After（multi-iteration cycle） |
|----------------------|--------------------------------|
| Read → plan → execute once → report → stop | Read → plan → execute → validate → commit? → update → **re-queue** → continue |
| One READY task done ⇒ day ends | Day ends only when no safe READY remains / interrupt / budget / safety |



---

# 2. Execution cycle（normative）


```text
CYCLE_START (within one Daily Loop run)
    ↓
Read state
    ↓
Generate / refresh queue
    ↓
Select highest-value safe task
  （task priority policy v2: P1→P5）
    ↓
Execute (bounded allowed_action)
    ↓
Validate (evidence + red lines)
    ↓
Commit if allowed (commit autonomy v2)
    ↓
Update state (plan + track status + evidence pointers)
    ↓
Re-read queue
    ↓
Continue if safe READY tasks exist
    ↓
else → STOP_CYCLE → Daily Report + Progress intelligence
```


One **iteration** = one pass through select → execute → validate → optional commit → update → re-read.



---

# 3. Selection rules


When refreshing the queue, Controller must:


1. Re-classify A/B/C/D using current git + evidence + PROJECT_CONTROL.  
2. Filter to **safe READY** only（no missing approval · no red-line action）.  
3. Rank remaining candidates with [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md):  
   **P1 mission progress → P2 bottleneck reduction → P3 evidence/quality → P4 maintenance → P5 optional**.  
4. Select the **highest-value safe** task（or parallel-safe wave）per that ladder + within-class factors.  
5. Prefer offline / capability-advancing work over speculative live（also encoded as safety factor）.  
6. Never select an action that requires missing Level-2 approval.  
7. Never invent a READY task to fill idle budget.  
8. Do not prefer easy P4/P5 work while safe P1–P3 READY remains.  


If multiple READY tracks exist: may run in parallel when worktree isolation allows（Daily Loop Phase 3）；each parallel unit still counts toward iteration / commit / runtime budgets as defined in §6. Parallel waves must still respect priority ladder（no P4 filler beside an available P1）.


Selection authority: **task priority policy v2**. Mission objective v2 defines what mission progress means; progress tracking v2 supplies bottleneck / coverage inputs.



---

# 4. Stop conditions（only these end the daily run’s execution cycles）


Stop **execution cycling** and proceed to Daily Report when **any** of:


| Stop reason | Meaning |
|-------------|---------|
| `NO_SAFE_READY` | no track has a safe READY `allowed_action` |
| `HUMAN_INTERRUPT` | interrupt policy requires human before further autonomous work（may be track-scoped; see §5） |
| `BUDGET_REACHED` | any daily execution budget limit hit（§6） |
| `SAFETY_VIOLATION` | red-line / ownership / evidence honesty breach — halt further autonomous actions |


After stop:


1. Emit Daily Report + Progress intelligence（progress tracking v2）.  
2. Record stop reason and remaining HOLD / WAITING_APPROVAL.  
3. **Never** auto-push.  



---

# 5. HOLD / WAITING_APPROVAL — not global stop


Known `HOLD` or `WAITING_APPROVAL` on one track **must not** stop the entire daily run.


| Situation | Behavior |
|-----------|----------|
| Track D `WAITING_APPROVAL` | escalate D · **continue** A/B/C if READY |
| Track C snapshot `HOLD` | keep C HOLD · **continue** other READY tracks |
| Track A/B post-integration `HOLD` | do not invent live retry · **continue** independent READY work |
| All tracks HOLD/WAITING/BLOCKED | `NO_SAFE_READY` → stop cycling |


Interrupt policy nuance:


- Track-scoped interrupt → record human decision needed · **do not** cancel other tracks’ cycles.  
- Global safety interrupt / safety violation → stop all further autonomous execution in this run.  



---

# 6. Daily execution budget


Purpose: prevent infinite autonomous execution inside one daily run.


## 6.1 Default budgets（Operational Mode）


| Budget | Default | Notes |
|--------|---------|-------|
| `max_iterations` | 8 | select→execute→validate→update cycles per daily run |
| `max_runtime` | 120 minutes | wall-clock from LOOP_START；soft stop at limit |
| `max_autonomous_commits` | 6 | local commits created by this daily run |


Defaults may be tightened by human in PROJECT_CONTROL / daily plan header. Raising budgets above defaults requires human acceptance（not silent expansion mid-run）.


## 6.2 Budget accounting


- Parallel track dispatches in one wave count as **one iteration wave** if started from the same queue snapshot; each still consumes commit budget individually.  
- Failed / skipped preflight that does no work does **not** count as a successful capability iteration, but still consumes runtime.  
- Docs-only report write at end does not require a separate iteration slot.  


## 6.3 On budget reached


```text
status: BUDGET_REACHED
action: stop cycling · write daily report · list unfinished READY (if any) as remaining work
forbidden: extending budget silently · starting live to “finish faster”
```



---

# 7. State update between iterations


After each successful or failed execution unit, Controller must:


1. Refresh track `status` / `allowed_action` / `human_interrupt`.  
2. Attach evidence paths produced this iteration.  
3. Update commit shortsha list for the run.  
4. Recompute bottleneck + progress notes when material coverage changed（progress tracking v2）.  
5. **Not** churn PROJECT_CONTROL every iteration — control file updates remain explicit packages when policy requires.  


Stale plan reuse without re-read is forbidden.



---

# 8. Integration with Daily Loop phases


| Loop phase | Cycle role |
|------------|------------|
| Phase 1 Read state | entry + every re-read |
| Phase 2 Plan / queue | generate then **refresh** each iteration |
| Phase 3–6 | execute / evidence / commit inside iteration |
| Phase 7 Report | **after** cycle stop |
| Phase 8 Interrupt | may stop one track or all · per interrupt policy |


Task pick at each iteration: [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md).


Normative algorithm lives in Daily Loop v2 §11（multi-iteration）. This file is the cycle / budget authority.



---

# 9. Honesty / anti-patterns


Forbidden:


- one-shot execute then stop while other safe READY tasks remain and budget remains  
- stopping all tracks because one track is HOLD / WAITING_APPROVAL  
- spinning iterations with empty/no-op actions to consume budget  
- treating budget exhaustion as mission completion  
- auto-raising `max_*` mid-run  
- live CNINFO / push to “use remaining budget”  
- selecting easy P4/P5 maintenance while safe P1–P3 READY remains  
- inventing artificial READY tasks to satisfy priority pressure  



---

# 10. Reporting fields（required on stop）


Daily report / stop context must include:


```text
execution_cycle:
  iterations_completed:
  stop_reason: NO_SAFE_READY | HUMAN_INTERRUPT | BUDGET_REACHED | SAFETY_VIOLATION
  budget:
    max_iterations: / used:
    max_runtime: / used:
    max_autonomous_commits: / used:
  continued_despite_hold_or_waiting: true|false
  tracks_still_ready_at_stop: []
```
