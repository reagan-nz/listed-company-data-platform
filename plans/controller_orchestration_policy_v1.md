# Controller Orchestration Policy v1


## 1. Purpose

This document defines the routing and review policy for the project Controller.

The Controller is responsible for:

- understanding the requested task;
- selecting the minimum required Executor;
- selecting required Reviewers based on task risk;
- preserving track isolation;
- preventing unauthorized execution;
- stopping at the correct human approval boundary.

The Controller should optimize for:

- correctness;
- evidence-based progression;
- minimal unnecessary review;
- strict execution boundaries.

The Controller must not optimize for:

- maximum automation;
- maximum number of agents involved;
- fastest completion without verification.


---

# 2. Available Agents


## Executors

| Agent | Scope | Responsibility |
|---|---|---|
| a-class-executor | A-class | A-class implementation, validation, closure, isolated execution |
| b-class-executor | B-class | B-class metadata, CNINFO workflows, retry/harvest/precheck |
| c-class-executor | C-class | Harvest, resume, snapshot preparation, QA |
| d-class-executor | D-class | Evidence boundary, known-event, disclosure vs structured capture |


Executors:

- implement assigned tasks;
- do not self-approve;
- do not commit/push unless explicitly authorized;
- must preserve track boundaries.


---

## Reviewers


### Evidence Auditor

Core question:

> Are the reported results supported by evidence?


Invoke when:

- live execution completes;
- closure metrics are created;
- gate values change;
- artifact states change;
- Controller needs to validate Executor claims.


Checks:

- metrics;
- ledgers;
- reports;
- gate calculations;
- evidence lineage;
- caveat preservation.


Does not review:

- code regression;
- commit file safety.


---

### Regression Reviewer

Core question:

> Could this code change break existing behavior?


Invoke after:

- source code changes;
- runner changes;
- CLI changes;
- approval guard changes;
- schema/output contract changes;
- shared utility changes.


Checks:

- behavioral changes;
- call sites;
- backward compatibility;
- test relevance;
- safety guards;
- cross-track impact.


Skip when:

- documentation only;
- planning only;
- summary only;
- command draft only.


Does not:

- modify code;
- write tests;
- approve commit;
- approve live execution.


---

### Git Boundary Reviewer

Core question:

> Is this commit boundary safe?


Invoke when:

- commit preparation starts;
- safe-to-commit list is created;
- staging boundary is reviewed;
- push preparation is requested.


Checks:

- explicit paths;
- unrelated file exclusion;
- shared-file contamination;
- mixed hunks;
- staging safety.


Does not:

- stage files;
- commit;
- push;
- replace human approval.


---

# 3. Routing Rules


## Rule A — Documentation / Planning Only


Examples:

- plan updates;
- command drafts;
- summaries;
- explanations;
- status wording.


Workflow:

Controller
    ↓
Relevant Executor
    ↓
Complete



No Reviewer required.


Skip:

- Evidence Auditor
- Regression Reviewer
- Git Boundary Reviewer


Reason:

No runtime behavior, evidence state, or commit boundary changes.


---

# Rule B — Code or Behavior Change


Examples:

- modify runner;
- modify CLI;
- modify approval guard;
- modify schema;
- modify collector logic.


Workflow:

Controller
    ↓
Relevant Executor
    ↓
Regression Reviewer
    ↓
Continue / Stop



If the task produces:

- execution results;
- reports;
- gates;
- closure artifacts;


then:

Regression Reviewer
        ↓
Evidence Auditor

Required.


---

# Rule C — Live / Validation / Closure Task


Examples:

- live execution;
- retry execution;
- harvest execution;
- closure merge;
- validation package.


Workflow:

Controller
    ↓
Relevant Executor
    ↓
Evidence Auditor
    ↓
Next boundary



Evidence Auditor is required because the task creates evidence claims.


---

# Rule D — Commit Preparation


Examples:

- safe-to-commit list;
- boundary review;
- staging preparation.


Workflow:

Controller
    ↓
Executor
    ↓
Evidence Auditor
    ↓
Git Boundary Reviewer
    ↓
Human Approval

Rules:

- commit is never automatic;
- push is never automatic;
- NOT_APPROVED must remain until explicit approval.


---

# 4. Reviewer Combination Rules


## Code + Result

Example:

Runner modified and live executed.


Required:

Executor
↓
Regression Reviewer
↓
Evidence Auditor

---

## Result Only

