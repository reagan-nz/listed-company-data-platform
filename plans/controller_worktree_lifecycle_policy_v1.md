# Controller Worktree Lifecycle Policy v1


## 1. Purpose


This document defines how Controller manages Git worktree lifecycle during multi-agent execution.


The purpose:


- prevent stale execution environments;
- ensure Executors run on correct project state;
- preserve branch isolation;
- support safe parallel execution.


Worktree management is part of execution infrastructure.


---

# 2. Worktree Lifecycle Stages


Each worktree follows:


Create
↓
Validate
↓
Synchronize
↓
Execute
↓
Review
↓
Merge or Archive


---

# 3. Worktree Creation Rule


A worktree should be created when:


- a new independent execution track starts;
- an Executor requires isolated modification;
- a parallel batch requires separation.


Creation must record:


- worktree path;
- branch;
- base commit;
- creation time;
- assigned track.


Example:


Track:
B-class
Worktree:
../listed_company_data_collector-worktrees/b-class
Branch:
agent/b-class
Base commit:
85abad0


---

# 4. Base Revision Rule


Every execution batch must record its starting revision.


Required:


base_commit:
<git commit hash>


The Controller must know:


- what state the Executor started from;
- what changed during execution.


A worktree running on an unknown base revision should not be accepted.


---

# 5. Synchronization Rule


Before starting a new execution batch:


Controller should check:


- main branch changes;
- worktree commit difference;
- pending dirty files;
- previous task completion.


If a worktree is stale:


Controller should stop and decide:


Options:


1. synchronize;
2. recreate worktree;
3. continue with explicit reason.


---

# 6. Safe Synchronization


Synchronization depends on task type.


## Documentation / Analysis Tasks


Allowed:


- update branch;
- recreate worktree;
- synchronize from approved base.


No reviewer required.


---

## Code Tasks


Require additional checks:


- branch status;
- changed files;
- dependency impact.


Regression review may be required.


---

## Commit Preparation Tasks


Require:


Executor
↓
Evidence Auditor
↓
Git Boundary Reviewer
↓
Human Approval


before final commit.


---

# 7. Dirty Worktree Rule


A dirty worktree must be classified before reuse.


Possible states:


## Clean


Allowed.


## Dirty with unfinished task


Controller must not overwrite.


## Dirty unrelated changes


Controller must isolate and investigate.


## Dirty completed artifact


Controller must determine whether to:


- merge;
- archive;
- preserve.


---

# 8. Worktree Isolation Rule


Worktrees provide:


- independent files;
- independent branches;
- independent staging.


Worktrees do not automatically provide:


- approval;
- evidence validity;
- permission to commit;
- permission to push.


---

# 9. Parallel Execution Rule


Parallel execution requires:


- each task has its own worktree;
- each task has a known base commit;
- outputs are isolated.


Parallel execution must stop if:


- shared files conflict;
- branches become unclear;
- external resources conflict.


---

# 10. Completion Rule


After task completion:


Controller records:


Track:
Executor:
Worktree:
Branch:
Base commit:
Files changed:
Commit:
Push:
Reviewer result:


---

# 11. Worktree Archive Rule


Completed temporary worktrees may be archived when:


- task finished;
- changes merged or intentionally abandoned;
- no pending artifacts remain.


Deletion requires Controller decision.


---

# 12. Operating Principle


Prefer:


fresh isolated execution environment
+
known starting state
+
clear completion state


Avoid:


unknown stale worktree
+
parallel modification
+
unclear ownership


The Controller is responsible for ensuring every Executor starts from a trustworthy environment.


---

# End of Policy
