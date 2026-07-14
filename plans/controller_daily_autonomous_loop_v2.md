# Controller Daily Autonomous Loop v2


_最后更新：2026-07-14_  
_状态：Operational Mode 默认运行策略_  
_依赖：controller_*_policy_v1 · PROJECT_CONTROL · worktree policies · push policy_  
_目标层：[controller_mission_objective_v2.md](controller_mission_objective_v2.md)_  
_进度层：[controller_progress_tracking_v2.md](controller_progress_tracking_v2.md)_  
_周期层：[controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md)_  
_优先级层：[controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md)_


## 1. Purpose


定义 **Daily Autonomous Loop v2**：Controller 每日启动后，在不绕过安全边界的前提下，自动完成：


1. 读取当前状态  
2. 生成当日执行计划 / 队列  
3. 编排 A/B/C/D worktree  
4. 调度 specialized agents  
5. 产出 evidence package  
6. 在允许范围内做 bounded local commit  
7. **在同一次日运行内重新评估队列并继续**（直到无 READY / interrupt / budget / safety）  
8. 生成日报（含 Progress intelligence）  
9. 仅在规定打断点请求 human  


**Mission（最高目标）：** 在安全边界内，推动 A/B/C/D 朝全市场数据采集能力前进，并最大化独立 track 的自主进度。详见 [controller_mission_objective_v2.md](controller_mission_objective_v2.md)。


**System intent：** Daily Loop v2 是 **mission-progress execution system**（经 track agents 推进 A/B/C/D），**不是** controller 自我维护循环。Controller 维护不得在仍有可发现的安全 mission/evidence 工作时装满预算。


本文件是 **主运行策略**。配套：


| 文件 | 职责 |
|------|------|
| [controller_mission_objective_v2.md](controller_mission_objective_v2.md) | 最高目标 · track 目标 · 审批哲学 · 优化优先级 |
| [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) | 能力覆盖进度 · bottleneck · effort 估计 · 停机进度块 |
| [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) | 同日多轮执行 · 再排队 · 停机条件 · 日预算 |
| [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) | 安全 READY 任务优先级 P1–P5 · 同级排序因子 |
| [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md) | 日计划 / 日报 schema |
| [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md) | human 打断规则 |
| [controller_commit_autonomy_policy_v2.md](controller_commit_autonomy_policy_v2.md) | 自动 commit 权限 |


v2 **继承** v1 红线；冲突时以更严格者为准。



---

# 2. Architecture


```text
Daily start
    ↓
Read state
  PROJECT_CONTROL.md
  CURRENT_STATUS.md
  PROJECT_MAP.md
  git reality (HEAD / dirty / ahead-behind / worktrees)
    ↓
┌── Execution cycle (same daily run) ─────────────────────┐
│  Classify / refresh queue A/B/C/D                       │
│    READY | RUNNING | HOLD | WAITING_APPROVAL | …        │
│       ↓                                                 │
│  Select highest-value safe READY task(s)                │
│       ↓                                                 │
│  Worktree orchestration + bounded agent execution       │
│       ↓                                                 │
│  Evidence packaging + validate                          │
│       ↓                                                 │
│  Autonomous commit (if policy allows)                   │
│       ↓                                                 │
│  Update state → re-read queue                           │
│       ↓                                                 │
│  Continue while safe READY remain                       │
│    AND budget not exhausted                             │
│    AND no global safety / required global interrupt     │
└─────────────────────────────────────────────────────────┘
    ↓
Daily report + Progress intelligence
    ↓
Human interrupt only at defined gates
    ↓
(no auto push)
```


HOLD / WAITING_APPROVAL on one track does **not** end the cycle for other READY tracks. Cycle / budget authority: [execution cycle policy v2](controller_execution_cycle_policy_v2.md).


当前已落地基础（设计假设）：


| Layer | Checkpoint |
|-------|------------|
| Controller policies | `0f63a90` |
| Runtime isolation | `d385bb6` |
| Agents | `4a62f78` |
| PROJECT_CONTROL sync | `710b3c3` |
| Docs / source / evidence consolidation | through `8960bbc` |



---

# 3. Phase 1 — Read Current State


## 3.1 Required sources


