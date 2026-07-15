# Controller Mission Execution Engine v3


_最后更新：2026-07-15_
_状态：Architecture design only · 未启用 · 不含代码实现 · 不含 live/CNINFO/push 授权变更_
_性质：整合层（integration layer）— 不重写 · 不复制 v2 各政策内部规则，只重新组织它们如何协同工作_


---


# 0. Purpose and Non-duplication Statement


本文件是 **Mission Execution Engine v3**：把已经验证的 Controller v2 十八份政策（Daily Autonomous Loop v2 · Mission Objective v2 · Progress Tracking v2 · Human Interrupt v2 · Commit Autonomy v2 · Execution Cycle v2 · Task Priority v2 · Task Generator v2 · Task Continuation v2 · Capability Gap Analysis v2 · Task Memory v2 · Resource Allocation v2 · Stuck Detection v2 · Milestone Management v2 · Mission Replanning Loop v2 · Track Execution Queue v2 · Track Stop Reason v2 · Daily Execution Schema v2）**组装成一个连贯的引擎**：


```text
Mission → Capability Gap → Tasks → Execution → Measurement → Replanning
```


**本文件不做的事：**


- 不重写任何 v2 政策内部规则（优先级公式、安全过滤、审批分类等仍以各自文件为权威）。
- 不新增第二套队列文档（`controller_track_execution_queue_policy_v2.md` 仍是队列权威）。
- 不引入代码、runner、live 执行、CNINFO 调用、push 授权变更。
- 不降低任何现有红线。

**本文件新增的东西（v3 的真实增量）仅限于：**

1. 一个统一的 **Track Capability State** 数据对象（§2.2），把目前分散在 progress tracking / capability gap analysis / execution queue / stop reason 四份文件里的字段合并成 controller 每次 replan 都读写的**单一对象**。
2. 一个持久化的 **Dynamic Track Queue v3** 字段扩展（§4），把目前只在 candidate audit 里"临时出现一次"的 candidate / rejected 列表变成**队列对象的常驻字段**。
3. 一个新的分类词表 **Capability Gain Check**（§6）：`CAPABILITY_ADVANCED / CAPABILITY_MAINTAINED / NO_CAPABILITY_CHANGE`，并给出它与既有 `gap_closed/gap_partial/gap_unchanged/failed`（task continuation v2 §3）的精确映射，供 anti-stagnation 使用。
4. 一份 **Historical velocity** 记忆字段（§8），供 progress tracking v2 §5 的 effort 估计和 resource allocation v2 的 staleness 判断使用。
5. 一个 **Mission Execution Loop** 主循环伪代码（§7 / §11），把 Daily Loop v2 §11、Execution Cycle v2 §2、Mission Replanning Loop v2 §2 这三层循环合并成一个带 Capability Gain Check 的单一循环视图（供理解全局，不替代任一份的权威细则）。
6. 对"queue empty → stop"这一失效心智模型的**正式废止声明**（§3），并给出它与既有 stop-reason 体系的精确对齐（现有政策其实已经不允许这个失效模式——v3 把它写成显式架构原则，避免未来实现者退回旧模型）。
7. 一个 **Mission Completion Model**（§16）：正式定义"Controller 如何知道自己正在接近/到达全市场使命目标"，以能力维度而非 commit/file/task/agent 计数衡量，并给出 denominator 未冻定时必须报告 `UNKNOWN` 的硬规则。
8. 一个 **Approval Information Layer**（§10.1，2026-07-15 由 Approval Guidance Layer 更名/改造）：常驻展示 scope 状态 / exec_status / pending push / destructive-action 警示的纯呈现层——**不再**以 exact-phrase 匹配作为执行门（那已收窄到仅 push 与不可逆动作两类，见 [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)）。
9. 一套 **Scope-Driven Execution 模型**（§10，2026-07-15 NEW）：human 授权方向（scope）一次，implementation → test → dry-run → CNINFO live → validate → evidence → commit 全部自主执行，不逐阶段批准。

其余所有行为规则（安全过滤、审批分类、commit 权限、优先级排序、fairness、stuck 阈值……）**继续以对应 v2 文件为唯一权威**，本文件只引用。


---


# 1. Core Principle


```text
旧模型（禁止）：

Mission
  ↓
Generate candidates
  ↓
Create queue
  ↓
Agents execute
  ↓
Queue drained
  ↓
STOP


v3 模型（强制）：

Mission
  ↓
Capability Gap（per track，§2）
  ↓
Tasks（generated from fresh gaps，§3–§5）
  ↓
Execution（track agent，§7）
  ↓
Measurement（Capability Gain Check，§6）
  ↓
Replanning（recalculate gaps → refill queue → continue，§3/§7）
  ↑___________________________________________________|
```


**Queue empty 不是停机条件。** 这一点 mission replanning loop v2 §5 和 execution cycle v2 §4 早已规定（"Do NOT stop because generated task list finished"）。v3 把它提升为**架构第一原则**：Controller 管理的对象永远是 A/B/C/D 四个 **capability ownership domain**，队列只是它们在某一时刻的执行缓冲区，不是 mission 本身。


**A/B/C/D 不是任务容器，是能力所有权域：**

| Track | 能力域（mission objective v2 §3） |
|-------|-----------------------------------|
| A | company information capability（全市场公司信息能力） |
| B | disclosure / event capability（全市场披露与事件能力） |
| C | evidence and quality capability（全市场证据与质量能力） |
| D | shareholder / capital capability（全市场股东与资本结构能力） |


---


# 2. Mission State Layer


## 2.1 Global Mission State


```yaml
GlobalMissionState:
  mission: "Full-market A/B/C/D capability achievement"    # mission objective v2 §2
  overall_completion_pct: <pct|unknown>                     # progress tracking v2 §2.2
  completed_capability_units: <int|list>
  remaining_capability_units: <int|unknown>
  estimated_remaining_effort: <value|unknown>                # progress tracking v2 §5 + §8 historical velocity
  active_milestones: [...]                                   # milestone management v2 §2
  mission_not_complete: true|false                           # loop guard, §7
```


权威：[controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_milestone_management_v2.md](controller_milestone_management_v2.md)。v3 不改变这些字段的计算规则，只把它们放进一个顶层对象。


## 2.2 Track Capability State（v3 新增的统一对象）


这是 v3 唯一要求 Controller 在**每次 replan**时维护的核心数据结构，逐轨（A/B/C/D）各一份：


