# CNINFO D 类 shareholder_change First-Slice — S4 Runner Extension Design

_生成时间：2026-07-14_

> **性质：** Era D S4 runner 扩展设计 only · **CNINFO calls = 0** · **无实现** · **无 runner 执行** · **无 commit** · **无 push**
>
> **任务 ID：** D-GEN-20260714-08
>
> **边界：** 设计 gate = **READY_FOR_IMPLEMENTATION_APPROVAL** · live = **NOT_APPROVED** · **不是 verified** · **不是 production_ready**

---

## 1. Prior Artifact Citations（D-06 / D-07 · read-only）

| 任务 | 路径 | 角色 |
|------|------|------|
| D-GEN-20260714-06 | [cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md](cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md) | AQ-D-SC 组件批准 · universe lock · Tier-1/2 路径 · CNINFO cap |
| D-GEN-20260714-06 | [cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv](cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv) | DSC001–DSC005 锁定宇宙 |
| D-GEN-20260714-06 | [cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md](cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md) | 未来命令形状草案 |
| D-GEN-20260714-07 | [cninfo_d_class_shareholder_change_fixture_vr_validation_20260714.md](cninfo_d_class_shareholder_change_fixture_vr_validation_20260714.md) | Tier-1 VR PASS_OFFLINE · 8/8 fixtures |
| D-GEN-20260714-07 | [cninfo_d_class_shareholder_change_fixture_vr_matrix_20260714.csv](cninfo_d_class_shareholder_change_fixture_vr_matrix_20260714.csv) | VR-001–VR-042 矩阵 |
| 只读引用 | [cninfo_d_class_shareholder_change_validation_rules_20260714.md](cninfo_d_class_shareholder_change_validation_rules_20260714.md) | VR-001–VR-042 验收规则 |
| 只读引用 | [cninfo_d_class_shareholder_change_sample_prep_20260714.md](cninfo_d_class_shareholder_change_sample_prep_20260714.md) | Tier-0/1/2 分层规格 |
| 只读引用 | [cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv) | raw 字段 → artifact pattern |
| Tier-1 fixtures | `fixtures/d_class/shareholder_change_first_slice/`（8 JSON） | 离线对照 · **本设计不修改** |
| 参照实现 | `lab/run_cninfo_d_class_tiny_live_validation.py` · `equity_pledge_first_slice` 模式 | 第一切片 runner 扩展样板 |

**本包不修改：** universe lock · fixtures · schema_prep · event_model · validation_rules · evidence_map。

---

## 2. Current Runner Status

`lab/run_cninfo_d_class_tiny_live_validation.py` **尚未支持** `--shareholder-change-first-slice`。

现有相关能力：

| 模式 | 状态 |
|------|------|
| Phase 1 v1 tiny live | 已实现 · generic `shareholder_change` 多参数探测 |
| v2 bounded probe | 已实现 |
| known-event replacement / targeted probe | 已实现 · DLC006R 含 `shareholder_change` |
| equity_pledge / margin_trading / block_trade / RSU / disclosure first-slice | 已实现 dry-run（部分 live） |
| **shareholder_change first-slice** | **未实现** |

**关键隔离：** generic tiny-live 路径中 `_build_live_params` 对 `shareholder_change` 使用 **5 参数多探测**（含 `type=desc` 与多 `tdate`）。first-slice 模式 **必须** 使用独立 plan builder，**仅** `type=inc` + `tdate=2026-07-03`（VR-007/008），**不得** 复用 generic multi-probe。

**本设计不实现代码。**

---

## 3. Required CLI Flags

| Flag | 类型 | 说明 |
|------|------|------|
| `--shareholder-change-first-slice` | bool | 启用 shareholder_change 第一切片模式；与 replacement/v1/v2/其他 first-slice 互斥 |
| `--approve-d-class-shareholder-change-first-slice` | bool | live 必需；dry-run **不需要** |
| `--universe-csv` | path | **必须显式指定** universe lock CSV（禁止默认 tiny-live universe） |
| `--output-root` | path | 默认 `cninfo_d_class_shareholder_change_first_slice/` |
| `--dry-run` / `--live` | mode | dry-run 默认 · CNINFO=0 |

**禁止 flag（与 prior slices 一致）：**

- `--pdf-download` · `--ocr` · `--extraction`
- `--db-write` · `--minio-write` · `--rag-run`
- harvest / scale expansion flags

