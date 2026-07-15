# Controller Capability Gap Analysis v2


_最后更新：2026-07-14_  
_配套：[controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_milestone_management_v2.md](controller_milestone_management_v2.md)_


## 1. Purpose


Translate progress numbers into **actionable gaps** — not percentage-only reporting.


Progress intelligence answers “how far?”  
Gap analysis answers “what is missing, why, and what task closes it?”



---

# 2. Input → output model


### Input examples


| Track | Progress signal |
|-------|-----------------|
| C | 193/200 complete |
| A | cumulative 486 effective codes · unresolved 6 |
| B | 299/300 · BD2E624 deferred |


### Required output


```text
gap_id:
track:
metric_observed:
gap_statement:          # e.g. 7 partial cases
root_cause:             # evidence-backed · or unknown
impact_on_mission:
next_tasks:             # actionable · generator-ready
blocked_by:             # scope_missing / technical_failure / destructive_approval / push / none — 2026-07-15 修订：不再用 "approval"/"live" 泛指（live 本身在已授权 scope 内不是 blocker，见 human interrupt v2 §12）
evidence_paths:
```


**Do not only report percentage.**



---

# 3. Worked example（C）


Input:


- C: 193/200 complete · 7 partial · 0 missing · snapshot blocked  


Output（illustrative）:


| Field | Value |
|-------|-------|
| gap_statement | 7 partial cases |
| root_cause | missing / incomplete normalized evidence on delisted-or-error sources（cite caveat ledger） |
| next_tasks | investigate evidence sources · improve validation packaging · offline QA matrix |
| blocked_by | snapshot rebuild approval（if action needs snapshot）· else none for offline packaging |


Offline next_tasks may proceed under HOLD; snapshot-dependent tasks stay gated.



---

# 4. Per-track gap lenses


| Track | Prefer gap dimensions |
|-------|----------------------|
| A | company coverage · attribute coverage · missing scope / unresolved |
| B | source coverage · extraction coverage · event completeness · deferred failures |
| C | validation coverage · evidence completeness · QA status · snapshot readiness（not flip） |
| D | shareholder coverage · ownership events · capital structure completeness · approval-prep gaps |



---

# 5. Integration


1. State Reader / Progress block supplies metrics.  
2. Gap analyzer emits gap records.  
3. Task generator turns `next_tasks` into candidates.  
4. Continuation re-checks gaps after each task.  
5. Daily report includes gap→task mapping · not % alone.  



---

# 6. Honesty


- UNKNOWN denominator ⇒ overall % UNKNOWN · still emit concrete local gaps when numerators exist.  
- PASS_WITH_CAVEAT ≠ gap_closed for full-market mission.  
- Do not fabricate root causes — use `unknown` and propose investigation tasks.  



---

# 7. Anti-patterns


Forbidden:


- “C is 96.5% done” with no gap_statement  
- converting commit counts into gaps closed  
- hiding approval blockers inside vague “remaining work”  