| Source | Use |
|--------|-----|
| `PROJECT_CONTROL.md` | queue · track stage · approvals · blockers · autonomy split |
| `CURRENT_STATUS.md` | human-readable tip · caveats · NOT verified / NOT production_ready |
| `PROJECT_MAP.md` | architecture layer map · protected roots |
| `git status` / `git log` / `git worktree list` | HEAD · dirty · ahead/behind · worktree ownership |
| track evidence under `outputs/validation/` | latest gate artifacts when cited by control docs |


**Priority when conflict：** git reality + evidence files **outrank** control prose.



## 3.2 State extraction checklist


Controller must record:


1. `HEAD` short hash  
2. `ahead` / `behind` vs `origin/main`  
3. dirty inventory classed as: source · plans · evidence · runtime · bak-exception  
4. active Controller Queue items  
5. open live / commit / component / push approvals  
6. per-track `current_stage` / `current_gate` / `next_allowed_task` / `blocked_actions`  
7. worktree branch tips vs main tip  
8. known HOLD / WAITING_APPROVAL / BLOCKED reasons  



## 3.3 Track ownership map


| Track | Worktree / branch | Executor | Default reviewers |
|-------|-------------------|----------|-------------------|
| A | `../listed_company_data_collector-worktrees/a-class` · `agent/a-class` | `a-class-executor` | evidence-auditor · git-boundary-reviewer · regression-reviewer (when code) |
| B | `.../b-class` · `agent/b-class` | `b-class-executor` | same |
| C | `.../c-class` · `agent/c-class` | `c-class-executor` | same |
| D | `.../d-class` · `agent/d-class` | `d-class-executor` | same |


Cross-track work → `CROSS_TRACK_REVIEW_REQUIRED` · do not silent-split.



---

# 4. Phase 2 — Daily Execution Plan


计划生成必须以 [mission objective v2](controller_mission_objective_v2.md) 为优化方向：优先推进独立 track 的全市场能力相关自主工作；被阻塞 track 不拖停其他 track。


## 4.1 Track status vocabulary


| Status | Meaning |
|--------|---------|
| `READY` | next offline task clear · no missing approval · may start |
| `RUNNING` | agent/worktree actively executing assigned task |
| `HOLD` | intentional pause (caveats retained · snapshot blocked · deferred case) |
| `WAITING_APPROVAL` | Level-2 human phrase required before next action |
| `BLOCKED` | safety / ownership / sync / evidence conflict prevents progress |
| `COMPLETED` | bounded package closed for the day (not project-finished) |


## 4.2 Per-track decision fields


For each of A/B/C/D, plan must state:


- `status`
- `allowed_action`（exactly one primary action）
- `forbidden_actions`
- `required_agent`
- `required_reviewers`
- `evidence_expected`
- `commit_eligible`（yes/no under commit autonomy v2）
- `human_interrupt`（none / listed reasons）


## 4.3 Planning rules


1. Prefer **offline** continuation over live.  
2. Prefer **HOLD** over inventing **live / next-scale** without scope — HOLD does **not** mean “no offline mission work”.  
3. `READY_FOR_APPROVAL` ≠ approved.  
4. post-integration HOLD tracks: no live retry unless new human scope；**still require Task Discovery** for safe offline candidates.  
5. One track failure must not cancel other READY tracks.  
6. Do not schedule push in daily auto plan.  
7. After a task completes, **re-evaluate the queue** in the same daily run（execution cycle policy v2）— do not stop solely because one iteration finished.  
8. HOLD / WAITING_APPROVAL on one track must not stop other READY tracks.  
9. **Mission Progress Priority：** A/B/C/D capability > track evidence/QA > controller maintenance（task priority v2）.  
10. If queue has no READY → **Task Discovery** over A/B/C/D mission objectives before `NO_SAFE_READY`.  
11. Do not spend budget on controller self-updates when mission work exists or is discoverable.  


## 4.4 Task Discovery


When refresh yields no safe READY:


1. Inspect A/B/C/D mission objectives（mission objective v2）.  
2. Generate safe autonomous candidates（examples: A coverage expansion analysis · B disclosure/event preparation · C QA/evidence improvement · D offline component preparation）.  
3. Promote only candidates that pass safety / approval / red lines.  
4. Re-rank with task priority v2（mission-first）.  
5. Only then may Controller set `NO_SAFE_READY`.  


Authority detail: [execution cycle policy v2 §3.1](controller_execution_cycle_policy_v2.md).



