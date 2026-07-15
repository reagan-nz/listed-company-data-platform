# Controller Commit Autonomy Policy v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md)_  
_互补：controller_autonomy_policy_v1 · controller_integration_policy_v1 · controller_push_policy_v1_


## 1. Purpose


定义 Daily Autonomous Loop v2 下，Controller **何时可自动 local commit**，以及 **何时必须 human**。


Hard split:


```text
local commit / local merge  ≠  push
```


Push remains human-controlled under push policy v1.



---

# 2. Preconditions for any autonomous commit


All must hold:


1. explicit-path staging only（禁止 `git add .` / `-A`）  
2. paths owned by a single domain package  
3. no secrets / credentials  
4. no runtime bulk（raw / normalized harvest dumps / raw_metadata / live_snapshots / run_meta）  
5. git-boundary checks satisfied when commit includes shared runners or mixed tracks  
6. message states domain purpose（docs/feat/test）  
7. post-commit: Push count remains 0 unless separate human push executed  


If any fails → do not auto-commit · escalate or hold paths dirty.



---

# 3. Allowed autonomous commit classes


Controller **may** auto-commit when package is purely:


| Class | Examples |
|-------|----------|
| Documentation | CURRENT_STATUS / PROJECT_MAP / README / CHANGELOG / plans updates that sync tip without gate inflation |
| Validation evidence | human-readable summaries · ledgers · matrices · audit packets under `outputs/validation/` |
| Tests | isolated test hardening with mock roots · no production wipe |
| Isolated source | track-local runners/guards/builders already reviewed or low-risk offline tooling |
| Bounded artifacts | schema drafts under `schemas/` paired with portrait/tooling packages |
| Control-adjacent docs | **new** controller policy design docs under `plans/controller_*`（not silent rewrite of live PROJECT_CONTROL without explicit package） |
| **CNINFO live 执行成果**（2026-07-15 · Scope-Driven Execution Amendment） | 已授权 scope 内 CNINFO live 抓取产出的 report/summary/quality-report/evidence（`outputs/validation/` 下），以及实现该 scope 所需的 runner/collector 源码变更——见 [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)；不需要为每次 live 执行单独申请批准才能提交 |


Preferred: **one domain per commit**（C evidence ≠ D plans ≠ portrait schema）.



---

# 4. Requires human before commit


Do **not** auto-commit; interrupt or wait:


| Class | Examples |
|-------|----------|
| Push-related | anything whose purpose is remote publication |
| Merge conflicts | unresolved conflict markers / contested shared files |
| Destructive | deletions of historical evidence · protected-root removals |
| Production mutation payloads | commits whose sole intent is to apply production status/harvest mutations without prior approved apply execution record |
| Gate changes | edits that upgrade to verified / production_ready / flip snapshot approval |
| Ambiguous ownership | mixed A+B+C paths in one index  
| Policy authority changes | rewriting interrupt/commit allow-lists to expand risk without human acceptance |


Note: production **apply tools** may be committed as source（guarded by flags）under §3 Isolated source after review; the **act of applying** to production CSV remains approval-gated and is not “fixed by commit”.



---

# 5. Daily Loop commit procedure


```text
agent prepares explicit_paths + message_draft
    ↓
Controller verifies allow-list class
    ↓
optional git-boundary-reviewer
    ↓
git add -- <paths...>
    ↓
verify staged set == intended set
    ↓
git commit
    ↓
record sha in daily report
    ↓
never push
```



---

# 6. Multi-commit batching


Allowed in one loop day:


- multiple bounded commits  
- sequential packages (plans → evidence → source)  


Forbidden:


- one giant mixed commit across lifecycle domains  
- committing ignored runtime by force-add unless human explicitly orders an exception package  



---

# 7. Special case — bak / recovery files


`company_harvest_status.csv.bak_pre_offline_rebuild_*`:


- default: **do not commit** from harvest tree  
- preferred: ignore regenerations; if retention needed, **copy** into `outputs/validation/...` evidence package then commit the copy  
- current force-visible un-ignore in `.gitignore` is a known exception; tightening ignore is a separate hygiene task（may be autonomous docs/ignore commit if scoped only to ignore rule + evidence copy）



---

# 8. Relationship to autonomy levels (v1)


| v1 Level | v2 commit stance |
|----------|------------------|
| Level 0 | push / live / gate promotion — no auto-commit that enacts them |
| Level 1 | human approved a bounded commit workflow — Controller may finish explicit-path commit |
| Autonomous Loop | docs/evidence/tests/isolated source may commit without per-commit human ping |


v2 does **not** revoke Level 0.



---

# 9. Safety counters (must appear in daily report)


After commits:


- Commit count = number of local commits created by the loop  
- Push count = 0  
- `git add .` = no  
- Files deleted = no（unless human-approved destructive package — then interrupt policy applies） |



---

# 10. Anti-patterns


Forbidden:


- auto-commit because “tests passed” while paths include harvest bulk  
- amending pushed commits  
- using commit message to claim verified/production_ready  
- committing PROJECT_CONTROL gate flips without evidence + explicit control package intent  
- treating local merge as push authority
