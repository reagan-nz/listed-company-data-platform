# CNINFO A 类 Next-Scale Slice2 S1 +100 — Runner Extension Design

_生成时间：2026-07-14_

> **性质：** Era D A-class slice2 S1 runner extension **设计包 only** · **CNINFO = 0** · **NOT IMPLEMENTED** · **NOT APPROVED live** · **NOT APPROVED runner execution** · **HOLD preserved** · **NOT verified** · **NOT production_ready**

**任务 ID：** **A-GEN-20260714-11**

**前置证据：**
- [cohort freeze note](cninfo_a_class_erad_next_scale_slice2_s1_cohort_freeze_note_20260714.md)（A-GEN-20260714-09）
- [S1 +100 lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md) — 综合 **PASS** · L-D4 ST=**0**
- [live prep package](cninfo_a_class_erad_next_scale_slice2_s1_live_prep_package_20260714.md)（A-GEN-20260714-10）
- [command draft](cninfo_a_class_erad_next_scale_slice2_s1_command_draft_20260714.md)
- [live precheck checklist](cninfo_a_class_erad_next_scale_slice2_s1_live_precheck_20260714.csv)

**模式参照：**
- [slice1 runner extension summary](cninfo_a_class_erad_next_scale_slice1_runner_extension_summary.md) — `--erad-a-scale-500-slice1` · 17/17 tests PASS
- [B fuller slice2 runner extension summary](cninfo_b_class_erad_fuller_next_slice2_runner_extension_summary.md) — `--erad-b-fuller-slice2` · 16/16 tests PASS

---

## 1. Executive Summary

| 项 | 值 |
|----|-----|
| 阻塞项（A-10） | `--erad-a-scale-500-slice2` **未实现** |
| 本包交付 | runner extension **设计** + implementation checklist |
| cohort | `next_scale_slice2` · **S1 +100 non-ST** |
| universe | [s1_plus100 candidate](cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv)（**100** rows） |
| case_id | **AD2E501** – **AD2E600** |
| company_code | `603701` – `688772` |
| output root | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/` |
| request cap | 点估计 **~210** · 硬 cap **≤240** |
| acceptance（future live） | **≥90/100** → `PASS_WITH_CAVEAT` |
| CNINFO（本包） | **0** |
| gate（本包） | `a_class_erad_next_scale_slice2_s1_runner_extension_gate = DESIGN_ONLY` |

---

## 2. Proposed Flags

| Flag | dest | 说明 | 状态 |
|------|------|------|------|
| `--erad-a-scale-500-slice2` | `erad_a_scale_500_slice2` | slice2 S1 +100 主模式 | **设计 · 未实现** |
| `--approve-a-class-erad-scale-500-slice2` | `approve_a_class_erad_scale_500_slice2` | live 人批 gate（dry-run 不需要） | **设计 · 未实现** |
| `--universe-csv` | `universe_csv` | 指向 S1 +100 freeze universe | 复用现有 arg |
| `--output-root` | `output_root` | 隔离 slice2 S1 根 | 复用现有 arg |
| `--case-range AD2E501:AD2E600` | `case_range` | session 切分（推荐 2×50） | 复用 slice1 形状 |
| `--dry-run` | `mode=dry_run` | 规划模式 · CNINFO **0** | 复用现有 arg |
| `--live` | `mode=live` | live 模式（**须 separate approval**） | 复用现有 arg |

**模式互斥（须 enforce，同 slice1）：**

```
--erad-a-scale-500-slice2 不可与以下并存：
  --erad-a-scale-200
  --erad-a-scale-200-failed-retry
  --erad-a-scale-500-slice1
  --phase3-50 / retry / precheck 等其他模式
