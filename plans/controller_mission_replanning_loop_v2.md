# Controller Mission Replanning Loop v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_task_continuation_policy_v2.md](controller_task_continuation_policy_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_stuck_detection_policy_v2.md](controller_stuck_detection_policy_v2.md)_


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


Per track **A / B / C / D**:


```text
Track: A|B|C|D
Candidates considered:
Rejected candidates:
Reason rejected:   # one of: requires approval | unsafe | duplicate | already completed | low mission value | other（cite）
```


Aggregate stop packet:


```text
Candidate search summary:
  tracks_searched: A,B,C,D
  considered_count:
  rejected_count:
  rejection_breakdown: { requires_approval, unsafe, duplicate, already_completed, low_mission_value, other }
Why no higher-value task exists:
```


Rules:


1. Audit is required even when the answer is “only human-gated work remains.”  
2. “HOLD exists” is **not** a sufficient Why — list considered offline_safe ideas and why rejected.  
3. Duplicate / already completed reasons must cite task memory ids when available.  
4. Skipping candidate audit before `NO_VALUABLE_SAFE_TASK` is a policy violation.  



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
3. Prefer the **single highest-value** next target（or parallel-safe wave only when isolation + gain justify）.  
4. Do not “drain the original four” out of habit if replanning shows a different bottleneck.  
5. Continuation policy + task generator + gap analysis are invoked **every** post-task replan.  



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
Why no higher-value task exists:
Why stopped:
Next recommended autonomous target:
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