---

# 5. Phase 3 — Worktree Orchestration


## 5.1 Pre-execution checks


Before dispatching a track:


| Check | Fail → |
|-------|--------|
| branch ownership matches track | BLOCKED |
| worktree exists and is registered | BLOCKED |
| no foreign-track dirty in that worktree | BLOCKED or quarantine |
| sync policy satisfied (or explicit stale-ok for read-only) | WAITING_APPROVAL / BLOCKED |
| no conflicting claim on same protected root | BLOCKED |
| required approval present if action needs it | WAITING_APPROVAL |


## 5.2 Parallelism


- A/B/C/D may run in parallel when each is READY and isolated.  
- Shared-file edits require serialization + git-boundary review.  
- If track X fails: mark X BLOCKED/HOLD · continue Y/Z.


## 5.3 Sync model


Follow `controller_worktree_synchronization_policy_v1.md`:


- capability sync ≠ authorization  
- main tip advancement does not auto-approve live  
- stale worktree may still do offline packaging if roots untouched



---

# 6. Phase 4 — Agent Execution Model


## 6.0 Agent routing（normative）


Track progress and track-evidence tasks **MUST** use:


| Track | Agent |
|-------|-------|
| A | `a-class-executor` |
| B | `b-class-executor` |
| C | `c-class-executor` |
| D | `d-class-executor` |


Controller **coordinates**（plan · discover · budget · commit gate · daily report）but **must not replace** these agents for A/B/C/D work.


A run with 0 track-agent dispatches while discovery could have produced safe track candidates is a **failed mission-progress run**.


## 6.1 Agent must


1. Read assigned track slice from daily plan + PROJECT_CONTROL  
2. Execute **only** `allowed_action`  
3. Write evidence under agreed validation roots  
4. Validate red lines / output-root guards  
5. Prepare explicit-path commit inventory when commit_eligible（prefer **batched** package）  
6. Return structured completion report to Controller  


## 6.2 Agent must NOT


- decide or execute push  
- bypass WAITING_APPROVAL  
- edit `PROJECT_CONTROL.md` policy sections without Controller ownership of that task  
- change gates / claim verified / production_ready  
- run CNINFO unless live approval spent for that exact scope  
- `git add .` / `-A`  
- mutate protected production harvest/snapshot roots outside explicit scope  


## 6.3 Reviewer insertion


| Change type | Reviewer |
|-------------|----------|
| metrics / gates / closure | evidence-auditor |
| runner / CLI / guards / shared utils | regression-reviewer |
| commit/push boundary | git-boundary-reviewer |


Reviewers remain read-only · never grant human approvals.



---

# 7. Phase 5 — Evidence Lifecycle


```text
execution output (may be runtime)
    ↓
validation / QA / ledgers (human-readable)
    ↓
evidence package (commit-eligible)
    ↓
git history
```


| Class | Examples | Git |
|-------|----------|-----|
| Runtime | raw / normalized bulk / live_snapshots / raw_metadata / run_meta | ignore |
| Evidence | summaries · ledgers · matrices · audit packets · commit status | bounded commit |
| Recovery bak | `*.bak_pre_offline_rebuild_*` | prefer ignore; copy into evidence if must retain |


Runtime ≠ historical evidence.



---

# 8. Phase 6 — Autonomous Commit + No Push


Commit rules: see [controller_commit_autonomy_policy_v2.md](controller_commit_autonomy_policy_v2.md).


Hard rule for Daily Loop v2:


**local commit/merge may be autonomous when policy satisfied · push always human-controlled.**


### Commit batching（required）


Prefer:


```text
task batch → validation → bounded explicit-path commit
```


Avoid burning `max_autonomous_commits` on tiny controller commits（tip-align chains · one-line HEAD rewrites · dripped policy files）.


- One completed agent task package → prefer **one** domain commit  
- Related controller docs shipping together → **one** commit  
- Daily report → prefer **one** end-of-cycle commit  
- Detail: [execution cycle policy v2 §3.3](controller_execution_cycle_policy_v2.md)



---

# 9. Phase 7 — Daily Report


Schema: see [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md).


Minimum sections: Date · HEAD · Tracks A–D · **Progress intelligence**（[progress tracking v2](controller_progress_tracking_v2.md)）· Human attention · Safety counters.


