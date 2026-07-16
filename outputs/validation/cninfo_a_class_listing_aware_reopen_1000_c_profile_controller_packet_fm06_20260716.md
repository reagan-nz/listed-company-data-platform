# Controller packet — C-class basic_profile harvest 前置条件（A reopen listing-aware ~1000）

_track A · task A-FM-06 · 2026-07-16 · CNINFO=0 · 只读规格包 · 不指令 C 执行_

## Review question

在 overlay 并集仍为 **2213**、listing-aware 诚实 scale 残差已耗尽（S24=371 live；post-S24 micro=2）的前提下，C-class 需要交付什么，A 才能 reopen listing-aware **~1000**？

## Track and stage

- Track: **A**（消费方） / **C**（profile 生产方）
- Stage: **denominator unblock** before any S25 / ~1000 listing-aware live

## Verified metrics（A-FM-06 offline probe）

| 指标 | 值 |
|------|-----|
| overlay union | **2213** |
| with usable listing_date | **2207** |
| A cumulative exclude（含 S24） | **2221** codes |
| post-S24 selectable residual | **2**（micro；非 scale） |
| full_market_2024 codes | **6124** |
| missing profile vs full_market | **3911** |
| reopen gate | `selectable_residual >= 1000` |
| shortfall vs gate | **998**（相对 micro=2）或实质需 **≥1000 新可选码** |
| CNINFO（本包） | **0** |

## What C must supply（exact）

### 1. Artifact shape

每个缺口码一份 normalized `company_basic_profile` JSON，路径形态：

```text
outputs/harvest/cninfo_c_class/<batch_id>/normalized/company_basic_profile/{code}.json
```

或并入 canonical：

```text
outputs/harvest/cninfo_c_class/normalized/company_basic_profile/{code}.json
```

A 只做 **symlink overlay**（`lab/cninfo_a_class_profile_coverage.py`），**不**写 C harvest 根，**不**伪造日期。

### 2. Required fields（A listing_period_gate 可读）

A 门禁提取顺序（`lab/cninfo_a_class_listing_period_gate.py`）：

1. 顶层 **`listing_date`**（ISO `YYYY-MM-DD`）— **首选**
2. 回退：`raw_record_json.basicInformation[0].F006D`（同格式）

同时建议保留（universe / 审计用，非 gate 硬依赖）：

- `company_code`（6 位）
- `company_name` / `legal_name`
- `org_id`（若已有）
- `raw_record_json` 完整落盘（可追溯）

**禁止：** 用 `establishment_date` 冒充 `listing_date`；空日期伪成功；A 侧手写日期。

### 3. Target universe for harvest

只读候选表（A 已导出）：

```text
outputs/validation/cninfo_a_class_listing_aware_fm06_missing_profile_vs_full_market_20260716.csv
```

- 行数：**3911**
- 含义：`lab/eval_companies_full_market_2024.yaml` 有名，但当前 A overlay 无 profile
- C 不需一次 harvest 全部 3911；但必须使 A 重建 overlay 后 **可选残差 ≥1000**

### 4. Volume gate（硬门槛）

C 交付并经 A 离线验证后：

```text
build_listing_aware_cohort(
  target_size=1000,
  case_id_start=2222,   # 或 Controller 指定的下一窗
  a_exclude = scale200 ∪ slice1 ∪ slice2_s1 ∪ listing_aware_S2..S24,
  profile_dir = refreshed overlay,
  max_same_prefix = <Controller 指定；不得为凑数而放宽 listing_period_gate>
)
→ selected == 1000
→ else DENOMINATOR_BLOCKED
```

等价表述：

```text
residual_after_S24_exclude >= 1000
```

micro residual=2 **不满足**该 gate。

### 5. A-side consume path（C 完成后）

1. C 落盘 profiles（C 轨任务；本包不执行）
2. A：`python lab/cninfo_a_class_profile_coverage.py`（CNINFO=0）刷新  
   `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`
3. A：offline builder dry-run 证明 `target_size=1000` 不 undersize
4. 仅当 #3 PASS → 才允许讨论 S25 / ~1000 listing-aware live  
5. **仍禁止** mutate S1–S24 live 主根

## Relevant files only

- `lab/cninfo_a_class_listing_period_gate.py`
- `lab/cninfo_a_class_profile_coverage.py`
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`
- `outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06/`
- `outputs/validation/cninfo_a_class_listing_aware_fm06_missing_profile_vs_full_market_20260716.csv`
- `outputs/validation/cninfo_a_class_listing_aware_s24_fm06_overlay_residual_probe_20260716.json`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s24_residual371_universe_20260716.csv`
- `lab/eval_companies_full_market_2024.yaml`

## Unverified / out of scope

- C 实际 harvest 批次大小、节奏、CNINFO 预算（属 C / Controller）
- 3911 中有多少码最终有非空 listing_date（须 C 落盘后由 A 再探）
- 是否改用非 listing-aware 的 A offline 轴（备选，见下）

## Options（最多 2）

1. **Preferred — 派 C-class basic_profile harvest**  
   对缺口表补 profile（含可用 `listing_date`/`F006D`）→ A overlay rebuild → residual≥1000 gate → 再谈 S25/~1000。

2. **Alternate — 关闭 listing-aware scale ladder / 换 A offline 轴**  
   承认当前分母下无法诚实 ~1000；A 转其他 standing metadata 离线任务；勿伪扩 cohort。

## Controller recommendation

选 **1** 若仍要 excellence@1000 listing-aware；否则选 **2**。  
**不要**在 residual < 1000 时授权 A 开 S25/~1000 live。

## Requested output

`APPROVE` / `APPROVE_WITH_CONDITIONS` / `REJECT_AND_REPLAN` / `NEED_MORE_EVIDENCE` / `HUMAN_DECISION_REQUIRED`

## Maximum review scope

- 勿巡检无关 B/D 轨
- 勿修改文件
- 勿执行命令 / live / CNINFO
