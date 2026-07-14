# PROJECT_CONTROL — listed_company_data_collector

_Last verified by Controller: 2026-07-14_  
_Workflow upgrade: project subagent team enabled for routine orchestration (2026-07-13)_  
_Workflow: `regression-reviewer` promoted to ROUTINE_READ_ONLY (2026-07-14)_  
_State reconciliation: Git / A-B / queue / autonomy synced to HEAD `4a62f78` (2026-07-14)_  
_Operating mode: **Daily Autonomous Loop v2 Operational Mode**（默认运行；非 Pilot）· policies `c1662f4` · bak ignore `a32d338` · acceptance 2026-07-14_

> This file is the **workflow state register**. Update only after executor completion (when applicable) · Controller verification · required independent review · gate reconciliation · artifact checks.  
> Executor claims alone are insufficient. **Actual files / reports / Git history outrank this file** when they conflict.  
> **Daily execution churn** goes to Daily Autonomous Operation Report；本文件仅记录慢变控制/架构/策略状态。

---

## Project Subagent Team (routine orchestration)

| Agent | Role | Status |
|-------|------|--------|
| `a-class-executor` | A-class track execution | **ACTIVE** |
| `b-class-executor` | B-class track execution | **ACTIVE** |
| `c-class-executor` | C-class track execution | **ACTIVE** |
| `d-class-executor` | D-class track execution | **ACTIVE** |
| `evidence-auditor` | Independent evidence / gate / red-line review | **ROUTINE_READ_ONLY** |
| `git-boundary-reviewer` | Independent commit/push boundary review | **ROUTINE_READ_ONLY** |
| `regression-reviewer` | Independent regression risk / test-coverage review | **ROUTINE_READ_ONLY** |

Agent definitions: `.cursor/agents/*.md`  
**Do not create another subagent** until the human explicitly asks.

**Operating principle:** Executors perform bounded track work · Regression Reviewer checks behavioral impact and test-evidence sufficiency · Evidence Auditor checks factual support of metrics/gates · Git Boundary Reviewer checks commit/push scope safety · Controller coordinates and chooses next valid state.  
**Daily Autonomous Loop v2 Operational Mode:** Controller may daily read state · classify queue · execute allowed offline tasks · bounded local commits · emit daily report · **silent success**.  
**Autonomy split:** local **commit / merge** may proceed under controller autonomy / commit-autonomy v2 when boundary evidence is complete · **push / force-push / remote publication** remain **human-controlled**.  
**Human** still grants live · architecture · policy · and any action outside autonomy scope.  
No agent may propose, execute, review, and approve the same high-risk action alone.  
Reviewers do **not** replace each other.

---

## Git / Branch

| Item | Verified value |
|------|----------------|
| current branch | `main` @ `a32d338`（operational enablement tip; git outranks if moved） |
| origin relationship | **ahead 42 · behind 4** (do not push/rebase without human approval) |
| integrated commits | B fuller slice2 `f0bff3a` · A next-scale slice1 `4118974` · merge `71a83c1` |
| recovery | Option C unique-path recovery `3b0c7ce` |
| controller foundation | policy `0f63a90` · runtime ignore `d385bb6`/`a32d338` · agents `4a62f78` · Daily Loop v2 `c1662f4` |
| prior local commits of note | `85abad0` equity_pledge · `350cdda` B slice1 · `aa087b5` RSU · `41dc049` A scale-200 · `403472d` block_trade · `e738fa9` B scale-200 |
| push | **NOT authorized** · remote publication checkpoint **pending** |
| working tree | main clean at enablement · worktrees may be stale/dirty（preflight Option A） |

---

## Active Approvals

| Type | Status |
|------|--------|
| live approvals | spent for A slice1 · B fuller slice2 · C fuller slice1 · D equity_pledge live (historical) |
| commit approvals | spent for A scale-200 · B scale-200 · B slice1 · B fuller slice2 `f0bff3a` · A next-scale slice1 `4118974` · D RSU · D equity_pledge |
| open live approvals | **none pending** |
| open commit approvals | **none pending** for A/B integrated packages |
| open human decisions | D shareholder_change **component** approval · **remote publication / push** · C snapshot still blocked |