```yaml
TrackCapabilityState:
  track: A | B | C | D
  capability_domain: "<mission objective v2 §3 一句话目标>"
  current_capability:                       # progress tracking v2 §3 逐轨 metrics
    metrics: { ... }
    evidence_basis: [...]
  completed_capability_units: <int|list>    # progress tracking v2 §2.1
  remaining_gaps:                           # capability gap analysis v2 §2 输出（一条或多条）
    - gap_id:
      gap_statement:
      root_cause:
      impact_on_mission:
      next_tasks:
      blocked_by: approval | live | none
      evidence_paths: []
  current_bottleneck:                       # progress tracking v2 §4
    reason:
    recommended_next_focus:
  available_autonomous_actions: []          # = Autonomous Queue heads（track execution queue v2 §2）
  human_blocked_actions: []                 # = Approval Queue（task generator v2 §3.1）
  stop_reason: <track stop-reason enum>      # track stop reason v2 §2
  last_capability_gain: CAPABILITY_ADVANCED | CAPABILITY_MAINTAINED | NO_CAPABILITY_CHANGE | unknown   # §6，NEW
  historical_velocity: <units/period | unknown>   # §8，NEW
  state_refresh_timestamp: "<ISO>"           # mission replanning loop v2 §2.1
```


字段来源对照（说明这是整合，不是新造规则）：

| `TrackCapabilityState` 字段 | 计算权威（不变） |
|------------------------------|-------------------|
| `current_capability` / `completed_capability_units` | progress tracking v2 §2–§3 |
| `remaining_gaps` | capability gap analysis v2 §2 |
| `current_bottleneck` | progress tracking v2 §4 |
| `available_autonomous_actions` | track execution queue v2 §2（Autonomous Queue） |
| `human_blocked_actions` | task generator v2 §3.1（Approval Queue） |
| `stop_reason` | track stop reason v2 §2 |
| `last_capability_gain` / `historical_velocity` | 本文件 §6 / §8（新增字段，附加式，不冲突现有字段） |


Controller 必须能在任意时刻回答：**"track T 距全市场能力还差什么、被什么卡住、下一步是什么"**——这正是 `TrackCapabilityState` 存在的理由，也是用户在任务描述中提出的"A/B/C/D are not just task containers"的落地形式。


---


# 3. Capability Gap Driven Planning


## 3.1 废止声明


> **"Queue empty → stop" 在 v3 架构下是无效停机原因，永远不得作为 global 或 track 级唯一停机依据单独出现。**


替代流程（已由 mission replanning loop v2 §2 + execution cycle v2 §3.1 + task generator v2 §2/§7 分别定义，v3 只是把它们串成一条显式链）：


```text
Queue empty (for track T)
    ↓
Refresh T.TrackCapabilityState                     (§2.2 / mission replanning v2 §2.1)
    ↓
Recalculate T.remaining_gaps                        (capability gap analysis v2)
    ↓
Generate successor candidates from fresh gaps       (task generator v2 §2/§7)
    ↓
Score candidates                                    (§5 mission priority system)
    ↓
Refill T.TrackQueueState（§4）
    ↓
Continue execution — or, only if refill yields nothing safe for T:
    set T.stop_reason (§3.2)
```


## 3.2 何时才允许停机（track 级 vs global 级，精确对齐既有枚举）


用户需求中列出的五个"only stop when"条件里，前三个（`HUMAN_GATE_BLOCKED` / `NO_SAFE_AUTONOMOUS_TASK` / `LOW_PRIORITY_DEFERRED`）在既有政策中是 **track 级**枚举（[track stop reason v2 §2](controller_track_stop_reason_policy_v2.md)），后两个（safety violation / budget exhausted）是 **global 级**枚举（[execution cycle v2 §4](controller_execution_cycle_policy_v2.md) 的 `SAFETY_VIOLATION` / `BUDGET_REACHED`）。v3 把两层显式区分，避免"某一轨 HUMAN_GATE_BLOCKED"被误读成"全局停机"（这正是 track stop reason v2 §4 已经写明的硬规则，v3 重申并结构化）：


| 层级 | 允许的停机值 | 触发条件 |
|------|--------------|----------|
| **Track T** | `HUMAN_GATE_BLOCKED`（2026-07-15 收窄，见 §10/§12） | T 的下一步是 push、事实不可逆动作、或 scope 本身未授权，且 Autonomous Queue 为空或只剩低价值残留（**不再**包括已授权 scope 内的 implementation/test/dry-run/CNINFO live——那些用 `exec_status`，见 track stop reason v2 §2.1） |
| **Track T** | `NO_SAFE_AUTONOMOUS_TASK` | 完整 candidate audit 后 T 没有任何安全自主候选存活 |
| **Track T** | `LOW_PRIORITY_DEFERRED` | T 有安全候选，但本轮被更高价值的其他轨道抢占资源 |
| **Track T** | `RESOURCE_ALLOCATED_ELSEWHERE` / `CURRENT_TASK_COMPLETED` / `RUNNING` / `BUDGET_HOLD` | 见 track stop reason v2 §2（未在用户列表中显式点名，但仍是有效枚举，不得省略） |
| **Global** | `NO_VALUABLE_SAFE_TASK`（别名 `NO_SAFE_READY`） | **且仅当** A/B/C/D **全部**处于上表任一非可继续状态（即全部 track 完成 candidate audit 且无一存在可派发的 autonomous READY 项） |
| **Global** | `SAFETY_VIOLATION` | 红线 / 所属权 / 证据诚信被破坏 |
| **Global** | `BUDGET_REACHED` | `max_iterations` / `max_runtime` 耗尽（commit 预算耗尽只停止 commit，不停止推理/重算） |
| **Global** | `HUMAN_INTERRUPT` | S3/S4 级别打断（human interrupt v2 §8） |


**硬规则（继承 mission replanning loop v2 §5 + track stop reason v2 §4，v3 不放宽）：**

1. 单一 track 的 `HUMAN_GATE_BLOCKED` **绝不**等于 global `NO_VALUABLE_SAFE_TASK`。
2. Global 停机前必须完成 **四轨候选审计**（mission replanning loop v2 §2.2 candidate audit）。
3. 只要任意一轨仍是 `LOW_PRIORITY_DEFERRED` 或 `RESOURCE_ALLOCATED_ELSEWHERE` 且队列非空 → global 停机无效。


---


# 4. Dynamic Track Queue v3


## 4.1 字段合并


用户要求每轨维护：`Current task` · `Ready successors` · `Candidate successors` · `Rejected tasks` · `Reason rejected`。


既有 [track execution queue v2 §7](controller_track_execution_queue_policy_v2.md) 已定义 `active_task` / `queued_tasks` / `stop_reason` / `approval_queued`；[mission replanning loop v2 §2.2](controller_mission_replanning_loop_v2.md) 的 candidate audit 已经**临时计算** considered/rejected 列表，但只在停机报告里出现一次，不是队列对象的常驻字段。v3 的唯一增量：把 candidate audit 的输出**固化**为队列对象的两个新字段，供下一轮 replan 直接复用（避免每轮重新计算全部历史拒绝原因）。


