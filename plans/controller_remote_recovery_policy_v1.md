# Controller Remote Recovery Policy v1


## 1. Purpose


This document defines how Controller handles remote divergence before push.


Remote reconciliation is a separate lifecycle stage.


The Controller must distinguish:


local completion
≠
remote publication


A successful local merge does not imply that push is safe.



---

# 2. Remote Divergence Model


Controller must classify remote state:


LOCAL_ONLY
REMOTE_ONLY
DIVERGED
SYNCHRONIZED


Examples:


LOCAL_ONLY:

Local commits exist, remote unchanged.


REMOTE_ONLY:

Remote commits exist, local missing them.


DIVERGED:

Both local and remote contain unique commits.


SYNCHRONIZED:

Same history.



---

# 3. Push Block Rule


If:


local != remote


Controller must not push automatically.


Required:


Remote analysis

Recovery decision

Human approval


---

# 4. Forbidden Actions


Without explicit recovery decision:


Controller must not:


- force push;
- overwrite remote history;
- silently discard remote commits;
- automatically rebase;
- automatically merge conflicting histories.



---

# 5. Recovery Options


Controller should evaluate:


## Option A — Merge Remote History


Use when:


- remote commits must remain;
- histories should become unified;
- conflicts can be intentionally resolved.


Requires:


- conflict review;
- integration review.



## Option B — Preserve Separate Histories


Use when:


- ownership unclear;
- remote state requires investigation;
- immediate reconciliation unsafe.


No push allowed.



## Option C — Targeted Recovery


Use when:


- only specific remote commits are required;
- full merge would introduce unnecessary conflicts.


Examples:


- cherry-pick selected commits;
- recover specific artifacts.



---

# 6. Conflict Handling


If conflicts exist:


Controller must:


- stop;
- identify conflicting files;
- explain ownership;
- request decision.


Never:


- auto overwrite;
- choose silently.



---

# 7. Shared File Rule


Special attention required for:


- PROJECT_CONTROL.md
- CURRENT_STATUS.md
- PROJECT_MAP.md
- execution plans
- shared runners


These files require intentional reconciliation.



---

# 8. Remote Recovery Review


Before recovery:


Required checks:


- commit ownership;
- purpose;
- overlap;
- conflict risk;
- downstream impact.



---

# 9. Human Decision Boundary


Human approval is required for:


- recovery strategy;
- conflict resolution;
- force push decisions;
- remote history changes.



---

# 10. Operating Principle


Prefer:


understand remote state

preserve history

controlled reconciliation


Avoid:


blind push

silent overwrite

history destruction



---

# End of Policy
