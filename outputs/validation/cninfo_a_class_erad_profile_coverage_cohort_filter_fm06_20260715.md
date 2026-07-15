# A-FM-06 — Profile coverage overlay + prefix cohort filter + S7 universe（offline）

_生成时间：2026-07-15 · track A · executor a-class-executor · task_id A-FM-06_

> **standing_scope：** full-market periodic / metadata scale  
> **本 turn：** **offline only** · **CNINFO = 0** · **无 live** · **无 commit/push** · **无 B/C/D**  
> **未 mutate 封闭 S1–S6 live 权威报告**（mtime 核验通过）  
> **不**把 S6 旁路 retry / 合并后 50/50 抬升为本包 PASS；S6 包装门禁仍以 A-FM-05 诚实记录为准

## 1. Task chosen

| 项 | 值 |
|----|-----|
| horizon | **2** next cohort 防护 + **3** profile 分母扩展 |
| 本 turn 动作 | 扩大 basic_profile 可用分母（A 轨 overlay）+ 前缀浓度门禁 + 生成 S7（AD2E851–900）universe |
| 为何不是 bounded timeout retry | S6 首轮 18×`network_timeout` 在独立 retry 根已 18/18 恢复；点名黑名单无判别力（同板同 orgId 覆盖）；更高价值是避免下一片再 mono-prefix 批爆 |
| 为何不是 IDLE | A-FM-05 next_hint 明确要求 profile/cohort filter；standing authorization 覆盖下一 cohort 准备 |

## 2. Evidence from S6 first-pass（只读）

| 指标 | 值 |
|------|-----|
| first-pass acceptable | **32/50** |
| first-pass failures | **18/50** 全为 `network_timeout` |
| failure prefix | **301×18**（但整片亦为 301×50 → **非点名缺陷**） |
| board / org_id 判别 | fail vs pass **无稳定字段差** |
| 分类 | `session_burst_network_timeout_not_name_defect` |
| 台账 | `outputs/validation/cninfo_a_class_erad_s6_first_pass_timeout_ledger_20260715.csv` |

结论：不永久拉黑这 18 码；改为 **prefix_concentration_cap** + **扩大分母多样性**。

## 3. Cohort / coverage rules（本包冻结）

1. Overlay：`canonical normalized/company_basic_profile` ∪ 只读 latent harvest batches（canon 优先）
2. Overlay 落在 A 轨 `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（symlink · **不写** C harvest）
3. S7 exclude：A cumulative 含 listing-aware **S2–S6**
4. ST-EXCLUDE · 非 BSE · `listing_period_gate` 硬拒
5. **prefix_concentration**：本片同一 3 位前缀最多 **25**
6. case_id：**AD2E851–AD2E900** · cohort=`next_scale_listing_aware`

## 4. Files

### Created
- `lab/cninfo_a_class_profile_coverage.py`
- `lab/test_cninfo_a_class_profile_coverage.py`
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（1726 symlinks）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv`
- `outputs/validation/cninfo_a_class_basic_profile_coverage_fm06_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_plus50_universe_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_reject_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_s6_first_pass_timeout_ledger_20260715.csv`
- `outputs/validation/cninfo_a_class_erad_profile_coverage_cohort_filter_fm06_20260715.md`（本报告）

### Modified
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（prefix cap · S7 · 默认 slice=s7）
- `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`（prefix + S7 用例）

### Not touched（保护）
- 封闭 S1–S6 **live** summary / report（mtime 核验）
- C-class harvest 根
- B/C/D 生产根 · commit/push

## 5. Verified metrics

| 指标 | 值 |
|------|-----|
| canon profiles | **863** |
| latent-only added | **863** |
| overlay union | **1726** |
| S7 universe size | **50**（AD2E851–900） |
| S7 prefix mix | **000×25 · 001×5 · 002×20**（无 mono-301） |
| S7 reject ledger（扫描至填满） | **183**（a_cumulative_exclude=104 · prefix_concentration_exclude=62 · st_exclude=10 · listing_period_gate=7） |
| S7 profile_candidates | **57** |
| CNINFO calls（本 turn） | **0** |
| closed S1–S6 live mutated | **no** |
| execution gate（本包） | **`PASS_OFFLINE`**（能力/宇宙准备；**不是** live PASS） |

## 6. Tests / wall times（CNINFO=0）

| 步骤 | 结果 | wall |
|------|------|------|
| `test_cninfo_a_class_profile_coverage.py` | 3/3 OK | ~0.12s |
| `test_cninfo_a_class_listing_aware_cohort_builder.py` | 10/10 OK | ~0.13s |
| `test_cninfo_a_class_listing_period_gate.py` | 8/8 OK | ~0.07s |
| `test_cninfo_a_class_erad_listing_aware_s6_runner.py` | 5/5 OK | ~0.23s |
| `cninfo_a_class_profile_coverage.py` | union=1726 | ~0.81s |
| `cninfo_a_class_listing_aware_cohort_builder.py --slice s7` | 50/50 | ~2.32s |

## 7. Allow-list（ready_for_commit）

1. `lab/cninfo_a_class_profile_coverage.py`
2. `lab/test_cninfo_a_class_profile_coverage.py`
3. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`
6. `outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv`
7. `outputs/validation/cninfo_a_class_basic_profile_coverage_fm06_20260715.md`
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_plus50_universe_20260715.csv`
9. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s7_reject_ledger_20260715.csv`
10. `outputs/validation/cninfo_a_class_erad_s6_first_pass_timeout_ledger_20260715.csv`
11. `outputs/validation/cninfo_a_class_erad_profile_coverage_cohort_filter_fm06_20260715.md`

**Exclude：** 封闭 S1–S6 live 根；C harvest；B/C/D 脏文件；未请求的 commit/push；S6 runner live 重跑。

## 8. capability_gain

```text
capability_gain = true
- A-local basic_profile overlay doubles usable denominator (863 → 1726) without CNINFO / without mutating C harvest
- listing-aware cohort builder gains prefix_concentration_exclude (S7 default max_same_prefix=25)
- S7 universe AD2E851–900 generated offline with diversified prefixes (000/001/002)
- S6 first-pass timeout ledger filed as session-burst evidence (not permanent blacklist)
- closed S1–S6 live authority untouched
```

## 9. Gate

```text
a_class_fm06_profile_coverage_cohort_filter_gate = PASS_OFFLINE
cninfo_calls = 0
live = no
ready_for_commit = yes
push = no
```

**不是 PASS（live）** · **不是 PASS_WITH_CAVEAT（live）** · **不是 verified** · **不是 production_ready**

## 10. Next hint

```text
next_hint = wire listing-aware S7 into phase2 runner（独立输出根 · 禁止写 S1–S6 live）后 dry-run；
            live 须新批准；勿 mutate S1–S6；commit 仅 allow-list；勿 push。
```