```yaml
TrackQueueStateV3:
  track: A | B | C | D
  current_task: <task_id | none>              # = active_task（术语沿用 v2，不改字段名以保持兼容）
  ready_successors: [<task_id>, ...]           # = queued_tasks（术语沿用 v2）
  candidate_successors: [<task_id>, ...]       # NEW：generator v2 产出但尚未通过安全/优先级筛选晋级的候选
  rejected_tasks:                              # NEW：持久化的拒绝记录（此前只在 candidate audit 里出现一次）
    - task_id:
      reason_rejected: requires_approval | unsafe | duplicate | already_completed | low_mission_value | other
      rejected_at: "<ISO>"
  approval_queue: [<task_id or gate id>, ...]   # 沿用 v2 approval_queued
  stop_reason: <track stop-reason enum>          # 沿用 v2
```


向后兼容：`current_task` / `ready_successors` / `approval_queue` / `stop_reason` 是既有字段的**同义重述**（未改名底层实现时可直接沿用 `active_task` / `queued_tasks` / `approval_queued`）；仅 `candidate_successors` 与 `rejected_tasks` 是新增可选字段，旧 Controller 忽略它们不影响既有行为（对齐 [daily execution schema v2 §7](controller_daily_execution_schema_v2.md) 的 additive-field 原则）。


## 4.2 Refill 流程（after every completed task，权威不变，仅重申）


```text
execute (track agent)
    ↓
validate (evidence reviewer when required)
    ↓
collect evidence
    ↓
capability gain check（§6，NEW）
    ↓
update memory（task memory v2 + §8 historical velocity）
    ↓
update TrackCapabilityState（§2.2）
    ↓
generate successor tasks（task generator v2 + task continuation v2）
    ↓
re-score TrackQueueStateV3（task priority v2 + resource allocation v2 + §5）
    ↓
move survivors → candidate_successors → ready_successors
move non-survivors → rejected_tasks（with reason_rejected）
    ↓
A/B/C/D continue independently（no forced equal drain — resource allocation v2 §3 fairness applies）
```


---


# 5. Mission Priority System


用户要求的排序因子（capability gain / bottleneck reduction / dependency unlocking / track staleness / effort）与既有两份政策的因子**基本一致**，v3 做的是**统一措辞并锁定顺序**，避免 task priority v2 §5（mission impact / blocked dependencies / estimated effort / safety level）和 resource allocation v2 §2（mission impact / bottleneck reduction / track staleness / queue availability）两套因子表未来出现顺序冲突：


| 顺位 | v3 统一命名 | 对应既有因子 | 权威 |
|------|-------------|--------------|------|
| 1 | Mission capability gain | mission impact | task priority v2 §5 · resource allocation v2 §2 |
| 2 | Bottleneck reduction | bottleneck reduction | resource allocation v2 §2 |
| 3 | Dependency unlocking | blocked dependencies | task priority v2 §5 |
| 4 | Track staleness | track staleness（+ staleness penalty/boost） | resource allocation v2 §3 |
| 5 | Effort | estimated effort（**仅作 tie-break**，永不作主排序） | task priority v2 §5 |


**安全过滤永远先于此排序**（unsafe / approval-missing 任务永不入选，无论分数多高——task priority v2 §1 已定，v3 不改变）。


**明确禁止（继承 task priority v2 §5 + §10，直接照抄不弱化）：**

- easiest task first（用 effort 作主排序）
- most visible task first
- equal task distribution（round-robin A→B→C→D，不管收益）
- endless documentation tasks（P4/P5 controller maintenance 在任何 P1–P3 track 候选存在时都不得入选——task priority v2 §2/§3）


---


# 6. Capability Gain Validation


## 6.1 Capability Gain Check（NEW 词表）


每个完成的任务，除了既有 [task continuation v2 §3](controller_task_continuation_policy_v2.md) 的 `gap_closed / gap_partial / gap_unchanged / failed` 判定外，v3 额外要求派生出一个供 anti-stagnation（§9）使用的三值结果：


```yaml
CapabilityGainCheck:
  task_id:
  track:
  continuation_outcome: gap_closed | gap_partial | gap_unchanged | failed   # task continuation v2 §3（不变）
  capability_gain: CAPABILITY_ADVANCED | CAPABILITY_MAINTAINED | NO_CAPABILITY_CHANGE   # 派生（v3 新增）
  evidence_delta: "<具体哪个 metric / gap 发生了什么变化，或 none>"
  commit_created: true|false
```


## 6.2 派生映射（唯一新增判定规则）


| `continuation_outcome`（task continuation v2） | 附加条件 | `capability_gain`（v3） |
|---|---|---|
| `gap_closed` | — | `CAPABILITY_ADVANCED` |
| `gap_partial` | 目标 gap 的 metric_observed 有实际数值移动（覆盖率/完整度上升） | `CAPABILITY_ADVANCED` |
| `gap_partial` | 只有证据/QA 质量提升，核心覆盖 metric 未变 | `CAPABILITY_MAINTAINED` |
| `gap_unchanged` | — | `NO_CAPABILITY_CHANGE` |
| `failed` | — | `NO_CAPABILITY_CHANGE`（且失败原因单独记入 task memory v2 §2 Failed 类，不与 gain 分类混淆） |


## 6.3 与 anti-stagnation 的接口（§9 的输入）


```text
IF commit_created == true AND capability_gain == NO_CAPABILITY_CHANGE
   for the same track, ≥2 次连续（stuck detection v2 §5 默认阈值）:
     → 判定为 stuck detection v2 §2 信号 1（"repeated cycles produce no capability progress"）
     → 该 track 后续候选 priority 降级（task priority v2 §3 ranking procedure 重新评估）
     → 触发 task generator v2 §2 第 4 条（stuck detection 请求 alternative autonomous actions）
```


这正是用户描述的"commit++ docs++ capability unchanged"坏循环检测——v3 没有发明新的检测机制，只是把 Capability Gain Check 接到已有的 stuck detection v2 输入端，让"capability 未变"有一个显式、可编程判定的信号源（此前 stuck detection v2 §2 信号 1 是定性描述，没有绑定具体的逐任务判定产物）。


---


# 7. Continuous Replanning Loop / Mission Execution Loop


v3 不新造循环机制——[daily autonomous loop v2 §11](controller_daily_autonomous_loop_v2.md)、[execution cycle v2 §2](controller_execution_cycle_policy_v2.md)、[mission replanning loop v2 §2](controller_mission_replanning_loop_v2.md) 三者已经是同一个多轮循环的三个视图（scheduler 视图 / 迭代 & 预算视图 / 重规划视图）。v3 提供的是把三者叠加、并嵌入 Track Capability State + Capability Gain Check 之后的**单一阅读视图**，供架构理解使用；**逐条实现细则仍以三份原文件为权威**。


