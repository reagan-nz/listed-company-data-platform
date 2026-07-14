# Controller Task Generator Policy v2


_最后更新：2026-07-14_  
_配套：[controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_task_memory_policy_v2.md](controller_task_memory_policy_v2.md) · [controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md)_


## 1. Purpose


When the Daily Autonomous Loop queue has **no READY task**, Controller must **generate** safe autonomous candidate tasks — not stop immediately.


This policy is the **task generation** authority behind Task Discovery.  
It turns mission + progress + gaps + memory into structured candidates for ranking and agent routing.



---

# 2. When to generate


Run the generator when **any** of:


1. Refresh yields empty safe READY set.  
2. Continuation policy requests a successor after a completed task.  
3. Stuck detection asks for alternative autonomous actions.  
4. Gap analyzer emits actionable gaps without an existing READY task.  


Do **not** skip generation solely because PROJECT_CONTROL shows HOLD / WAITING_APPROVAL.



---

# 3. Analysis inputs


Before emitting candidates, analyze:


| Input | Source |
|-------|--------|
| Mission objective | mission objective v2 · A/B/C/D goals |
| Progress intelligence | progress tracking v2 · latest baseline/report |
| Track gaps | capability gap analysis v2 |
| Historical tasks | task memory v2（completed / failed / deferred / rejected / blockers） |


Reject candidates that memory marks as completed-equivalent, human-rejected, or known-blocked approaches.



---

# 4. Candidate schema（required）


Each candidate **must** contain:


```text
task_id:              # stable id e.g. A-GEN-20260714-01
track:                # A | B | C | D
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
| D | offline schema preparation · event modeling · approval package preparation |


These are templates — concrete candidates must cite evidence paths and gap ids.



---

# 7. Promotion


```text
generate candidates
    ↓
filter by safety + memory
    ↓
gap-align + priority rank
    ↓
promote offline_safe → READY
    ↓
dispatch required_agent
```


If zero candidates survive filters → only then may cycle use `NO_SAFE_READY`（after stuck analysis if repeats）.



---

# 8. Anti-patterns


Forbidden:


- stop on empty queue without generation  
- generate live/approval fiction to fill budget  
- duplicate completed memory entries  
- Controller-only busywork labeled as A/B/C/D mission progress  
- candidates without `expected_capability_improvement`  