```

**错误码（规划命名，对齐 slice1 风格）：**

| 常量 | 值 |
|------|-----|
| `ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED` | `erad_a_scale_500_slice2_universe_csv_required` |
| `ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION` | `output_root_must_be_under_cninfo_a_class_erad_next_scale_slice2_s1` |
| `ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION` | `erad_a_next_scale_slice2_universe_size_must_equal_100` |
| `ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED` | `approve_a_class_erad_scale_500_slice2_required` |
| `ERAD_NEXT_SCALE_SLICE2_INCOMPATIBLE_WITH_OTHER_MODES` | `erad_a_scale_500_slice2_incompatible_with_other_modes` |
| `ERAD_SLICE2_REQUEST_CAP_EXCEEDED` | `erad_a_next_scale_slice2_request_cap_exceeded` |
| `ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN` | `erad_a_slice2_slice1_root_write_forbidden` |

---

## 3. Universe CSV（S1 +100 · Frozen）

**Canonical path：**

```text
outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv
```

**Schema（冻结 · 4 列）：**

| 列 | 说明 |
|----|------|
| `company_code` | 主键 · 100 唯一 |
| `company_name` | 显示名 |
| `case_id` | AD2E501–AD2E600 连续 |
| `cohort` | 固定 `next_scale_slice2` |

**Runner load 设计（实现任务）：**

1. 接受上述 4 列 CSV（与 freeze note 一致 · **不 mutate 源文件**）
2. 在 load 时派生 slice1 同型运行字段（参照 `load_erad_next_scale_slice1_universe`）：
   - `market` ← `_market_label_from_code(company_code)`
   - `report_type` / `expected_period` / title keywords ← `_derive_a_slice2_report_fields(case_num)`（case_num 501–600 · mod-10 比例同 slice1）
   - `prior_in_scale_200` = `no`
   - `erad_include` = `yes`
   - `include_reason` = `next_scale_slice2_s1_st_exclude;zero_prior_overlap;metadata_only_no_pdf`
3. `company_name` 以 CSV 列为准（freeze 已含中文名）

**校验常量（规划）：**

| 常量 | 值 |
|------|-----|
| `REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE` | **100** |
| `ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS` | AD2E501–AD2E600 |
| `ERAD_NEXT_SCALE_SLICE2_COHORT` | `next_scale_slice2` |
| `ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE` | **2** |
| `ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP` | **240** |
| `ERAD_SLICE2_ACCEPTABLE_THRESHOLD` | **90** |
| `ERAD_SLICE2_EXECUTION_GATE_PASS` | `PASS_WITH_CAVEAT` |

---

## 4. Isolated Output Root

**默认根（规划 · 本任务不创建）：**

```text
outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/
├── reports/
│   ├── session1/          # AD2E501–550（若分 session）
│   ├── session2/          # AD2E551–600
│   ├── a_class_erad_next_scale_slice2_s1_dryrun_report.csv
│   ├── a_class_erad_next_scale_slice2_s1_dryrun_summary.md
│   ├── a_class_erad_next_scale_slice2_s1_live_report.csv
│   ├── a_class_erad_next_scale_slice2_s1_live_quality_report.csv
│   └── a_class_erad_next_scale_slice2_s1_live_summary.md
├── raw_metadata/          # bulk · local-only · not in git
└── ledgers/
    └── a_class_erad_next_scale_slice2_s1_unresolved_ledger.csv
