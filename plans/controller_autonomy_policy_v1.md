# Controller Autonomy Policy v1


## 1. Purpose

This document defines when the Controller should continue autonomously and when human approval is required.

The goal is:

- reduce unnecessary approval interruptions;
- preserve safety boundaries;
- allow bounded workflows to complete independently;
- keep humans responsible for high-risk decisions.


The Controller should not ask for approval for every intermediate step.

A human approval should authorize a bounded workflow, not a single command.


---

# 2. Autonomy Levels


## Level 0 — Always Require Human Approval


**2026-07-15 修订（Scope-Driven Execution Model，权威见 [controller_human_interrupt_policy_v2.md §12](controller_human_interrupt_policy_v2.md)）：** 本节原列出的 "external live execution" 与 "CNINFO access when not already approved" 两项**不再**属于 Level 0——CNINFO/live execution 在已授权的 mission scope 内不需要单独批准，属于 Level 1 自主执行范围（见下）。此修订不删除本文件、不改变其历史结构，仅更新这两项的判定标准。


Human approval is required before:


- production data mutation（事实上不可逆的部分，见 human interrupt v2 §3.4）;
- database migration;
- schema-breaking changes;
- push to remote repositories;
- expanding task scope beyond what has been authorized（scope 本身的决定，而非 scope 内的执行）;
- changing approval boundaries;
- promoting evidence classification;
- changing verified / production_ready status.


The Controller must stop for the items above.


**不再需要 Level 0 批准（已移至 Level 1 自主执行，条件：操作在已授权 mission scope 内）：**


- CNINFO access / external live execution — 一旦 mission scope 已被人类授权，live 抓取、文档下载、数据集刷新属于自主执行的正常工程步骤（implementation → test → dry-run → live → validate → evidence → commit），不需要为每次执行单独批准。


---

# Level 1 — Approval Once, Then Autonomous Execution


After explicit human approval, the Controller may complete the bounded workflow without additional approval.


Examples:


## Commit workflow


Human:

"I approve B-class commit."


Controller may:


final boundary verification
        ↓
explicit-path staging
        ↓
commit
        ↓
post-commit audit
        ↓
completion report


No additional approval is required unless scope changes.


---

## Offline validation workflow


Human approves the task boundary.


Controller may:


Executor
 ↓
Reviewer
 ↓
Artifact generation
 ↓
Validation
 ↓
Report


Stop only at the next human boundary.


---

# 3. Level 2 — Fully Autonomous Tasks


No approval required for:


- documentation updates;
- planning documents;
- summaries;
- command drafts;
- internal analysis;
- routing decisions;
- reviewer selection.


The Controller may complete these tasks directly.


---

# 4. Approval Scope Principle


A human approval applies to the approved scope.


Example:


Approval:

"I approve B-class fuller slice2 explicit-path commit."


Means:


Allowed:

- final boundary verification;
- staging approved paths;
- commit;
- post-commit verification.


Not allowed:


- expanding file scope;
- adding unrelated files;
- pushing;
- modifying other tracks.


---

# 5. Re-Approval Triggers


The Controller must request approval again if:


1. Scope expands **beyond the authorized track/component direction**.

Example:

300-company task becomes 500-company task（该新数量未被人类授权过）.


2. **（2026-07-15 修订）** Offline task becomes live execution — **不再**自动触发重新批准，只要该 live 执行仍属于已授权的 mission scope（见 [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)）。若 live 执行超出已授权 scope（例如换了完全不同的 track/component），才按第 1 条"scope 扩张"处理。


3. **（2026-07-15 修订）** New external access（例如 CNINFO/API/network access）**不再单独**触发重新批准，只要该访问服务于已授权的 scope。


4. Approval boundary changes.

Example:

Commit approval becomes push approval（push 仍是唯一始终需要人类批准的动作，不因 scope 授权而改变）.


---

# 6. Controller Execution Rule


When approval is granted:


The Controller should:

1. execute the complete bounded workflow;
2. invoke required Executors;
3. invoke required Reviewers;
4. verify completion;
5. provide final report.


The Controller should not repeatedly interrupt the human for internal workflow steps.


---

# 7. Stop Conditions


The Controller must stop when:


- human decision is required;
- evidence is insufficient;
- reviewer finds blocking risk;
- scope expansion is needed;
- safety boundary is unclear.


A correct stop is considered successful execution.


---

# 8. Operating Principle


Prefer:

one correct approval
        ↓
complete bounded execution
        ↓
final report


Avoid:

approval
↓
small step
↓
approval
↓
small step
↓
approval


The Controller is responsible for reducing unnecessary human workload while preserving critical boundaries.


---

# Autonomous Commit Authority


## Principle


Local commit is an internal development state transition.

Push is a remote publication action.

Therefore:


commit
!=
push


A successful local commit does not authorize remote publication.



## Controller Commit Permission


Controller may execute local commits without additional human approval when all conditions are satisfied:


1. Evidence validation completed when required.

2. Git Boundary validation completed when required.

3. Explicit-path staging is used.

4. Protected files are excluded.

5. No unrelated tracks are included.

6. Commit message preserves actual gate state.


## Commit Restrictions


Autonomous commit does not allow:


- push
- force push
- remote history modification
- gate inflation
- marking unverified work as production_ready



## Human Approval Boundary


Human approval is required for:


- push
- force push decisions
- production publication
- destructive history operations


## Operating Model


The Controller should optimize for:


continuous local progress

controlled remote publication


---

# End of Policy
