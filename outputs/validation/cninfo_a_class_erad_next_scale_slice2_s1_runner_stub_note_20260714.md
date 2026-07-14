# CNINFO A 类 Next-Scale Slice2 S1 +100 — Runner Stub / 桩测试说明

_生成时间：2026-07-14_

> **性质：** Era D A-class slice2 S1 runner **桩测试 only** · **CNINFO = 0** · **NOT IMPLEMENTED** · **NOT APPROVED live** · **NOT APPROVED runner execution** · **HOLD preserved**

**任务 ID：** **A-GEN-20260714-12**

**引用设计：** [A-11 runner design](cninfo_a_class_erad_next_scale_slice2_s1_runner_design_20260714.md)（A-GEN-20260714-11）

**测试文件：** `lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py`

---

## 1. 本包交付范围

| 交付物 | 路径 | 状态 |
|--------|------|------|
| 桩测试骨架 | `lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py` | **本包** |
| 桩测试说明 | 本文档 | **本包** |
| runner 实现 | `lab/run_cninfo_a_class_phase2_metadata_expansion.py` | **未修改 · 阻塞** |
| 完整 dry-run 测试 | `lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py` | **未创建 · 阻塞** |
| live path 测试 | `lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py` | **未创建 · 阻塞** |

---

## 2. 桩测试已覆盖（PASS 预期）

### 2.1 设计证据链

- A-11 design doc 存在且含 `A-GEN-20260714-11`、`--erad-a-scale-500-slice2`、`DESIGN_ONLY`
- runner checklist CSV 存在
- 冻结 universe CSV 存在
- 182 台账 · remainder draft · universe 受保护 CSV 路径存在

### 2.2 设计常量文档化（测试模块内 · 待迁入 runner）

| 常量 | 值 |
|------|-----|
| `REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE` | **100** |
| `ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS` | AD2E501–AD2E600 |
| `ERAD_NEXT_SCALE_SLICE2_COHORT` | `next_scale_slice2` |
| `ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE` | **2** |
| `ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP` | **240** |
| `ERAD_SLICE2_ACCEPTABLE_THRESHOLD` | **90** |
| `ERAD_SLICE2_EXECUTION_GATE_PASS` | `PASS_WITH_CAVEAT` |

### 2.3 路径与命令形状

| 项 | 路径 / 形状 |
|----|-------------|
| universe CSV | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv` |
| output root | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/` |
| mock 子目录 | `_mock_test/` · `_mock_live_test/` |
| dry-run 命令 | `--erad-a-scale-500-slice2` + `--universe-csv` + `--output-root` + `--dry-run` |

### 2.4 冻结 universe 只读校验

- 4 列 schema：`company_code` · `company_name` · `case_id` · `cohort`
- 100 行 · AD2E501–AD2E600 连续 · `next_scale_slice2` 单一 cohort
- `company_code` 603701–688772 · 无重复
- L-D4 ST 名称命中 **0/100**
- SHA-256 前后一致（测试不 mutate 源 CSV）

### 2.5 阻塞态显式断言

- `a_class_erad_next_scale_slice2_s1_runner_extension_gate = DESIGN_ONLY`
- `--erad-a-scale-500-slice2` argparse **未注册** → `unrecognized arguments` · exit **2**
- `--approve-a-class-erad-scale-500-slice2` **未注册**
- subprocess dry-run **拒绝执行** · CNINFO **0**（未进入 runner 主逻辑）
- A-11 §10 规划符号在 runner 中 **全部缺失**（预期阻塞）
- slice1 回归符号仍可用（`process_erad_next_scale_slice1_dry_run` 等）

---

## 3. 仍阻塞（本包未实现）

对照 [runner checklist](cninfo_a_class_erad_next_scale_slice2_s1_runner_checklist_20260714.csv) RE-S2S1-005..029：

| 阻塞项 | checklist ID | 说明 |
|--------|--------------|------|
| flag 注册 | RE-S2S1-005/006 | `--erad-a-scale-500-slice2` · `--approve-a-class-erad-scale-500-slice2` |
| mode 互斥 | RE-S2S1-007 | vs scale-200 / failed-retry / slice1 / phase3 |
| universe 校验 | RE-S2S1-008/009/010 | path · size=100 · load 派生字段 |
| output root 校验 | RE-S2S1-011 | canonical + `_mock_*` |
| write-block | RE-S2S1-012..015 | scale-200 · failed_retry · **slice1 主根** · phase3/A3M017 |
| overlap lint | RE-S2S1-016..019 | L-A1..L-B4 · AB_182 · L-D4 运行时 re-assert |
| request cap | RE-S2S1-020 | ≤240 enforce |
| dry-run 100/100 | RE-S2S1-021 | `planned_ok=100` · CNINFO=0 |
| report 命名 | RE-S2S1-022 | `a_class_erad_next_scale_slice2_s1_*` |
| session split | RE-S2S1-023 | AD2E501:AD2E550 · AD2E551:AD2E600 |
| 完整测试 | RE-S2S1-025/026/027 | 参照 slice1 17/17 · live path mock |
| gate 升级 | RE-S2S1-029 | → `READY_FOR_APPROVAL` |

**live 阻塞（本包不涉及）：** RE-S2S1-030..035 · HOLD · human approval · precheck · O3 Controller

---

## 4. Gate 状态（本包后）

```text
a_class_erad_next_scale_slice2_s1_cohort_freeze_gate = FROZEN          # 不变
a_class_erad_next_scale_slice2_s1_lint_gate = PASS                     # 不变
a_class_erad_next_scale_slice2_s1_live_prep_gate = READY_FOR_NEXT_STEP # 不变
a_class_erad_next_scale_slice2_s1_runner_extension_gate = DESIGN_ONLY  # 不变（桩 ≠ 实现）
a_class_erad_next_scale_slice2_s1_runner_stub_gate = STUB_TESTS_PASS   # 本包新增语义
a_class_erad_next_scale_slice2_s1_dryrun_gate = NOT_APPLICABLE         # 不变
a_class_erad_next_scale_slice2_s1_live_gate = NOT_APPROVED             # 不变
```

**语义：** `STUB_TESTS_PASS` 仅表示设计常量/路径/阻塞态已文档化并通过桩测试；**不等于** runner 已实现 · dry-run 完成 · live 批准。

---

## 5. 红线遵守

| 约束 | 本包 |
|------|------|
| CNINFO | **0** |
| live | **未执行** |
| push | **未执行** |
| universe CSV mutate | **否**（SHA-256 断言） |
| slice1 / scale-200 生产根写入 | **未触碰** |
| 182 台账 / remainder mutate | **未触碰** |

---

## 6. 下一步（Separate Task）

1. 在 `run_cninfo_a_class_phase2_metadata_expansion.py` 实现 A-11 §10 最小清单
2. 将桩测试常量迁入 runner 模块
3. 创建 `lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py`（参照 slice1 17/17）
4. dry-run 100/100 `planned_ok` · CNINFO=0 → `runner_extension_gate = READY_FOR_APPROVAL`
5. slice1 regression 17/17 保持 PASS
