# CNINFO A 类 Next-Task Search — A-R16-04 IDLE

_生成时间：2026-07-15 · honest search only · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | A-R16-04 |
| track | A |
| executor | a-class-executor |
| controller_execution_allowed | false |
| result | **IDLE** |
| CNINFO live | **0** |
| commit / push | **无** |
| ready_for_commit | **false**（无能力增量产物；仅 IDLE 拒绝记录） |

## 1. 前置已关闭（本轮不得重做）

| 包 / HEAD | 内容 | 状态 |
|-----------|------|------|
| A-R16-01 `ec2e0a3` | orgId fallback hook + isolated retry（AD2E578/590/598） | closed · org present 仍 records=0 |
| A-R16-02 `e68dd7a` | matching-empty → listing_gap triage + offline gate | closed · CAPABILITY_ADVANCED |
| A-R16-03 `35afbcf` | `listing_period_gate` 接入 slice2 lint / builder filter | closed · `PASS_OFFLINE` |
| Slice2 S1 live | session1+2 · observational **97/100** · closure candidate | closed-with-caveat（candidate） |
| Slice2 S1 cohort freeze | AD2E501–600 · ST-EXCLUDE +100 · O3 | **FROZEN** |

权威证据：
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_period_wire_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_matching_empty_triage_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_closure_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_cohort_freeze_note_20260714.md`

A-R16-03 `next_hint`：下一 slice/cohort 选码时调用 `filter_erad_next_scale_slice2_cases_by_listing_period`。

## 2. 候选搜索与拒绝

| # | 候选 | capability_gain_expected | 结论 |
|---|------|--------------------------|------|
| 1 | 在已授权 `erad_a_scale_500_slice2` 内再做 S1 live / retry / caveat 重审计 | false | **拒绝** — S1 live+orgId+listing 根因链已闭合；再跑为重复证据 |
| 2 | 构建 AD2E601+（+8 非 ST complement）+ listing filter 后 dry-run/live | 极低 | **拒绝** — 见 §2.1；过滤后仅 **2** 码对 2024 期窗 listing_ok |
| 3 | 打开 S1 已永久排除的 48 ST 余量做 filtered cohort | 政策冲突 | **拒绝** — freeze note S1 ST-EXCLUDE；改策略需 Controller / 新 scope |
| 4 | 为 6 个上市日≥2025 的余量码发明 listing-aware period 重配 | 设计未冻结 | **拒绝** — 非机械套用 filter；属 period-policy 新决策，executor 不得静默发明 |
| 5 | 从 `full_market_2024`（6124）刷新 A remainder → 大片 next-scale | 高（mission） | **拒绝本轮自治** — 889 非 ST 余量已尽；扩分母 / 选取规则 / case 空间属 **scope_missing**（须人类方向） |
| 6 | Attribute-gap Phase A 对 486 effective 做 catalog 填充率评分 | 低–中 | **拒绝** — ledger/skeleton 已有；无冻结评分 rubric 时易成 docs busywork；对 next-scale 覆盖增量≈0 |
| 7 | 对封闭 S1 三案再 live / mutate S1 live 根 | n/a | **禁止** — R16-02 `retry_recommended=no` · 不得 mutate 封闭 S1 live 根 |
| 8 | gate 升级 verified / production_ready / push | n/a | **禁止** — 人控红线 |

### 2.1 +8 余量 × listing_period 实证（CNINFO=0）

源：`cninfo_a_class_slice2_pool_remainder_draft_20260714.csv` − S1 +100 · ST-EXCLUDE。

| company_code | name | listing_date | vs expected_period=2024-12-31 |
|--------------|------|--------------|-------------------------------|
| 688777 | 中控技术 | 2020-11-24 | **listing_ok** |
| 688786 | 悦安新材 | 2021-08-26 | **listing_ok** |
| 688781 | 视涯科技 | 2026-03-25 | listing_gap reject |
| 688785 | 恒运昌 | 2026-01-28 | listing_gap reject |
| 688795 | 摩尔线程 | 2025-12-05 | listing_gap reject |
| 688797 | 臻宝科技 | 2026-06-24 | listing_gap reject |
| 688809 | 强一股份 | 2025-12-30 | listing_gap reject |
| 688818 | 电科蓝天 | 2026-02-10 | listing_gap reject |

```text
unused_non_st_remainder = 8
listing_ok_under_s1_2024_period_mix = 2
listing_gap_reject = 6
viable_micro_cohort_size = 2   # 不足以支撑有意义的 next-scale / live 片
```

Runner 现状：`validate_erad_next_scale_slice2_universe_csv_path` **硬绑定** S1 +100 CSV；AD2E601+ 需新 universe 路径 / 模式接线，不在已消耗的 S1 执行包内「顺手」可做。

```text
queue_depth: 0
lifecycle: IDLE_NO_TASK
stop_reason: NO_SAFE_AUTONOMOUS_TASK
authorized_scope_exhausted: erad_a_scale_500_slice2 (S1 AD2E501-600)
next_scale_blockers: residual_non_st_pool_exhausted_after_listing_filter | fuller_denominator_scope_missing
```

## 3. 与治理状态对齐

- `PROJECT_CONTROL.md` A 线：`next_allowed_task` 仍写 post-integration HOLD（slice1）；`blocked_actions` 仅放行已授权 **`erad_a_scale_500_slice2`**（Run 10）— 该 scope 的 S1 执行链已收口。
- Cohort freeze §7：+8 / +108 扩批 **须新任务** · case_id 自 AD2E601 起 — 且未冻结 listing-aware period 策略。
- A-R16-03 已交付 builder 硬拒能力；**缺少**可过滤后仍达规模的下一候选池，故 hint 无法在本轮转化为高价值执行。

## 4. 仍存在但不构成可派发任务的事实缺口

| 缺口 | 分类 | 为何不派发 |
|------|------|------------|
| 889 池非 ST 仅剩 2 个 2024-期窗可行码 | pool exhausted | 微片 ROI≈0；非 next-scale |
| 6 个 2025/2026 IPO 余量 | period-policy unset | 需 Controller 裁定是否改 expected_period 规则 |
| full_market_2024 分母 / A 新 remainder | scope_missing | 须人类授权「A 超出 889 池 / slice2 S1」方向 |
| S1 closure_gate candidate → formal | controller | executor 不升级 gate |
| Attribute completeness UNKNOWN | rubric unset | 无冻结评分则易成台账 busywork |
| 182 A∩B 治理 O3 PENDING_CONTROLLER | controller | 跨轨决策，非本 executor |

## 5. 未触碰

- 封闭 S1 live 根 / raw_metadata / live report
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（本轮无改）
- B/C/D 文件与 harvest/snapshot 生产根
- CNINFO live · PDF · DB · MinIO · RAG
- commit / push · verified / production_ready 声称

## 6. 建议 Controller

1. 保持 A 线 **IDLE_NO_TASK**，直至出现明确新 scope，优先其一：
   - **(a)** 授权 A 类基于 `eval_companies_full_market_2024.yaml`（或等价分母）的下一 coverage 片，并冻结选取/overlap/listing_period 规则；或
   - **(b)** 授权 listing-aware period 策略（允许对 IPO 余量使用 ≥ listing_date 的报告期）后再开 AD2E601+ 小片；或
   - **(c)** 明确改写 ST 策略（与 S1 freeze 冲突时须显式废止）。
2. 本文件仅作拒绝审计；**不要**当作 commit 候选。

## Gate

```
a_class_r16_04_next_task_search_gate = IDLE_NO_TASK
cninfo_calls = 0
live = no
ready_for_commit = false
```
