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

# 6. Example — D after offline package（2026-07-15 更新，对齐 Scope-Driven Execution Model）


D finishes shareholder_change offline package. Component scope（shareholder_change）已被人类授权。


**Wrong：** D stops permanently · day reports `NO_VALUABLE_SAFE_TASK` or `HUMAN_GATE_BLOCKED` because live/runner implementation is treated as approval-gated.


**Right：**


```text
D Autonomous Queue（examples，scope 已授权后）:
  next validation / VR matrix task
  next evidence mapping refinement
  next fixture offline validation
  S4 runner implementation           # NEW — 属于 scope 内自主执行，不是审批缺口
  S5 CNINFO live execution            # NEW — 同上
```


If the D component scope is **authorized**, S4/S5 implementation and live execution **belong to the Autonomous Queue** — they use `exec_status = READY|RUNNING|COMPLETED|FAILED|WAITING_RETRY`（[track stop reason v2 §2.1](controller_track_stop_reason_policy_v2.md)), not `HUMAN_GATE_BLOCKED`.


`D stop_reason = HUMAN_GATE_BLOCKED`（now `HUMAN_DECISION_REQUIRED`）only applies when:


```text
- D's next step is push, or
- D's next step is a truly irreversible/destructive production action, or
- the shareholder_change scope itself has NOT yet been authorized by a human
```


**not** global `NO_VALUABLE_SAFE_TASK` solely because D's live path is blocked（other tracks may still have autonomous work）— this hard rule from track stop reason v2 §4 is unchanged.



---

# 7. Queue status fields（for reports）


Per track:


```text
active_task:     # task_id or none
queued_tasks:    # ordered list of autonomous task_ids still READY
stop_reason:     # see stop-reason policy · or RUNNING
approval_queued: # human-gated items（not dispatchable）
```


## 7.1 v3 additive fields（optional · backward compatible）


[controller_mission_execution_engine_v3.md §4](controller_mission_execution_engine_v3.md) 定义了两个**可选、追加式**字段，persist 此前只在 candidate audit（mission replanning loop v2 §2.2）里临时出现一次的 considered/rejected 信息，供跨轮 replan 直接复用。旧 Controller 若不读取这两个字段，行为不受影响；`active_task` / `queued_tasks` / `stop_reason` / `approval_queued` 的既有语义**不变**：


```text
candidate_successors:  # generator v2 产出但尚未晋级 queued_tasks 的候选（可选）
rejected_tasks:         # 持久化拒绝记录，每条含 task_id + reason_rejected（可选）
                        #   reason_rejected ∈ {requires_approval, unsafe, duplicate,
                        #                       already_completed, low_mission_value, other}
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
