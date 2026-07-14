# Controller Track Execution Queue Policy v2


_最后更新：2026-07-14_  
_配套：[controller_track_stop_reason_policy_v2.md](controller_track_stop_reason_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_resource_allocation_policy_v2.md](controller_resource_allocation_policy_v2.md) · [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md)_


## 1. Purpose


Allow each track **A / B / C / D** to maintain a **dynamic autonomous execution queue** so that completing one task does not idle the track while Controller-approved safe successors still exist.


### Problem this solves


| Failure mode | Required behavior |
|--------------|-------------------|
| Task complete → wait only for global replan → track idle | Track may pull **next queued autonomous task** after local validate/evidence/memory |
| One task per track per wave then stop | Per-track queue drained under safety + mission priority |
| Live gate open → entire track abandoned | Approval Queue coexists; Autonomous Queue continues |


**Throughput goal：** improve multi-track progress **without** forcing low-value or unsafe work.



---

# 2. Architecture


```text
Controller:
  state refresh
      ↓
  generate global mission candidates
      ↓
  safety filter + approval split
      ↓
  assign into per-track Autonomous Queues（+ Approval Queues）
      ↓
  schedule / dispatch under resource allocation

A queue:  A-task-001 → A-task-002 → A-task-003
B queue:  B-task-001 → B-task-002
C queue:  C-task-001 → C-task-002
D queue:  D-task-001 → D-task-002
```


Queues are **hints owned by Controller**, not agent-invented schedules.  
After every completion, Controller **re-scores** queues against fresh gaps（mission replanning）— stale items may be dropped.



---

# 3. Queue membership rules（normative）


### 3.1 What may enter an Autonomous Queue


A task may be enqueued only if **all** hold:


1. Emitted by Controller candidate generation（or continuation）from **fresh** gaps  
2. `queue = autonomous` · `safety_class = offline_safe`（or spent-scope only）  
3. Passes safety filters（no invent live · no approval bypass · no unprotected prod mutation · no push）  
4. Has **explicit scope**（paths · caps · write-blocks · CNINFO=0 when offline）  
5. Aligns with mission priority / gap id  
6. Not memory-equivalent to a completed or human-rejected package  


### 3.2 What must stay on Approval Queue only


- live CNINFO / harvest / snapshot **execute**  
- gates needing new Level-2 phrases  
- push / WT-sync / remote merge  
- scope expansion beyond Controller-approved bounds  


### 3.3 Agents must not


- invent live tasks  
- bypass approvals  
- expand scope without Controller review  
- promote Approval Queue items to Autonomous Queue  
- continue after `NO_SAFE_AUTONOMOUS_TASK` or `HUMAN_GATE_BLOCKED` without new Controller assignment  



---

# 4. Post-task track continuation（normative）


When a track agent finishes a dispatched task:


```text
1. Validate output（evidence reviewer when required）
2. Update evidence package
3. Update task memory（via Controller）
4. Bounded commit if commit autonomy allows（Controller gate）
5. Request next task from this track’s Autonomous Queue
6. Continue only if Controller confirms the next item is still READY + valuable
```


### Controller gate on step 5–6


Before handing the next queued item:


1. **State refresh**（git · evidence · memory · progress · track status）  
2. Re-score: drop stale / duplicate / now-blocked items  
3. Apply [stop reason](controller_track_stop_reason_policy_v2.md) if queue empty or only approval work remains  
4. Apply [resource allocation](controller_resource_allocation_policy_v2.md)：another track may take the next iteration（`RESOURCE_ALLOCATED_ELSEWHERE`）  
5. Only then dispatch the next Autonomous Queue head（or a newly generated higher-value task）  


**Track queue ≠ unlimited autonomy.** Continuation is always Controller-mediated.



---

# 5. Parallelism vs single-track drain


| Mode | When |
|------|------|
| **Parallel multi-track** | Isolation allows · fairness requires · budget allows |
| **Same-track continuation** | Queue non-empty · item still highest-value under fairness · not over-serving |
| **Switch track** | Staleness boost · higher mission impact elsewhere · queue availability elsewhere |


Soft fairness remains: do not drain one easy track’s entire queue while other Autonomous Queues sit idle for ≥2 iterations.



---

# 6. Example — D after offline package


D finishes shareholder_change offline package.


**Wrong：** D stops permanently · day reports `NO_VALUABLE_SAFE_TASK` because live is blocked.


**Right：**


```text
D Autonomous Queue（examples）:
  next validation / VR matrix task
  next evidence mapping refinement
  next fixture offline validation
```


If Autonomous Queue empty and only S4/S5 live/runner remain:


```text
D stop_reason = HUMAN_GATE_BLOCKED
```


**not** global `NO_VALUABLE_SAFE_TASK` solely because D’s live path is blocked（other tracks may still have autonomous work）.



---

# 7. Queue status fields（for reports）


Per track:


```text
active_task:     # task_id or none
queued_tasks:    # ordered list of autonomous task_ids still READY
stop_reason:     # see stop-reason policy · or RUNNING
approval_queued: # human-gated items（not dispatchable）
```



---

# 8. Safety


- No live execution changes by this policy alone  
- No push · no approval bypass · no automatic scope expansion  
- No production harvest/snapshot mutation without explicit approved scope  
- Queue continuation never invents CNINFO live work  



---

# 9. Anti-patterns


Forbidden:


- agent self-scheduling tasks not in Controller Autonomous Queue  
- treating Approval Queue as Autonomous Queue  
- forcing equal queue lengths / equal drain rates  
- continuing low-value queue items to “keep busy” when higher-value work exists elsewhere  
- reporting track idle as `NO_VALUABLE_SAFE_TASK` when reason is actually `HUMAN_GATE_BLOCKED`  
