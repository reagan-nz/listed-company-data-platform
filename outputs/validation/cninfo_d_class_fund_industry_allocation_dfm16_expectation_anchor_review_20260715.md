# CNINFO D 类 fund_industry_allocation — D-FM-16 Expectation / Anchor Offline Review

_生成时间：2026-07-15 · D-FM-16 · wall≈短（纯离线）_

> **性质：** DFIA001 / DFIA005 期望与锚点离线复核 · **CNINFO = 0** · **无 live** · **无 universe lock mutate** · **无 commit/push**
>
> **NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-16** |
| track | D · d-class-executor |
| phase | `fund_industry_allocation_dfia001_dfia005_expectation_anchor_offline_review` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false** |
| prefer taken | FIA DFIA001/DFIA005 expectation/anchor offline review（高于 re-live SD/AT / Level-2 IDLE） |
| commit/push | **禁止** |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| CNINFO live | **0**（本任务） |
| universe lock mutate | **no** |
| FIA / SD / AT re-live | **no** |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |
| Level-2 IDLE | **否** |

Universe lock sha256（复核前后一致 · 未修改）:

```text
048799c7279f3c2ce0d3392a5404ef8f3e0e9532ed59d7bdaa7b31b910f3e8ee
```

## Inputs（只读）

| 输入 | 路径 |
|------|------|
| universe lock | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv` |
| D-FM-13 live evidence | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm13_bounded_live_20260715.md` |
| live / quality reports | `.../first_slice/reports/d_class_fund_industry_allocation_first_slice_{live,quality}_report.csv` |
| live snapshots | `.../live_snapshots/DFIA00{1-5}_fund_industry_allocation.json` |
| Tier-0 cite | `fixtures/d_class/fund_industry_allocation/sample_raw.json` |
| VR | `outputs/validation/cninfo_d_class_fund_industry_allocation_validation_rules_20260715.md`（VR-010/012/014） |
| Phase2 planning | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_component_planning_summary_20260715.md` |

## D-FM-13 Caveat Recap（不重跑）

| case_id | expected | retrieval | records | acceptable | failure_type |
|---------|----------|-----------|--------:|:----------:|--------------|
| DFIA001 | captured_normal | empty_but_valid | 0 | no | expectation_mismatch |
| DFIA002 | captured_normal | found | 16 | yes | — |
| DFIA003 | captured_normal | found | 19 | yes | — |
| DFIA004 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DFIA005 | empty_but_valid | http_error | 0 | no | transport_or_http_error |

execution_gate 仍为 `PASS_WITH_CAVEAT`（3/5）· live_gate=`NOT_APPROVED`。

---

## DFIA001 — Expectation Review

### Lock / Tier-0 basis

- lock：`industry_code=C26` · `query_mode=default` · `expected_behavior=captured_normal`
- Tier-0 `sample_raw.json`：单行 C26 · **ENDDATE=2026-03-31**（骨架 cite · 非「default 滚动截面必含 C26」证明）
- fixture `DFIA001_found.json`：合成 captured 路径 · 同 ENDDATE=2026-03-31

### Live evidence（D-FM-13）

- 共享探针 `default`：全截面 **16** 行 · sample `ENDDATE=2026-06-30` · F001V 样本为粗粒度 **A / B / C**（制造业聚合）等
- 离线 F001V=`C26` 过滤后 **0** 行 → 合法 `empty_but_valid`（VR-010）
- 同探针下 DFIA002 `found` 证明 transport/payload 正常；失败点在 **期望过严**，非 endpoint 失效
- 对照 DFIA004：同 C26 过滤 · 已用 `captured_normal_or_empty_but_valid` · live empty **acceptable=yes**

### Classification

```text
DFIA001_review = expectation_too_strict
anchor_industry_code_C26 = KEEP
query_mode_default = KEEP
recommended_future_expected = captured_normal_or_empty_but_valid
lock_mutate_this_task = no
```

### Offline counterfactual（CNINFO=0）

对 D-FM-13 既有 retrieval 摘要，调用 `is_fund_industry_allocation_first_slice_acceptable`：

| 场景 | DFIA001 expected | DFIA001 acceptable | slice acceptable |
|------|------------------|:------------------:|:----------------:|
| 当前 lock | `captured_normal` | no | **3/5** |
| 建议（未来 amend） | `captured_normal_or_empty_but_valid` | yes | **4/5**（DFIA005 transport 仍 no） |

---

## DFIA005 — Anchor / Expectation Review

### Lock / Phase2 basis

- lock：`anchor_rdate=20251231` · `expected_behavior=empty_but_valid`
- Phase2 precedent：`fia_rdate_20251231` · **records=0** · empty_but_valid control（planning summary）
- VR-014 / VR-027：DFIA005 期望 empty_but_valid · 不 forced pass

### Live evidence（D-FM-13）

- 共享探针 `rdate_20251231`：**Read timeout(10s)** → `http_error` / `transport_or_http_error`
- **未**观察到非空截面；**无法**用本 live 证伪 empty 锚点
- failure_type ≠ `expectation_mismatch` → 属传输层，非期望/锚点错误

### Classification

```text
DFIA005_review = transport_not_expectation
anchor_rdate_20251231 = KEEP
expected_behavior_empty_but_valid = KEEP
lock_mutate_this_task = no
optional_future = bounded_single_probe_retry_rdate_20251231_only_if_authorized
unbounded_FIA_relive = forbidden
```

### Offline counterfactual（CNINFO=0）

若同锚点未来返回 `empty_but_valid` / records=0 → 在当前 expected 下 **acceptable=yes**（锚点+期望自洽）。

---

## Explicit Non-Actions（本任务）

- **不** mutate universe lock / 不改 DFIA001–DFIA005 行
- **不** 无界重跑 FIA live · **不** re-live SD/AT
- **不** reopen DLC006R / 301259 / 688671
- **不** Level-2 IDLE · **不** 触碰 A/B/C
- **不** 将 industry aggregate 写入 company event/metric schema
- **不** 本任务 commit / push
- **不** 本任务修改 runner 判定逻辑（见观察项）

## Runner Observation（记录 · 不修）

`is_fund_industry_allocation_first_slice_acceptable` 末尾对 `rs=found` 有宽泛放行；若 DFIA005 未来返回非空，`empty_but_valid` 期望可能仍被判 acceptable。属 **另批 runner tighten** 候选 · **本任务不改代码**。

## Artifacts

| artifact | path |
|----------|------|
| this review | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm16_expectation_anchor_review_20260715.md` |
| matrix | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm16_expectation_anchor_matrix_20260715.csv` |
| next-step | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_next_step_recommendation_20260715.md` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_fund_industry_allocation_first_slice_runner.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_fund_industry_allocation_fixtures.py` | **14/15 PASS** · 1 skipped（jsonschema 不可用） |
| `lab/test_cninfo_d_class_fund_industry_allocation_offline_prep.py` | **5/6 PASS** · 1 skipped（jsonschema 不可用） |
| aggregate | **34 ran + 2 skipped · OK** · CNINFO=0 |

## Gates

```text
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_execution_gate = PASS_WITH_CAVEAT
d_class_fund_industry_allocation_dfm16_expectation_anchor_review_gate = PASS_OFFLINE
```

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-16 FIA 期望/锚点离线复核包）· executor **不** commit/push。

Secondary（另批 · 择一）：

1. **DFIA001 lock amend**（仅 `expected_behavior` → `captured_normal_or_empty_but_valid` · 保持 C26/default）+ 同步 VR/notes · **仍不**无界重跑 live
2. **DFIA005** 授权下单探针 bounded retry（仅 `rdate=20251231` · CNINFO≤1）· 验证 empty 锚点
3. next capital **discovery** offline planning（registry 已切片组件不重开；禁 Level-2 IDLE）

## Status Block

```text
task_id = D-FM-16
phase = fund_industry_allocation_dfia001_dfia005_expectation_anchor_offline_review
cninfo_calls = 0
live = NOT_RUN
universe_lock_mutated = false
dfia001_review = expectation_too_strict
dfia005_review = transport_not_expectation
review_gate = PASS_OFFLINE
ready_for_commit = true
```
