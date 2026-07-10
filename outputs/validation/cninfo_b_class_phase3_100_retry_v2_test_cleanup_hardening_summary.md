# CNINFO B 类 Phase 3 Retry v2 Test Cleanup Hardening Summary

_生成时间：2026-07-10_

> **性质：** Phase 0 离线硬化 · **无 CNINFO** · **无 live**（本文件生成时）

---

## Problem

`test_cninfo_b_class_phase3_100_retry_v2_live_path.py` 原 `_cleanup_mock_live_artifacts()` 在 mock live 测试后删除 **生产** `DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT` 下的 live 报告、`quality/`、`raw_metadata/`，导致 commit 前 **185** 个 inventory 路径丢失。

---

## Hardening Changes

| 项 | 变更 |
|----|------|
| 文件 | `lab/test_cninfo_b_class_phase3_100_retry_v2_live_path.py` |
| mock output root | 改为 `outputs/validation/cninfo_b_class_phase3_100_retry_v2/_mock_live_test/run_*` 临时子目录 |
| cleanup | `_cleanup_temp_output_root()` 仅允许删除 `_mock_live_test/` 下目录；生产根目录 **硬拒绝** |
| 回归测试 | `test_cleanup_refuses_production_output_root` |
| 回归测试 | `test_mock_live_teardown_does_not_delete_production_output_root` |

---

## Test Results

| Suite | Result |
|-------|--------|
| `test_cninfo_b_class_phase3_100_retry_v2_live_path.py` | **26/26 PASS** |
| `test_cninfo_b_class_phase3_100_retry_v2_runner.py` | **26/26 PASS** |
| CNINFO（hardening round） | **0** |

---

## Gate

```
b_class_phase3_100_retry_v2_test_cleanup_hardening_gate = PASS_OFFLINE
```

---

## Residual Risk

- `_mock_live_test/` 目录本身留在生产 retry_v2 根下（测试残留）；不影响 live 产物路径，但建议后续 `.gitignore` 或定期清理该子树。
- 其他 B-class live-path 测试文件若存在类似 cleanup 模式，应单独审计（本任务仅硬化 retry_v2 live-path）。

---

## Next

Phase 1 isolated retry_v2 live recovery（须 in-session approval · **已批准**）
