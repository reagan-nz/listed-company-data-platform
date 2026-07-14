# Controller Milestone Management v2


_最后更新：2026-07-14_  
_配套：[controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md)_


## 1. Purpose


Divide the ultimate mission — **full-market listed company intelligence platform** — into **milestones** so Daily Loop planning has intermediate goals, metrics, and completion criteria.


Milestones guide generation, allocation, and progress reporting.  
They do **not** authorize live, push, or gate flips.



---

# 2. Milestone schema


Each milestone contains:


```text
milestone_id:
track:                 # A | B | C | D | cross
goal:
metrics:               # measurable signals（coverage counts · QA completeness · components closed）
completion_criteria:   # evidence-backed · caveat-honest
dependencies:          # other milestones · approvals · none
status:                # planned | in_progress | blocked | completed_with_caveat | completed
```



---

# 3. Example milestone ladder（illustrative · not approvals）


| ID | Track | Goal（example） |
|----|-------|----------------|
| M-A1 | A | staged expansion path closed with caveat ledger |
| M-A2 | A | unresolved residual offline-packaged · next slice prep ready |
| M-A3 | A | broader coverage toward adopted full-market denominator |
| M-B1 | B | fuller disclosure metadata path closed with deferred cases explicit |
| M-B2 | B | deferred failure offline triage + prep for approved retry/scale |
| M-C1 | C | slice QA closure with partial evidence packages |
| M-C2 | C | snapshot readiness package（still needs human flip to rebuild） |
| M-D1 | D | component first-slices closed（pledge/unlock/…） |
| M-D2 | D | next component approval package ready（e.g. shareholder_change） |
| M-X1 | cross | progress denominator policy adopted（enables % ≠ UNKNOWN） |


Exact active milestone set should live in validation memory / control notes when adopted — this file defines the **management rules**.



---

# 4. Management rules


1. Daily Loop prefers tasks that advance the **active** milestone for the allocated track.  
2. Completing a task may complete a milestone only if completion_criteria evidence exists.  
3. `completed_with_caveat` is allowed · never silently upgrade to verified/production_ready.  
4. Blocked milestones stay on approval/dependency queue · other tracks continue.  
5. Generator tags candidates with `milestone_id` when known.  



---

# 5. Reporting


Daily report should state:


- active milestones  
- milestones advanced this run  
- blocked milestones + dependencies  



---

# 6. Anti-patterns


Forbidden:


- one giant “full market done” milestone with no metrics  
- marking milestone complete because commits landed  
- using milestones to justify unauthorized live/push  