```text
MISSION_EXECUTION_LOOP:
  budget = load_daily_budget()                          # execution cycle v2 §6
  mission = read_global_mission_state()                 # §2.1
  for T in [A,B,C,D]:
    T.capability_state = refresh_track_capability_state(T)   # §2.2

  while mission_not_complete:
    if budget_exhausted(budget):     stop = BUDGET_REACHED；break
    if safety_violation_detected():  stop = SAFETY_VIOLATION；break

    state_refresh()                                      # mission replanning v2 §2.1（mandatory，每轮）
    for T in [A,B,C,D]:
      T.capability_state = refresh_track_capability_state(T)     # §2.2
      T.queue = refresh_dynamic_queue(T)                          # §3/§4：recalc gaps → generate → filter → score → refill

    ready = collect_ready_across_tracks(A,B,C,D)          # task priority v2 + resource allocation v2 + §5 顺序

    if ready is empty:
      audit = candidate_audit_all_tracks(A,B,C,D)          # mission replanning v2 §2.2
      if audit.every_track_non_continuable:                # §3.2 表：全部 track 均为 HUMAN_GATE_BLOCKED/NO_SAFE_AUTONOMOUS_TASK/…
        stop = NO_VALUABLE_SAFE_TASK；break
      # 否则：至少一轨仍有价值 → 不停机，继续下一轮 refill

    target = select_highest_value_safe_target(ready)       # §5
    if not preflight_worktree_ok(target.track):
      target.track.status = BLOCKED；continue
    if not target.track.scope_authorized:                  # 2026-07-15 NEW，见 §10 Scope-Driven Execution
      target.track.status = HUMAN_DECISION_REQUIRED；continue   # 仅"方向未授权"才停，不是"这一步需要批准"

    target.track.exec_status = RUNNING                      # §10.2 execution status，取代逐阶段 HUMAN_GATE_BLOCKED
    R = dispatch_agent(required_track_agent(target.track), target)   # daily loop v2 §6.0 routing，不变
                                                              # dispatch 内部覆盖 implement → test → dry-run → CNINFO live（如任务需要）
    evidence = validate(R)                                  # evidence reviewer when required
    if R.technical_failure:
      target.track.exec_status = FAILED if retry_budget_exhausted(target) else WAITING_RETRY
    else:
      target.track.exec_status = COMPLETED
    gain = capability_gain_check(target, evidence)           # §6，NEW
    if R.commit_eligible and commit_budget_remaining(budget):
      explicit_path_commit_batched(R)                        # commit autonomy v2
    write_task_memory(R, gain)                                # §8
    update_track_capability_state(target.track, R, gain)      # §2.2
    successors = generate_successors(target.track, gain)       # task continuation v2 + task generator v2
    refill_track_queue(target.track, successors)                # §4.2
    if gain.capability_gain == NO_CAPABILITY_CHANGE:
      check_stuck_and_deprioritize(target.track)                # §6.3 → stuck detection v2
    # loop → mandatory replan（不得盲目执行剩余生成批次）

  write_mission_execution_report(...)                        # §11 reporting model
  NEVER push
LOOP_END
```


**安全打断始终覆盖此循环**（human interrupt v2 §3 S3/S4 立即 break；S2 仅打断相关 track，其余轨继续——human interrupt v2 §7/§8，不变）。


---


# 8. Execution Memory Upgrade


既有 [task memory policy v2 §2](controller_task_memory_policy_v2.md) 已定义 Completed / Failed / Deferred / Human rejected / Known blockers 五类记忆。v3 的唯一新增字段：


```yaml
TrackHistoricalVelocity:            # NEW，附加到 task memory v2 的记忆产物之上
  track: A|B|C|D
  period: "<daily loop 运行日期范围>"
  completed_capability_units_in_period: <int>
  capability_gain_breakdown:          # §6 分类计数
    advanced: <int>
    maintained: <int>
    no_change: <int>
  velocity: <units/period | unknown>   # 供 progress tracking v2 §5 effort 公式 · resource allocation v2 staleness 判断
```


用途（不改变既有计算公式，只提供输入）：

- `progress tracking v2 §5` 的 `estimated_remaining_effort = remaining_capability_units / average_completed_capability_units_per_period` —— `velocity` 字段即此处的分母来源。
- `resource allocation v2 §3` staleness penalty/boost —— 可用 `velocity` 趋势辅助判断"该轨最近是否持续产出真实能力"，而不仅仅是"是否被调用过"。

Memory 记录规则（`Completed` / `Failed` / `Deferred` / `Rejected` 各字段：task / track / reason / capability gained 或 retry policy 或 dependency 或 why-lower-value）**继续以 task memory v2 §2/§4/§5 为权威**，v3 不重写这些规则，仅要求每条 Completed 记忆额外附带 `capability_gain`（§6）取值，供后续 velocity 统计使用。


---


# 9. Anti-Stagnation System


v3 不新建检测机制——[stuck detection v2](controller_stuck_detection_policy_v2.md) 已完整定义信号、输出格式、响应动作与阈值。v3 唯一的整合动作是把 §6 的 `CapabilityGainCheck` 接到 stuck detection v2 §2 信号 1 的输入端（见 §6.3），使"好循环"与"坏循环"有精确、逐任务的判定依据：


```text
好循环（继续执行，不触发 stuck）：
  task → validation → capability_gain = CAPABILITY_ADVANCED（或 MAINTAINED 且 evidence 有实质改善）

坏循环（触发 stuck detection v2 响应）：
  commit++ / docs++ / capability_gain = NO_CAPABILITY_CHANGE（连续 ≥2 次，同一轨）
    ↓
  stuck detection v2 §3 输出（Cause / Possible autonomous actions / Human dependency）
    ↓
  stuck detection v2 §4：
    - 有新的 autonomous action → generate → rank → 执行一次
    - 只剩 human dependency → 走 human interrupt v2 §5 track-scoped 打断
    - controller-only churn → 停止 maintenance band，切换轨道
```


结果反馈进 task generator v2 §8 anti-pattern 清单（"letting one track's easy successors monopolize generation" 等）与 task priority v2 §3 ranking procedure（该轨候选降级，不再优先入选），确保下一轮 replan 会主动寻找"更高价值的替代任务"，而不是重复同类低价值工作。


---


# 10. Human Approval Integration — Scope-Driven Execution（2026-07-15 · Major revision）


## 10.0 变更性质


这是对本节的**架构性修订**（不是新层）。上一版本把 [mission objective v2 §5](controller_mission_objective_v2.md) 的"approval 是同步点"解读为"每个动作阶段都需要重新核对批准"，实践中导致 A/C/D 三轨在人类已经清楚授权方向后仍被判定为 `HUMAN_GATE_BLOCKED`（见 Run 8/9/10 报告）。修订后的模型：


| 角色 | 职责 |
|------|------|
| Human | project owner / scope setter / final push authority |
| Agent | engineering team：implementation → test → dry-run → **CNINFO live** → validate → evidence → commit → 继续下一个有价值任务 |


