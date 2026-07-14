# Controller Execution Cycle Policy v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_task_continuation_policy_v2.md](controller_task_continuation_policy_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_task_memory_policy_v2.md](controller_task_memory_policy_v2.md) · [controller_resource_allocation_policy_v2.md](controller_resource_allocation_policy_v2.md) · [controller_stuck_detection_policy_v2.md](controller_stuck_detection_policy_v2.md) · [controller_milestone_management_v2.md](controller_milestone_management_v2.md) · [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md) · [controller_commit_autonomy_policy_v2.md](controller_commit_autonomy_policy_v2.md)_


## 1. Purpose


Daily Autonomous Loop v2 在**同一次日运行（one daily run）**内，不得在完成单次 queue 执行后立即结束。


本政策定义 **Execution Cycle**：任务完成后更新状态、重新评估队列，并在同一 daily run 内继续自主工作，直到合法停机条件触发。


**System intent：** the cycle exists to advance **full-market A/B/C/D mission progress** via track agents — **not** to burn budget on controller self-maintenance.


### Problem this solves


| Before（失败模式） | After（目标行为） |
|--------------------|-------------------|
| 单次 queue / 或仅 controller 维护后停止 | multi-iteration · **mission-first** · discovery before stop |
| HOLD ⇒ 立刻 `NO_SAFE_READY` | HOLD 阻断 live/审批项 · **仍须发现**安全离线候选 |
| 多次微小 controller commit 耗尽预算 | **task batch → validate → bounded commit** |
| Controller 代替 track 干活 | **A/B/C/D 进度任务必须路由到对应 executor** |



---

# 2. Execution cycle（normative）


```text
CYCLE_START (within one Daily Loop run)
    ↓
Read state
    ↓
Generate / refresh queue
    ↓
If no safe READY → Task Discovery（inspect A/B/C/D mission objectives）
    ↓
Select highest-value safe task
  （mission progress > evidence > controller maintenance）
  （task priority policy v2）
    ↓
Dispatch owning track agent（not Controller substitute）
    ↓
Execute (bounded allowed_action)
    ↓
Validate (evidence + red lines)
    ↓
Bounded commit if allowed（prefer batched package · not microcommits）
    ↓
Update state (plan + track status + evidence pointers)
    ↓
Re-read queue
    ↓
Continue if safe READY / discoverable mission tasks exist
    ↓
else → STOP_CYCLE → Daily Report + Progress intelligence
```


One **iteration** = one pass through select →（discover if needed）→ agent execute → validate → optional **batched** commit → update → re-read.



---

# 3. Selection rules


When refreshing the queue, Controller must:


1. Re-classify A/B/C/D using current git + evidence + PROJECT_CONTROL.  
2. Filter to **safe READY** only（no missing approval · no red-line action）.  
3. If the safe READY set is empty → run **Task Discovery**（§3.1）before considering stop.  
4. Rank remaining candidates with [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md):  
   **Mission Progress Priority:** A/B/C/D capability > track evidence/QA > controller maintenance；  
   then P1→P5 within that hard order.  
5. Select the **highest-value safe** task（or parallel-safe wave）.  
6. **Route** track progress tasks to the owning agent（§3.2）— Controller coordinates only.  
7. Prefer offline / capability-advancing work over speculative live.  
8. Never select an action that requires missing Level-2 approval.  
9. Never invent **live / approval-bypass** READY to fill idle budget.  
10. Do not prefer controller P4/P5 while safe mission/evidence candidates exist or were just discovered.  
11. Do not consume execution budget on controller self-updates when mission work exists.  


If multiple READY tracks exist: may run in parallel when worktree isolation allows（Daily Loop Phase 3）；each parallel unit still counts toward iteration / commit / runtime budgets as defined in §6. Parallel waves must still respect mission-first priority（no controller filler beside an available track P1）.


Selection authority: **task priority policy v2**. Mission objective v2 defines what mission progress means; progress tracking v2 supplies bottleneck / coverage inputs.


## 3.1 Task Discovery / Task Generation Requirement


If no READY task exists after refresh:


**Do NOT** conclude `NO_SAFE_READY` immediately.


Controller **must**:


1. Run capability gap analysis（[capability gap analysis v2](controller_capability_gap_analysis_v2.md)）.  
2. Read task memory（[task memory policy v2](controller_task_memory_policy_v2.md)）.  
3. Generate candidates via [task generator policy v2](controller_task_generator_policy_v2.md) against A/B/C/D mission objectives.  
4. Apply resource allocation（[resource allocation v2](controller_resource_allocation_policy_v2.md)）and priority.  
5. Promote `offline_safe` survivors to READY.  


