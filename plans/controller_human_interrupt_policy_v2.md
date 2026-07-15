# Controller Human Interrupt Policy v2


_最后更新：2026-07-14_  
_配套：[controller_daily_autonomous_loop_v2.md](controller_daily_autonomous_loop_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md)_


## 1. Purpose


定义 Daily Autonomous Loop v2 **何时必须停止并请求 human**，以及 **何时不得打断**。


目标：


- 减少对例行工作的打扰  
- 保留高风险决策的人控  
- 与 push / autonomy / orchestration v1 一致  
- 与 [mission objective v2](controller_mission_objective_v2.md) 审批哲学一致：**approval 是同步点，不是全局停机**  



---

# 2. Principle


Human interrupt = **决策边界**，不是进度汇报。


Routine progress → continue  
Irreversible / ambiguous / publication / newly actionable approval → stop  


From [mission objective v2](controller_mission_objective_v2.md):


- Approval is a **synchronization point**, not a global workflow stop.  
- A blocked track must not idle the whole system.  
- Do not re-interrupt for **known** HOLD / WAITING_APPROVAL already on the approval queue.  
- Interrupt for approval when it unlocks meaningful next execution, safety requires it, or **no autonomous progress remains**.



---

# 3. Required interrupts (MUST stop)


Controller **must** stop and ask human before continuing when any applies:


## 3.1 Publication / remote


- push to `origin`  
- force-push  
- rewrite shared remote history  
- accept/reject remote-divergence recovery strategy beyond already-approved Option C unique-path recovery  


## 3.2 Approvals

**修订（2026-07-15 · Scope-Driven Execution Amendment，见 §12）：** 本节原列出的 CNINFO live / component 批准 / snapshot rebuild 批准 / gate 促升 四类，**不再**属于 §3 必须停机清单。一旦人类已经**授权某轨/某能力方向**（scope 决策），实现 → 测试 → dry-run → CNINFO live → 验证 → evidence → commit 属于该 scope 内的正常工程执行，见 §12。

本节此后只保留两类硬性批准边界：

- **scope 本身不明确或存在冲突**（例如：两个 track 声称同一能力方向、mission 目标本身有歧义）— 这不是"批准某个动作"，是"批准要做什么"，仍须人类决定。
- **verified / production_ready / testing_stable_sample 等 gate 促升声明** — 这类声明会被下游当作"已验证的事实"引用，一旦错误升级难以撤销其影响（其他轨可能已经基于错误声明做出决策），因此保留为人控（见 §3.4 的"事实上不可逆"标准，而不是因为它是 CNINFO/live 动作本身）。


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
- **known HOLD** already recorded  
- **known WAITING_APPROVAL** already on the approval queue（do not re-page）  
- existing blockers already listed in PROJECT_CONTROL / prior daily report  
- continuing independent tracks while another track waits approval  
- **implementing source code within an already-authorized track/component scope**（2026-07-15 amendment）  
- **running unit / integration tests, regression tests**  
- **CNINFO live collection / crawling / document download / dataset refresh within authorized scope**（2026-07-15 amendment — see §12; this was previously listed under §3.2 and is now explicitly non-interrupting）  
- **local commits of the resulting implementation, tests, or collected evidence**（subject to commit autonomy v2, still never push）


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


**2026-07-15 修订：** 以下表格中的 "D component" / "C snapshot rebuild" / "Live scope" 三行**不再是执行门**——一旦track/component的scope已被授权（例如已有一次"我批准 D-class shareholder_change 作为下一个 Era D component"），implementation → test → dry-run → **CNINFO live** → validate → evidence → commit 都属于该 scope 内的自主执行，不需要为每个阶段重新逐字匹配批准短语（见 §12）。这三行保留在表中仅作为**scope 授权**记录格式的参考，不再是"live 需要逐字短语才能跑"的意思。

`Push main` 是本表**唯一**仍然是硬性执行门的行。

| Situation | Example phrase | 性质 |
|-----------|----------------|------|
| Push main | `I approve push main to origin.` | **执行门（硬性）** |
| Destructive / irreversible external action | `I approve <exact destructive action> on <exact target>.` | **执行门（硬性）** |
| D component scope | `I approve D-class shareholder_change as the next Era D component.` | Scope 授权记录（非逐次执行门） |
| C snapshot rebuild scope | `I approve C-class snapshot rebuild for <exact universe>.` | Scope 授权记录（非逐次执行门） |
| Live/track scope | `I approve <track> <exact scope id>.` | Scope 授权记录（非逐次执行门） |


