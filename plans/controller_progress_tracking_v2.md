# Controller Progress Tracking v2


_最后更新：2026-07-14_  
_配套：[controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md)_


## 1. Purpose


Daily Autonomous Loop v2 不能只报告「今天做了什么」，还必须估计相对最高使命的距离：


> **Full-market listed company intelligence platform**  
> （推动 A/B/C/D 朝全市场数据采集能力前进）


本文件定义：


- progress 计量原则  
- A/B/C/D 能力覆盖指标  
- bottleneck 分析  
- effort 估计规则  
- 停机 / 日报必须输出的进度块  



---

# 2. Progress model


## 2.1 Capability unit


Progress is measured in **capability units**, not commits or files.


A capability unit is a validated, scoped achievement toward full-market coverage, for example:


- N companies with accepted metadata / harvest / component capture under a defined gate  
- a closed first-slice / scale package with explicit caveats retained  
- a QA/evidence package that materially reduces unknown scope  


Non-units（不得当作进度）：


- commit count  
- dirty file count  
- lines of markdown  
- number of agents invoked  


## 2.2 Global progress


Every stop / daily report should include:


| Field | Meaning |
|-------|---------|
| `overall_completion_pct` | estimated % toward full-market platform mission · or `unknown` |
| `completed_capability_units` | counted completed units with evidence pointers |
| `remaining_capability_units` | estimated remaining units · or `unknown` |
| `estimated_remaining_effort` | effort estimate · or `unknown` |


### Completion percentage rules


1. Prefer **coverage ratios** derived from evidence（companies covered / target universe, validated sources / planned sources）.  
2. If denominators are undefined → `overall_completion_pct = unknown`（do not invent 37.2%）.  
3. Weighted blend across A/B/C/D only when each track has a defined denominator; otherwise report per-track and leave global `unknown`.  
4. Never treat HOLD/WAITING_APPROVAL as 0% capability if prior units already exist.  
5. Never claim 100% while any of: unverified gates inflated, snapshot blocked without policy, material unresolved caveats ignored.  



---

# 3. Track progress metrics


## A-class — Full-market company information coverage


Track:


| Metric | Prefer source |
|--------|----------------|
| company coverage | effective accepted / target universe |
| attribute coverage | required fields present vs catalog |
| missing scope | unresolved / deferred / not-in-universe counts |


## B-class — Full-market disclosure / event coverage


Track:


| Metric | Prefer source |
|--------|----------------|
| source coverage | endpoints / categories validated |
| extraction coverage | acceptable retrieval / planned cases |
| event completeness | timeline/event gaps ledger |


## C-class — Full-market evidence and quality coverage


Track:


| Metric | Prefer source |
|--------|----------------|
| validation coverage | companies/sources QA-complete vs harvest universe |
| evidence completeness | required artifacts present |
| QA status | PASS_WITH_CAVEAT / partial / missing · snapshot readiness（not approval） |


## D-class — Full-market shareholder / capital structure coverage


Track:


| Metric | Prefer source |
|--------|----------------|
| shareholder coverage | components/companies with accepted capture |
| ownership events | known-event / component event coverage |
| capital structure completeness | pledge / unlock / change components closed vs roadmap |


Each track progress block must also state:


- `status`（READY/HOLD/…）  
- `evidence_basis`（paths or “insufficient”）  
- `not_verified` / `not_production_ready` reminder when gates are caveat-based  



---

# 4. Bottleneck analysis（required）


Every report / pause must identify:


```text
Current bottleneck:
Reason:
Recommended next focus:
```


Rules:


1. Bottleneck is the **binding constraint** on mission progress（often approval, snapshot block, unresolved network caveats, worktree dirty preventing sync）.  
2. Recommended next focus must prefer **autonomous work on independent tracks** when bottleneck is approval-gated（mission objective v2）.  
3. Do not recommend live/push/gate flip unless human interrupt conditions are already met.  



---

# 5. Time / effort estimation


### Preferred formula（when velocity exists）


```text
estimated_remaining_effort =
  remaining_capability_units / average_completed_capability_units_per_period
```


Period = successful Daily Loop days or closed packages with comparable unit definitions.


### If insufficient data


Return:


```text
estimated_remaining_effort: unknown
```


### Forbidden


- fabricating calendar ETAs（“3 days left”）without velocity evidence  
- using commit velocity as proxy for capability velocity  
- converting CNINFO call counts into completion %  



---

# 6. Pause / stop reporting（required block）


Whenever Controller stops（end of daily loop, human interrupt, or no autonomous progress remaining）, emit:


```markdown
## Progress intelligence

### Global
- overall_completion_pct:
- completed_capability_units:
- remaining_capability_units:
- estimated_remaining_effort:

### Tracks
#### A
- goal:
- company_coverage:
- attribute_coverage:
- missing_scope:
- progress_note:

#### B
- goal:
- source_coverage:
- extraction_coverage:
- event_completeness:
- progress_note:

#### C
- goal:
- validation_coverage:
- evidence_completeness:
- qa_status:
- progress_note:

#### D
- goal:
- shareholder_coverage:
- ownership_events:
- capital_structure_completeness:
- progress_note:

### Remaining work
- ...

### Bottleneck
- Current bottleneck:
- Reason:
- Recommended next focus:

### Stop context
- Reason for stopping:
- Human decisions required:
```



---

# 7. Integration with Daily Loop


1. State Reader gathers coverage evidence pointers（do not invent counts）.  
2. Queue Engine still classifies READY/HOLD/…  
3. Before choosing `allowed_action`, consult bottleneck + mission priority.  
4. Daily Report / interrupt packet **must** include Progress intelligence block.  
5. Bounded commits of progress notes are docs/evidence class when evidence-based.  



---

# 8. Honesty constraints


- `PASS_WITH_CAVEAT` ≠ full capability complete  
- coverage ≠ verified  
- snapshot blocked ⇒ C quality goal not “done”  
- D `READY_FOR_APPROVAL` ≠ shareholder coverage advanced  
- unknown is preferable to false precision  



---

# 9. Anti-patterns


Forbidden:


- “We made 12 commits ⇒ +20% progress”  
- “Worktree dirty ⇒ 0% global progress”  
- inventing full-market denominator without universe definition  
- hiding bottleneck behind SUCCESS status  
- stopping all tracks because one track’s effort estimate is unknown  
