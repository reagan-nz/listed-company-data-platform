# CNINFO D 类 Tiny Live V2 Runner Modification Plan

_生成时间：2026-07-09_

> **性质：** 修改计划 only · **不实现** · **不调用 CNINFO**

**目标文件：** `lab/run_cninfo_d_class_tiny_live_validation.py`

---

## 1. Scope

仅规划 v2 bounded probe 所需 runner 变更；**本回合不写代码**。

---

## 2. New CLI Flags

| flag | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--bounded-probe-v2` | bool | false | 启用 v2 有界探测模式 |
| `--approve-d-class-tiny-live-v2-bounded-probe` | bool | false | v2 live 显式批准 |
| `--dlc003-max-requests` | int | 24 | DLC003 硬顶 |
| `--dlc006-max-requests` | int | 20 | DLC006 硬顶 |
| `--cases` | str | all | 逗号分隔 case_id 过滤（v2 默认 `DLC003,DLC006`） |
| `--v1-report-path` | path | v1 默认路径 | 只读 v1 报告用于对照 |

**互斥：**

- `--bounded-probe-v2` + `--approve-d-class-tiny-live-validation`（v1）不可同时用于 live
- v2 live 必须 `--approve-d-class-tiny-live-v2-bounded-probe`

---

## 3. V2 Output Root Isolation

| 行为 | 实现要点 |
|------|----------|
| 默认 v2 root | `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` |
| v1 写保护 | 若 `output_root` 解析为 v1 路径且 `--bounded-probe-v2` → **拒绝启动** |
| 报告命名 | `d_class_tiny_live_v2_*.csv|md` 前缀，避免与 v1 混淆 |
| snapshot 路径 | `live_snapshots/DLC003_*.json` 仅写 v2 根 |

---

## 4. Bounded Probe Caps

### 4.1 `_build_bounded_probe_params_v2(case)` — 新函数

**DLC003：**

1. 生成 `v1_baseline` tdate 列表（与现 `_build_live_params` 一致）
2. 生成 `recent_12m_monthly` 月尾 tdate（12 个）
3. 生成 `recent_24m_quarterly` 季尾 tdate（8 个）
4. union dedup → 按序迭代 → **计数 ≤ `--dlc003-max-requests`**
5. **early stop**：公司级 `>=1` 行即 break

**DLC006：**

1. 生成 `v1_baseline` 五组合
2. 生成 `recent_12m_quarterly_inc`（4）
3. 生成 `recent_24m_quarterly_both`（inc+desc × 8 季尾 dedup）
4. union dedup → **计数 ≤ `--dlc006-max-requests`**
5. **early stop** 同上

**禁止：** 猜测事件日期 · 发明 replacement 公司

### 4.2 请求计数

- `LiveStats` 增加 per-case cap 与 `stopped_reason`（`cap_reached` · `early_stop_hit` · `error_abort`）
- 全局 v2 cap = DLC003 cap + DLC006 cap

---

## 5. No Overwrite of V1 Outputs

| 检查 | 动作 |
|------|------|
| output_root == v1 默认路径 | `sys.exit(1)` + 错误信息 |
| 试图写入 v1 `d_class_tiny_live_report.csv` | 拒绝 |
| 读取 v1 报告 | 只读 `open(..., 'r')` 用于 comparison |

---

## 6. DLC003 / DLC006 Only

| case | v2 CNINFO |
|------|-----------|
| DLC003 | **yes** — bounded probe |
| DLC006 | **yes** — bounded probe |
| DLC001 | **no** — 从 v1 报告复制对照行至 comparison（无新请求） |
| DLC002 | **no** |
| DLC004 | **no** |
| DLC005 | **no** |
| DLC007 | **no** |

`--cases DLC003,DLC006` 为 v2 默认过滤。

---

## 7. Preserve Baseline Cases

DLC001 · DLC002 · DLC004 · DLC005 · DLC007：

- v2 执行时 **不发 CNINFO**
- comparison report 从 v1 `d_class_tiny_live_report.csv` **只读引用**
- 标注 `source=v1_baseline_reference`

---

## 8. V2 Comparison Report

**新输出：** `reports/d_class_tiny_live_v2_comparison_report.csv`

| 列 | 说明 |
|----|------|
| case_id | DLC001–DLC007 |
| v1_retrieval_status | 只读 v1 |
| v2_retrieval_status | v2 实测或 `v1_reference` |
| v1_cninfo_request_count | v1 |
| v2_cninfo_request_count | v2（baseline cases = 0） |
| expectation_met_v1 | yes/no |
| expectation_met_v2 | yes/no/na |
| probe_extension_applied | yes/no |
| notes | early_stop · cap_reached 等 |

---

## 9. Universe Handling

- 加载 `universe_v2_draft.csv`
- `requires_human_candidate=true` 或 `company_code` 为空 → **skip** + 日志
- **不修改** universe v2 文件

---

## 10. Tests Plan（未来实现时）

| 测试 | 断言 |
|------|------|
| v2 dry-run | `cninfo_calls=0` |
| v2 without approval flag | live 拒绝 |
| v1 path write guard | bounded-v2 拒绝写 v1 root |
| DLC003 param dedup cap | ≤24 params |
| DLC006 param dedup cap | ≤20 params |
| placeholder skip | `*_CANDIDATE_REQUIRED` 不探测 |
| comparison report | 7 行含 v1 baseline 引用 |

---

## 11. Non-goals（runner 修改不做）

- DB / MinIO / RAG 集成
- verified / production_ready 标记
- harvest 路径
- universe v2 placeholder 自动填码
- v1 报告行修改

---

## 12. Gate

```text
d_class_tiny_live_v2_bounded_probe_design_gate = READY_FOR_APPROVAL
```

实现完成后的未来 gate（**不在本计划设定**）：`d_class_tiny_live_v2_execution_gate` — 需单独批准包。
