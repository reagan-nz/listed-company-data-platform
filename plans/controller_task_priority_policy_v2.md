# Controller Task Priority Policy v2


_最后更新：2026-07-14_  
_配套：[controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md)_


## 1. Purpose


定义 Daily Autonomous Loop v2 在 **multi-iteration execution** 中，如何从安全 READY 队列选出 **next highest-value task**。


本政策是 execution cycle「Select highest-value safe task」步骤的权威规则。  
Safety gate 先于 priority：unsafe / approval-missing 任务永不入选，无论优先级多高。



---

# 2. Priority ladder（normative）


Only tasks already classified as **safe READY**（execution cycle + interrupt + commit policies）enter ranking.


| Rank | Class | Prefer tasks that… |
|------|-------|--------------------|
| **P1** | Mission progress | directly increase full-market coverage · capability completion · data availability |
| **P2** | Bottleneck reduction | raise the lowest-progress track · or unblock multiple future tasks |
| **P3** | Evidence and quality | improve validation · QA · evidence completeness |
| **P4** | Maintenance | documentation · cleanup · refactoring（bounded · no behavior risk expansion） |
| **P5** | Optional improvements | nice-to-have polish · non-blocking UX/docs extras |


### Ranking procedure


1. Assign each candidate its **highest applicable** priority class（P1–P5）.  
2. Sort by class ascending（P1 first）.  
3. Within the same class, apply §3 selection factors.  
4. Emit the top task（or parallel-safe wave of non-conflicting tops）to the cycle executor.  


A task may touch multiple classes; use the **highest** class it materially advances（e.g. QA package that also unblocks scale → score as P2 if bottleneck-clearing is primary, else P3）.



---

# 3. Selection factors（within same priority class）


When comparing same-class READY tasks, weigh:


| Factor | Prefer |
|--------|--------|
| **mission impact** | larger gain toward full-market A/B/C/D capability（progress tracking denominators） |
| **blocked dependencies** | clears gates that unlock more READY work downstream |
| **estimated effort** | smaller effort **only as tie-break** after impact/unblock — never as primary sort |
| **safety level** | lower risk class first when impact is comparable（offline > live；docs/evidence > source mutation） |


### Explicit anti-preferences


Avoid:


- choosing **easy tasks only**（effort-first scheduling）  
- **generating artificial READY** tasks to keep the cycle busy  
- **ignoring bottlenecks** while polishing P4/P5 work  
- picking P4/P5 while any safe P1–P3 READY remains（unless budget/safety forbids higher work）  
- inventing live scope to inflate “mission progress”  



---

# 4. Mapping to tracks（guidance）


| Track goal（mission objective） | Typical high-value signals |
|--------------------------------|----------------------------|
| A — company information coverage | company/attribute coverage gains · missing-scope closure |
| B — disclosure/event coverage | source/extraction coverage · event completeness |
| C — evidence and quality | validation coverage · evidence completeness · QA status（not gate flip） |
| D — shareholder/capital | shareholder coverage · ownership events · capital structure completeness |


HOLD / WAITING_APPROVAL tracks are **out of selection** until safe READY; their bottleneck may still elevate **other** tracks’ P2 work that reduces future wait（e.g. packaging approval packet）only when that action is itself safe READY and policy-allowed.



---

# 5. Parallel waves


When multiple top candidates:


1. Prefer one P1 over many P5.  
2. May run parallel if worktree isolation allows and none shares a protected root conflict.  
3. Do not dilute a P1 wave with P4 filler in the same iteration solely to “use budget”.  
4. If only P4/P5 remain and budget remains → allowed；report class honestly.  



---

# 6. Relationship to other policies


| Policy | Role vs priority |
|--------|------------------|
| mission objective v2 | defines what “mission progress” means |
| progress tracking v2 | supplies coverage / bottleneck inputs for P1–P2 |
| execution cycle v2 | calls this policy at select step · owns stop/budget |
| interrupt / commit autonomy | hard filters before ranking |
| Daily Loop algorithm §11 | `select_highest_value_safe_tasks(..., task_priority_v2)` |


Conflict rule: **safety / approval / red lines outrank priority**.



---

# 7. Decision record（per iteration）


Each iteration should briefly record:


```text
selected_task:
  track:
  priority_class: P1|P2|P3|P4|P5
  rationale:   # mission impact / bottleneck / quality / maintenance / optional
  rejected_higher: none | <why unsafe or not READY>
  factors: { mission_impact, blocked_dependencies, estimated_effort, safety_level }
```


Do not fabricate numeric scores. Qualitative rationale + class is enough.



---

# 8. Anti-patterns


Forbidden:


- “docs cleanup first because it’s quick” while P1/P2 READY exists  
- marking HOLD work as READY to force P1 selection  
- skipping bottleneck track’s unblock packaging because another track’s refactor is easier  
- treating commit count or file count as mission impact  
- using priority to justify push / live / gate promotion  
