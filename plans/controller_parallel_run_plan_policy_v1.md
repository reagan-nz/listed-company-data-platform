# Controller Parallel Run Plan Policy v1


## 1. Purpose


This document defines how the Controller creates, executes, and monitors multi-track execution batches.


The purpose:

- allow safe parallel progress;
- assign correct Executors;
- assign correct worktrees;
- preserve dependencies;
- aggregate completion status.


Parallel execution is controlled by the Controller.

Executors do not independently create parallel plans.


---

# 2. Parallel Run Plan Structure


A parallel run plan must define:


- batch identifier;
- tasks included;
- executor assignment;
- worktree assignment;
- branch assignment;
- reviewer requirement;
- dependency;
- approval boundary.


Example:


Parallel Run Batch:
Batch ID:
20260714_001
Task 1:
Track:
B-class
Executor:
b-class-executor
Worktree:
b-class
Reviewer:
Evidence Auditor
Task 2:
Track:
C-class
Executor:
c-class-executor
Worktree:
c-class
Reviewer:
Evidence Auditor


---

# 3. Task Classification


Before creating a parallel run, Controller classifies tasks.


## Independent Task


May run in parallel when:


- different track;
- different worktree;
- isolated output;
- no dependency.


Example:


B offline planning

C QA analysis

D documentation planning


Allowed.


---

## Dependent Task


Must run sequentially when:


- requires previous artifact;
- requires previous approval;
- modifies shared state;
- requires previous commit.


Example:


Merge closure
↓
Commit boundary
↓
Human approval
↓
Commit


---

# 4. Executor Assignment


Each task must map to exactly one Executor.


Mapping:


| Track | Executor | Worktree |
|-|-|-|
| A-class | a-class-executor | a-class |
| B-class | b-class-executor | b-class |
| C-class | c-class-executor | c-class |
| D-class | d-class-executor | d-class |


The Controller must not assign:

- B task to A executor;
- A task to main worktree;
- multiple tracks to one executor simultaneously.


---

# 5. Reviewer Assignment


Reviewer selection follows task type.


## Documentation / Planning


Usually:

Executor only


No reviewer unless claims or state changes are produced.


---

## Code / Behavior Change


Required:


Executor
↓
Regression Reviewer


If execution results are generated:


Executor
↓
Regression Reviewer
↓
Evidence Auditor


---

## Live / Validation / Closure


Required:


Executor
↓
Evidence Auditor


---

## Commit Preparation


Required:


Executor
↓
Evidence Auditor
↓
Git Boundary Reviewer
↓
Human Approval


---

# 6. Parallel Safety Rules


Parallel execution requires:


- separate worktree;
- separate branch;
- isolated output;
- no shared mutable state.


Worktree isolation does not remove:


- approval requirements;
- reviewer requirements;
- merge requirements.


---

# 7. Shared State Handling


The following files cannot be concurrently modified:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans


If multiple tasks need these files:


Controller must:


1. serialize updates;
2. collect changes;
3. reconcile final state.


---

# 8. Completion Aggregation


After parallel tasks finish:


Controller creates a consolidated report.


Format:


Parallel Run Report
Batch:
Task A:
status
Task B:
status
Task C:
status
Reviewers:
Blockers:
Human decisions required:
Next action:


---

# 9. Human Boundary


Parallel execution never bypasses human approval.


Examples:


Allowed:


B preparation

C QA

D planning


Not allowed:


B commit

A commit

push


without approval.


---

# 10. Failure Handling


If one parallel task fails:


Controller should:


- isolate failure;
- continue independent tasks;
- report blocker;
- avoid stopping unrelated safe tasks.


Example:


B blocked by evidence issue
C QA continues
D planning continues


---

# 11. Operating Principle


The Controller should maximize:


safe independent progress


not:


maximum parallel execution


Parallelism is a tool.

Safety boundaries remain primary.


---

# End of Policy
