# Controller Approval Queue 2026-07-14


_Daily Autonomous Loop v2 · offline packaging only_  
_规则：已知 HOLD / WAITING_APPROVAL **不重复打断**；本文件维护审批队列，供 human 在解锁有意义下一步时使用_


## 1. Queue（open）


| ID | Track | Decision needed | Unlocks if approved | Status |
|----|-------|-----------------|---------------------|--------|
| AQ-D-SC | D | shareholder_change **component** Level-2 approval phrase | D first-slice planning→runner/dry-run/live package chain（仍分步审批） | **WAITING_APPROVAL** · READY_FOR_APPROVAL ≠ approved |
| AQ-C-SNAP | C | flip `approved_for_snapshot_rebuild`（explicit） | C snapshot rebuild candidate path | **blocked** · do not rebuild |
| AQ-PUSH | repo | remote publication / push phrase | publish diverged `main`（ahead/behind） | **NOT authorized** |
| AQ-WT-SYNC | worktrees | human clean unknown dirty in A/B/C/D worktrees | Option A sync to main tip · track execute from worktrees | **SKIP sync** while dirty+stale |


## 2. Do not re-interrupt for（known）


- A post-integration HOLD（unresolved 6 retained）  
- B post-integration HOLD（BD2E624 deferred）  
- C snapshot blocked（already listed）  
- D shareholder_change waiting（already listed）  
- historical spent live/commit approvals  


## 3. Evidence pointers（D shareholder_change）


Already on main（planning · not approved）:


- `plans/cninfo_d_class_shareholder_change_next_component_planning.md`  
- `plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md`  
- `outputs/validation/cninfo_d_class_shareholder_change_next_component_*.md`  
- `outputs/validation/cninfo_d_class_autonomous_batch_v1_shareholder_change_gate.md`  


Exact approval phrase remains a **human** Level-2 decision. Controller must not invent approval text as granted.



---

## 4. Autonomous progress while queue open


Per mission / interrupt / cycle policies:


- Continue other safe READY work（docs/evidence/offline packaging）  
- Do **not** stop entire daily run solely because this queue is non-empty  
- Do **not** execute D shareholder_change live/runner without component approval  



---

## 5. Safety


- CNINFO: 0  
- Live: 0  
- Push: 0  
- Approval bypass: no  