**错误 approval flag 拒绝（0 CNINFO）：**

- `--approve-d-class-tiny-live-validation`
- `--approve-d-class-known-event-replacement-validation`
- `--approve-d-class-known-event-targeted-probe`
- `--approve-d-class-equity-pledge-first-slice`
- 其他 first-slice / v2 approval flags

---

## 4. Universe CSV Contract

**正式路径（locked · 只读加载）：**

```text
outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv
```

| 约束 | 值 |
|------|-----|
| 行数 | **exactly 5** |
| case_id | **DSC001–DSC005**（连续无缺口） |
| component | `shareholder_change` |
| first_slice_include | `yes`（全案） |
| anchor_tdate | `2026-07-03`（全案共享） |
| query_type | `inc` |
| forbidden company_code | **688671** · **301259** |
| exclude_flags | 含 `exclude_688671;exclude_301259` |

**期望 company_code 映射（硬编码校验）：**

| case_id | company_code |
|---------|--------------|
| DSC001 | 000550 |
| DSC002 | 000895 |
| DSC003 | 600000 |
| DSC004 | 002415 |
| DSC005 | 601988 |

**expected_behavior mix（来自 D-06 lock）：**

| case_id | expected_behavior |
|---------|-------------------|
| DSC001 | captured_normal_or_empty_but_valid |
| DSC002 | captured_normal_or_empty_but_valid |
| DSC003 | captured_normal_or_empty_but_valid |
| DSC004 | captured_normal_or_needs_review |
| DSC005 | empty_but_valid |

---

## 5. Query Plan & Request Shape

| 项 | 值 |
|----|-----|
| endpoint | `POST https://www.cninfo.com.cn/data20/shareholeder/detail` |
| registry path | `shareholder_change/shareholeder/detail`（拼写 **shareholeder** 保留） |
| query_mode | **`type_inc` + `tdate_daily`** |
| per-case params | `{"type": "inc", "tdate": "2026-07-03"}` |
| records_path | `data.records` |
| company filter | `SECCODE` == universe `company_code` |
| sleep default | 0.6s between requests（live 规划值） |
| early_stop | per-case 命中公司行后停止 |

**per-case 计划请求数：** **1**（单 type+tdate）

**禁止（VR-008）：**

- `type=desc` / decrease 模式
- 多 `tdate` 邻近日探测
- generic `_build_live_params` multi-probe 路径

---

## 6. CNINFO Request Cap（future live only）

| 项 | 值 |
|----|-----|
| per-case max | **≤ 4** |
| total cap | **≤ 20** |
| planned (5-case dry-run/live) | **~5**（1 请求/案） |
| dry-run CNINFO | **0** |

Preflight 拒绝超 cap plan · live 后 `validate_shareholder_change_first_slice_request_caps(stats)` 校验。

---

## 7. Isolated Output Root

```text
outputs/validation/cninfo_d_class_shareholder_change_first_slice/
├── reports/
│   ├── d_class_shareholder_change_first_slice_dryrun_report.csv
│   ├── d_class_shareholder_change_first_slice_dryrun_summary.md
│   ├── d_class_shareholder_change_first_slice_live_report.csv
│   ├── d_class_shareholder_change_first_slice_quality_report.csv
│   ├── d_class_shareholder_change_first_slice_live_summary.md
│   └── d_class_shareholder_change_first_slice_live_outcome_ledger.csv
├── live_snapshots/
│   └── {case_id}_shareholder_change.json
└── planned_snapshots/
    └── {case_id}_shareholder_change.json
```

**默认 output root 常量（实现时）：**

```python
DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_d_class_shareholder_change_first_slice",
)
```

---

## 8. Write-Blocks

### 8.1 Output Root 写保护（禁止作为 output-root）

| 受保护路径 | token（建议命名） |
|-----------|------------------|
| `cninfo_d_class_tiny_live_validation/`（v1） | `v1_output_root_write_blocked` |
| `cninfo_d_class_tiny_live_validation_v2/`（v2） | `v2_output_root_write_blocked` |
| `cninfo_d_class_known_event_replacement_validation/` | `replacement_output_root_write_blocked` |
| `cninfo_d_class_known_event_targeted_probe/` | `targeted_probe_output_root_write_blocked` |
| `cninfo_d_class_equity_pledge_first_slice/` | `equity_pledge_first_slice_output_root_write_blocked` |
| `cninfo_d_class_margin_trading_first_slice/` | `margin_trading_first_slice_output_root_write_blocked` |
| `cninfo_d_class_disclosure_schedule_first_slice/` | `disclosure_schedule_first_slice_output_root_write_blocked` |
| `cninfo_d_class_block_trade_first_slice/` | `block_trade_first_slice_output_root_write_blocked` |
| `cninfo_d_class_restricted_shares_unlock_first_slice/` | `rsu_first_slice_output_root_write_blocked` |