详见 [human interrupt v2 §12 Scope-Driven Execution Amendment](controller_human_interrupt_policy_v2.md)（判定权威）。本节只做架构层面的整合说明。


## 10.1 scope_authorized 字段（NEW，附加于 §2.2 TrackCapabilityState）


```yaml
TrackCapabilityState:
  ...
  scope_authorized: true|false   # 人类是否已经就该 track/component 的方向表态（一次性，不是逐阶段）
  exec_status: READY|RUNNING|COMPLETED|FAILED|WAITING_RETRY   # 见 track stop reason v2 §2.1，取代阶段级 HUMAN_GATE_BLOCKED
```


`scope_authorized=true` 之后，implementation / test / dry-run / **CNINFO live** / validate / evidence / commit **全部**属于自主执行范围（§7 loop 中体现为 `exec_status` 流转，不再逐阶段检查批准）。


## 10.2 Worked example（更新，对齐 Scope-Driven Execution）


```text
Example — D shareholder_change：component 方向已被人类授权（"我批准 D-class shareholder_change 作为下一个 Era D component"）：

D.TrackCapabilityState.scope_authorized = true
D.TrackCapabilityState.exec_status = RUNNING   （implement S4 runner → test → dry-run → CNINFO live → validate → evidence → commit）
D.TrackCapabilityState.available_autonomous_actions =
  [runner implementation, schema refinement, event taxonomy, sample preparation,
   validation rules, offline evidence mapping, CNINFO live execution, evidence packaging, commit]
D.stop_reason = 不适用（除非技术故障耗尽重试，或 push 阶段到达）
```


`D.stop_reason = HUMAN_GATE_BLOCKED`（现称 `HUMAN_DECISION_REQUIRED`）**只在以下情况**才成立：scope 本身尚未被授权（人类还没说"做 D 的 shareholder_change"），或下一步是 push，或需要执行事实上不可逆的动作。

同时：
A.stop_reason ≠ HUMAN_GATE_BLOCKED → A 继续 coverage work
B.stop_reason ≠ HUMAN_GATE_BLOCKED → B 继续 evidence preparation
C.stop_reason ≠ HUMAN_GATE_BLOCKED → C 继续 quality work

Global stop_reason 不受 D 单独影响（§3.2 表：需全部四轨非可继续才允许 global NO_VALUABLE_SAFE_TASK）。
```


这与既有 [track stop reason v2 §4](controller_track_stop_reason_policy_v2.md)"Global stop vs track stop"完全一致，v3 只是把它作为架构级设计原则重申，避免未来实现把"某轨被 approval 卡住"误实现为"停止整个 Controller"。


## 10.1 Approval Information Layer（2026-07-15 · RENAMED from Approval Guidance Layer · 纯呈现层）


### 目的（修订）


上一版本（Approval Guidance Layer）围绕"如何证明批准已满足 exact-phrase"组织，实践证明这会让人类为**已经授权过的方向**反复寻找逐字短语，阻碍正常工程执行（见 Run 8/9/10 报告）。修订后，本层不再围绕逐阶段批准判定组织，而是围绕人类**真正需要知道**的三件事组织：当前 mission scope 状态、pending push、destructive action 警示。


### 硬性边界（修订）


1. **不阻塞正常工程工作。** implementation / test / dry-run / CNINFO live / validate / evidence / commit 不经过本层判定（见 [human interrupt v2 §12](controller_human_interrupt_policy_v2.md)）。
2. **不要求 exact-phrase 才能执行。** exact-phrase 匹配只保留给 push 与 destructive/irreversible action 两类（human interrupt v2 §6，收窄后）。
3. **不拒绝合理的人类授权表述。** scope 授权（"做 X track/component"）不要求逐字模板；模板仅供参考格式，不是判定门槛。
4. **不产生人为等待态。** 若 scope 已授权，本层不得展示"仍在等待批准"。


### 输出 schema（`ApprovalInformation`，替代 `ApprovalGuidance`）


```yaml
ApprovalInformation:                     # 常驻展示，不限于某个 stop_reason
  track: A | B | C | D
  current_scope: "<该轨当前被授权的方向摘要，来自 scope 历史记录>"
  exec_status: READY | RUNNING | COMPLETED | FAILED | WAITING_RETRY   # track stop reason v2 §2.1
  pending_push: true|false               # 该轨是否有已完成工作等待 push 决策
  destructive_action_pending: "<若有，描述具体动作与原因；否则 null>"
  approval_history: ["<按时间顺序记录的 scope 授权语句，供人类查阅>", ...]
