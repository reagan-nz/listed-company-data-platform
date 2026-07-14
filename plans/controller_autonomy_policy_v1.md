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


Human approval is required before:


- external live execution;
- CNINFO access when not already approved;
- production data mutation;
- database migration;
- schema-breaking changes;
- push to remote repositories;
- expanding task scope;
- changing approval boundaries;
- promoting evidence classification;
- changing verified / production_ready status.


The Controller must stop.


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


1. Scope expands.

Example:

300-company task becomes 500-company task.


2. Risk category changes.

Example:

Offline task becomes live execution.


3. New external access is required.


Example:

CNINFO/API/network access.


4. Approval boundary changes.


Example:

Commit approval becomes push approval.


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
