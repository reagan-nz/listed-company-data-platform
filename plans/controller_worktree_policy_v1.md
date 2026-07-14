# Controller Worktree Isolation Policy v1


## 1. Purpose

This document defines how A/B/C/D Executors use isolated Git worktrees.

The purpose:

- prevent cross-track file contamination;
- allow parallel execution;
- preserve independent branches;
- reduce merge conflicts.


Worktree isolation provides:

- independent filesystem;
- independent Git branch;
- independent staging area.


Worktree isolation does NOT automatically authorize:

- commit;
- push;
- live execution;
- CNINFO access;
- scope expansion.


---

# 2. Worktree Mapping


Each execution track has a dedicated worktree.


## A-class

Path:

../listed_company_data_collector-worktrees/a-class

Branch:

agent/a-class


---

## B-class

Path:

../listed_company_data_collector-worktrees/b-class

Branch:

agent/b-class


---

## C-class

Path:

../listed_company_data_collector-worktrees/c-class

Branch:

agent/c-class


---

## D-class

Path:

../listed_company_data_collector-worktrees/d-class

Branch:

agent/d-class


---

# 3. Executor Rules


Executors must:

- operate inside assigned worktree;
- avoid modifying other track worktrees;
- report branch and worktree location;
- preserve track boundaries.


Executors must not:

- directly modify main worktree;
- stage unrelated files;
- commit without approval.


---

# 4. Parallel Execution Rules


With isolated worktrees:


Allowed:

- A/B/C/D offline tasks in parallel;
- independent documentation;
- independent validation;
- isolated implementation.


Still requires Controller review:


- shared status files;
- commits;
- merges;
- pushes;
- live execution.


---

# 5. Shared Files


The following require reconciliation:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans


Worktrees prevent simultaneous editing conflicts.

They do not remove merge conflicts.


---

# 6. Controller Responsibility


The Controller decides:

- whether worktree isolation is required;
- which executor receives which worktree;
- when branches can merge;
- when human approval is required.


---

# 7. Operating Principle


Prefer:


isolated parallel progress


over:


single working tree sequential execution.


However:


safety boundaries override speed.


# End of Policy
