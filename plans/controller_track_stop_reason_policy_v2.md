# Controller Track Stop Reason Classification Policy v2


_最后更新：2026-07-14_  
_配套：[controller_track_execution_queue_policy_v2.md](controller_track_execution_queue_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_daily_execution_schema_v2.md](controller_daily_execution_schema_v2.md)_


## 1. Purpose


Differentiate **why a track is not running** so Controller and humans do not confuse:


- human approval dependency  
- current task / successor exhaustion  
- low priority deferral  
- absence of safe autonomous work  
- intentional scheduler choice  


**Transparency goal：** every track stop has exactly **one primary** `stop_reason`.



---

# 2. Primary stop reasons（normative enum）


| Code | Meaning | Typical evidence |
|------|---------|------------------|
| **HUMAN_GATE_BLOCKED** *(2026-07-15 收窄，见 §2.1)* | Next *valuable* action requires **push** or a **truly irreversible** external action, **or** the mission scope/direction itself is unclear or conflicting | Push pending · destructive/irreversible action pending · scope ambiguity — **NOT** implementation, testing, dry-run, or CNINFO live (those use §2.1 execution status instead) |
| **HUMAN_DECISION_REQUIRED** *(preferred alias, 2026-07-15)* | 与 `HUMAN_GATE_BLOCKED` 同义，人类更易读的命名；新文档优先使用此名，旧文档/工具中的 `HUMAN_GATE_BLOCKED` 不需要批量重命名 | 同上 |
| **CURRENT_TASK_COMPLETED** | Current task done and **successor candidates exhausted** for this track | Memory shows package complete · generator finds no new autonomous gap for track |
| **LOW_PRIORITY_DEFERRED** | Safe autonomous tasks exist but lower mission value than other work | Autonomous Queue non-empty · not selected this iteration |
| **NO_SAFE_AUTONOMOUS_TASK** | No safe autonomous task remains **for this track** after candidate audit | Audit: autonomous considered=0 surviving filters |
| **RESOURCE_ALLOCATED_ELSEWHERE** | Task exists but scheduler prioritizes another track | Fairness / mission impact chose B while A still queued |
| **RUNNING** | Track currently has an active dispatched task | `active_task` set |
| **BUDGET_HOLD** | Track paused because daily iteration/runtime/commit budget hit | Budget counters exhausted mid-queue |


Optional secondary notes allowed; **primary** must be one enum above.



---

# 2.1 CNINFO / Live Execution Status（2026-07-15 · NEW · not a stop_reason）


**Scope-Driven Execution Amendment**（see [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)）：一旦 track/component scope 已授权，implementation / test / dry-run / **CNINFO live 执行** / validate / evidence / commit 都是自主执行范围。这些阶段**不使用** `HUMAN_GATE_BLOCKED`/`HUMAN_DECISION_REQUIRED`；改用以下执行状态词表描述 track 当前在做什么：


| Status | Meaning |
|--------|---------|
| `READY` | scope 已授权，任务已生成，尚未开始执行 |
| `RUNNING` | 正在执行（implementation / test / dry-run / CNINFO live 抓取 中的任一阶段） |
| `COMPLETED` | 本次任务的执行 + validate + evidence + commit 均完成 |
| `FAILED` | 技术故障（网络 / CNINFO 拒绝 / 解析失败等），非安全问题、非批准缺口 |
| `WAITING_RETRY` | `FAILED` 后按既有重试策略排队重试，未耗尽重试预算 |


**分类规则：**


1. CNINFO live 请求失败 → `FAILED`，**不是** `HUMAN_GATE_BLOCKED`。重试预算未耗尽 → `WAITING_RETRY`。
2. 重试预算耗尽且问题仍是技术性的 → 保持 `FAILED`，在报告中说明原因；**仅当**根因涉及安全问题或 scope 本身有歧义时才升级为 `HUMAN_DECISION_REQUIRED`。
3. 这套词表只描述"轨道在做什么"，不取代 §2 的 `stop_reason` 枚举——一个 track 可以同时有 `stop_reason=CURRENT_TASK_COMPLETED`（本任务链结束）和最后一次执行状态 `COMPLETED`。



---

# 3. Classification rules


### 3.1 HUMAN_GATE_BLOCKED / HUMAN_DECISION_REQUIRED


**2026-07-15 收窄：** 使用条件不再包括 live / snapshot execute / 常规 approval phrase——这些现在走 §2.1 execution status（`READY`/`RUNNING`/`FAILED`/...），因为一旦 scope 已授权，它们是自主执行，不是批准缺口。


Use when:


