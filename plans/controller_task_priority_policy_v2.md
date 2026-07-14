# Controller Task Priority Policy v2


_最后更新：2026-07-14_  
_配套：[controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md)_


## 1. Purpose


定义 Daily Autonomous Loop v2 在 **multi-iteration execution** 中，如何从安全 READY 队列选出 **next highest-value task**。


本政策是 execution cycle「Select highest-value safe task」步骤的权威规则。  
Safety gate 先于 priority：unsafe / approval-missing 任务永不入选，无论优先级多高。


**System intent：** Daily Loop is a **mission-progress execution system** for full-market A/B/C/D capability — **not** a controller self-maintenance loop.



---

# 2. Mission Progress Priority（hard order）


When ranking any candidate set, apply this **hard order** before fine-grained P1–P5:


```text
A/B/C/D capability progress
        >
Evidence improvement（track QA / validation / evidence completeness）
        >
Controller maintenance（policy docs · controller reports · tip-align · OS plumbing）
```


### Normative consequences


1. **Business track progress must always outrank controller maintenance.**  
2. Controller **must not** consume iteration / commit / runtime budget on self-updates when **any** safe mission or track-evidence work exists（including discovered candidates §4）.  
3. Controller-only packages（progress baseline rewrite · approval-queue redo · policy tip-chasing · daily-report microcommits）are **maintenance** unless they are the **sole** remaining safe work after discovery.  
4. A day that only lands controller docs while safe A/B/C/D offline mission candidates were discoverable is a **policy failure**.  



---

# 3. Priority ladder（normative）


Only tasks already classified as **safe READY**（execution cycle + interrupt + commit policies）enter ranking — including candidates produced by **task discovery**（execution cycle / Daily Loop）.


| Rank | Class | Prefer tasks that… | Hard-order band |
|------|-------|--------------------|-----------------|
| **P1** | Mission progress | directly increase full-market coverage · capability completion · data availability on **A/B/C/D** | capability |
| **P2** | Bottleneck reduction | raise the lowest-progress **track** · or unblock multiple future **track** tasks | capability |
| **P3** | Evidence and quality | improve **track** validation · QA · evidence completeness | evidence |
| **P4** | Maintenance | documentation · cleanup · refactoring · **controller OS / report plumbing** | controller |
| **P5** | Optional improvements | nice-to-have polish · non-blocking extras | controller |


### Ranking procedure


1. Discard unsafe / approval-missing / red-line actions.  
2. Apply **Mission Progress Priority**（§2）：drop or defer controller-band items if any capability/evidence-band candidate remains.  
3. Assign each remaining candidate its **highest applicable** P1–P5 class.  
4. Sort by class ascending（P1 first）.  
5. Within the same class, apply §5 selection factors.  
6. Emit the top task（or parallel-safe wave）to the cycle executor **via the owning track agent**（Daily Loop agent routing）.  


A task may touch multiple classes; use the **highest** class it materially advances（e.g. track QA that also unblocks scale → P2 if bottleneck-clearing is primary, else P3）.



---

# 4. Discovery vs invention


| Allowed | Forbidden |
|---------|-----------|
| Discover **safe offline** mission candidates from A/B/C/D objectives when queue looks empty | Invent **live** / approval-bypass / gate-flip work |
| Promote discovered safe candidates to READY for ranking | Fabricate busywork to burn budget |
| Prefer track capability/evidence candidates over controller maintenance | Treat “tracks are HOLD” as “no work exists” without discovery |


Discovery examples（must still pass safety）:


| Track | Example safe autonomous candidates |
|-------|--------------------------------------|
| A | coverage expansion **analysis** · missing-scope / unresolved caveat offline packaging · attribute-gap ledger（no live） |
| B | new disclosure/event **preparation** · deferred-case offline triage notes · extraction-gap matrix（no live） |
| C | QA/evidence **improvement** · caveat ledger hardening · validation completeness offline（no snapshot flip） |
| D | offline **component preparation** · approval-ready planning refresh · universe sketch（no unapproved live） |



