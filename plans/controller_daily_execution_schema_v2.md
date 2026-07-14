# Controller Daily Execution Schema v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md)_


## 1. Purpose


定义 Daily Autonomous Loop v2 的：


- **Daily Execution Plan** 输入/中间结构  
- **Daily Autonomous Operation Report** 输出结构  


便于 Controller、human、reviewers 用同一字段对话。



---

# 2. Track status enum


```text
READY
RUNNING
HOLD
WAITING_APPROVAL
BLOCKED
COMPLETED
```


Definitions: see Daily Autonomous Loop v2 §4.1.



---

# 3. Daily Execution Plan schema


## 3.1 Top-level


```yaml
daily_execution_plan_v2:
  date: "YYYY-MM-DD"           # local calendar date of loop
  generated_at: "ISO-8601"
  controller_mode: "daily_autonomous_loop_v2"
  repo:
    head: "<shortsha>"
    branch: "main"
    ahead: <int>
    behind: <int>
    dirty_summary:
      source: <int>
      plans: <int>
      evidence: <int>
      runtime_visible: <int>
      bak_exception: <int>
  sources_read:
    - PROJECT_CONTROL.md
    - CURRENT_STATUS.md
    - PROJECT_MAP.md
    - git
  global_blockers: []            # strings
  push_authorized: false         # always false unless human phrase recorded
  tracks:
    A: { ... TrackPlan ... }
    B: { ... TrackPlan ... }
    C: { ... TrackPlan ... }
    D: { ... TrackPlan ... }
```


## 3.2 TrackPlan


```yaml
TrackPlan:
  track: "A" | "B" | "C" | "D"
  status: READY | RUNNING | HOLD | WAITING_APPROVAL | BLOCKED | COMPLETED
  current_stage: "<from PROJECT_CONTROL>"
  current_gate: "<string or list>"
  worktree:
    path: "<absolute or repo-relative>"
    branch: "agent/<track>-class"
    tip: "<shortsha|unknown>"
  ownership_ok: true|false
  allowed_action: "<one bounded action>"
  forbidden_actions:
    - push
    - live_without_approval
    - git_add_dot
    # ...
  required_agent: "a-class-executor" | "b-class-executor" | "c-class-executor" | "d-class-executor"
  required_reviewers:
    - evidence-auditor      # optional per action
    - regression-reviewer
    - git-boundary-reviewer
  evidence_expected:
    - "<path or pattern>"
  commit_eligible: true|false
  human_interrupt:
    required: true|false
    reasons: []
  notes: "<caveats / unresolved counts / HOLD rationale>"
```


## 3.3 Plan validity rules


1. Exactly **one** `allowed_action` per READY track.  
2. `commit_eligible=true` only if action class ∈ commit autonomy allow-list.  
3. `push_authorized` must be `false` unless interrupt policy records an explicit human push phrase for this day.  
4. WAITING_APPROVAL tracks must list the **exact approval type** in `human_interrupt.reasons`.  
5. HOLD tracks must cite gate or caveat IDs (e.g. unresolved 6 · BD2E624 · snapshot false).  



---

# 4. Agent completion report schema


Agents return to Controller:


```yaml
agent_completion_v2:
  track: A|B|C|D
  agent: "<name>"
  action_attempted: "<string>"
  result: SUCCESS | PARTIAL | FAILED | SKIPPED
  cninfo_calls: <int>
  live_executed: true|false
  files_modified: [<paths>]
  evidence_written: [<paths>]
  tests_run: [<id>]
  reviewers_invoked: []
  commit_prepared:
    eligible: true|false
    explicit_paths: []
    message_draft: "<optional>"
  gate_claims: []              # must not invent verified/production_ready
  human_interrupt_needed: true|false
  interrupt_reasons: []
  errors: []
```



---

# 5. Daily Autonomous Operation Report schema


## 5.1 Required markdown outline


```markdown
# Daily Autonomous Operation Report

Date: YYYY-MM-DD
HEAD: <shortsha>
Branch: main (ahead X / behind Y)

## Tracks

### A
- status:
- actions:
- commit:
- evidence:
- notes:

### B
- status:
- actions:
- commit:
- evidence:
- notes:

### C
- status:
- actions:
- commit:
- evidence:
- notes:

### D
- status:
- actions:
- commit:
- evidence:
- notes:

## Human attention required
- Push:
- Approval:
- Conflicts:
- Other:

## Safety
- CNINFO count:
- Live execution count:
- Commit count:
- Push count: 0
- git add .: no
- Files deleted: no

## Remaining dirty
- ...

## Next loop recommendation
- ...
```


## 5.2 Field semantics


| Field | Rule |
|-------|------|
| status | final status after loop for that track |
| actions | list of attempted allowed actions (not aspirations) |
| commit | `none` or shortsha list created by this loop for that track |
| Push count | must be `0` unless human-approved push executed outside auto loop |
| CNINFO count | sum of real network CNINFO calls across tracks |
| Live execution count | number of live scopes executed (0 if offline-only day) |


## 5.3 Machine-readable companion (optional)


Same content may also be emitted as:


`outputs/validation/controller_daily_report_YYYYMMDD.yaml`


Must not contain secrets. Prefer summaries over bulk runtime dumps.



---

# 6. Example (illustrative only)


```yaml
daily_execution_plan_v2:
  date: "2026-07-14"
  repo:
    head: "8960bbc"
    ahead: 40
    behind: 4
    dirty_summary: { bak_exception: 1 }
  push_authorized: false
  tracks:
    A:
      status: HOLD
      allowed_action: "none_post_integration_hold"
      required_agent: "a-class-executor"
      commit_eligible: false
      human_interrupt: { required: false, reasons: [] }
      notes: "unresolved 6 retained"
    B:
      status: HOLD
      allowed_action: "none_post_integration_hold"
      notes: "BD2E624 deferred"
    C:
      status: HOLD
      allowed_action: "none_snapshot_blocked"
      notes: "approved_for_snapshot_rebuild=false"
    D:
      status: WAITING_APPROVAL
      allowed_action: "none_await_component_approval"
      human_interrupt:
        required: true
        reasons: ["D shareholder_change component approval"]
```


This example is **not** an authorization to run live or push.



---

# 7. Versioning


- Schema id: `daily_execution_plan_v2` / `daily_autonomous_operation_report_v2`  
- Incompatible field renames require v3  
- Additive optional fields allowed without version bump if ignored by older Controllers
