# Controller Human Interrupt Policy v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md)_


## 1. Purpose


定义 Daily Autonomous Loop v2 **何时必须停止并请求 human**，以及 **何时不得打断**。


目标：


- 减少对例行工作的打扰  
- 保留高风险决策的人控  
- 与 push / autonomy / orchestration v1 一致  



---

# 2. Principle


Human interrupt = **决策边界**，不是进度汇报。


Routine progress → continue  
Irreversible / ambiguous / publication / approval-gated → stop



---

# 3. Required interrupts (MUST stop)


Controller **must** stop and ask human before continuing when any applies:


## 3.1 Publication / remote


- push to `origin`  
- force-push  
- rewrite shared remote history  
- accept/reject remote-divergence recovery strategy beyond already-approved Option C unique-path recovery  


## 3.2 Approvals


- new CNINFO live / resume-live / retry-live without spent scoped approval  
- component approval (e.g. D `shareholder_change` while `READY_FOR_APPROVAL`)  
- flipping `approved_for_snapshot_rebuild` from false → true  
- any gate promotion to verified / production_ready / testing_stable_sample  


## 3.3 Conflicts / ownership


- merge conflicts on shared docs or runners  
- ambiguous track ownership of dirty paths  
- cross-track protected-root collision  
- worktree claims it owns a path already owned by another running track  


## 3.4 Destructive / production mutation


- deleting historical evidence or closed roots  
- mutating production harvest/snapshot roots outside explicit approved scope  
- `status` CSV production apply without approval flag **and** without recorded human intent for that apply  
- destructive git (`reset --hard`, clean -fdx on protected trees, etc.)  


## 3.5 Policy / architecture


- changing controller policies / interrupt rules / commit autonomy allow-lists  
- expanding Daily Loop scope beyond approved tracks  
- schema-breaking platform/storage decisions  



---

# 4. Do NOT interrupt (MUST continue when otherwise safe)


Controller **must not** stop solely for:


- normal documentation updates (status/map/readme/plans wording aligned to git truth)  
- validation evidence packaging under `outputs/validation/`  
- isolated offline tests / dry-runs with CNINFO=0  
- bounded explicit-path local commits allowed by commit autonomy v2  
- worktree offline packaging with no live  
- regenerating ledgers / summaries that do not change gates  
- marking a track HOLD when PROJECT_CONTROL already says HOLD  
- daily report generation  


If these items fail technically, record PARTIAL/FAILED in the daily report — that is **not** automatically a human interrupt unless §3 also triggers.



---

# 5. Interrupt packet format


When stopping, emit:


```markdown
## Human Interrupt Required

Track: <A|B|C|D|CROSS|REPO>
Reason class: <push|approval|conflict|destructive|policy>
Exact decision needed:
Suggested exact phrase (if approval):
Evidence pointers:
Blocked actions until resolved:
Safe autonomous work that will continue on other tracks:
```


Do not ask vague “should I continue?”.



---

# 6. Exact-phrase examples (non-exhaustive)


| Situation | Example phrase |
|-----------|----------------|
| Push main | `I approve push main to origin.` |
| D component | `I approve D-class shareholder_change as the next Era D component.` |
| C snapshot rebuild | `I approve C-class snapshot rebuild for <exact universe>.` |
| Live scope | `I approve <track> <exact live scope id> live.` |


Phrases authorize **only** the named scope. They do not authorize push unless push is named.



---

# 7. Multi-track behavior during interrupt


If track D is WAITING_APPROVAL:


- A/B/C may continue if READY and isolated  
- Daily report must list D under Human attention  
- Controller must not invent a substitute D action to “keep busy”



---

# 8. Escalation severity


| Severity | Examples | Behavior |
|----------|----------|----------|
| S1 Info | HOLD unchanged | no interrupt · report only |
| S2 Approval | component / live / push | interrupt · other tracks may continue |
| S3 Safety | conflict / destructive / red-line | interrupt · pause related tracks · continue unrelated if safe |
| S4 Stop-all | policy corruption / unknown ownership of main WT | interrupt · halt Daily Loop |



---

# 9. Relationship to v1


Extends:


- `controller_autonomy_policy_v1.md` Level 0 stops  
- `controller_autonomous_operation_policy_v1.md` human decision boundaries  
- `controller_push_policy_v1.md` push separation  


v2 clarifies **Daily Loop non-interrupt list** so documentation/evidence/test/commit noise does not page humans.



---

# 10. Anti-patterns


Forbidden:


- interrupting every commit for “confirmation”  
- bundling push approval into commit approval  
- treating `READY_FOR_APPROVAL` as approved  
- continuing live after interrupt reason was only push  
- silencing S3 conflicts to keep the loop green