Push / destructive 短语仍然**只授权其命名的范围**，不因为命名了 scope 就自动授权 push。Scope 授权短语一旦给出，覆盖该 scope 下 §12 定义的全部工程生命周期（不需要为 live/commit 再单独批准）。



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



---


# 11. Relationship to Mission Execution Engine v3 Approval Information Layer


[controller_mission_execution_engine_v3.md §10.1](controller_mission_execution_engine_v3.md)（**2026-07-15 更名：Approval Guidance Layer → Approval Information Layer**）定义了一个纯呈现层：告知人类当前 mission scope、pending push、destructive action 警示。它不再围绕 `HUMAN_GATE_BLOCKED` 的 exact-phrase 判定组织（该 stop_reason 已收窄，见 §12），而是围绕 §12 定义的两类硬性执行门（push / 不可逆外部动作）组织提示。


**本文件 §6 中 push / destructive 两行的 exact-phrase 判定规则不受影响、不被该层修改或放宽。** 对于已收窄出 §3.2 之外的 scope 授权类短语，该层记录 scope 历史供人类查阅，但**不**据此生成任何"仍在等待批准"的提示——scope 一旦授权，下游执行是自主的。



---


# 12. Scope-Driven Execution Amendment（2026-07-15 · Major）


## 12.1 变更性质


这是对本政策的**架构性修订**，不是新增политика层。人类明确要求：approval-driven execution（每个动作都要批准）→ scope-driven execution（一次授权方向，agent 自主完成全生命周期）。见 `controller_mission_execution_engine_v3.md §10` 同步修订。


## 12.2 新的角色划分


| 角色 | 职责 |
|------|------|
| Human | project owner / scope setter / final push authority |
| Agent | engineering team：implementation / test / dry-run / **CNINFO live 执行** / validation / evidence / local commit |


## 12.3 硬性执行门（仅两类，取代原 §3.2 四类）


1. **Push to remote**（push / force-push / remote branch modification）— 不变，仍是 §3.1 的硬性门。
2. **事实上不可逆的外部动作** — 例如：删除历史证据 / destructive migration / 无回滚路径的生产 mutation / 变更外部系统且不可撤销。这类动作**不因为"是 CNINFO 相关"而被门控**，而是因为其后果不可逆。


## 12.4 一旦 scope 被授权，以下全部自主执行，不逐项批准


实现（implementation）· 单元/集成测试 · dry-run · **CNINFO live 抓取 / 下载 / API-browser collection** · validation · evidence 生成 · local commit · 继续下一个有价值任务。


## 12.5 CNINFO live 执行的状态词表（取代 `HUMAN_GATE_BLOCKED` 用于此场景）


CNINFO/live 执行不再分类为 `HUMAN_GATE_BLOCKED`。改用（定义见 [track stop reason v2 §2.1](controller_track_stop_reason_policy_v2.md)）：


```text
READY | RUNNING | COMPLETED | FAILED | WAITING_RETRY
```


只有以下情况才停机请求人类：技术故障（`FAILED` 且重试耗尽）· 安全问题 · scope 本身不明确 · 需要 push。


## 12.6 不受本修订影响（仍然人控）


- push / force-push / remote history rewrite（§3.1）
- 事实不可逆的外部/生产动作（§3.4，收窄后的判定标准见 §12.3.2）
- scope 本身模糊或冲突时的**首次**方向决策（人类仍需说"做 X"，但一旦说了，如何做由 agent 决定）
- verified / production_ready / testing_stable_sample 等下游会被当作既定事实引用的 gate 促升声明


## 12.7 历史记录（不删除，仅标注失效）


§3.2 原四类（CNINFO live 批准 / component 批准 / snapshot rebuild 批准 / gate 促升）中，**前三类**自 2026-07-15 起不再是执行门（改为 §12.4 自主执行范围内），仅**第四类（gate 促升）**保留人控，理由见 §12.6 最后一条。§6 表格中对应三行改为"scope 授权记录"而非"逐次执行门"（已在 §6 标注）。
