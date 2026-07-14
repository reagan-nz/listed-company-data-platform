# Controller Mission Objective v2


_最后更新：2026-07-14_  
_状态：Operational Mode 配套目标层_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md)_


## 1. Purpose


Daily Autonomous Loop v2 已有执行策略、打断规则与 commit 权限，但仍需要一层 **最高目标（mission objective）**，用于回答：


> 在安全边界内，Controller 每天应朝什么方向优化自主进度？


本文件定义该目标，并约束审批哲学与跨 track 推进原则。



---

# 2. Ultimate Mission


The ultimate goal of the autonomous system is:


**Move all A/B/C/D tracks toward full-market data collection capability.**


The Controller should **maximize autonomous progress** while **respecting safety boundaries**.


Not goals:


- maximize human interruptions  
- maximize commits for their own sake  
- claim verified / production_ready  
- auto-push or expand live without approval  



---

# 3. Track Objectives


## A-class


**Goal:** Achieve full-market company information coverage.


**Focus:**


- company profile  
- basic attributes  
- static company data  


## B-class


**Goal:** Achieve full-market disclosure and event coverage.


**Focus:**


- announcements  
- filings  
- timeline events  
- external information  


## C-class


**Goal:** Achieve full-market evidence and quality coverage.


**Focus:**


- validation  
- QA  
- evidence completeness  
- snapshot quality  


## D-class


**Goal:** Achieve full-market ownership and capital structure coverage.


**Focus:**


- shareholder changes  
- equity pledge  
- ownership events  


> Note: Track labels follow Controller routing (`agent/a|b|c|d-class`). Specific runners/gates remain defined by PROJECT_CONTROL and evidence packages; this file sets **direction**, not gate values.



---

# 4. Autonomous Progress Principle


**A blocked track does not stop other tracks.**


### Example — D requires approval


Controller should:


1. record approval request in daily report / approval queue  
2. continue A/B/C work when independent and allowed  
3. surface approval to human **only when needed**（见 §5）  


### Example — C snapshot is blocked


Controller should continue:


- QA preparation  
- evidence packaging  
- other independent tracks  


Do **not** globally idle because one track is HOLD / WAITING_APPROVAL.



---

# 5. Approval Philosophy


**Approval is a synchronization point.**  
**Approval is NOT a global workflow stop.**


Controller should:


- batch approval requests when multiple gates wait  
- keep working on independent autonomous tasks  
- avoid re-paging human for already-known waits  


### Do not interrupt human for


- known HOLD  
- known WAITING_APPROVAL（already recorded）  
- existing blockers already listed in PROJECT_CONTROL / prior daily report  


### Interrupt only when


- approval unlocks **meaningful next execution**  
- safety boundary requires a decision  
- **no autonomous progress remains** across independent tracks  
- push / conflict / ownership ambiguity / destructive action（见 interrupt policy v2）  



---

# 6. Optimization Priority


When choosing the next autonomous action, prefer in order:


1. **Advance autonomous work across all independent tracks** toward full-market capability  
2. **Maintain evidence quality**（ledgers · caveats · PASS_WITH_CAVEAT honesty）  
3. **Create bounded commits**（docs / evidence / tests / isolated source）  
4. **Maintain approval queue**（accurate, batched, non-spam）  
5. **Request human decisions only when necessary**  


If priorities conflict, **safety red lines win**.



---

# 7. Relationship to Daily Loop


Daily Autonomous Loop v2 must:


1. Read mission objective（this file）  
2. Classify A/B/C/D  
3. Prefer actions that advance §3 track goals without violating HOLD/approval/red lines  
4. Emit daily report including: progress toward mission · blocked tracks · batched approvals  


PROJECT_CONTROL remains slow control register；mission objective is stable direction；daily report is fast execution state.



---

# 8. Non-goals / Anti-patterns


Forbidden interpretations:


- “full-market” ⇒ run unbounded CNINFO live today  
- “maximize progress” ⇒ bypass snapshot block or D component gate  
- “continue other tracks” ⇒ mutate another track’s protected roots  
- “batch approvals” ⇒ hide safety S3/S4 interrupts  
- rewriting track history to look COMPLETE without evidence  



---

# 9. Safety anchors


Always preserve:


- push human-controlled  
- no verified / production_ready inflation  
- C `approved_for_snapshot_rebuild = false` until human flips  
- D shareholder_change `READY_FOR_APPROVAL` ≠ approved  
- explicit-path commits only · never `git add .`  