### 8.2 Universe / Fixture 写保护

| 受保护路径 | 说明 |
|-----------|------|
| `cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv` | universe lock · 只读加载 |
| `cninfo_d_class_phase1_tiny_live_universe_calibrated.csv` | calibrated universe |
| `cninfo_d_class_tiny_live_replacement_universe_*.csv` | replacement universe |
| `fixtures/d_class/shareholder_change_first_slice/` | Tier-1 synthetic · 不写入 |

### 8.3 运行时写保护

`enforce_shareholder_change_first_slice_write_block_targets(output_paths)` 在 dry-run / live 入口执行，拒绝向受保护根目录写入。

---

## 9. Approval Guard & Gate Semantics

| 模式 | approval flag | CNINFO | gate 行为 |
|------|---------------|--------|-----------|
| dry-run | **不需要** | **0** | 输出 planned_snapshots + dryrun report · runner gate 保持 `READY_FOR_APPROVAL` |
| live（无 approval flag） | 缺失 | **0** | **拒绝** · exit 2 |
| live（错误 approval flag） | 其他 slice flag | **0** | **拒绝** · exit 2 |
| live（正确 approval + 人工 S5 短语） | `--approve-d-class-shareholder-change-first-slice` | ≤20 | 允许 CNINFO · 评估 execution gate |

**强制语义：**

```text
shareholder_change_first_slice_runner_design_gate = READY_FOR_IMPLEMENTATION_APPROVAL
shareholder_change_first_slice_runner_gate = NOT_APPROVED (until implementation + human runner approval)
shareholder_change_first_slice_live_gate = NOT_APPROVED
shareholder_change_first_slice_execution_gate = NOT_APPLICABLE (until live)
```

`COMPONENT_APPROVED`（AQ-D-SC）≠ runner_approved ≠ live_approved ≠ verified ≠ production_ready。

---

## 10. Dry-Run Behavior（future · after implementation approval）

1. 加载 universe lock CSV · 校验 5 行 · DSC001–005 · forbidden codes
2. 校验 output root 隔离 · 执行 write-block
3. 为每案生成 plan：`type_inc_tdate_2026-07-03` · planned_request_count=1
4. 写入 `planned_snapshots/{case_id}_shareholder_change.json`（synthetic envelope · `cninfo_called=false`）
5. 输出 dryrun report + summary
6. **CNINFO calls = 0**

**成功标准：** 5/5 `dryrun_status=planned_ok` · `planned_request_count_total=5`

---

## 11. Future Live Behavior（S5 · NOT APPROVED）

1. 要求 `--approve-d-class-shareholder-change-first-slice`
2. 仅 DSC001–DSC005 · 每案 1 请求 `type=inc,tdate=2026-07-03`
3. SECCODE 公司过滤 · 写入 `live_snapshots/`
4. 字段映射按 VR-015–VR-024 · registry `shareholder_change`
5. `cninfo_requests` 累计 ≤ 20 · per-case ≤ 4
6. 评估 acceptable · outcome ledger · execution gate

**Acceptable 判定（参照 equity_pledge first-slice · VR-031）：**

| expected_behavior | acceptable 条件 |
|-------------------|---------------|
| `empty_but_valid` | `retrieval_status=empty_but_valid` · record_count=0 |
| `captured_normal_or_empty_but_valid` | found+records≥1 **或** empty_but_valid+records=0 |
| `captured_normal_or_needs_review` | found+records≥1 **或** needs_review+records≥1 |

**禁止：** disclosure-only 证据升级为 `captured_normal`（VR-038）。

---

## 12. Execution Gate Logic（future live）

| 结果 | gate |
|------|------|
| ≥ **3/5** acceptable | `shareholder_change_first_slice_execution_gate = PASS_WITH_CAVEAT` |
| < 3/5 acceptable | `FAIL_REVIEW_REQUIRED` |

