# Controller Worktree Synchronization Policy v1


## 1. Purpose


This document defines how Controller synchronizes Executor worktrees before execution.


The purpose:


- prevent stale execution;
- maintain trustworthy execution state;
- avoid accidental overwrite;
- preserve branch isolation.


Synchronization is a controlled operation.

It does not automatically authorize:

- commit;
- push;
- live execution;
- scope expansion.


---

# 2. Synchronization Decision


Before launching an Executor, Controller checks:


- current branch;
- current HEAD;
- dirty state;
- base commit;
- required artifacts;
- relation to main state.


Possible results:


READY
↓
SYNC_REQUIRED
↓
RECREATE_REQUIRED
↓
BLOCKED


---

# 3. READY State


A worktree is READY when:


- branch is correct;
- expected base state exists;
- no conflicting dirty files exist;
- required project state is available.


Controller may launch Executor.


---

# 4. SYNC_REQUIRED State


A worktree requires synchronization when:


- main has newer approved changes;
- required artifacts exist outside worktree;
- worktree is behind expected execution state.


Example:


Main:
85abad0
+
approved Era D artifacts
Worktree:
85abad0 only


Controller must not launch execution without resolving the difference.


---

# 5. Synchronization Methods


Controller may choose:


## Option A — Recreate Worktree


Recommended for:


- documentation tasks;
- analysis tasks;
- disposable execution.


Process:


archive old worktree
↓
create fresh worktree
↓
assign correct branch
↓
validate


---

## Option B — Synchronize Existing Worktree


Allowed when:


- branch ownership is clear;
- no conflicting changes exist;
- synchronization does not overwrite work.


Process:


inspect
↓
sync
↓
validate
↓
execute


---

## Option C — Continue With Explicit Reason


Allowed only when:


- stale state is intentional;
- task specifically requires historical state;
- Controller records reason.


Example:


Reviewing historical commit behavior.
Current stale state is intentional.


---

# 6. Automatic Synchronization Rules


Controller may automatically synchronize only for:


- documentation tasks;
- offline analysis;
- disposable planning tasks.


Controller must not automatically synchronize for:


- commit preparation;
- merge operations;
- release workflows;
- production-impacting tasks.


---

# 7. Commit Workflow Synchronization


For commit-related tasks:


Required:


Executor
↓
Evidence Auditor
↓
Git Boundary Reviewer
↓
Human Approval


before final commit actions.


The Controller must not silently update commit worktrees.


---

# 8. Dirty Worktree Handling


Dirty worktree classification:


## Completed artifact


Controller decides:


- preserve;
- archive;
- merge;
- recreate.


---

## Unfinished work


Controller must stop.


Do not:

- reset;
- overwrite;
- delete.


---

## Unknown modification


Controller requires investigation.


---

# 9. Parallel Synchronization Rule


When multiple worktrees require synchronization:


Controller may synchronize independent worktrees in parallel.


However:


Shared state synchronization must be serialized.


Examples:


Allowed:


A worktree refresh

C worktree refresh


Not allowed:


A + B modifying shared control documents simultaneously


---

# 10. Synchronization Report


Before execution, Controller should record:


Track:
Worktree:
Branch:
Before HEAD:
After HEAD:
Synchronization action:
Reason:
Approval required:


---

# 11. Operating Principle


Prefer:


fresh execution state

known ownership

controlled synchronization


Avoid:


stale worktree

blind execution

unclear changes


The Controller is responsible for ensuring every Executor starts from a reliable execution environment.


---

# 12. Execution Capability Validation


A synchronized worktree is not considered READY only because artifacts exist.


Controller must distinguish:


Artifact State
vs
Execution Capability State


A worktree is READY only when both are valid.


---

## 12.1 Artifact State Validation


Check:


- required artifacts exist;
- expected output paths exist;
- task evidence files exist;
- previous completion packages are available.


Example:


A boundary package:
exists
=
artifact ready


Artifact presence alone does not prove execution readiness.


---

## 12.2 Execution Capability Validation


Controller must verify that the worktree can perform the intended task.


Check:


- required scripts exist;
- required CLI flags exist;
- runner implementation matches expected version;
- configuration files are available;
- execution entry points are present.


Example:


Artifact:
present
Runner:
missing required flag
Result:
NOT READY


---

## 12.3 Synchronization Completion Rule


A synchronization operation is complete only when:


READY
=
Artifact State Valid

Execution Capability Valid

Branch State Known


If any condition fails:


state:


SYNC_REQUIRED
or
BLOCKED


---

## 12.4 Runner Drift Detection


Controller should detect:


- main runner newer than worktree runner;
- missing CLI options;
- outdated execution scripts;
- configuration mismatch.


Example:


Main:
retry-v3 flag available
Worktree:
retry-v3 flag absent
Decision:
execution capability drift


---

## 12.5 Commit Preparation Exception


For commit preparation tasks:


artifact readiness is insufficient.


Required:


Artifact validation

Execution capability validation

Evidence review

Git Boundary review


before human approval.


---

## 12.6 Operating Principle


A trustworthy worktree requires:


correct files

correct execution capability

known ownership


The Controller must never assume:


files exist
=
task can run


---

# End of Policy
