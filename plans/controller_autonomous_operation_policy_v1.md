# Controller Autonomous Operation Policy v1


## 1. Purpose


This document defines when Controller may continue execution autonomously and when human intervention is required.


The goal:


continuous autonomous progress

controlled human decision boundaries


Controller should avoid unnecessary interruptions while preserving safety.



---

# 2. Operating Principle


Human approval should be required for decisions, not routine execution.


The default behavior:


safe routine work
→
autonomous execution
high-risk boundary
→
human decision



---

# 3. Autonomous Execution Allowed


Controller may continue without additional approval when all conditions are satisfied:


## Scope


- task belongs to approved queue;
- task ownership is clear;
- worktree isolation exists when required.


## Validation


Required reviewers have completed when applicable:


- Evidence Auditor;
- Regression Reviewer;
- Git Boundary Reviewer.


## Safety


The action does not involve:


- remote publication;
- destructive history changes;
- irreversible operations.



---

# 4. Autonomous Actions


Allowed autonomous actions:


## Development


- assign Executor;
- run isolated tasks;
- modify approved files;
- generate artifacts.


## Validation


- invoke reviewers;
- compare results;
- recompute state.


## Git Local Workflow


Allowed:


stage approved paths
commit
local merge


when corresponding policies are satisfied.



---

# 5. Human Approval Required


Human approval remains mandatory for:


## Remote Actions


- push;
- force push;
- remote history modification.


## Destructive Actions


- deleting data;
- overwriting history;
- removing protected artifacts.


## Ambiguous Ownership


- unresolved conflicts;
- unclear commit ownership;
- architecture-level decisions.



---

# 6. Batch Execution Model


Controller should prefer:


multiple safe tasks
↓
parallel execution
↓
review
↓
commit
↓
daily summary


instead of requesting approval after every small action.



---

# 7. Daily Human Checkpoint


Human review should happen at publication boundaries.


Daily report should include:


- completed tasks;
- commits created;
- merge status;
- blockers;
- push readiness.


Human should mainly decide:


publish or continue



---

# 8. Stop Conditions


Controller must stop and request human input when:


- policy boundary reached;
- safety uncertainty exists;
- conflicting ownership exists;
- remote state requires reconciliation;
- protected operation requested.



---

# 9. Final Principle


The Controller should maximize:


autonomous local progress

minimal human interruption

explicit control of irreversible actions



# End of Policy
