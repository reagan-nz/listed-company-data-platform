# Daily Loop v2 — Task Discovery Queue 2026-07-14 (run2)


_Controller coordination only · not mission execution_


## Preflight


| Item | Value |
|------|-------|
| HEAD | `afbc274` |
| Worktrees | A/B/C/D stale+dirty → Option A **SKIP sync** · no overwrite |
| Track control labels | A HOLD · B HOLD · C HOLD · D WAITING_APPROVAL |
| Discovery | **required** before NO_SAFE_READY |


## Discovered safe READY candidates（promoted）


| ID | Track | Agent | Priority | Allowed action | Forbidden |
|----|-------|-------|----------|----------------|-----------|
| A-D1 | A | a-class-executor | P1/P2 | offline coverage-gap + unresolved-6 packaging | live · CNINFO · gate upgrade |
| B-D1 | B | b-class-executor | P1/P2 | offline BD2E624 deferred-case triage package | live · CNINFO · force resolve |
| C-D1 | C | c-class-executor | P3 | offline QA/evidence completeness for partial-7 | snapshot rebuild · harvest mutate |
| D-D1 | D | d-class-executor | P2 | offline shareholder_change prep refresh | live · claim approved · runner execute |


Hard order: capability/evidence bands first · controller policy dirty deferred.