```

**Mock 测试子目录（同 slice1 模式）：**

```text
.../cninfo_a_class_erad_next_scale_slice2_s1/_mock_test/
.../cninfo_a_class_erad_next_scale_slice2_s1/_mock_live_test/
```

**`validate_erad_next_scale_slice2_output_root` 规则：**

- 允许：canonical root 及其 `_mock_*` 子目录
- 拒绝：任何其他路径 → `ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION`

---

## 5. Write-Blocks vs Slice1

### 5.1 Slice2 新增写保护（相对 slice1）

| 禁止写入 | 错误码 / 原因 |
|----------|---------------|
| `cninfo_a_class_erad_next_scale_slice1/` | **`ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN`** — slice1 主根 294/300 effective · merge closure 已收口 |
| slice1 `reports/` · `quality/` · session 子目录 | 同上 · 不得 overwrite live 产物 |

**说明：** slice1 runner 已 block scale-200 / failed_retry / phase3 / a3m017；slice2 runner **须继承全部 slice1 write-block 并追加 slice1 主根 block**。

### 5.2 共有写保护（slice1 + slice2 一致）

| 禁止写入 | 原因 |
|----------|------|
| `cninfo_a_class_erad_scale_200/` | scale-200 生产根 |
| `cninfo_a_class_erad_scale_200_failed_retry/` | failed-retry 根 |
| Phase 3 / A3M017 production roots | 跨阶段隔离 |
| Phase 1/2/retry/precheck baseline | 历史基线 |
| [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) | **禁止 mutate** |
| [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv) | **禁止 mutate** |
| 旧 S4 +100 / +50 superseded draft CSV | **禁止 mutate** |
| B / C / D validation / harvest / snapshot production roots | 跨轨隔离 |

### 5.3 Slice1 未 block 但 slice2 亦不得写入

| 路径 | 政策 |
|------|------|
| `cninfo_a_class_erad_next_scale_slice2_s1/`（canonical） | 仅 slice2 runner 可写 · 其他模式拒绝 |
| superseded draft 路径 | 只读审计 |

---

## 6. Overlap Lint（Runner 阶段）

离线 lint 已在 [S1 +100 lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md) **PASS**；runner 实现须 **re-assert at dry-run**（同 slice1 `lint_erad_next_scale_slice1_overlap` 模式）。

**`lint_erad_next_scale_slice2_overlap` 对照集：**

| 规则 ID | 对照集 | 数据源（规划） | 期望 |
|---------|--------|----------------|------|
| L-A1 | A_ALL_U | scale-200 universe + slice1 universe | **0** |
| L-A2 | A_CUM_EFF | scale-200 effective + slice1 effective ledgers | **0** |
| L-A3 | A_S200_U | scale-200 universe CSV | **0** |
| L-A4 | A_S1_U | slice1 universe draft | **0** |
| L-B1 | B_CUM | B scale-200 + slice1 + fuller slice2 effective | **0** |
| L-B2 | B_S200_U | B scale-200 universe | **0** |
| L-B3 | B_S1_U | B slice1 universe | **0** |
| L-B4 | B_S2_U | B fuller slice2 universe | **0** |
| AB_182 | AB_182 ledger | `cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv` | **0** |
| L-D4 | ST 名称命中 | `/(?:\*?ST|S\*ST)/` on company_name | **0** |

**Lineage 政策：**

- AD2E001–500：**reference_only** · **not rerun**
- scale-200 unresolved **8** · slice1 unresolved **6**：**side-track only**
- slice2：**fresh_metadata only** for 100 new codes

---

## 7. CNINFO Cap Pointers（from Live-Prep · A-10）

引用 [live prep package §5](cninfo_a_class_erad_next_scale_slice2_s1_live_prep_package_20260714.md)：

| 组件 | 估算（100 cases） |
|------|-------------------|
| orgId / search primary | **100** |
| v2 rematch / expanded window | **~110** |
| **合计（点估计）** | **~210** |
| **合计（硬 cap）** | **≤240**（100 × 2.4） |

**Session / Daily Caps（future live）：**

| 层级 | 建议值 |
|------|--------|
| 单次 session cases | **≤50** 或 **≤100** |
| 推荐节奏 | **2×50**（AD2E501–550 · AD2E551–600） |
| 单日 cases 合计 | **≤100** |
| 单日 CNINFO 请求 | **≤240** |
| inter-request sleep | **≥1.0s** |
| inter-session gap | **≥4h** 或次日 |

**Dry-run 期望：**

- `planned_ok` = **100/100**
- `planned_request_count_total` ≈ **200**（100 × 2）
- cap check ≤ **240**
- CNINFO = **0**

---

## 8. Dry-Run Gate

**命令形状（NOT EXECUTED · 设计）：**

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --dry-run
```

**Dry-run 通过条件：**

| 检查 | 阈值 | gate |
|------|------|------|
| planned_ok | **100/100** | `READY_FOR_APPROVAL`（runner extension） |
| universe_issues | **0** | 同上 |
| overlap lint | L-A1..L-B4 + AB_182 全 0 | 同上 |
| L-D4 ST | **0**/100 | 同上 |
| planned_request_count_total | ≤ **240** | 同上 |
| CNINFO | **0** | 强制 |
| write-block 探针 | scale-200 / slice1 / failed_retry / phase3 根拒绝 | 测试覆盖 |

**Gate 流转（规划）：**

```text
DESIGN_ONLY（本包）
  → NOT_IMPLEMENTED（实现前）
  → READY_FOR_APPROVAL（dry-run 100/100 + tests PASS）
  → NOT_APPROVED live（须 separate live phrase）
```

---

## 9. Live Gate（NOT APPROVED · 设计 only）

**须全部满足前不得 `--live`：**

