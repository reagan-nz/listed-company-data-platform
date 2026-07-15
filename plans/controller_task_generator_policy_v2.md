# Controller Task Generator Policy v2


_最后更新：2026-07-14_  
_配套：[controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_task_memory_policy_v2.md](controller_task_memory_policy_v2.md) · [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_track_execution_queue_policy_v2.md](controller_track_execution_queue_policy_v2.md) · [controller_track_stop_reason_policy_v2.md](controller_track_stop_reason_policy_v2.md)_


## 1. Purpose


When the Daily Autonomous Loop needs a **next target**, Controller must **generate** safe autonomous candidate tasks from **current** mission gaps — not only when the queue is empty, and not as a once-per-day fixed todo list.


This policy is the **task generation** authority behind Task Discovery **and** continuous [mission replanning](controller_mission_replanning_loop_v2.md).  
It turns mission + progress + **fresh** gaps + memory into structured candidates for ranking and agent routing.



---

# 2. When to generate


Run the generator when **any** of:


1. Refresh yields empty safe READY set.  
2. **After every completed task** — as part of mandatory replan（even if prior candidates remain）.  
3. Continuation policy requests a successor after a completed task.  
4. Stuck detection asks for alternative autonomous actions.  
5. Gap analyzer emits actionable gaps without an existing READY task that still matches.  


Do **not** skip generation solely because PROJECT_CONTROL shows HOLD / WAITING_APPROVAL.  
Do **not** treat an earlier generated batch as the remaining schedule without re-scoring against recalculated A/B/C/D gaps.



---

# 3. Analysis inputs


**Prerequisite：** complete [state refresh](controller_mission_replanning_loop_v2.md)（git · evidence · memory · progress · track status）before reading inputs below. Do not generate from stale snapshots.


Before emitting candidates, analyze:


| Input | Source |
|-------|--------|
| Mission objective | mission objective v2 · A/B/C/D goals |
| Progress intelligence | progress tracking v2 · latest baseline/report（refreshed） |
| Track gaps | capability gap analysis v2（after refresh） |
| Historical tasks | task memory v2（refreshed） |
| Track status | PROJECT_CONTROL + git reality（refreshed） |


Reject candidates that memory marks as completed-equivalent, human-rejected, or known-blocked approaches.


When no candidate is promoted, emit a **candidate audit**（mission replanning §2.2）before `NO_VALUABLE_SAFE_TASK` — including **Autonomous Queue vs Approval Queue** per track.



---

# 3.1 Approval Split（normative）


Every track **MUST** maintain two queues:


| Queue | Contents |
|-------|----------|
| **Autonomous Queue** | Tasks executable **without** new human approval（offline_safe · spent-scope only） |
| **Approval Queue** | Tasks blocked by missing Level-2 / live / snapshot / push approval |


### Hard rules


1. Approval-gated **live** work must **not** block autonomous offline work on the same track.  
2. A track in `WAITING_APPROVAL` / HOLD-for-live **MUST NOT** be removed from autonomous planning.  
3. Generator **must** still emit Autonomous Queue candidates for that track when gaps allow.  
4. Approval Queue items are recorded for human attention — they are **not** READY for dispatch.  


### Example — D shareholder_change


| Queue | Examples |
|-------|----------|
| Approval | live shareholder_change execution · runner with CNINFO · unapproved component go-live |
| Autonomous | event taxonomy · schema refinement · sample preparation · validation rules · offline evidence mapping |


Skipping D-class-executor for an entire daily run solely because AQ-D-SC is open is a **policy failure** when Autonomous Queue items existed.


### Assignment into track execution queues


After generation + safety filter, Controller **assigns** surviving autonomous candidates into per-track [execution queues](controller_track_execution_queue_policy_v2.md):


```text
global candidates
    ↓
split autonomous | approval
    ↓
A Autonomous Queue ← ordered by priority
B Autonomous Queue ← …
C Autonomous Queue ← …
D Autonomous Queue ← …
```


Ordering within a track queue uses mission impact · bottleneck reduction · explicit dependencies — not FIFO alone.  
Agents pull **only** Controller-assigned queue heads after re-score（no invent）.



---

# 3.2 Stop reason when generation yields empty autonomous set


If a track’s Autonomous Queue is empty after generation:


| Condition | Track `stop_reason` |
|-----------|---------------------|
| Approval Queue has the next valuable step | `HUMAN_GATE_BLOCKED` |
| No approval next step · no autonomous survivors | `NO_SAFE_AUTONOMOUS_TASK` or `CURRENT_TASK_COMPLETED` |
| Autonomous items exist but not selected | do not mark empty — use `LOW_PRIORITY_DEFERRED` / `RESOURCE_ALLOCATED_ELSEWHERE` |


Never collapse the above into global `NO_VALUABLE_SAFE_TASK` until **all** tracks are audited.  

