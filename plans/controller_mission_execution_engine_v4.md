# Controller Mission Execution Engine v4

_最后更新：2026-07-15_  
_状态：Architecture upgrade · Scope-Driven Execution（v3.1）之上的调度层升级_  
_性质：异步连续执行引擎（asynchronous continuous autonomous execution）— 不重写 v2/v3 安全与能力规则_

配套权威：

- [Mission Execution Engine v3](controller_mission_execution_engine_v3.md) — 使命 / 能力缺口 / Capability Gain / Scope-Driven / Completion Model
- [Track Execution Queue v2](controller_track_execution_queue_policy_v2.md)
- [Resource Allocation v2](controller_resource_allocation_policy_v2.md)
- [Execution Cycle v2](controller_execution_cycle_policy_v2.md)
- [Daily Autonomous Loop v2](controller_daily_autonomous_loop_v2.md)
- [Human Interrupt v2 §12](controller_human_interrupt_policy_v2.md) — Scope-Driven 权限边界

---

# 0. Purpose

Run 12 已验证：

- 多波 refill 有效
- A/B/C/D 可独立推进能力
- live CNINFO 可在授权 scope 内执行
- evidence → review → commit 闭环有效

**Run 12 的效率瓶颈：** Controller 以 **Global Wave** 同步调度——必须等 A/B/C/D **全部**完成才开启下一波。长任务（例如 A 的 CNINFO live）会让已完成的 B/C/D **空转等待**。

v4 唯一升级目标：

```text
同步多波批次执行  →  异步轨内连续执行
(global wave sync)    (per-track independent loops)
```

**v4 不改变：**

- Scope-Driven 权限模型（push / 不可逆动作仍人控）
- Capability Gap / Capability Gain Check / Mission Completion
- 安全红线、commit 边界、evidence 要求

**v4 改变：**

- 调度粒度：从 global wave → **track-local wave**
- 完成语义：一轨完成立即 replan/dispatch，**不等**其他轨
- 预算：扩大 runtime / commit 上限；停机条件改为全轨审计后无有价值任务

---

# 1. Core Principle — Asynchronous Track Independence

## 1.1 Forbidden (v3/v4 sync-wave anti-pattern)

```text
Global Wave N:
  dispatch A,B,C,D
      ↓
  wait until ALL complete
      ↓
  review all
      ↓
  commit batch
      ↓
  replan all
      ↓
  Global Wave N+1
```

问题：`max(runtime_A, runtime_B, runtime_C, runtime_D)` 决定波次墙钟时间；短轨被迫等待长轨。

## 1.2 Required (v4)

```text
Each track T ∈ {A,B,C,D} has an independent loop:

  READY
    ↓
  EXECUTING          # agent dispatched; other tracks may also be EXECUTING
    ↓
  VALIDATING         # evidence-auditor (+ regression if shared runner)
    ↓
  COMMITTED          # git-boundary + explicit-path commit (track package only)
    ↓
  REFRESH_GAP        # only T's capability state
    ↓
  GENERATE_NEXT      # only T's successors
    ↓
  READY              # dispatch immediately if valuable safe task exists
```

**硬规则：**

1. Track T 完成 ≠ 等待其他轨。  
2. Track T 的 `READY` 可在 Track U 仍 `EXECUTING`（例如长 CNINFO live）时立刻派发。  
3. Global Wave 编号**废止**为调度单位；报告改用 **track-local wave**（`A-wave-1`, `B-wave-2`, …）。  
4. 禁止为填满空闲轨而发明低价值任务（仍遵守 task priority / anti-stagnation）。

---

# 2. Track Lifecycle State（v4）

附加于 v3 `TrackCapabilityState` / `exec_status`：

```yaml
TrackAsyncState:                         # v4 NEW
  track: A|B|C|D
  lifecycle: READY | EXECUTING | VALIDATING | COMMITTED | REFRESHING | IDLE_NO_TASK
  track_wave_index: <int>                # 本轨内部波次计数（从 1 递增）
  active_task_id: <str|null>
  blocked_by_other_tracks: false         # 恒为 false；禁止设为 true
  parallel_peers_running: [A|B|C|D...]   # 仅供报告，不阻塞调度
```

与 v3 `exec_status`（READY/RUNNING/COMPLETED/FAILED/WAITING_RETRY）关系：

| lifecycle | 典型 exec_status |
|-----------|------------------|
| READY | READY |
| EXECUTING | RUNNING |
| VALIDATING | COMPLETED（执行已结束，审阅中） |
| COMMITTED | COMPLETED |
| REFRESHING | — |
| IDLE_NO_TASK | 对应 stop_reason=`NO_SAFE_AUTONOMOUS_TASK` 等 |

长任务（CNINFO live）：

```text
T.lifecycle = EXECUTING
T.exec_status = RUNNING
# 其他轨照常 READY→EXECUTING；不得因 T 运行而全局暂停
```

---

# 3. Controller Scheduler（v4 主循环）

取代 v3 §7 中隐含的"每轮四轨齐步走"：