| # | 阻塞项 | 当前状态 |
|---|--------|----------|
| R1 | post-integration **HOLD** 解除 | **blocked** |
| R2 | runner extension 实现 + tests PASS | **blocked**（本设计包 · 未实现） |
| R3 | dry-run **100/100** `planned_ok` · CNINFO **0** | **blocked**（依赖 R2） |
| R4 | [precheck checklist](cninfo_a_class_erad_next_scale_slice2_s1_live_precheck_20260714.csv) 全 `ready` | **blocked** |
| R5 | human slice2 live 显式批准短语 | **blocked** |
| R6 | controller approval queue 含 slice2 live 条目 | **blocked** |
| R7 | O3 / 182 治理 Controller 终裁（若 live 前要求） | **PENDING_CONTROLLER** |

**示意批准短语（未消费）：**

```text
I approve A-class Era D next-scale slice2 S1 +100 live metadata validation.
```

**Live 命令形状（DO NOT RUN）：**

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --live
```

**验收（future）：** ≥**90/100** acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS** · **不是 verified** · **不是 production_ready**

---

## 10. Implementation Scope（Separate Task · 非本包）

**目标文件：** `lab/run_cninfo_a_class_phase2_metadata_expansion.py`

**最小实现清单（对齐 slice1 分支）：**

1. 常量块：`DEFAULT_ERAD_NEXT_SCALE_SLICE2_*` · `ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS` · cap/threshold
2. `EraDNextScaleSlice2UniverseCase` dataclass（或复用 slice1 结构 + cohort 校验）
3. `load_erad_next_scale_slice2_universe` · `_derive_a_slice2_report_fields`
4. `validate_erad_next_scale_slice2_*` 系列（case · size · csv path · output root · duplicate codes）
5. `lint_erad_next_scale_slice2_overlap`（§6 对照集）
6. `build_erad_next_scale_slice2_dryrun_row` · `process_erad_next_scale_slice2_dry_run`
7. `write_erad_next_scale_slice2_dryrun_report` · `write_erad_next_scale_slice2_dryrun_summary`
8. live path stub + mock live（CNINFO=0 · 同 slice1 `erad_a_next_scale_slice1_live_not_implemented` 模式或 mock-only）
9. argparse 注册 + `main()` 分支 + mode isolation
10. `enforce_erad_next_scale_slice2_request_cap`

**测试文件（规划）：**

| 文件 | 覆盖 |
|------|------|
| `lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py` | dry-run 100/100 · isolation · write-block · cap |
| `lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py` | approval gate · mock live · CNINFO=0 |

**回归：** slice1 tests **17/17** 须保持 PASS（不得破坏 `--erad-a-scale-500-slice1`）。

---

## 11. Gates（当前）

```text
a_class_erad_next_scale_slice2_s1_cohort_freeze_gate = FROZEN
a_class_erad_next_scale_slice2_s1_lint_gate = PASS
a_class_erad_next_scale_slice2_s1_live_prep_gate = READY_FOR_NEXT_STEP
a_class_erad_next_scale_slice2_s1_runner_extension_gate = DESIGN_ONLY
a_class_erad_next_scale_slice2_s1_dryrun_gate = NOT_APPLICABLE
a_class_erad_next_scale_slice2_s1_live_gate = NOT_APPROVED
a_class_erad_next_scale_slice2_s1_execution_gate = NOT_APPLICABLE
```

**强制语义：** `DESIGN_ONLY` ≠ implemented ≠ dryrun_complete ≠ live_approved ≠ verified ≠ production_ready。

---

## 12. Red Lines

- **不得** rerun AD2E001–500（lineage-reference only）
- **不得**写入 scale-200 · **slice1** · failed_retry · Phase 3 / A3M017 生产根
- **不得** mutate [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) · [remainder](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv) · superseded draft
- **无** PDF / DB / MinIO / RAG / verified 宣称
- **CNINFO = 0**（本设计任务）

---

## 13. Evidence Chain

- [S1 +100 candidate universe](cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv)
- [cohort freeze note](cninfo_a_class_erad_next_scale_slice2_s1_cohort_freeze_note_20260714.md)
- [S1 lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md)
- [live prep package](cninfo_a_class_erad_next_scale_slice2_s1_live_prep_package_20260714.md)
- [command draft](cninfo_a_class_erad_next_scale_slice2_s1_command_draft_20260714.md)
- [live precheck](cninfo_a_class_erad_next_scale_slice2_s1_live_precheck_20260714.csv)
- [runner checklist](cninfo_a_class_erad_next_scale_slice2_s1_runner_checklist_20260714.csv)（本包）
- [slice1 runner extension summary](cninfo_a_class_erad_next_scale_slice1_runner_extension_summary.md)
