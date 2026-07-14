# Controller Mission Replanning Loop v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_task_continuation_policy_v2.md](controller_task_continuation_policy_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_stuck_detection_policy_v2.md](controller_stuck_detection_policy_v2.md) · [controller_track_execution_queue_policy_v2.md](controller_track_execution_queue_policy_v2.md) · [controller_track_stop_reason_policy_v2.md](controller_track_stop_reason_policy_v2.md)_


## 1. Purpose


Upgrade Daily Autonomous Loop v2 from **batch task execution** into a **continuously replanning** autonomous system that keeps optimizing toward:


> Full-market listed company intelligence platform


### Problem this solves


| Batch todo behavior（failure mode） | Mission replanning（required） |
|------------------------------------|-------------------------------|
| Generate A/B/C/D candidates once | Reassess mission after **every** completion |
| Execute fixed list | Dynamic queue · next target from fresh gaps |
| Commit then stop when list ends | Continue until reassessment finds no valuable safe work |
| “Todo batch complete” = day done | Completed package ≠ mission complete |



---

# 2. Continuous execution model（normative）


```text
State refresh（mandatory）
    ↓
Mission state assessment
    ↓
Generate highest-value target
    ↓
Assign track agent
    ↓
Execute task
    ↓
Collect evidence
    ↓
Validate result（evidence reviewer when required）
    ↓
Commit bounded changes（if commit budget remains）
    ↓
Update memory
    ↓
State refresh again
    ↓
Recalculate mission gaps（A · B · C · D）
    ↓
Generate next target
    ↓
Continue
```


**Critical rule：** Generated tasks are **NOT** a fixed todo list. The queue is **dynamic**.


After every completed task, Controller **MUST** re-evaluate:


- A capability gap  
- B capability gap  
- C capability gap  
- D capability gap  


**before** deciding the next task — even if unused candidates remain from an earlier generation wave.


Do **not** generate successor tasks from **stale** state（§2.1）.



---

# 2.1 State Refresh Requirement（normative）


**Before every replanning cycle**（including the first assessment and every post-task replan）, Controller MUST refresh:


| Refresh domain | Minimum sources |
|----------------|-----------------|
| **git state** | `git status` · HEAD · ahead/behind · dirty summary · worktree tips when relevant |
| **evidence state** | cited validation artifacts · latest package paths for active gaps |
| **task memory** | completed / failed / deferred / rejected / blockers |
| **progress metrics** | progress tracking signals · baseline / report numerators |
| **track status** | PROJECT_CONTROL + git reality for A/B/C/D（READY/HOLD/WAITING/…） |


Record `state_refresh_timestamp`（ISO local or UTC）in the cycle log / stop report.


Forbidden:


- replan using only the previous iteration’s in-memory snapshot  
- generating successors from an outdated generated-task file without re-reading git/evidence/memory  
- treating HOLD labels from an old control prose as fresher than git/evidence  



---

# 2.2 Candidate Audit（before NO_VALUABLE_SAFE_TASK）


Before stopping with **`NO_VALUABLE_SAFE_TASK`**（alias of execution-cycle `NO_SAFE_READY` after full reassessment）, Controller **MUST** record a candidate audit.


**`NO_VALUABLE_SAFE_TASK` is valid only after all tracks A/B/C/D are checked.**


Per track **A / B / C / D**（required shape）:


```text
Track: A|B|C|D
  autonomous candidates:
  approval blockers:
  Candidates considered:
  Rejected candidates:
  Reason rejected:   # requires approval | unsafe | duplicate | already completed | low mission value | other
```


Aggregate stop packet:


```text
Candidate search summary:
  tracks_searched: A,B,C,D
  considered_count:
  rejected_count:
  rejection_breakdown: { requires_approval, unsafe, duplicate, already_completed, low_mission_value, other }
Track queue status:
  A: active_task / queued_tasks / stop_reason
  B: active_task / queued_tasks / stop_reason
  C: active_task / queued_tasks / stop_reason
  D: active_task / queued_tasks / stop_reason
Human blocked:     # tracks with HUMAN_GATE_BLOCKED
Priority deferred: # LOW_PRIORITY_DEFERRED
No safe task:      # NO_SAFE_AUTONOMOUS_TASK
Why no higher-value task exists:
Track execution balance:
  A iterations:
  B iterations:
  C iterations:
  D iterations:
  Last executed iteration per track:
Next recommended action:
```


Rules:


1. Audit is required even when the answer is “only human-gated work remains.”  
2. “HOLD exists” / “WAITING_APPROVAL” is **not** a sufficient Why — list **autonomous candidates** considered and why rejected.  
3. Duplicate / already completed reasons must cite task memory ids when available.  
4. Skipping candidate audit before `NO_VALUABLE_SAFE_TASK` is a policy violation.  
5. Skipping any of A/B/C/D in the audit is a policy violation.  
6. If a track shows non-empty **autonomous candidates** that were never dispatched while another track dominated iterations → stop reason must explain fairness failure or execute that track before stopping.  
7. Per-track `stop_reason` from [stop-reason policy](controller_track_stop_reason_policy_v2.md) is **required** in the audit packet.  
8. Global `NO_VALUABLE_SAFE_TASK` is **invalid** if any track is `LOW_PRIORITY_DEFERRED` or `RESOURCE_ALLOCATED_ELSEWHERE` with a non-empty Autonomous Queue, or if any track still has dispatchable autonomous READY work.  
9. Tracks that are only `HUMAN_GATE_BLOCKED` do **not** by themselves authorize global stop.  