`READY_FOR_APPROVAL` / `READY_FOR_HUMAN_COMMIT_APPROVAL` **≠ approved**. Prior approvals do not carry forward.  
Local commit/merge may be autonomous under policy · **push remains human-gated**.

---

## A-class

| Field | Value |
|-------|-------|
| current_stage | next-scale slice1 **committed** `4118974` · merged via `71a83c1` → **post-integration HOLD** |
| current_gate | execution `PASS_WITH_CAVEAT` · merge_closure `PASS_WITH_CAVEAT` · commit spent `4118974` · **NOT verified** · **NOT production_ready** |
| executor_used | `a-class-executor` (E2E orchestration pilot #2 · offline boundary) |
| reviewer_used | `evidence-auditor` · `git-boundary-reviewer` |
| reviewer_result | Evidence Auditor `VERIFIED_ENOUGH_TO_CONTINUE` HIGH 90% · Git Boundary `READY_FOR_HUMAN_COMMIT_APPROVAL` HIGH 92% (pre-commit; now spent) |
| reviewer_confidence | Evidence 90% · Git Boundary 92% |
| evidence_paths | live report · effective **294** · unresolved **6** · cumulative **486** · commit `4118974` · merge `71a83c1` · prior boundary package (**39** whole-file) |
| known_caveats | unresolved AD2E216/270/284/308/323/373 · OPTION 1 excluded mixed shared files · bulk raw_metadata 300 excluded · WT soft note: scale-200 dryrun_summary dirt outside include list · live_path post-live guard test known fail |
| next_allowed_task | **post-integration HOLD** · no live retry · no gate upgrade · optional later offline caveat planning only with new scope |
| blocked_actions | push · live rerun · CNINFO · `git add .` / `-A` · PDF/DB/RAG · verified · production_ready · mutate scale-200/Phase3 production roots |
| last_verified_at | 2026-07-14 (state reconciliation · Git history) |

---

## B-class

| Field | Value |
|-------|-------|
| current_stage | fuller slice2 **committed** `f0bff3a` · integrated on main → **post-integration HOLD** |
| current_gate | execution `PASS_WITH_CAVEAT` · merge_closure `PASS_WITH_CAVEAT` · commit spent `f0bff3a` · **NOT verified** · **NOT production_ready** |
| executor_used | `b-class-executor` (health check OK) |
| reviewer_used | `evidence-auditor` · `git-boundary-reviewer` |
| reviewer_result | Evidence Auditor `VERIFIED_ENOUGH_TO_CONTINUE` HIGH 92% · Git Boundary `READY_FOR_HUMAN_COMMIT_APPROVAL` HIGH 90% (pre-commit; now spent) |
| reviewer_confidence | Evidence 92% · Git Boundary 90% |
| evidence_paths | slice2 report CSV · merge closure · boundary package (**36** whole-file) · commit `f0bff3a` · unresolved ledger **1** (BD2E624) |
| known_caveats | BD2E624 network_error · deferred · 8 empty_response acceptable_edge · mixed shared files **excluded** from commit (OPTION 1) · bulk sidecars excluded · retry_v2 sidecars recovered via Option C where applicable |
| next_allowed_task | **post-integration HOLD** · no live rerun · BD2E624 remains deferred · no gate upgrade |
| blocked_actions | push · rerun · live · gate upgrade · `git add .` · `git add -A` · PDF/DB/RAG · verified · production_ready · mutate scale-200/slice1 roots |
| last_verified_at | 2026-07-14 (state reconciliation · Git history) |
| prior commits | scale-200 `e738fa9` · slice1 `350cdda` · fuller slice2 `f0bff3a` — **NOT pushed** |

---

## C-class

| Field | Value |
|-------|-------|
| current_stage | fuller-market slice1 **status-ledger rebuilt + QA closure recorded** · snapshot **blocked** |
| current_gate | execution `PASS_WITH_CAVEAT` · status_ledger_rebuild `PASS_WITH_CAVEAT` · qa_closure `PASS_WITH_CAVEAT` · `approved_for_snapshot_rebuild = false` |
| executor_used | `c-class-executor` (orchestration pilot · offline ledger+QA) |
| reviewer_used | `evidence-auditor` |
| reviewer_result | `VERIFIED_ENOUGH_TO_CONTINUE` |
| reviewer_confidence | HIGH **92%** |
| computed_note | universe/disk/ledger **200** · complete **193** · partial **7** · missing **0** · prior ledger **100** → rebuilt **200** · resume-audit dual-layer 190+3 empty-dividend (not contradiction) |
| evidence_paths | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` · bak `...bak_pre_offline_rebuild_20260713T100619Z` · `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` · caveat ledger · metrics · reconcile CSV · qa_closure_audit/ |
| known_caveats | partial CE1E002/003/034/061/067/070/071 · empty-dividend CE1E176/188/193 · harvest ≠ snapshot · Session 2 historical resume caveat |
| next_allowed_task | **hold** · optional later slice2 planning (separate approval) · **not** snapshot rebuild |
| blocked_actions | live without new approval · 863/phase3/phase35 mutation · snapshot rebuild · commit/push harvest bulk without boundary · verified / production_ready / bare PASS |
| last_verified_at | 2026-07-13 (E2E orchestration pilot) |

---

## D-class

| Field | Value |
|-------|-------|
| current_stage | equity_pledge **committed** `85abad0` → shareholder_change planning **READY_FOR_APPROVAL** |
| current_gate | equity_pledge commit `PASS_WITH_CAVEAT` · shareholder_change planning `READY_FOR_APPROVAL` · known-event final `PASS_WITH_CAVEAT` |
| executor_used | `d-class-executor` (health check OK · evidence-boundary stress test **PASS**) |
| reviewer_used | (n/a for health/stress read-only) |
| evidence_paths | equity_pledge commit `85abad0` · shareholder_change planning package · known-event `389cd9c` |
| known_caveats | disclosure→structured promotion **forbidden** · DLC006R/301259 separate disclosure lineage · `disclosure_schedule` `d37ce0a` **not** on current `main` (side-branch risk) · several D commits **NOT pushed** |
| next_allowed_task | **Human approve** shareholder_change as next component (Level 2) — queue unchanged · **not executed** by this upgrade |
| blocked_actions | live · CNINFO · targeted probe · runner without package · reopen DLC006R/301259 · claim verified · push without approval |
| last_verified_at | 2026-07-13 |

---

## Cross-track / Protected Roots

Protected / do-not-mutate without explicit scope:

- A: `cninfo_a_class_erad_scale_200/` · Phase 3 / A3M017 production roots
- B: `cninfo_b_class_erad_scale_200/` · `cninfo_b_class_erad_next_scale_slice1/` · Phase 3 roots
- C: 863 harvest/snapshot · phase3/phase35 production harvest/snapshot
- D: closed first-slice roots for margin/disclosure/block_trade/RSU/equity_pledge

Global red lines: no PDF/OCR/DB/MinIO/RAG · no bare PASS · no verified · no production_ready · no disclosure→structured promotion.

**Cross-track tasks:** classify as `CROSS_TRACK_REVIEW_REQUIRED` · do not silently split among executors · inform human or bounded architecture review.

---

## Senior Review Routing Policy

| Route | When |
|-------|------|
| **1 Controller + project reviewers** | offline · single-track · no schema/identity · no live/commit/push · evidence consistent · confidence ≥85% · existing workflow |
| **2 ChatGPT Project Chat** | confidence 70–85% · 1–2 evidence conflicts · disputed classification · large single-track commit · bounded packet only |
| **3 ChatGPT Work** | cross-track · architecture/schema · full-market Era · new storage/product · long formal design |

Do **not** recommend Work for ordinary next-step routing.

---

## Controller Role

Controller is the main workflow manager. It must:

1. Read this file  
2. Identify exact track and stage  
3. Select the correct executor  
4. Provide **one bounded** task (never vague “continue X”)  
5. Receive executor completion report  
6. Independently inspect the most important evidence  
7. Invoke the appropriate reviewer  
8. Compare executor / Controller / reviewer conclusions  
9. Recompute the next state  
10. Continue automatically only when allowed  
11. Notify the human only at approval boundaries, material conflicts, or important milestones  

Controller must **not** normally implement track-specific code when a specialized executor exists.

### Executor routing

| Executor | Use for |
|----------|---------|
| `a-class-executor` | periodic-report metadata · A/Q report lineage · A retry/reachability/runner/dry-run/live/closure/boundary |
| `b-class-executor` | announcement metadata · CNINFO retrieval · fuller slices · EP002/orgId · B retry/harvest/closure/boundary |
| `c-class-executor` | F10/profile harvest · fuller-market · isolated resume · status-ledger rebuild · QA closure · snapshot planning |
| `d-class-executor` | market-behavior components · known-event · probes · replacement · evidence boundary · component closure |

### Executor delegation must include

track · stage · exact goal · allowed/protected roots · file-mod allowed? · tests required? · CNINFO allowed? · live approved? · request cap · output root · expected artifacts · gate rule · stop conditions · completion-report requirements.

Never: “Continue B.” / “Fix C.” / “Do the next step.” / “Finish D.”

---

## Evidence Auditor (ROUTINE_READ_ONLY)

| Item | Value |
|------|-------|
| agent | `.cursor/agents/evidence-auditor.md` |
| mode | **ROUTINE_READ_ONLY** |
| promoted_at | 2026-07-13 |
| shadow trials | #1 A slice1 merge · #2 B slice2 merge+boundary |

**Invoke after:** live / retry-live / resume-live · QA/merge/failure/final closure · cumulative lineage merge · status-ledger rebuild · snapshot candidate selection · this file changes · protected-root “untouched” claims · metrics that determine next gate · `PASS_WITH_CAVEAT` · `READY_FOR_COMMIT_REVIEW`

**Skip:** prompt drafting · read-only health checks · basic planning with no state claim · wording-only edits · no gate consequence

Must remain read-only. Does not approve live/commit/push/schema/identity/expansion.

---

## Regression Reviewer (ROUTINE_READ_ONLY)

| Item | Value |
|------|-------|
| agent | `.cursor/agents/regression-reviewer.md` |
| mode | **ROUTINE_READ_ONLY** (promoted from shadow 2026-07-14) |
| shadow #1 | A-class Retry v3 Live Path · `TARGETED_TESTS_REQUIRED` · confidence **78%** |
| shadow #2 | B-class EP002 Reachability Precheck · `TARGETED_TESTS_REQUIRED` · confidence **80%** |
| note | Promotion ≠ approval of any live/commit · does **not** replace Evidence Auditor or Git Boundary Reviewer |

**Invoke after Executor implementation** (and before closure / commit-boundary prep) when:

- runners / CLI / approval guards / output-root logic / report writers / schemas change
- shared runners or shared utilities are touched
- live-path or dry-run control flow is added or altered
- test claims are offered as proof of non-regression

**Skip:** prompt drafting · read-only health checks · planning-only with no code change · pure documentation wording · artifact-only packaging with no behavioral code change

**Must:**

- classify changed files (track-local / shared runner / CLI_OR_GUARD / report writer / test / docs)
- inspect behavioral impact · call sites · safety guards · data contracts
- map risks → tests · distinguish **claimed** pass counts from **executed** evidence
- remain read-only · **not** run tests unless Controller authorizes an exact offline command later
- **not** modify code/tests · **not** approve live/commit/push · **not** change gates

**Allowed verdicts:** `REGRESSION_RISK_ACCEPTABLE` · `TARGETED_TESTS_REQUIRED` · `EXECUTOR_FIX_OR_TEST_REQUIRED` · `CROSS_TRACK_REGRESSION_REVIEW_REQUIRED` · `INSUFFICIENT_REGRESSION_EVIDENCE` · `RED_LINE_REGRESSION_RISK` · `HUMAN_DECISION_REQUIRED`

**Continuation:** auto-continue past implementation only when verdict = `REGRESSION_RISK_ACCEPTABLE` **and** confidence ≥ **85%** (and other offline continuation rules hold).  
`TARGETED_TESTS_REQUIRED` → stop for Controller-authorized offline re-run / targeted test evidence · then re-review.

---

## Git Boundary Reviewer (ROUTINE_READ_ONLY)

| Item | Value |
|------|-------|
| agent | `.cursor/agents/git-boundary-reviewer.md` |
| mode | **ROUTINE_READ_ONLY** (promoted from shadow 2026-07-13) |
| shadow #1 | `BOUNDARY_RECONCILIATION_REQUIRED` (mixed shared hunks) |
| shadow #2 | `READY_FOR_HUMAN_COMMIT_APPROVAL` HIGH 90% · **36** whole-file paths · 0 staged · `NOT_APPROVED` |
| note | Promotion ≠ approval of any live/push · B fuller slice2 commit already spent `f0bff3a` |

**Invoke when:** commit-boundary artifacts complete · safe-to-commit prepared · commit proposed · shared files in include list · unrelated dirty WT · path-count reconcile · staged paths exist · post-commit scope check · push review requested

**Must check:** exact paths · actual diff · staged · unchanged/missing · mixed hunks · prohibited files · cross-track · tests · branch divergence · approval-state separation

May recommend `READY_FOR_HUMAN_COMMIT_APPROVAL`.  
Must **not** grant `HUMAN_COMMIT_APPROVED`. Must remain read-only. Must not emit commit commands as approval.

---

## Standard Task Flows

### Ordinary track work

```text
Human / queue
→ Controller classifies track+stage
→ matching Executor
→ Controller initial verification
→ Regression Reviewer (when code/behavior changed)
→ Evidence Auditor (when required)
→ Controller recomputes gate
→ next offline task may auto-continue
```

### Implementation → closure

```text
Executor implements runner/live-path/guard change
→ Regression Reviewer (routine)
→ if TARGETED_TESTS_REQUIRED: authorize offline tests · re-review
→ if REGRESSION_RISK_ACCEPTABLE: continue to dry-run / live-approval boundary / closure as defined
→ Evidence Auditor on metrics/gates when required
→ commit-boundary only after closure verified
→ Git Boundary Reviewer before local commit (autonomy) or human commit approval
```

### Commit work

```text
Closure verified
→ commit boundary prepared
→ Git Boundary Reviewer
→ Controller compares
→ if autonomy policy conditions met: local explicit-path commit / local merge may proceed
→ else: human commit approval requested before commit
→ push never implied by local commit
```

### Push work

```text
Commit executed
→ post-commit evidence check
→ Git Boundary Reviewer (push-boundary)
→ human push approval requested
→ push only after explicit approval
```

---

## Automatic Continuation (offline only)

All must hold:

- single track · no live · no push · no schema/identity · no full-market expansion  
- evidence consistent  
- when Evidence Auditor required: `VERIFIED_ENOUGH_TO_CONTINUE` · confidence ≥ **85%** · Controller↔reviewer gates match  
- when Regression Reviewer required: `REGRESSION_RISK_ACCEPTABLE` · confidence ≥ **85%** (else stop for targeted offline tests)  
- no material red-line · next step clearly defined by state machine  
- local commit/merge only when autonomy policy + Git Boundary conditions are met · **never** auto-push  

Examples: planning→runner · runner→dry-run · live audited→offline closure · closure audited→offline commit-boundary · ledger rebuilt audited→offline QA · boundary-ready→local explicit-path commit (when policy allows).

---

## Human Approval Boundaries

Stop before: CNINFO live · resume/retry live · **push** · remote publication · branch sync that rewrites shared history without human · full-market expansion · schema · identity merge · caveat-as-final-policy · disclosure→structured promotion · PDF/OCR/DB/MinIO/RAG Era · cross-track architecture.

Local **commit / merge** may proceed under controller autonomy policy when Git Boundary evidence is complete; they are **not** a substitute for human **push** approval.  
When autonomy conditions are not met, stop before commit/merge and request human approval.

---

## Material Disagreement Rule

Do **not** choose the most optimistic conclusion. Use the **safest supported** state.

Examples: Auditor `INSUFFICIENT_EVIDENCE` → stop · Git Reviewer `BOUNDARY_RECONCILIATION_REQUIRED` → reconcile before human approval · Regression Reviewer `TARGETED_TESTS_REQUIRED` → authorize offline re-run before treating non-regression as closed.  
Executor must not review/approve its own work.

---

## PROJECT_CONTROL update rule

Update **only the relevant track** after: executor completion · Controller verification · required review · gate reconcile · artifacts exist · no material contradiction.

Record: `current_stage` · `current_gate` · `executor_used` · `reviewer_used` · `reviewer_result` · `reviewer_confidence` · `evidence_paths` · `known_caveats` · `next_allowed_task` · `blocked_actions` · `last_verified_at`.

---

## Human Notification Policy

Do **not** report every routine internal delegation.

Notify when: live/push approval required · remote publication checkpoint · autonomy commit/merge outside clear policy · material contradiction · reviewer confidence <85% · red-line risk · cross-track/architecture · important milestone · queue cannot continue safely.

### Human report format

Track · Stage · Executor · Reviewer · Executor/Controller/Reviewer gates · Reviewer verdict · Confidence · Material contradictions · Action completed · Decision required · Exact approval requested · Next action if approved · Blocked actions.

---

## Pending Reviews

| Item | Route | Note |
|------|-------|------|
| A next-scale slice1 | **INFO** | committed `4118974` · merged `71a83c1` · **post-integration HOLD** · unresolved **6** retained · **NOT verified** |
| B fuller slice2 | **INFO** | committed `f0bff3a` · **post-integration HOLD** · BD2E624 deferred · **NOT verified** |
| C slice1 ledger+QA | **HOLD** | pilot closed `PASS_WITH_CAVEAT` · snapshot still **blocked** (`approved_for_snapshot_rebuild = false`) |
| D shareholder_change | **Human Level-2** | component approval pending · `READY_FOR_APPROVAL` ≠ approved |
| remote publication | **Human** | `main` ahead **42** / behind **4** · push **NOT authorized** |
| D commits unpushed · disclosure `d37ce0a` not on main | **INFO / Controller** | no self-approve push |
| Daily Autonomous Loop v2 | **OPERATIONAL** | default mode · policies `c1662f4` · first run 2026-07-14 |

---

## Controller Queue (priority)

1. **C** — slice1 ledger+QA **done** (`PASS_WITH_CAVEAT`) · **HOLD** · optional later slice2 planning · **no snapshot**
2. **D** — human component approval for shareholder_change (Level 2) · `READY_FOR_APPROVAL` ≠ approved
3. **Remote publication checkpoint** — human push / recovery strategy for `main` (ahead 42 · behind 4) · **pending**
4. **A** — **post-integration HOLD** (`4118974` / `71a83c1`) · unresolved caveats retained · no live retry
5. **B** — **post-integration HOLD** (`f0bff3a`) · BD2E624 deferred · no live rerun

A/B Level-2 commit waits are **closed** (spent). Push remains human-controlled.  
Daily Loop v2 Operational Mode active：例行成功静默；仅审批/冲突/破坏性/push/安全边界打断。