```text
ASYNC_MISSION_LOOP_V4:
  budget = load_budget(max_runtime=240min, max_commits=30)
  for T in [A,B,C,D]:
    T = refresh_track_async_state(T)

  while budget_ok and not safety_stop:
    # 1. 收割已完成 agents（非阻塞）
    for done in poll_completed_agents():
      T = done.track
      T.lifecycle = VALIDATING
      evidence = evidence_auditor(done)           # per-track，非全局波次末
      if shared_runner_changed(done):
        regression = regression_reviewer(done)
      boundary = git_boundary_reviewer(done)
      if evidence.ok and boundary.ready and commit_budget_remaining():
        explicit_path_commit(done.allow_list)     # 一轨一包；禁止 git add -A
        T.lifecycle = COMMITTED
        write_task_memory(done)
        gain = capability_gain_check(done)
        T.track_wave_index += 1

        # 2. 仅刷新完成轨
        T.lifecycle = REFRESHING
        refresh_track_capability_state(T)         # 不强制刷新其他轨
        successors = generate_successors(T, gain)
        refill_track_queue(T, successors)

        # 3. 立刻派发（若有价值）
        if T.queue.has_valuable_ready():
          T.lifecycle = READY
          dispatch_agent(T)                       # 不等 B/C/D
          T.lifecycle = EXECUTING
        else:
          T.lifecycle = IDLE_NO_TASK

    # 4. 为仍 IDLE 但 gap 刷新过期的轨做轻量审计（非同步屏障）
    for T in idle_tracks():
      if stale_gap(T):
        refresh_track_capability_state(T)
        maybe_dispatch(T)

    # 5. 全局停机仅当：四轨均 IDLE_NO_TASK 且 candidate audit 全无有价值任务
    if all_tracks_idle_and_audited_empty():
      stop = NO_VALUABLE_SAFE_TASK
      break

    if budget.runtime_exhausted():
      stop = BUDGET_REACHED
      break

  NEVER push
```

**关键差异 vs Run 12：**

| Run 12 | v4 |
|--------|-----|
| 等 A+B+C+D 齐 | 每轨完成即处理 |
| Global Wave N | `A-wave-k` / `B-wave-m` … |
| 审阅在波末集中 | 每轨任务完成后立即审阅 |
| 短轨空等长 live | 短轨并行前进 |

---

# 4. Independent Track Waves（报告模型）

报告必须按轨列出内部波次，而不是单一 Global Wave 表：

```markdown
## Track-local waves

### A
- A-wave-1: <task> → review → commit <sha>
- A-wave-2: <task> → ...
- internal_wave_count: N

### B
- B-wave-1: ...
- internal_wave_count: M
```

**Parallel efficiency** 段必填：

```text
While A was EXECUTING (CNINFO live ...):
  B completed B-wave-k and started B-wave-(k+1)
  C completed ...
  D completed ...
```

---

# 5. Budget Model（v4）

| 预算项 | v4 默认 |
|--------|---------|
| max_runtime | **240 minutes** |
| max_commits | **30**（仍要求 domain 分包；禁止无意义 micro-commit） |
| max_global_waves | **废除**（不再作为停机/迭代上限） |
| per-track wave | 无硬上限；受 runtime + 有价值任务约束 |

停机仅当：

1. `BUDGET_REACHED`（runtime 或 commit 上限）  
2. `NO_VALUABLE_SAFE_TASK`（**四轨** candidate audit 后均无有价值安全任务）  
3. `SAFETY_STOP` / `HUMAN_DECISION_REQUIRED`（push / 不可逆 / scope 不清）

**禁止**因下列原因停机：

- 一轨仍在 RUNNING  
- 一轨暂时 IDLE_NO_TASK（其他轨仍有工作）  
- "本轮 global wave 结束"  
- 单轨完成

---

# 6. Priority（不变，重申调度含义）

沿用 task priority v2 / v3 §5：

1. mission capability gain  
2. track bottleneck reduction  
3. evidence generation  
4. quality improvement  
5. maintenance  

v4 附加：

- 空闲轨**不得**被分配伪造小任务。  
- 若空闲轨确有 P1–P4 有价值任务 → **立即** dispatch（即使另一轨长任务进行中）。

---

# 7. Review Pipeline（per-track）

每个 **track task** 完成后（非全局波末）：

1. **evidence-auditor** — 证据完整 / 溯源 / capability claim  
2. **regression-reviewer** — 仅当 shared runner / collector / 核心路径变更  
3. **git-boundary-reviewer** — explicit-path allow-list  

然后才 commit 该轨包。其他轨的 EXECUTING 任务不受影响。

---

# 8. Live CNINFO（非阻塞）

在 Scope-Driven 授权 scope 内：

- live 可执行，`lifecycle=EXECUTING`  
- **不得**阻塞其他轨的 offline / QA / evidence / live  

报告 CNINFO 时按轨累计，并标注并行时段。

---

# 9. Relationship to v3

| 层 | 权威 |
|----|------|
| 使命 / 缺口 / Gain / Completion / Scope-Driven | **v3** |
| 异步调度 / track-local waves / 非阻塞 live | **v4（本文件）** |
| 队列字段 / stop reason 枚举 | v2 + v3 收窄后的 HUMAN_DECISION_REQUIRED |

v3 Mission Execution Loop（§7）在启用 v4 后解释为：**逻辑步骤不变，但循环实例按轨并发**，不再要求四轨 barrier。

---

# 10. Activation

- Schema id：`mission_execution_engine_v4`  
- 启用需人类确认（与 v3 相同）。  
- 验证建议：至少一次 Run，证明 **B/C/D 在 A 长 live 期间完成 ≥1 个 track-local wave 并 commit**。  
- Push 仍人控。

---

# 11. Non-goals

- 不是多进程/多机编排实现规范（仍可由单 Controller 会话用后台 agent 模拟异步）  
- 不是取消 evidence/regression/boundary  
- 不是提高 commit 噪音（仍禁止 `git add .`；仍按域分包）  
- 不是放宽 push / 破坏性动作门控
