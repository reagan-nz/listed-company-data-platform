# Controller Daily Autonomous Loop v2


_最后更新：2026-07-14_  
_状态：设计稿 · 未启用为强制运行时_  
_依赖：controller_*_policy_v1 · PROJECT_CONTROL · worktree policies · push policy_


## 1. Purpose


定义 **Daily Autonomous Loop v2**：Controller 每日启动后，在不绕过安全边界的前提下，自动完成：


1. 读取当前状态  
2. 生成当日执行计划  
3. 编排 A/B/C/D worktree  
4. 调度 specialized agents  
5. 产出 evidence package  
6. 在允许范围内做 bounded local commit  
7. 生成日报  
8. 仅在规定打断点请求 human  


本文件是 **主运行策略**。配套：


| 文件 | 职责 |
|------|------|
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
Classify tracks A/B/C/D
  READY | RUNNING | HOLD | WAITING_APPROVAL | BLOCKED | COMPLETED
    ↓
Generate daily execution plan
    ↓
Worktree orchestration
  agent/a-class · agent/b-class · agent/c-class · agent/d-class
    ↓
Agent execution (bounded)
    ↓
Evidence packaging
    ↓
Autonomous commit (if policy allows)
    ↓
Daily report
    ↓
Human interrupt only at defined gates
    ↓
(no auto push)
```


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
2. Prefer **HOLD** over inventing next scale.  
3. `READY_FOR_APPROVAL` ≠ approved.  
4. post-integration HOLD tracks: no live retry unless new human scope.  
5. One track failure must not cancel other READY tracks.  
6. Do not schedule push in daily auto plan.



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


## 6.1 Agent must


1. Read assigned track slice from daily plan + PROJECT_CONTROL  
2. Execute **only** `allowed_action`  
3. Write evidence under agreed validation roots  
4. Validate red lines / output-root guards  
5. Prepare explicit-path commit inventory when commit_eligible  
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



---

# 9. Phase 7 — Daily Report


Schema: see [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md).


Minimum sections: Date · HEAD · Tracks A–D · Human attention · Safety counters.



---

# 10. Phase 8 — Human Interrupt


Rules: see [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md).


Daily Loop must not interrupt for normal docs/evidence/tests/bounded commits.



---

# 11. Daily Loop Algorithm (normative)


```text
LOOP_START(date):
  S = read_state()
  P = build_daily_plan(S)          # schema v2
  for track in {A,B,C,D} parallel-safe:
    if P[track].status not in {READY}:
      record_and_continue
    if not preflight_worktree(track):
      P[track].status = BLOCKED
      continue
    R = dispatch_agent(track, P[track])
    if R.needs_human:
      escalate(R.reasons)          # interrupt policy
      continue
    if R.commit_eligible and commit_autonomy_allows(R):
      explicit_path_commit(R)
    package_evidence(R)
  write_daily_report(P, results)
  NEVER push
LOOP_END
```



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
