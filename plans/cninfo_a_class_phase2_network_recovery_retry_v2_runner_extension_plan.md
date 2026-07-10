# CNINFO A 类 Phase 2 Network Recovery Retry v2 Runner Extension 规划

_生成时间：2026-07-09_

> **性质：** 离线 extension 规划 only · **本回合不实现 live** · **无 CNINFO**

**目标文件：** `lab/run_cninfo_a_class_phase2_metadata_expansion.py`

---

## 1. 当前 Runner 缺口

| 能力 | 现状 | v2 需要 |
|------|------|---------|
| approval flag | `--approve-a-class-phase2-failed-retry`（v1 only） | `--approve-a-class-phase2-network-recovery-retry-v2` |
| output root | 仅允许 `cninfo_a_class_phase2_metadata_retry/` | 允许 `cninfo_a_class_phase2_metadata_retry_v2/` |
| universe CSV | `retry_include` + `expected_period` 列 | 兼容 `retry_v2_include` + `report_period` |
| v1 write-block | v1 根可写 | v1 根在 v2 模式下 **只读** |

当前 `validate_retry_output_root()` 仅接受 `DEFAULT_RETRY_OUTPUT_ROOT`；指定 `retry_v2/` 将返回 `RETRY_OUTPUT_ROOT_VIOLATION`。

---

## 2. Required CLI Flag

```python
parser.add_argument(
    "--approve-a-class-phase2-network-recovery-retry-v2",
    action="store_true",
    help="显式批准 A-class Phase 2 network recovery retry v2 live",
)
```

**常量：**

```python
RETRY_V2_APPROVAL_REQUIRED = "approve_a_class_phase2_network_recovery_retry_v2_required"
DEFAULT_RETRY_V2_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry_v2"
)
DEFAULT_RETRY_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv",
)
```

---

## 3. Preflight Requirements

Live retry v2 前须全部满足：

1. `--retry-failed-only` 已设置
2. `--approve-a-class-phase2-network-recovery-retry-v2` 已设置（live only）
3. **不得** 同时设置 `--approve-a-class-phase2-failed-retry` 或 `--approve-a-class-phase2-metadata-expansion`
4. universe size = 8 · `retry_v2_include=yes`（或 `retry_include=yes` 别名）
5. case_ids ⊆ `RETRY_ALLOWED_CASE_IDS`
6. case_ids ∩ `SUCCESSFUL_CASE_IDS` = ∅
7. output root = `retry_v2/` 子树
8. 禁止 PDF / OCR / extraction / DB / MinIO / RAG / verified flags

---

## 4. Accepted Case IDs（禁止进入 universe）

```text
A2M001 A2M002 A2M003 A2M004 A2M006 A2M007 A2M008 A2M009
A2M014 A2M015 A2M016 A2M017
```

复用现有 `SUCCESSFUL_CASE_IDS`；校验失败返回 `SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN`。

---

## 5. Output-Root Isolation

新增 `validate_retry_v2_output_root()`：

| 路径 | v2 模式 |
|------|---------|
| `cninfo_a_class_phase2_metadata_expansion/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry_v2/` | **允许** |
| Phase 1 baseline | **禁止** |

**模式检测：** 当 `--output-root` 指向 `retry_v2/` 或 universe 为 v2 CSV 时，启用 v2 校验与 v2 approval gate。

---

## 6. Successful 12 Case Rejection

- `validate_retry_case()` 已有 successful case 拒绝逻辑
- v2 universe loader 须映射 `retry_v2_include` → internal `retry_include`
- `report_period` → `expected_period` 别名

---

## 7. Original Report Write-Blocking

v2 live 不得写入：

- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/*`
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/raw_metadata/*`

---

## 8. Retry v1 Report Write-Blocking

v2 live 不得覆盖：

- `outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/*`
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/raw_metadata/*`

v1 保留 network outage 审计记录。

---

## 9. No PDF / OCR / Extraction / DB / MinIO / RAG

复用 `enforce_forbidden_options()`；v2 不新增例外。

---

## 10. Expected Dry-Run Behavior

| 项 | 预期 |
|----|------|
| CNINFO calls | **0** |
| cases | **8/8** planned_ok |
| output | `retry_v2/reports/*_dryrun_*` |
| gate | `a_class_phase2_network_recovery_retry_v2_runner_gate = READY_FOR_APPROVAL` |
| PDF | **0** |

报告命名建议：`a_class_phase2_network_recovery_retry_v2_dryrun_report.csv`

---

## 11. Expected Live Behavior（显式批准后）

| 项 | 预期 |
|----|------|
| CNINFO | orgId resolution + announcement query per case |
| cases | **8** only |
| matching | v2 unchanged |
| PDF download / parse | **0** |
| success threshold（规划） | ≥6/8 correct → `PASS_WITH_CAVEAT` |
| gate field | `a_class_phase2_network_recovery_retry_v2_execution_gate` |

---

## 12. Tests Required（下一回合 offline）

新文件建议：`lab/test_cninfo_a_class_phase2_network_recovery_retry_v2_runner.py`

覆盖：

- v2 approval gate enforcement
- v2 output-root isolation
- v1 / expansion write-block
- successful 12 rejection
- universe column alias (`retry_v2_include`, `report_period`)
- dry-run CNINFO=0

---

## 13. Implementation Scope（本回合）

**不实现 live 执行。** 仅规划 extension；下一 offline 回合实现 flag stub + tests + dry-run。

**无 CNINFO · 无 live · 无 commit（除非用户另行要求）**