1. The next step for the track is **push**，**or** a **truly irreversible** external/production action，**or** the track's mission scope/direction is itself unclear or conflicting, **and**  
2. Autonomous Queue is empty **or** remaining autonomous items are memory-equivalent / low-value after audit.  


Examples（更新后，仅剩三类）：


- track 的下一步是把结果 push 到 remote（等待人类 push 决策）  
- track 需要执行事实上不可逆的动作（删除历史证据 / 无回滚生产 mutation）  
- track 的能力方向本身未被授权 / 与另一 track 冲突（scope 决策尚未做出）


**不再属于本类**（改用 §2.1）：C production snapshot execute · D S4 runner 实现 / live · B live retry —— 这些只要 scope（component/track 方向）已授权，就是 `RUNNING`/`READY`，不是 `HUMAN_GATE_BLOCKED`。


### 3.2 CURRENT_TASK_COMPLETED


Use when the just-finished task has no valuable successor **and** the track’s autonomous gap set is empty — distinct from “waiting forever for live.” Prefer this when the offline chain is honestly finished, not when live is the only remaining high-value step（that is `HUMAN_GATE_BLOCKED`）.


### 3.3 LOW_PRIORITY_DEFERRED


Safe Autonomous Queue items exist; Controller deferred them because other tracks’ work has higher mission impact / bottleneck reduction this iteration.


### 3.4 NO_SAFE_AUTONOMOUS_TASK


After full per-track candidate audit, zero autonomous candidates survive safety + memory filters. Approval Queue may still be non-empty.


### 3.5 RESOURCE_ALLOCATED_ELSEWHERE


Autonomous Queue non-empty and READY, but this iteration’s dispatch went to another track under resource allocation / fairness.



---

# 4. Global stop vs track stop（critical）


| Level | Allowed when |
|-------|--------------|
| **Track** `HUMAN_GATE_BLOCKED` | That track’s next valuable path needs human — **other tracks may continue** |
| **Global** `NO_VALUABLE_SAFE_TASK` | **All** tracks have no dispatchable autonomous READY work after full A/B/C/D audit |


### Hard rules


1. **Do NOT** interpret `HUMAN_GATE_BLOCKED` as global `NO_VALUABLE_SAFE_TASK`.  
2. **Do NOT** remove a track from planning because its live path is blocked.  
3. A blocked live task **must coexist** with autonomous offline tasks on the same track when generator can emit them.  
4. Global stop requires per-track reasons in the daily report（see schema）.  
5. If any track is `LOW_PRIORITY_DEFERRED` or `RESOURCE_ALLOCATED_ELSEWHERE` with non-empty queue → global stop is **invalid** until those queues are drained or reclassified.  



---

# 5. Mapping to candidate audit rejection reasons


| Audit rejection | Typical track stop_reason |
|-----------------|---------------------------|
| requires_approval | `HUMAN_GATE_BLOCKED`（if that was the next valuable path） |
| already_completed / duplicate | contribute to `CURRENT_TASK_COMPLETED` or `NO_SAFE_AUTONOMOUS_TASK` |
| low_mission_value | `LOW_PRIORITY_DEFERRED` if still queued; else drop |
| unsafe | never enqueue · may yield `NO_SAFE_AUTONOMOUS_TASK` |



---

# 6. Reporting（required）


Daily report **must** include Track Queue Status with `stop_reason` per track, plus rollups:


```text
Human blocked:     # tracks with HUMAN_GATE_BLOCKED
Priority deferred: # LOW_PRIORITY_DEFERRED
No safe task:      # NO_SAFE_AUTONOMOUS_TASK
Resource elsewhere:# RESOURCE_ALLOCATED_ELSEWHERE
Next recommended action:
```



---

# 7. Anti-patterns


Forbidden:


- labeling D `NO_SAFE_AUTONOMOUS_TASK` when only S5 live remains and offline chain is done → use `HUMAN_GATE_BLOCKED`（仅当 scope 本身未授权时才适用；若 scope 已授权，直接执行 live，用 §2.1 `READY`/`RUNNING`）  
- stopping the whole day because one track is `HUMAN_GATE_BLOCKED` while others have Autonomous Queues  
- omitting `stop_reason` on idle tracks  
- inventing a sixth primary reason without policy update  
- **2026-07-15 新增反模式：** 把 CNINFO live / implementation / test 标记为 `HUMAN_GATE_BLOCKED` 当 scope 已经授权——这是过度限制，违反 Scope-Driven Execution Amendment（见 [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)）  
- **2026-07-15 新增反模式：** 为已授权 scope 内的每个执行阶段（实现/测试/live）重新要求逐字批准短语——短语只在**首次**授权 scope 时需要一次
