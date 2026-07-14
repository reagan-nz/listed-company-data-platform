# CNINFO B 类 BD2E624 — Isolated Retry Runner Extension Note（Minimal）

_生成时间：2026-07-14 · task **B-GEN-20260714-07** · **CNINFO = 0** · **未实现**_

> **性质：** dry-run blocker 触发的最小 runner-extension 说明 · **非实现 PR** · **无 live**

**触发：** [execution report](cninfo_b_class_bd2e624_isolated_retry_execution_report_20260714.md) · draft command dry-run exit **2**

---

## 1. Blocker Summary

| blocker | error code | 现状 |
|---------|------------|------|
| isolated 1-case universe CSV | `erad_b_fuller_slice2_universe_csv_required` | `validate_erad_fuller_slice2_universe_csv_path` 仅接受 canonical 300-case 路径 |
| isolated output root | `output_root_must_be_under_cninfo_b_class_erad_fuller_next_slice2` | `validate_erad_fuller_slice2_output_root` 不允许 `..._bd2e624_retry/` 独立根 |

**已验证可用（诊断）：** canonical universe + `--case-range BD2E624:BD2E624` + slice2 `_mock_test` 子目录 → 1/1 planned_ok · planned requests **2** · CNINFO **0**。

---

## 2. 建议扩展（separate task）

参照 [TLC002 isolated retry runner](cninfo_b_class_tlc002_retry_runner_extension_summary.md) 模式，最小扩展项：

1. **新 flag（示意）：** `--erad-b-bd2e624-isolated-retry` 或 `--erad-b-fuller-slice2-isolated-retry`
2. **universe 校验：** 接受 `cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv`（**1 row** · case_id=BD2E624 only）
3. **output root 校验：** 允许 `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/`；**write-block** slice2 主根 reports/quality/merge closure
4. **CNINFO cap：** live 模式 `MAX_CNINFO_REQUESTS = 2`（单 case EP002→EP001）
5. **approval gate：** `--approve-b-class-bd2e624-isolated-retry`（或复用 fuller-slice2 approval + isolated flag 双检）
6. **报告命名：** `b_class_erad_fuller_next_slice2_bd2e624_retry_*`（与 command draft §2 一致）
7. **测试：** 最小 runner test + live_path mock test（CNINFO=0）

**实现位置（候选）：** `lab/run_cninfo_b_class_phase25_expansion_validation.py` 新 mode 分支，或独立 `lab/run_cninfo_b_class_bd2e624_isolated_retry.py`。

---

## 3. Gate（extension 前）

```text
b_class_bd2e624_isolated_retry_runner_extension_gate = BLOCKED_NOT_IMPLEMENTED
bd2e624_isolated_retry_dryrun_gate = FAIL_BLOCKER
bd2e624_isolated_retry_live_gate = NOT_EXECUTED
```

**下一步：** controller 排期 runner extension → dry-run 1/1 planned_ok → bounded live（≤2 CNINFO）。