**永不使用 bare `PASS`** · **不自动升级** component gate · **不 claim** verified / production_ready。

---

## 13. Proposed Implementation Surface

参照 `equity_pledge_first_slice` 模式，实现时应新增：

| 类别 | 建议符号 |
|------|----------|
| 常量 | `DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_*` · `SHAREHOLDER_CHANGE_FIRST_SLICE_ALLOWED_CASE_IDS` |
| dataclass | `ShareholderChangeFirstSliceRow` |
| loader | `load_shareholder_change_first_slice_universe` |
| plan | `build_shareholder_change_first_slice_plan` · `compute_shareholder_change_first_slice_planned_requests` |
| validate | `validate_shareholder_change_first_slice_universe` · `validate_shareholder_change_first_slice_output_root` |
| guard | `enforce_shareholder_change_first_slice_write_block_targets` · `enforce_shareholder_change_first_slice_forbidden_options` · `enforce_shareholder_change_first_slice_live_approval_gate` |
| dry-run | `build_shareholder_change_first_slice_dryrun_rows` · `write_shareholder_change_first_slice_dryrun_report` · `write_shareholder_change_first_slice_dryrun_summary` |
| live | `shareholder_change_first_slice_row_to_universe_case` · `is_shareholder_change_first_slice_acceptable` · `execute_shareholder_change_first_slice_live` · `run_shareholder_change_first_slice` |
| main dispatch | `if args.shareholder_change_first_slice: return run_shareholder_change_first_slice(args)` |

**Live 请求路径：** 使用 **独立** `_build_shareholder_change_first_slice_params(row)` 返回 `[{"type": "inc", "tdate": row.anchor_tdate}]`，**不调用** generic `_build_live_params`。

---

## 14. Command Draft（cite · NOT APPROVED · DO NOT RUN）

来源：[cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md](cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md)

### Dry-Run（S4 实现后 · 须 runner implementation approval）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-change-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_first_slice/
```

### Live（S5 · 须 explicit live approval · 本任务禁止）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-change-first-slice \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_first_slice/ \
  --approve-d-class-shareholder-change-first-slice
```

---

## 15. Red Lines

| 禁止项 | 原因 |
|--------|------|
| DLC003R / DLC006R rerun | known-event closed |
| generic multi-probe（desc / 多 tdate） | VR-007/008 first-slice inc-only |
| disclosure → captured_normal | VR-038 |
| PDF / OCR / extraction / DB / MinIO / RAG | D-class metadata scope |
| mutate universe lock / fixtures | D-06/07 冻结 |
| verified / production_ready / testing_stable_sample | governance VR-042 |
| reopen closed tracks（equity_pledge / RSU / block_trade 等） | Era D 轨隔离 |

---

## 16. Safety Confirmations（this package）

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| runner execution | **no** |
| live execution | **no** |
| universe lock mutation | **no** |
| fixture mutation | **no** |
| commit / push | **no** |
| implementation | **no**（design only） |

---

## 17. Gate Summary Block

```text
task_id = D-GEN-20260714-08
phase = shareholder_change_s4_runner_design_20260714
component = shareholder_change
universe = DSC001-DSC005 (universe_lock_20260714.csv)
anchor = tdate=2026-07-03 type=inc
query_mode = type_inc (NOT generic multi-probe)
output_root = cninfo_d_class_shareholder_change_first_slice/
flags = --shareholder-change-first-slice (not implemented)
approval_flag = --approve-d-class-shareholder-change-first-slice (live only)
cninfo_cap_future_live = per_case<=4 total<=20 planned~5
dryrun_cninfo = 0
fixture_vr_gate = PASS_OFFLINE (D-07)
component_gate = COMPONENT_APPROVED (AQ-D-SC, D-06)
runner_design_gate = READY_FOR_IMPLEMENTATION_APPROVAL
runner_gate = NOT_APPROVED
live_gate = NOT_APPROVED
execution_gate = NOT_APPLICABLE
verified = false
production_ready = false
```

---

## 18. Next Steps（separately gated）

| 步骤 | 触发条件 | 当前状态 |
|------|----------|----------|
| **S4-impl** | human runner implementation approval | **blocked** · 本设计 READY_FOR_IMPLEMENTATION_APPROVAL |
| **S4-dry-run** | runner 已实现 + dry-run approval | **blocked** |
| **S5-live** | explicit live approval phrase + dry-run PASS | **blocked** · live NOT_APPROVED |
