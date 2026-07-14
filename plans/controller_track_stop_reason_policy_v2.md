# Controller Track Stop Reason Classification Policy v2


_最后更新：2026-07-14_  
_配套：[controller_track_execution_queue_policy_v2.md](controller_track_execution_queue_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md)_


## 1. Purpose


Differentiate **why a track is not running** so Controller and humans do not confuse:


- human approval dependency  
- current task / successor exhaustion  
- low priority deferral  
- absence of safe autonomous work  
- intentional scheduler choice  


**Transparency goal：** every track stop has exactly **one primary** `stop_reason`.



---

# 2. Primary stop reasons（normative enum）


| Code | Meaning | Typical evidence |
|------|---------|------------------|
| **HUMAN_GATE_BLOCKED** | Next *valuable* action requires human approval | Approval Queue non-empty for the next high-value step · Autonomous Queue empty **or** only low-value leftovers after audit |
| **CURRENT_TASK_COMPLETED** | Current task done and **successor candidates exhausted** for this track | Memory shows package complete · generator finds no new autonomous gap for track |
| **LOW_PRIORITY_DEFERRED** | Safe autonomous tasks exist but lower mission value than other work | Autonomous Queue non-empty · not selected this iteration |
| **NO_SAFE_AUTONOMOUS_TASK** | No safe autonomous task remains **for this track** after candidate audit | Audit: autonomous considered=0 surviving filters |
| **RESOURCE_ALLOCATED_ELSEWHERE** | Task exists but scheduler prioritizes another track | Fairness / mission impact chose B while A still queued |
| **RUNNING** | Track currently has an active dispatched task | `active_task` set |
| **BUDGET_HOLD** | Track paused because daily iteration/runtime/commit budget hit | Budget counters exhausted mid-queue |


Optional secondary notes allowed; **primary** must be one enum above.



---

# 3. Classification rules


### 3.1 HUMAN_GATE_BLOCKED


Use when:


1. The next **mission-valuable** step for the track is approval-gated（live · snapshot execute · Level-2 phrase · push）, **and**  
2. Autonomous Queue is empty **or** remaining autonomous items are memory-equivalent / low-value after audit.  


Examples:


- C production snapshot execute gate · prep already done  
- D S4 runner / S5 live gates after offline package complete  
- B live retry awaiting phrase（prep already done）  


### 3.2 CURRENT_TASK_COMPLETED


Use when the just-finished task has no valuable successor **and** the track’s autonomous gap set is empty — distinct from “waiting forever for live.” Prefer this when the offline chain is honestly finished, not when live is the only remaining high-value step（that is `HUMAN_GATE_BLOCKED`）.


### 3.3 LOW_PRIORITY_DEFERRED


Safe Autonomous Queue items exist; Controller deferred them because other tracks’ work has higher mission impact / bottleneck reduction this iteration.


### 3.4 NO_SAFE_AUTONOMOUS_TASK


After full per-track candidate audit, zero autonomous candidates survive safety + memory filters. Approval Queue may still be non-empty.


### 3.5 RESOURCE_ALLOCATED_ELSEWHERE


Autonomous Queue non-empty and READY, but this iteration’s dispatch went to another track under resource allocation / fairness.



---

# 4. Global stop vs track stop（critical）


| Level | Allowed when |
|-------|--------------|
| **Track** `HUMAN_GATE_BLOCKED` | That track’s next valuable path needs human — **other tracks may continue** |
| **Global** `NO_VALUABLE_SAFE_TASK` | **All** tracks have no dispatchable autonomous READY work after full A/B/C/D audit |


### Hard rules


1. **Do NOT** interpret `HUMAN_GATE_BLOCKED` as global `NO_VALUABLE_SAFE_TASK`.  
2. **Do NOT** remove a track from planning because its live path is blocked.  
3. A blocked live task **must coexist** with autonomous offline tasks on the same track when generator can emit them.  
4. Global stop requires per-track reasons in the daily report（see schema）.  
5. If any track is `LOW_PRIORITY_DEFERRED` or `RESOURCE_ALLOCATED_ELSEWHERE` with non-empty queue → global stop is **invalid** until those queues are drained or reclassified.  



---

# 5. Mapping to candidate audit rejection reasons


| Audit rejection | Typical track stop_reason |
|-----------------|---------------------------|
| requires_approval | `HUMAN_GATE_BLOCKED`（if that was the next valuable path） |
| already_completed / duplicate | contribute to `CURRENT_TASK_COMPLETED` or `NO_SAFE_AUTONOMOUS_TASK` |
| low_mission_value | `LOW_PRIORITY_DEFERRED` if still queued; else drop |
| unsafe | never enqueue · may yield `NO_SAFE_AUTONOMOUS_TASK` |



---

# 6. Reporting（required）


Daily report **must** include Track Queue Status with `stop_reason` per track, plus rollups:


```text
Human blocked:     # tracks with HUMAN_GATE_BLOCKED
Priority deferred: # LOW_PRIORITY_DEFERRED
No safe task:      # NO_SAFE_AUTONOMOUS_TASK
Resource elsewhere:# RESOURCE_ALLOCATED_ELSEWHERE
Next recommended action:
```



---

# 7. Anti-patterns


Forbidden:


- labeling D `NO_SAFE_AUTONOMOUS_TASK` when only S5 live remains and offline chain is done → use `HUMAN_GATE_BLOCKED`  
- stopping the whole day because one track is `HUMAN_GATE_BLOCKED` while others have Autonomous Queues  
- omitting `stop_reason` on idle tracks  
- inventing a sixth primary reason without policy update  
