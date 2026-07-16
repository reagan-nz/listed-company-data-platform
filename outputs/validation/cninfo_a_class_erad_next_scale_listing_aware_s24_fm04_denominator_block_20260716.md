# A-FM-04 — R19 excellence ladder：S24 listing-aware ~1000 **BLOCKED**

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-04 · R19 excellence-gated scale_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **本包：** overlay refresh **CNINFO=0** · **未** dry-run S24 live · **未** bounded live · **未 mutate S1–S23 live 主根** · **无 commit/push**  
> **Prior：** A-FM-03 S23 **200/200** EXCELLENT → ladder 升至 ~1000（禁止再无尽 +50 / 勿重复 +200）

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-04** |
| track | A |
| R19 ladder | ~50（S22）→ ~200（S23 EXCELLENT）→ **~1000（本包目标）** |
| 目标 | 新孤立根 S24 · AD2E1851–2850 · builder+runner · dry-run · bounded live · excellence≥95% |
| 保护 | **禁止** mutate S1–S23 live 主根；无 B/C/D；无 commit/push |

## 2. Result

| 项 | 值 |
|----|-----|
| **PASS/FAIL** | **FAIL**（`DENOMINATOR_BLOCKED`） |
| size | **n/a**（universe 未生成；不可达 1000） |
| accuracy / excellence | **n/a**（live 未执行） |
| CNINFO | **0**（仅 overlay refresh + capacity probe） |
| live executed | **no** |
| S1–S23 live 主根 mutated | **no** |

## 3. Verified metrics（offline · CNINFO=0）

| 指标 | 值 |
|------|-----|
| overlay union（refresh 后） | **2213** |
| overlay with listing_date | **2207** |
| canon / latent-only | **863** / **1350** |
| A cumulative exclude（含 S23） | **1850** unique codes |
| profile_candidates after exclude/ST/BSE | **429** |
| **max selectable residual**（prefix cap=1000） | **371** |
| S24 target | **1000** |
| **shortfall** | **629** |
| latent dirs exhausted | phase35 / phase35_resume / phase2_smoke_200 / fuller_slice1_200 / phase3_batch_500_001 **均已在 overlay** |
| raw∉overlay 且 remap 可得 listing_date | **0** |
| full_market_2024 缺 profile | **3911**（无离线 listing_date 源可补） |

Probe 工件（排除 commit）：`outputs/validation/_tmp_s24_denominator_probe_20260716.json`

## 4. Why live was not started

Listing-aware S24 硬依赖 `company_basic_profile`∪`listing_date` 分母。  
当前离线并集在 a_exclude=1850 后最多只能选出 **371** 码，无法形成 AD2E1851–2850（1000）universe，亦无法声称 excellence≥95% @1000。

禁止项（本包遵守）：

- 伪造 listing_date / 用 establishment_date 冒充
- 放宽 `listing_period_gate` 以凑数
- 复用 S1–S23 已占用码
- 为扩分母擅自对 C harvest 根写盘或跨轨 live
- mutate S1–S23 live 主根

## 5. Files

### Touched（overlay refresh only · CNINFO=0）

- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`（symlink 重建 · union 仍 2213）
- `outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv`
- `outputs/validation/cninfo_a_class_basic_profile_coverage_fm06_20260715.md`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_fm04_denominator_block_20260716.md`（本报告）
- `outputs/validation/_tmp_s24_denominator_probe_20260716.json`（probe · **勿 commit**）

### Not created（被挡）

- S24 universe / reject ledger / runner mode / isolated live root / dry-run+live reports

### Not touched（保护）

- S1–S23 **live** 主报告与输出根
- B/C/D · commit/push

## 6. Allow-list（ready_for_commit）— 可选证据包

Track-A only（排除 console / raw_metadata / `_tmp_*`）：

1. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_fm04_denominator_block_20260716.md`
2. （可选）overlay matrix + summary 若 Controller 要记录 refresh 无增量

**建议 commit message（若 Controller 收证据）：**

```text
docs(a-class): record S24 ~1000 denominator block after S23 excellence

Offline overlay refresh stays at 2213 profiles; residual listing-aware
capacity is 371 vs target 1000. No live; S1–S23 roots untouched.
```

## 7. Gate

```text
a_class_fm04_listing_aware_s24_gate = FAIL_DENOMINATOR_BLOCKED
excellence = n/a
cninfo_calls = 0
max_residual_selectable = 371
target = 1000
s1_s23_live_main_roots_mutated = no
ready_for_commit = evidence_only_optional
commit = not_done
push = not_done
```

## 8. Issues requiring Controller

**Decision question：** S24 ~1000 在 listing-aware 硬门下被离线分母挡住；如何解封？

**Options（最多 2）：**

1. **Preferred — component/profile harvest 扩分母（再开 S24）**  
   由 C-class（或显式授权的 A profile 采集）对 full_market 缺口码补 `company_basic_profile`（含 F006D/listing_date），落盘后 A 仅 symlink overlay（overlay 构建仍 CNINFO=0）。目标：overlay with listing_date 至少支撑 a_exclude+1000（约 ≥2850+余量）。

2. **Defer / redesign（需显式批准）**  
   批准非 listing-aware 选取规则或替代 listing_date 权威源（不得伪造）。在批准前 **不得** live。

**Controller recommendation：** 选 **1**。在分母未达 ≥1000 可选余量前，**不要**派发 S24 live。

## 9. Next recommendation（A-class）

```text
BLOCKED_ON = profile/listing_date denominator
next = component/profile work（扩 basic_profile∪listing_date 离线并集）
then = rebuild overlay (CNINFO=0) → S24 universe AD2E1851–2850
      → dry-run → bounded live → excellence≥95%
do_not = mutate S1–S23 live roots; no endless +50/+200; no B/C/D; no push
```