```


`ApprovalInformation` **不产生**任何"阻止执行"的效果——它是只读信息展示；执行与否完全由 §10.1 之外的 `scope_authorized` 字段（§10.1 上方 §10 表）与 §12 硬性执行门决定。


### 与既有政策的关系（不新增审批权威）


| 字段来源 | 权威 |
|---|---|
| `current_scope` / `approval_history` | scope 授权记录（human interrupt v2 §6 表，现为记录格式而非执行门） |
| `exec_status` | track stop reason v2 §2.1 |
| `pending_push` / `destructive_action_pending` | human interrupt v2 §3.1 / §3.4（唯二保留的硬性执行门） |


### Reporting 集成（附加式，替代原 §10.1 呈现）


```markdown
### Approval information（v3 §10.1，附加式，常驻展示）
- A: current_scope / exec_status / pending_push / destructive_action_pending
- B/C/D: 同上
```


### Anti-patterns


禁止：


- 为已授权 scope 内的每个执行阶段重新要求逐字短语
- 把 CNINFO live / implementation / test 标记为需要本层"确认"才能继续
- 把本层输出当作审批记录本身（审批记录仍以 human interrupt v2 + PROJECT_CONTROL Active Approvals 表为准）
- 对 push / destructive action 两类**放宽** exact-phrase 要求（这两类的判定标准不受本次修订影响）


---


# 11. Progress Reporting


v3 沿用 [daily execution schema v2 §5](controller_daily_execution_schema_v2.md) 的报告 outline（Tracks / Progress intelligence / Planning intelligence / Human attention / Safety / Remaining dirty / Next loop recommendation），**不改变现有必填字段**。v3 的唯一新增：在 `Progress intelligence` 与 `Planning intelligence` 之间插入一个 **Capability Gain 汇总块**（附加式字段，旧报告读取器可忽略）：


```markdown
### Capability gain summary（v3，附加式）
- A: capability_gain this cycle = <ADVANCED|MAINTAINED|NO_CHANGE> · historical_velocity = <value|unknown>
- B: capability_gain this cycle = <ADVANCED|MAINTAINED|NO_CHANGE> · historical_velocity = <value|unknown>
- C: capability_gain this cycle = <ADVANCED|MAINTAINED|NO_CHANGE> · historical_velocity = <value|unknown>
- D: capability_gain this cycle = <ADVANCED|MAINTAINED|NO_CHANGE> · historical_velocity = <value|unknown>
- Stagnation status: <none | track X flagged stuck per §9>
```


必填字段清单（全部继承，逐一列出以便实现核对，不新增计算规则）：


**Global（progress tracking v2 §2.2 + §6）：**
- `overall_completion_pct` · `completed_capability_units` · `remaining_capability_units` · `estimated_remaining_effort`


**Per track A/B/C/D（progress tracking v2 §6 + track execution queue v2 §7 + track stop reason v2 §6）：**
- `current_capability` · `completed_capability_units` · `remaining_gaps` · `queue depth`（= `len(ready_successors)+len(candidate_successors)`）· `last executed task` · `next recommended task` · `stop reason`


**Planning（daily execution schema v2 §5 Planning intelligence + mission replanning loop v2 §7）：**
- Generated tasks · Executed tasks · Rejected tasks（now sourced from §4.1 persisted `rejected_tasks`）· Capability delta（= §6 `capability_gain` 汇总）· Stagnation status（= §9 输出）


这些字段**没有一个是全新计算**——全部来自既有权威文件；v3 只是把它们在报告里的排列顺序和"Capability delta / Stagnation status"两个标签固定下来，方便和 §6/§9 的新词表对应。


`overall_completion_pct` 与逐轨 completion 的**具体判定规则**（何时允许给出百分比、denominator 未定时如何报告）由 §16 Mission Completion Model 统一定义；本节字段清单不变，仅新增 §16 作为其计算依据的权威来源。


---


# 12. Stop Conditions（consolidated view，重复 §3.2，供快速查阅）


| 条件 | 层级 | 触发前必须完成 |
|------|------|----------------|
| `HUMAN_GATE_BLOCKED` / `HUMAN_DECISION_REQUIRED`（2026-07-15 收窄，见 §10/§12 修订） | Track | scope 未授权，或下一步是 push / 事实不可逆动作（**不再**包括 implementation / test / dry-run / CNINFO live——那些用 `exec_status`，见 track stop reason v2 §2.1） |
| `NO_SAFE_AUTONOMOUS_TASK` | Track | 完整 candidate audit（mission replanning loop v2 §2.2） |
| `LOW_PRIORITY_DEFERRED` | Track | 有安全候选但被更高价值任务抢占（resource allocation v2） |
| `NO_VALUABLE_SAFE_TASK`（≡`NO_SAFE_READY`） | **Global** | 四轨候选审计全部完成且全部非可继续（§3.2） |
| `SAFETY_VIOLATION` | Global | 红线 / 所属权 / 证据诚信检测（execution cycle v2 §4） |
| `BUDGET_REACHED` | Global | `max_iterations`/`max_runtime` 耗尽（execution cycle v2 §6） |
| `HUMAN_INTERRUPT` | Global（S3/S4）或 Track（S2） | human interrupt v2 §8 escalation severity（S2 现仅覆盖 push / scope 冲突 / destructive，不再覆盖 CNINFO live/component 批准） |


---


# 13. Safety Constraints（重申，不新增，不放宽）


**禁止：**
- push / force-push（push policy v1 · human interrupt v2 §3.1）— **唯一不变的硬性门**
- 事实上不可逆的外部/生产 mutation（human interrupt v2 §3.4，收窄后的判定标准）
- destructive operations（`reset --hard`、清空受保护目录等，human interrupt v2 §3.4）
- 未经**方向授权**（scope）的范围扩张（human interrupt v2 §3.5）——注意：scope 一旦授权，implementation/test/CNINFO live 不再逐项禁止（2026-07-15 Scope-Driven Execution Amendment，见 §10/human interrupt v2 §12）

**允许（bounded commit 前提下）：**
- docs（commit autonomy v2 §3 Documentation）
- evidence（commit autonomy v2 §3 Validation evidence）
- tests（commit autonomy v2 §3 Tests）
- isolated source changes（commit autonomy v2 §3 Isolated source）

本文件（v3 架构设计文档）本身属于 **Control-adjacent docs** 类（commit autonomy v2 §3 最后一行："new controller policy design docs under `plans/controller_*`"），可在 human 批准落地后按该类走 bounded commit；**当前任务本身不要求也不执行任何 commit/push**（用户指令：documentation and policy design only）。


---


# 14. Policy Integration Map（核心交付物：证明整合而非复制）


| v2 / v1 文件 | v3 中的角色 | v3 是否修改其内部规则 |
|---|---|---|
| controller_mission_objective_v2.md | Global Mission + Track 目标定义（§1/§2.1）· 审批哲学来源（§10） | 否 |
| controller_progress_tracking_v2.md | `current_capability` / global 进度字段来源（§2.1/§2.2/§11）· completion 百分比诚实约束权威（§16） | 否 |
| controller_capability_gap_analysis_v2.md | `remaining_gaps` 计算权威（§2.2/§3）· 逐轨 gap 维度来源（§16.3 对齐表） | 否 |
| controller_task_generator_policy_v2.md | candidate 生成 + Approval Split 权威（§3/§4/§9） | 否（本次仅追加指针，见 §15 更新说明） |
| controller_task_continuation_policy_v2.md | `continuation_outcome` 权威，供 §6 派生 `capability_gain` | 否 |
| controller_task_priority_policy_v2.md | 排序因子权威（§5）· 安全过滤先于排序 | 否 |
| controller_resource_allocation_policy_v2.md | fairness / staleness / bottleneck 分配权威（§5/§8） | 否 |
| controller_task_memory_policy_v2.md | Completed/Failed/Deferred/Rejected 记忆权威（§8） | 否 |
| controller_stuck_detection_policy_v2.md | anti-stagnation 检测与响应权威（§9） | 否 |
| controller_milestone_management_v2.md | 里程碑分解，供 §2.1 `active_milestones` | 否 |
| controller_mission_replanning_loop_v2.md | 连续重规划循环、candidate audit、state refresh 权威（§3/§7） | 否 |
| controller_track_execution_queue_policy_v2.md | 队列基础字段权威（§4） | 是（本次追加两个可选字段，见 §15） |
| controller_track_stop_reason_policy_v2.md | track/global 停机枚举权威（§3.2/§12） | 否 |
| controller_execution_cycle_policy_v2.md | 迭代/预算/停机机制权威（§7/§12） | 否（本次仅追加指针，见 §15） |
| controller_daily_autonomous_loop_v2.md | 主调度算法权威（§7 Mission Execution Loop 的基底） | 否（本次仅追加指针，见 §15） |
| controller_daily_execution_schema_v2.md | 报告 schema 权威（§11） | 否 |
| controller_human_interrupt_policy_v2.md | 打断分级权威（§10/§13）· exact-phrase 判定唯一权威（§10.1，Approval Guidance Layer 只读引用） | 否（本次追加指针，见 §15 更新说明） |
| controller_commit_autonomy_policy_v2.md | commit 权限权威（§13） | 否 |

**结论：v3 对现有 v2 政策内部规则的修改面 = 0 处删除、0 处放宽；仅 4 处追加式指针说明 + 1 处追加式可选字段（见 §15）。**


---


# 15. Files Updated（与本文件配套的最小变更，详见对应文件）


以下四份文件各追加一个**指针小节**（不改变原有条款），说明它们如何被 v3 引用：

- `controller_daily_autonomous_loop_v2.md` — 追加"Relationship to Mission Execution Engine v3"小节。
- `controller_execution_cycle_policy_v2.md` — 追加"Relationship to Mission Execution Engine v3"小节。
- `controller_track_execution_queue_policy_v2.md` — 追加 §7 的两个可选字段（`candidate_successors` / `rejected_tasks`）说明。
- `controller_task_generator_policy_v2.md` — 追加"v3 Capability Gain 联动"小节，说明 candidate audit 输出应同时写入 §4.1 持久化字段。
- `controller_human_interrupt_policy_v2.md` — 追加"Relationship to Mission Execution Engine v3 Approval Guidance Layer"小节，明确 §6 exact-phrase 判定权威不受影响。

具体 diff 见各文件本身；本节仅作索引。


---


# 16. Mission Completion Model


## 16.1 Purpose


前面各节回答了"如何持续执行"，本节回答用户提出的缺失问题：**"Controller 如何知道自己正在接近，或已经到达全市场使命目标？"**


**完成度只能用能力衡量，不得用以下任何指标代替（继承 [progress tracking v2 §2.1](controller_progress_tracking_v2.md) 的 non-units 清单，v3 重申适用于本节全部字段）：**


- commit count
- file count
- task count（生成/执行的任务数量）
- agent activity（agent 被调用次数）


本节不新增计算公式——它把 progress tracking v2（§2）+ capability gap analysis v2（§2）+ §2.2 `TrackCapabilityState` 已经存在的字段，组织成一个明确回答"多接近使命"的判定模型，并把用户列出的四轨"possible dimensions"接到既有逐轨 metrics 表上。


## 16.2 Global Mission Completion


**定义：** A/B/C/D 四轨能力达成度的合成，衡量距离"全市场数据平台"使命的接近程度。


```yaml
GlobalMissionCompletion:
  global_mission_completion_pct: <pct | UNKNOWN>
  weighting_method: "equal_weight_default" | "<milestone-defined weights>"
  tracks:
    A: { track_completion_pct: <pct|UNKNOWN> }
    B: { track_completion_pct: <pct|UNKNOWN> }
    C: { track_completion_pct: <pct|UNKNOWN> }
    D: { track_completion_pct: <pct|UNKNOWN> }