# 4. Candidate schema（required）


Each candidate **must** contain:


```text
task_id:              # stable id e.g. A-GEN-20260714-01
track:                # A | B | C | D
queue:                # autonomous | approval
objective:            # one sentence capability intent
expected_capability_improvement:
risk_level:           # low | medium | high
required_agent:       # a-class-executor | b-class-executor | c-class-executor | d-class-executor
estimated_effort:     # S | M | L  or qualitative · never fake calendar ETA
safety_class:         # offline_safe | approval_gated | live_gated
maps_to_goal:         # cite track mission goal
approval_bypass:      # must be false
```


Optional useful fields: `depends_on` · `milestone_id` · `predecessor_task_id` · `gap_id`.



---

# 5. Safety filters（hard）


Candidates must:


1. Map to A/B/C/D mission goals.  
2. Be **safe autonomous work** under current gates（prefer `offline_safe`）.  
3. **Not** bypass approvals · snapshot block · spent-live bans · push.  
4. **Not** mutate production harvest/snapshot roots without explicit approved scope.  
5. **Not** invent live CNINFO scope.  
6. Route to the owning track agent（never Controller-as-substitute for track work）.  


`approval_gated` / `live_gated` candidates may be recorded on the approval queue / deferred list — they are **not** promoted to READY until the gate clears.



---

# 6. Example generators by track


| Track | Example safe autonomous candidates |
|-------|--------------------------------------|
| A | coverage gap analysis · missing field investigation · next slice **preparation**（offline） |
| B | event/source coverage expansion **prep** · taxonomy improvement · parser preparation |
| C | QA gap resolution · evidence completeness improvement |
| D | offline schema preparation · event modeling · approval package preparation · sample prep · validation rules · offline evidence mapping |


`approval_gated` / `live_gated` go to **Approval Queue** only. Autonomous examples above stay generatable while WAITING_APPROVAL.


These are templates — concrete candidates must cite evidence paths and gap ids.



---

# 7. Promotion / dynamic queue


```text
recalculate A/B/C/D gaps
    ↓
generate candidates（from fresh gaps + memory）
    ↓
filter by safety + memory
    ↓
assign into per-track Autonomous Queues（+ Approval Queues）
    ↓
gap-align + priority rank（global + within-track）
    ↓
select highest-value target under fairness / queue availability
    ↓
dispatch required_agent
    ↓
after completion → validate/evidence/memory → request next from track queue → Controller re-score → continue or replan
```


Stale candidates from a prior wave that no longer match gaps may be dropped or deferred.  
If zero candidates survive filters after reassessment → run **candidate audit**（per track: considered / rejected / reason / **stop_reason**）→ only then may cycle use `NO_VALUABLE_SAFE_TASK` / `NO_SAFE_READY`（after stuck analysis if repeats）.  
A single track `HUMAN_GATE_BLOCKED` is **not** sufficient for global stop.  



---

# 8. Anti-patterns


Forbidden:


- stop on empty queue without generation  
- generate live/approval fiction to fill budget  
- duplicate completed memory entries  
- Controller-only busywork labeled as A/B/C/D mission progress  
- candidates without `expected_capability_improvement`  
- treating a generated batch as a fixed todo list that must be fully drained before replan  
- skipping A/B/C/D gap recalculation because leftover candidates exist  
- generating candidates without state refresh  
- stopping with NO_VALUABLE_SAFE_TASK without recording rejected candidates and reasons  
- removing a WAITING_APPROVAL track from autonomous generation  
- treating “D needs approval” as “D has no autonomous candidates” without checking schema/taxonomy/sample/validation offline work  
- letting one track’s easy successors monopolize generation while other tracks’ Autonomous Queues are non-empty



---


# 9. Relationship to Mission Execution Engine v3


[controller_mission_execution_engine_v3.md](controller_mission_execution_engine_v3.md)（architecture design only · 未启用）在本文件的生成/过滤/晋级流程（§3–§7）之上追加两点，均为附加式，不改变本文件的安全过滤或 approval split 规则：


1. §3 candidate audit 的 considered/rejected 输出，v3 要求同时写入 [track execution queue v2 §7.1](controller_track_execution_queue_policy_v2.md) 的持久化字段 `candidate_successors` / `rejected_tasks`，而不仅在停机报告里出现一次。
2. §2 的生成触发条件（"after every completed task"）在 v3 下额外接收一个 `capability_gain`（v3 §6：`CAPABILITY_ADVANCED` / `CAPABILITY_MAINTAINED` / `NO_CAPABILITY_CHANGE`）作为上下文；当结果连续为 `NO_CAPABILITY_CHANGE` 时，生成器应优先探索本文件 §6 表中**尚未尝试**的候选维度，而不是重复上一批同类候选（呼应本文件 §8 anti-pattern "duplicate completed memory entries"）。  