Progress block is mandatory on every stop / end-of-day report. Prefer capability coverage over commit/file counts. Use `unknown` when denominators or velocity are missing.



---

# 10. Phase 8 — Human Interrupt


Rules: see [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md).


Daily Loop must not interrupt for normal docs/evidence/tests/bounded commits.



---

# 11. Daily Loop Algorithm (normative)


Multi-iteration authority: [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md).


```text
LOOP_START(date):
  budget = load_daily_budget()   # max_iterations / max_runtime / max_autonomous_commits
  S = read_state()
  P = build_daily_plan(S)        # schema v2
  iterations = 0

  while true:
    if budget_exhausted(budget):
      stop_reason = BUDGET_REACHED
      break
    if safety_violation_detected():
      stop_reason = SAFETY_VIOLATION
      break

    S = read_state()             # re-read each cycle
    P = refresh_queue(S, P)

    ready = tracks_with_safe_READY(P)
    if ready is empty:
      candidates = discover_safe_mission_candidates(A,B,C,D)  # mandatory
      P = promote_safe_candidates(P, candidates)
      ready = tracks_with_safe_READY(P)
      if ready is empty:
        stop_reason = NO_SAFE_READY
        break

    # Defer controller-band tasks if any capability/evidence-band ready exists
    ready = apply_mission_progress_priority(ready, task_priority_v2)

    # Track-scoped WAITING_APPROVAL / HOLD: escalate those tracks, do not break loop
    for track in tracks_needing_interrupt(P):
      escalate(track)            # interrupt policy · continue others

    wave = select_highest_value_safe_tasks(ready, task_priority_v2)
    iterations += 1

    for track in wave parallel-safe:
      if track in {A,B,C,D}:
        agent = required_track_agent(track)   # a/b/c/d-class-executor
      else:
        agent = controller_only_if_maintenance_band()
      if not preflight_worktree(track):
        P[track].status = BLOCKED
        continue
      R = dispatch_agent(agent, track, P[track])  # Controller must not substitute
      package_evidence(R)
      if R.needs_human and interrupt_is_global(R):
        stop_reason = HUMAN_INTERRUPT
        break outer
      if R.needs_human:
        escalate(R.reasons)      # track-scoped · continue
        continue
      if R.commit_eligible and commit_autonomy_allows(R):
        if commit_budget_remaining(budget):
          explicit_path_commit_batched(R)   # prefer one package commit
          budget.commits_used += 1
        else:
          stop_reason = BUDGET_REACHED
          break outer
      update_track_state(P, R)

    if stop_reason set:
      break
    # else: loop → re-read queue

  write_daily_report_once(P, results, stop_reason, budget, iterations)
  # include Progress intelligence + execution_cycle + agent dispatch counts
  NEVER push
LOOP_END
```


Stop only for: `NO_SAFE_READY`（**after discovery**）· `HUMAN_INTERRUPT`（global）· `BUDGET_REACHED` · `SAFETY_VIOLATION`.



---

# 12. Red Lines (unchanged)


- no PDF/OCR/DB/MinIO/RAG Era without human Era approval  
- no bare PASS / verified / production_ready inflation  
- no disclosure→structured promotion  
- C `approved_for_snapshot_rebuild = false` until flipped by human  
- D shareholder_change remains approval-gated while `READY_FOR_APPROVAL`  
- push / force-push / remote rewrite human-only  



---

# 13. Relationship to v1


| v1 doc | v2 role |
|--------|---------|
| orchestration_policy_v1 | agent routing base |
| autonomy_policy_v1 / autonomous_operation_policy_v1 | autonomy levels base |
| worktree_*_v1 | isolation/sync base |
| integration_policy_v1 | local merge base |
| push_policy_v1 | push remains separate |
| Daily Loop v2 | **daily scheduler + report + interrupt/commit specialization** |


Enabling Daily Loop v2 as default runtime requires human acceptance of these four docs (separate decision).



---

# 14. Non-goals


- Not a CI system replacement  
- Not auto remote publication  
- Not automatic gate promotion  
- Not silent PROJECT_CONTROL rewrite every loop（control updates remain explicit packages）  
- Not a single-iteration day（one queue pass then stop while safe READY + budget remain）  
- Not a **controller maintenance loop**（policy/report commits with 0 track-agent mission work while discoverable safe A/B/C/D candidates exist）