| Track | Mission lens | Example safe candidates（non-exhaustive） |
|-------|--------------|------------------------------------------|
| A | full-market company information coverage | coverage gap analysis · missing field investigation · next slice preparation |
| B | full-market disclosure/event coverage | event/source coverage expansion prep · taxonomy improvement · parser preparation |
| C | full-market evidence and quality | QA gap resolution · evidence completeness improvement |
| D | full-market shareholder/capital | offline schema preparation · event modeling · approval package preparation |


Discovery/generation rules:


1. Candidates must be **offline-safe** unless an exact live approval is already spent for that scope.  
2. Candidates must **not** bypass HOLD live bans · snapshot block · WAITING_APPROVAL component gates.  
3. Candidates that pass safety are promoted to READY for this cycle’s ranking.  
4. After a completed task, run [continuation policy v2](controller_task_continuation_policy_v2.md) before declaring the track idle.  
5. If generation yields nothing new, run [stuck detection v2](controller_stuck_detection_policy_v2.md) — do not endlessly repeat.  
6. Only if generation + stuck analysis leave **zero** safe candidates → `NO_SAFE_READY` is allowed.  
7. “Tracks show HOLD in PROJECT_CONTROL” is **not** sufficient discovery.  


## 3.2 Agent Routing Requirement


Track progress / track evidence tasks **MUST** use corresponding agents:


| Track | Required agent |
|-------|----------------|
| A | `a-class-executor` |
| B | `b-class-executor` |
| C | `c-class-executor` |
| D | `d-class-executor` |


Controller may coordinate（queue · budget · commit gate · report）but **must not replace** track agents for A/B/C/D capability or track-evidence work.


Controller-only execution is limited to true controller-band maintenance **after** discovery shows no safe track candidates（or for the final daily report packaging）.


## 3.3 Commit batching


Avoid consuming `max_autonomous_commits` with tiny controller commits（tip-align chains · one-file policy drips · repeated HEAD rewrites）.


Prefer:


```text
task batch（agent outputs）
    ↓
validation
    ↓
one bounded explicit-path commit（or few domain packages）
```


Rules:


1. Prefer **one commit per completed task package**（or tightly related domain batch）.  
2. Daily report: prefer **one** report commit at cycle end — not multiple tip-chase commits.  
3. Policy landings: batch related controller docs in **one** commit when they ship together.  
4. Do not start controller microcommit waves while mission task batches are pending.  



---

# 4. Stop conditions（only these end the daily run’s execution cycles）


Stop **execution cycling** and proceed to Daily Report when **any** of:


| Stop reason | Meaning |
|-------------|---------|
| `NO_SAFE_READY` | after refresh **and** task generation/discovery **and** stuck analysis（when applicable）, still no safe READY `allowed_action` |
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
| Track A/B post-integration `HOLD` | no live retry · **still run discovery** for safe offline A/B candidates · continue other tracks |
| Queue looks empty / all labeled HOLD or WAITING | **Task Discovery required** · `NO_SAFE_READY` only if discovery finds nothing safe |
| Discovery finds only controller maintenance | allowed only after mission/evidence discovery exhausted · report as maintenance band |


Interrupt policy nuance:


- Track-scoped interrupt → record human decision needed · **do not** cancel other tracks’ cycles.  
- Global safety interrupt / safety violation → stop all further autonomous execution in this run.  



---

# 6. Daily execution budget


Purpose: prevent infinite autonomous execution inside one daily run.


## 6.1 Default budgets（Operational Mode）


| Budget | Default | Notes |
|--------|---------|-------|
| `max_iterations` | **10** | select→discover/generate→execute→validate→continue cycles per daily run |
| `max_runtime` | **120 minutes** | wall-clock from LOOP_START；soft stop at limit |
| `max_autonomous_commits` | **12** | local commits created by this daily run · **batching still required** |


Defaults may be tightened by human in PROJECT_CONTROL / daily plan header. Raising budgets above defaults requires human acceptance（not silent expansion mid-run）.


## 6.2 Budget accounting


- Parallel track dispatches in one wave count as **one iteration wave** if started from the same queue snapshot; each still consumes commit budget individually.  
- Failed / skipped preflight that does no work does **not** count as a successful capability iteration, but still consumes runtime.  
- Docs-only report write at end does not require a separate discovery pass if mission iterations already ran；prefer **single** final report commit（§3.3）.  
- Controller maintenance iterations while mission candidates exist are a **budget accounting smell** — avoid；if they occur, report as policy deviation.  


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
- declaring `NO_SAFE_READY` **without** Task Discovery over A/B/C/D mission objectives  
- spinning iterations with empty/no-op actions to consume budget  
- treating budget exhaustion as mission completion  
- auto-raising `max_*` mid-run  
- live CNINFO / push to “use remaining budget”  
- selecting controller maintenance while safe mission/evidence candidates exist or are discoverable  
- inventing artificial live/approval READY tasks  
- Controller substituting for a/b/c/d-class executors on track progress  
- burning commit budget on tip-align / microcommits instead of batched task packages  



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