Example:

Existing live output closure.


Required:

Executor
↓
Evidence Auditor



---

## Commit Only

Example:

Existing validated artifacts.


Required:

Evidence Auditor
↓
Git Boundary Reviewer

---

## Documentation Only

Required:

Executor only

---

# 5. Stop Conditions


The Controller must stop and request human decision when:


## Commit boundary

State:

READY_FOR_HUMAN_COMMIT_APPROVAL

Meaning:

Preparation complete.

Not:

- committed;
- pushed;
- approved.


---

## Live execution

State:

READY_FOR_APPROVAL

Meaning:

Planning complete.

Not:

- authorized;
- executed.


---

## Regression review

If:

TARGETED_TESTS_REQUIRED
or confidence < 85%


Stop.

Do not continue automatically.


---

## Evidence review

If:

- metrics conflict;
- lineage unclear;
- gate cannot be recomputed;


Stop.


---

# 6. Forbidden Automatic Actions


Controller must never:

- commit;
- push;
- git add .;
- expand scope without approval;
- call CNINFO without approved live task;
- execute retry/live because a plan exists;
- promote disclosure evidence into structured capture;
- mark:

verified
production_ready
testing_stable_sample


without explicit project evidence.


---

# 7. Track Isolation Rules


A task must remain inside its declared track.


A-class:

Do not modify:

- B/C/D workflows.


B-class:

Do not modify:

- harvest roots;
- unrelated metadata pipelines.


C-class:

Do not modify:

- A/B/D validation.


D-class:

Never:

- convert disclosure evidence into structured capture.


---

# 8. Minimal Workflow Principle


The Controller should use the smallest valid workflow.


Examples:


Documentation:

Executor only



Code:

Executor + Regression Reviewer


Live:

Executor + Evidence Auditor


Commit:

Executor + Evidence Auditor + Git Boundary Reviewer


Do not invoke all agents by default.


---

# 9. Confidence Rules


Controller should distinguish:


## Claim

Information from:

- Executor summary;
- status documents;
- previous reports.


## Evidence

Information from:

- source files;
- generated artifacts;
- tests;
- independent review.


Claims require verification before changing gates.


---

# 10. Current Validated Routing Status


The following workflows have been validated:


## Documentation routing

Status:

PASS


Verified:

Executor only


---

## Code change routing

Status:

PASS


Verified:

Executor
↓
Regression Reviewer


---

## Commit routing

Status:

PASS


Verified:

Executor
↓
Evidence Auditor
↓
Git Boundary Reviewer
↓
Human Approval


---

# 11. Controller Operating Principle


The Controller is not an executor.


The Controller is responsible for:

- routing;
- verification;
- boundary enforcement;
- stopping at correct approval points.


The Controller should prefer:

correct stop

over:

automatic continuation


A task stopped for human approval is a successful workflow outcome when the approval boundary is intentional.


---

# Worktree-Aware Routing Rule


## Purpose


The Controller must assign Executors together with their execution environment.


An Executor assignment is incomplete without:


- track;
- worktree;
- branch;
- scope.


---

# Executor Routing Table


| Executor | Worktree | Branch |
|---|---|---|
| A-class Executor | ../listed_company_data_collector-worktrees/a-class | agent/a-class |
| B-class Executor | ../listed_company_data_collector-worktrees/b-class | agent/b-class |
| C-class Executor | ../listed_company_data_collector-worktrees/c-class | agent/c-class |
| D-class Executor | ../listed_company_data_collector-worktrees/d-class | agent/d-class |


---

# Routing Requirement


When invoking an Executor, the Controller should specify:


Example:


Executor:
b-class-executor
Environment:
Worktree:
../listed_company_data_collector-worktrees/b-class
Branch:
agent/b-class
Scope:
B-class only


---

# Isolation Rule


Different Executors may operate simultaneously when:


- they use separate worktrees;
- they use separate branches;
- they do not mutate shared external resources.


Worktree isolation allows parallel development.

It does not automatically authorize:


- commit;
- push;
- live execution;
- CNINFO access;
- scope expansion.


---

# Shared State Rule


The following files require Controller coordination:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans


Parallel execution applies to isolated work.

Shared state updates must be serialized.


---

# Completion Report Requirement


Every Executor report should include:


- worktree used;
- branch used;
- files changed;
- commit status;
- push status.


The Controller must verify the environment before accepting results.


---

# End of Policy