```


**计算规则（继承 [progress tracking v2 §2.2 规则 3](controller_progress_tracking_v2.md)，不放宽）：**


1. `global_mission_completion_pct` 只有在 **A/B/C/D 四轨的 `track_completion_pct` 全部已知**（非 `UNKNOWN`）时才可计算；否则 `global_mission_completion_pct = UNKNOWN`，即使部分轨道已有具体数值。
2. 默认权重为 **四轨等权**（`equal_weight_default`）；若人类通过 milestone management v2 显式指定了不同权重（例如某轨对"全市场平台"权重更高），必须在 `weighting_method` 字段写明依据，不得静默套用非等权。
3. `global_mission_completion_pct` 是一个**报告状态**，不是执行授权——达到 100% 不会自动触发 live / push / production 变更（§13 安全边界不变）。


## 16.3 Track-level completion — dimension mapping（对齐既有 metrics，不新造指标）


用户列出的四轨"possible dimensions"是对 [progress tracking v2 §3](controller_progress_tracking_v2.md) 既有逐轨 metrics 的**细化**（把"attribute coverage"拆成 required-attribute-coverage + attribute-completeness + profile quality 等），v3 用下表对齐，避免两套指标语义分裂：


| Track | 用户提出的 dimension（本次新增措辞） | 对齐到既有 metric（progress tracking v2 §3 / capability gap analysis v2 §4） |
|---|---|---|
| A | company universe coverage | company coverage |
| A | required attribute coverage | attribute coverage |
| A | attribute completeness | attribute coverage（细化：完整度而非仅"存在"） |
| A | validated company profile quality | evidence_basis / QA 关联（跨引 C track 质量口径，不重复定义） |
| B | disclosure source coverage | source coverage |
| B | event extraction coverage | extraction coverage |
| B | event timeline completeness | event completeness |
| B | event validation quality | evidence_basis / QA 关联（跨引 C track） |
| C | evidence coverage | evidence completeness |
| C | evidence validity | QA status |
| C | QA pass rate | QA status（细化：可量化比率） |
| C | audit completeness | evidence completeness（细化：audit trail 维度） |
| D | shareholder structure coverage | shareholder coverage |
| D | ownership event coverage | ownership events |
| D | capital structure completeness | capital structure completeness |
| D | validation confidence | evidence_basis / QA 关联（跨引 C track） |


**规则：**这些 dimension 是**报告细分维度**，不是新的 gate 或新的 track 职责划分——C track 仍是唯一的"evidence and quality"权威（mission objective v2 §3），A/B/D 的"quality/confidence"维度必须引用 C 的既有 QA 产物，不得各轨自建平行质量口径。


## 16.4 Track Completion State（schema，附加于 §2.2 `TrackCapabilityState`）


```yaml
TrackCompletionState:                 # 附加字段，挂在 TrackCapabilityState 之下，不替换 §2.2 既有字段
  track: A | B | C | D
  dimensions:                         # §16.3 对齐表中该轨的维度列表
    - dimension_id: "<e.g. company_universe_coverage>"
      metric_observed: "<数值或 evidence 指向>"
      denominator_status: known | unknown | not_frozen
      completion_pct: <pct | UNKNOWN>   # 仅当 denominator_status = known 才允许非 UNKNOWN
  current_capability: <ref §2.2>
  completed_capability_units: <int | list>       # = §2.2 字段，同源
  remaining_capability_units: <int | UNKNOWN>    # = §2.2 remaining_gaps 的量化视图
  track_completion_pct: <pct | UNKNOWN>          # 仅当该轨全部 dimensions 的 denominator 均已知才可计算，否则 UNKNOWN
