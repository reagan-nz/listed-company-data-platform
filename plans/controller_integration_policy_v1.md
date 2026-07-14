# Controller Integration Policy v1


## 1. Purpose


This document defines how Controller integrates completed Executor branches into the main branch.


The purpose:


- preserve branch isolation;
- prevent unsafe merges;
- validate completed work;
- maintain project consistency.


Commit completion does not automatically mean integration readiness.


---

# 2. Integration State Model


A branch moves through:


EXECUTOR_COMPLETE
↓
COMMIT_VERIFIED
↓
INTEGRATION_REVIEW
↓
MERGE_APPROVED
↓
MERGED
↓
POST_MERGE_VALIDATED


Each state requires separate validation.


---

# 3. Integration Preconditions


A branch is eligible for integration only when:


- commit exists;
- commit hash recorded;
- explicit boundary respected;
- reviewers completed;
- approval state confirmed.


Required:


Commit

Evidence validation

Boundary validation


---

# 4. Integration Planning


Before merge:


Controller creates an integration plan.


Example:


Integration Batch:
Branch:
agent/b-class
Commit:
f0bff3a
Target:
main
Order:
B-class

A-class



The Controller must define:

- merge order;
- expected conflicts;
- shared files;
- validation requirements.


---

# 5. Merge Ordering Rule


When multiple branches are ready:


Controller should merge based on:


1. dependency;
2. conflict risk;
3. scope isolation.


Example:


Independent artifact branches:

B
then
A


Shared control-file changes:

require serialization.


---

# 6. Shared File Rule


The following require special handling:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans


If multiple branches modify them:


Controller must:


- compare changes;
- resolve intentionally;
- avoid silent overwrite.


---

# 7. Merge Review Requirement


Before merge:


Required:


Integration Review


Checks:


- commit belongs to approved branch;
- no unexpected files;
- no scope expansion;
- no gate inflation.


---

# 8. Post-Merge Validation


After merge:


Controller verifies:


- main HEAD updated;
- expected files exist;
- previous boundaries preserved;
- no unrelated changes introduced.


---

# 9. Push Boundary


Merge does not authorize push.


Push requires separate approval.


State:


Merged locally
≠
Published remotely


---

# 10. Conflict Handling


If merge conflict occurs:


Controller must:


- stop;
- report conflict;
- identify files;
- request resolution.


Do not:


- auto overwrite;
- discard changes;
- choose silently.


---

# 11. Operating Principle


Prefer:


small controlled integrations

clear ownership

validated merge state


Avoid:


large uncontrolled merge

unknown ownership

automatic push


---

# Autonomous Local Integration


## Principle


A validated local merge may proceed without push authorization.


merge local
!=
publish remote


## Conditions for Autonomous Merge


Controller may merge locally when:


- source commits are verified;
- integration review passed;
- conflict risk acceptable;
- shared file handling validated.


## Restrictions


Local merge does not authorize:


- push
- force push
- remote modification



## Human Boundary


Human approval remains required for remote publication.



---

# End of Policy
