# Controller Parallel Execution Policy v1


## 1. Purpose


This document defines when the Controller may execute multiple workflows in parallel.


The goal:

- reduce idle time;
- allow independent tracks to progress simultaneously;
- preserve track isolation;
- prevent unsafe concurrent operations.


Parallel execution is a Controller optimization.

It must never override:

- approval boundaries;
- evidence requirements;
- commit safety;
- track isolation.


---

# 2. Parallel Execution Principle


The Controller should separate tasks into:


## Independent tasks


Tasks may run in parallel when:

- they operate on different tracks;
- they modify isolated outputs;
- they do not share mutable files;
- they do not depend on each other's results.


Example:


A-class validation
        +
C-class offline QA
        +
D-class planning


may run simultaneously.


---

## Dependent tasks


Tasks must run sequentially when:

- one task changes the input of another;
- one task requires previous evidence;
- one task requires human approval first;
- shared files are involved.


Example:


merge closure
        ↓
commit boundary
        ↓
human approval
        ↓
commit


cannot be reordered.


---

# 3. Track Parallel Rules


## A-class


Can run parallel with:

- C-class offline work;
- D-class planning;
- B-class planning.


Cannot run parallel with:

- A-class commit;
- shared status document updates;
- A-class live rerun.


Reason:

Commit and shared documentation may create conflicts.


---

# B-class


Can run parallel with:

- A-class offline work;
- C-class QA;
- D-class planning.


Cannot run parallel with:

- B-class live execution;
- B-class commit;
- snapshot/database mutation.


Reason:

B-class may involve external access and sensitive output boundaries.


---

# C-class


Can run parallel with:

- A-class commit preparation;
- B-class planning;
- D-class planning.


Cannot run parallel with:

- snapshot generation;
- production promotion;
- large harvest mutation.


Reason:

Snapshot and harvest operations require exclusive control.


---

# D-class


Can run parallel with:

- A/B/C offline documentation;
- planning tasks.


Cannot run parallel with:

- structured capture promotion;
- live targeted probes;
- evidence classification changes.


Reason:

D-class requires strict evidence boundary control.


---

# 4. Safe Parallel Examples


## Example 1


Allowed:


B-class merge documentation
        +
C-class QA ledger review
        +
D-class planning document


Reason:

Different outputs and no shared mutation.


---

## Example 2


Allowed:


A-class boundary review
        +
C-class offline status analysis


Reason:

Independent validation scopes.


---

# 5. Unsafe Parallel Examples


## Example 1


Not allowed:


B commit
+
A commit


Reason:

Both may modify shared status/control files.


Correct:


B commit
        ↓
post-commit verification
        ↓
A commit


---

## Example 2


Not allowed:


Live execution
+
snapshot generation


Reason:

External execution and data mutation boundaries conflict.


---

## Example 3


Not allowed:


D disclosure evidence promotion
+
structured capture update


Reason:

Evidence boundary may be violated.


---

# 6. Shared File Rule


The following files require special handling:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans


If multiple workflows need to update the same file:


The Controller must:


1. serialize updates;
2. avoid concurrent modification;
3. review final diff before writing.


Parallel execution applies to tasks.

It does not apply to shared state mutation.


---

# 7. Human Approval Rule


Parallel execution does not bypass human approval.


Example:


Allowed:


A commit prepared
+
C QA prepared
+
D planning prepared


Not allowed:


A commit
+
B commit
+
push


without approval.


---

# 8. Reviewer Parallelism


Reviewers may run in parallel only when independent.


Allowed:


Evidence review of A
+
Regression review of B


Not allowed:


Git Boundary Review
+
commit execution


because the review must happen before the action.


---

# 9. Controller Coordination Rule


When multiple tasks are available:


The Controller should:


1. classify dependency;
2. identify shared resources;
3. separate safe parallel tasks;
4. execute independent workflows;
5. serialize risky operations;
6. provide consolidated report.


The Controller should not maximize parallelism.

It should maximize safe progress.


---

# 10. Stop Conditions


Parallel execution must stop when:


- human approval is required;
- reviewers identify blocking risks;
- shared file conflicts appear;
- task scope expands;
- safety boundary becomes unclear.


A partial stop is acceptable.


---

# 11. Operating Principle


Prefer:


safe parallel progress
        +
controlled boundaries
        +
human approval at critical points


Avoid:


maximum parallel execution
        +
unclear ownership
        +
unsafe state mutation


The Controller is responsible for coordinating multiple agents while maintaining project integrity.


---

# Worktree-Based Parallel Execution


When Executors operate in isolated worktrees:


Allowed:

- A/B/C/D independent tasks running simultaneously;
- independent documentation;
- independent validation;
- independent implementation.


Conditions:


Required:

- separate worktree;
- separate branch;
- isolated output root;
- no shared mutable state.


Worktree isolation does not remove:


- human approval requirements;
- external API constraints;
- evidence requirements;
- merge requirements.


The Controller should prefer safe parallel execution when isolation exists.


---

# Parallel Completion Rule


Parallel tasks report independently.


The Controller aggregates:


- completion state;
- artifacts;
- reviewers;
- blockers.


The Controller does not require sequential completion unless dependency exists.


---

# End of Policy