```


## 16.5 Honesty rule（硬性，不得违反）


> **Denominator 未冻定 ⇒ 报告 `UNKNOWN`。禁止编造百分比。**


直接继承并适用于本节新字段（[progress tracking v2 §2.2 规则 2](controller_progress_tracking_v2.md)："If denominators are undefined → `overall_completion_pct = unknown`（do not invent 37.2%）"；[§8 honesty constraints](controller_progress_tracking_v2.md)："unknown is preferable to false precision"）：


1. 任一 dimension 的 `denominator_status ≠ known` → 该 dimension `completion_pct = UNKNOWN`。
2. 任一轨道存在 `UNKNOWN` dimension → 该轨 `track_completion_pct` 视具体规则可选择：仅对**已知 denominator 的 dimension** 做子集完成度陈述（并显式标注"部分维度"），但**不得**把子集完成度当作整轨完成度冒充上报。
3. 任一轨 `track_completion_pct = UNKNOWN` → `global_mission_completion_pct = UNKNOWN`（§16.2 规则 1）。
4. `PASS_WITH_CAVEAT` / snapshot blocked / `READY_FOR_APPROVAL` 均不构成"denominator known + 100%"（继承 progress tracking v2 §8 全部诚实约束，不重复枚举）。


## 16.6 Integration with Capability Gain Check（§6）


完成度变化必须与 §6 `capability_gain` 分类一致，不得出现"completion 上升但 capability_gain = NO_CAPABILITY_CHANGE"这类自相矛盾的报告：


| `capability_gain`（§6） | 对 completion 的预期影响 |
|---|---|
| `CAPABILITY_ADVANCED` | 至少一个 dimension 的 `completed_capability_units` 或 `completion_pct` 提升 |
| `CAPABILITY_MAINTAINED` | completion 数值不变，但证据/质量维度（evidence validity / QA pass rate / validation confidence）有真实提升，非纯重复 |
| `NO_CAPABILITY_CHANGE` | completion 数值与证据质量均未变 → **stagnation 信号**，接入 §9 anti-stagnation |


若某任务声称 `CAPABILITY_ADVANCED` 但对应 dimension 的 `completion_pct` / `completed_capability_units` 没有变化证据，视为记录不一致，应回退判定为 `CAPABILITY_MAINTAINED` 或 `NO_CAPABILITY_CHANGE`（以证据为准，不以任务自我声明为准——呼应 progress tracking v2 honesty constraints）。


## 16.7 Global mission-complete condition（形式化定义）


```text
mission_not_complete = NOT (
  A.track_completion_pct known AND A.track_completion_pct >= 100 AND
  B.track_completion_pct known AND B.track_completion_pct >= 100 AND
  C.track_completion_pct known AND C.track_completion_pct >= 100 AND
  D.track_completion_pct known AND D.track_completion_pct >= 100 AND
  no_unresolved_red_line_caveat_blocking_completion_claim   # progress tracking v2 §2.2 规则 5
)
```


**重要：** 只要任一轨 `track_completion_pct = UNKNOWN`，`mission_not_complete` 必须保持 `true`（即：不知道 ⇒ 不能宣称完成，而不是默认当作已完成）。达到该条件仅代表**报告口径的"使命完成"**，不自动改变 §13 的任何安全边界或审批要求。


## 16.8 Reporting integration（对齐 §11，附加式，不改变必填字段）


daily report（[daily execution schema v2 §5](controller_daily_execution_schema_v2.md) + §11 Progress Reporting）未来应支持以下附加字段，全部来自本节定义，不引入新计算：


```markdown
### Mission completion summary（v3 §16，附加式）
- Global mission completion: <pct|UNKNOWN>
- A completion: <pct|UNKNOWN>
- B completion: <pct|UNKNOWN>
- C completion: <pct|UNKNOWN>
- D completion: <pct|UNKNOWN>
- Remaining gaps: <ref §2.2 remaining_gaps 汇总>
- Largest bottleneck: <取四轨 current_bottleneck 中 impact 最大者，见 progress tracking v2 §4>
- Recommended next capability target: <取 mission priority system §5 排序后的 top-1 候选>
```


该块是"应尽快支持"（should eventually support），当前任务**不要求**立即修改 `daily_execution_schema_v2.md` 的必填结构；启用时机由后续验证任务决定（见任务报告"recommended next validation run"）。


## 16.9 Anti-patterns


禁止：


- 用 commit / file / task / agent 调用次数代替 completion 百分比
- denominator 未冻定时编造具体百分比（例如"37.2%"）
- 把 `PASS_WITH_CAVEAT` 或 snapshot-blocked 状态当作 100% 完成
- 任一轨 `UNKNOWN` 时仍计算 global completion
- 把 `NO_CAPABILITY_CHANGE` 周期报告为 completion 上升
- 用不同轨道自建的质量口径替代 C track 的 QA 权威


---


# 17. Non-goals


- 不是新的 runner / 代码实现（架构与政策设计阶段）。
- 不是第二套队列系统（仍是 track execution queue v2 的附加字段）。
- 不是审批绕过机制——2026-07-15 修订收窄了执行门的**范围**（仅 push + 不可逆动作），并未取消判定本身；scope 授权仍需人类明确表态一次。
- 不是自动 push 授权变更——push 仍是唯一硬性人控点，本次修订不改变这一点。
- 不是"能力提升百分比"的新计算公式（沿用 progress tracking v2；§16 只是把既有公式接到逐轨 dimension 上）。
- 不是取代 daily report schema（沿用 daily execution schema v2，仅附加 Capability gain summary 与 Mission completion summary 两个块）。


---


# 18. Versioning / Activation


- Schema id 建议：`mission_execution_engine_v3`（附加式，向后兼容 `daily_execution_plan_v2` / `daily_autonomous_operation_report_v2`）。
- 与 v2 四份文件（daily loop / mission objective / human interrupt / commit autonomy）在启用 Daily Loop v2 时一样，**启用 Mission Execution Engine v3 作为默认运行引擎需要单独的人类确认**——本次任务只交付架构文档，不代表已启用。
- **2026-07-15 · v3.1 Scope-Driven Execution Amendment**（本次修订）：人类明确要求用"scope 一次授权 + agent 自主完成全生命周期"取代"approval-driven 逐阶段批准"。修订范围：本文件 §0/§7/§10/§10.1/§12/§13，以及 `controller_human_interrupt_policy_v2.md §3.2/§4/§6/§11/§12(NEW)`、`controller_track_stop_reason_policy_v2.md §2.1(NEW)/§3.1/§7`、`controller_commit_autonomy_policy_v2.md §3`。唯一不变的硬性人控点：**push to remote** 与**事实上不可逆的外部/生产动作**。此修订不新增政策文件（遵循用户"不新增政策层"的明确要求）。
- 启用前建议的验证顺序见任务报告"recommended next validation run"部分。
- **2026-07-15 · 调度层升级见 v4：** [controller_mission_execution_engine_v4.md](controller_mission_execution_engine_v4.md) 在本文件能力/权限模型之上，将 **Global Wave 同步调度** 升级为 **track-local 异步连续循环**（一轨完成即 review→commit→replan→dispatch，不等其他轨）。本文件 §7 循环在启用 v4 后解释为按轨并发实例，不再要求四轨 barrier。