---

# 3. Agent loop（roles）


Each task lifecycle:


```text
Controller:        state refresh → find target（mission planner）
    ↓
Track agent:       execute（a/b/c/d-class-executor）
    ↓
Evidence reviewer: validate output（when policy requires）
    ↓
Commit manager:    bounded explicit-path commit（Controller commit gate）
    ↓
Controller:        update state + memory
    ↓
Mission planner:   state refresh → find next target（replan）
```


Controller coordinates and replans. Track agents execute. Reviewers stay read-only. Commit manager enforces batching + autonomy policy.  
Controller **must not** replace track agents for A/B/C/D capability work.



---

# 4. Dynamic queue rules


1. A prior generated list is a **hint**, not a binding schedule.  
2. After each completion: discard stale READY items that no longer match recalculated gaps（or re-rank them against fresh gaps）.  
3. Prefer the **single highest-value** next target under **track fairness**（resource allocation v2）— not endless same-track successors.  
4. Do not “drain one easy track” while other tracks’ Autonomous Queues are non-empty.  
5. Continuation + generator + gap analysis + **approval split** are invoked **every** post-task replan.  
6. WAITING_APPROVAL on live work does **not** remove the track from autonomous replan.  
7. Maintain **per-track Autonomous Queues** per [track execution queue v2](controller_track_execution_queue_policy_v2.md)：after validate/evidence/memory, a track may request its **next queued** Controller-approved autonomous task — Controller still re-scores before dispatch.  
8. Every idle track must carry a primary [stop reason](controller_track_stop_reason_policy_v2.md)；`HUMAN_GATE_BLOCKED` ≠ global `NO_VALUABLE_SAFE_TASK`.  


---

# 4.1 Post-task per-track continuation（normative）


```text
Task complete on track T
    ↓
Validate · evidence · memory · bounded commit
    ↓
Controller state refresh + re-score T’s Autonomous Queue
    ↓
If T queue head still READY and selected under allocation:
      dispatch next T task（same-track continuation）
Else if other tracks have higher-value READY:
      set T stop_reason = RESOURCE_ALLOCATED_ELSEWHERE or LOW_PRIORITY_DEFERRED
      dispatch other track
Else if T only has approval-gated next valuable work:
      set T stop_reason = HUMAN_GATE_BLOCKED
      continue other tracks’ Autonomous Queues
Else:
      set T stop_reason = CURRENT_TASK_COMPLETED or NO_SAFE_AUTONOMOUS_TASK
```


Do **not** idle the whole day when only one track is `HUMAN_GATE_BLOCKED`.  



---

# 5. Stop conditions


Stop **only** when:


1. **`NO_VALUABLE_SAFE_TASK`** — no valuable safe autonomous task exists after state refresh + full mission reassessment + **candidate audit**, **or**  
2. **Human interrupt** required（interrupt policy）, **or**  
3. **Execution budget** reached for actions that still need iteration/runtime（see §6 for commit nuance）, **or**  
4. **Safety violation**.  


### Do NOT stop because


- generated task list finished  
- one agent finished  
- one track finished a package  
- HOLD / WAITING_APPROVAL exists on some tracks  
- “we already did A/B/C/D once today”  



---

# 6. Budget rules


Budget is a **safety boundary**, not a completion condition for the mission.


| Budget | When hit |
|--------|----------|
| `max_iterations` / `max_runtime` | stop further agent execute cycles · write report |
| `max_autonomous_commits` | **stop additional commits** · may continue **reasoning / gap recalculation / reporting** without new commits |


Do not treat commit-budget exhaustion as “mission complete.”  
Do not invent live work to “use remaining iteration budget.”



---

# 7. Final report fields（required）


Every stop / daily report under replanning must include:


```text
State refresh timestamp:
Completed this cycle:
Generated next targets:
Current mission gaps:
Candidate search summary:
  Track A — autonomous candidates / approval blockers / rejected / reasons:
  Track B — autonomous candidates / approval blockers / rejected / reasons:
  Track C — autonomous candidates / approval blockers / rejected / reasons:
  Track D — autonomous candidates / approval blockers / rejected / reasons:
Why no higher-value task exists:
Why stopped:
Next recommended autonomous target:
Track execution balance:
  A iterations:
  B iterations:
  C iterations:
  D iterations:
  Last executed iteration per track:
```


Plus existing Progress / Planning intelligence blocks.



---

# 8. Integration


| Authority | Role |
|-----------|------|
| This file | continuous replan model · dynamic queue · stop/budget semantics |
| execution cycle v2 | iteration mechanics · calls replan each loop |
| task generator v2 | emit targets from **fresh** gaps · not once-per-day only |
| continuation v2 | post-task gap-closed check feeds replan |
| gap analysis v2 | recalculate A/B/C/D gaps every replan |
| stuck detection v2 | prevent endless equivalent regenerations |
| Daily Loop v2 | host algorithm |



---

# 9. Anti-patterns


Forbidden:


- generate four tasks · execute all · stop without reassessment  
- treat unused generated candidates as mandatory remaining todos  
- skip A/B/C/D gap recalculation because “list not empty”  
- stop solely because HOLD labels exist  
- claim mission progress from controller maintenance while skipping replan  
- replan from stale state without §2.1 refresh  
- declare `NO_VALUABLE_SAFE_TASK` without §2.2 candidate audit  
- skip D/B/C autonomous planning because live approval is pending  
- allow one track to consume all iterations while other Autonomous Queues are non-empty  