---

# 5. Selection factors（within same priority class）


When comparing same-class READY tasks, weigh:


| Factor | Prefer |
|--------|--------|
| **mission impact** | larger gain toward full-market A/B/C/D capability |
| **blocked dependencies** | clears gates that unlock more **track** READY work downstream |
| **estimated effort** | smaller effort **only as tie-break** after impact/unblock — never as primary sort |
| **safety level** | lower risk class first when impact is comparable（offline > live；track evidence > controller docs） |


### Explicit anti-preferences


Avoid:


- choosing **easy controller tasks only** while mission candidates exist or are discoverable  
- **skipping task discovery** and declaring `NO_SAFE_READY` because PROJECT_CONTROL shows HOLD  
- generating **artificial** READY（live/approval fiction）to keep the cycle busy  
- **ignoring bottlenecks** while polishing P4/P5 controller work  
- picking P4/P5 while any safe P1–P3 **track** READY remains  
- inventing live scope to inflate “mission progress”  
- Controller replacing a-class / b-class / c-class / d-class executors for track progress tasks  



---

# 6. Mapping to tracks（guidance）


| Track goal（mission objective） | Typical high-value signals |
|--------------------------------|----------------------------|
| A — company information coverage | company/attribute coverage gains · missing-scope closure |
| B — disclosure/event coverage | source/extraction coverage · event completeness |
| C — evidence and quality | validation coverage · evidence completeness · QA status（not gate flip） |
| D — shareholder/capital | shareholder coverage · ownership events · capital structure completeness |


HOLD / WAITING_APPROVAL blocks **live / approval-gated** actions — **not** all offline discovery.  
Known gates stay on the approval queue without global stop. Discovered offline candidates that do not bypass those gates may still be READY.



---

# 7. Parallel waves


When multiple top candidates:


1. Prefer one P1 **track** task over many P5 controller tasks.  
2. May run parallel if worktree isolation allows and none shares a protected root conflict.  
3. Do not dilute a P1 wave with controller P4 filler in the same iteration.  
4. If **only** controller P4/P5 remain **after discovery** and budget remains → allowed；report class honestly as maintenance.  



---

# 8. Relationship to other policies


| Policy | Role vs priority |
|--------|------------------|
| mission objective v2 | defines what “mission progress” means |
| progress tracking v2 | supplies coverage / bottleneck inputs for P1–P2 |
| execution cycle v2 | discovery before `NO_SAFE_READY` · budget · commit batching |
| interrupt / commit autonomy | hard filters before ranking |
| Daily Loop algorithm | `discover_safe_candidates` → `select_highest_value_safe_tasks` → `dispatch_track_agent` |


Conflict rule: **safety / approval / red lines outrank priority**.  
Priority conflict rule: **mission/track work outranks controller maintenance**.



---

# 9. Decision record（per iteration）


Each iteration should briefly record:


```text
selected_task:
  track: A|B|C|D|controller
  agent: a-class-executor|b-class-executor|c-class-executor|d-class-executor|controller
  priority_class: P1|P2|P3|P4|P5
  hard_order_band: capability|evidence|controller
  discovered: true|false
  rationale:
  rejected_higher: none | <why unsafe or not READY>
  factors: { mission_impact, blocked_dependencies, estimated_effort, safety_level }
```


Do not fabricate numeric scores. Qualitative rationale + class is enough.



---

# 10. Anti-patterns


Forbidden:


- first operational failure mode: **controller maintenance loop**（policy/report commits only · 0 track agents · claim complete）  
- “docs cleanup first because it’s quick” while P1/P2 track work exists or is discoverable  
- marking HOLD live work as READY to force P1 selection  
- skipping bottleneck track’s safe offline prep because controller refactor is easier  
- treating commit count or file count as mission impact  
- using priority to justify push / live / gate promotion  
- burning `max_autonomous_commits` on tip-align microcommits while mission batches are pending  
