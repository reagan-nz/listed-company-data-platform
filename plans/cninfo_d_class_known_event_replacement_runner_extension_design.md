# CNINFO D 类 Known Event Replacement — Runner Extension Design

_生成时间：2026-07-09_

> **性质：** 离线 runner 扩展设计 only · **无 CNINFO** · **无 live** · **NOT APPROVED**

**关联：** [command draft](cninfo_d_class_known_event_replacement_validation_command_draft.md) · [filled universe](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv)

---

## 1. Current Runner Status

`lab/run_cninfo_d_class_tiny_live_validation.py` **尚未支持** known-event replacement 模式。

现有 flag 仅覆盖：

- `--approve-d-class-tiny-live-validation`（Phase 1 v1 tiny live）
- `--bounded-probe-v2` + `--approve-d-class-tiny-live-v2-bounded-probe`（v2 bounded probe）

**本设计不实现代码** — 仅定义未来扩展契约。

---

## 2. Required CLI Flags

| Flag | 类型 | 说明 |
|------|------|------|
| `--known-event-replacement` | bool | 启用 replacement validation 模式；与 v1/v2 模式互斥 |
| `--approve-d-class-known-event-replacement-validation` | bool | live 必需；无此 flag → 拒绝 `--live` |
| `--universe-csv` | path | 默认指向 filled universe |
| `--output-root` | path | 隔离输出根 |
| `--cases` | str | 逗号分隔；默认 `DLC003R,DLC006R` |
| `--dry-run` / `--live` | mode | dry-run 默认；live 需双批准 |

**禁止 flag（与现有 runner 一致）：**

`--db-write` · `--minio-write` · `--rag-run` · `--mark-verified` · `--production-ready` · harvest 相关 approve flags

---

## 3. Preflight Requirements

live 前 runner 必须校验：

1. `--known-event-replacement` 已设置
2. universe CSV 存在且可读
3. 仅允许 case_id ∈ `{DLC003R, DLC006R}` 执行 CNINFO（`--cases` 过滤后）
4. 每行 `candidate_validation_status = HUMAN_CANDIDATE_VALIDATED`
5. 每行 `include_in_future_validation = true`
6. `company_code` 非空且与 [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv) 一致
7. `expected_behavior = captured_normal`
8. output-root **不等于** v1/v2 路径
9. `--live` 时必须有 `--approve-d-class-known-event-replacement-validation`
10. 禁止 `--bounded-probe-v2` 与 `--known-event-replacement` 同时使用

失败 → exit non-zero · **0 CNINFO**

---

## 4. Allowed Replacement Case IDs

| case_id | replaces | component | company | endpoint（预期） |
|---------|----------|-----------|---------|------------------|
| DLC003R | DLC003 | restricted_shares_unlock | 688671 碧兴物联 | `liftBan/detail` |
| DLC006R | DLC006 | shareholder_change | 301259 艾布鲁 | `shareholeder/detail` |

**不允许：** 任何其他 case_id · invented codes · placeholder 行

---

## 5. Approval Flag Requirement

```text
--approve-d-class-known-event-replacement-validation
```

- dry-run：**不需要** approval flag
- live：**必须**显式提供
- 与 `--approve-d-class-tiny-live-validation` **独立** — 不可互相替代

---

## 6. Output-Root Isolation

```text
outputs/validation/cninfo_d_class_known_event_replacement_validation/
├── reports/
│   ├── d_class_known_event_replacement_summary.md
│   └── per-case JSON/CSV
├── raw/          # CNINFO 原始响应（live only）
└── normalized/   # 规范化行（live only）
```

**写保护路径：**

- `outputs/validation/cninfo_d_class_tiny_live_validation/`
- `outputs/validation/cninfo_d_class_tiny_live_validation_v2/`

runner 启动时若 output-root 匹配 v1/v2 → **拒绝**

---

## 7. Request Cap · Bounded Probe · Early Stop

| case | 建议硬顶 | 策略 |
|------|----------|------|
| DLC003R | 24 requests | 以 event_date 2024-02-19 为中心 ±window 探针 |
| DLC006R | 20 requests | 以 event_date 2024-07-16 为中心 ±window 探针 |
| **合计** | **≤ 44** | 与 v2 bounded probe 同级上限 |

**Early stop：** 任一 case 获得 ≥1 符合 schema 的 captured 行 → 该 case 停止后续探针

**Baseline rows（DLC001/002/004/005/007）：** 0 CNINFO · reference only

---

## 8. Safety Constraints

| 项 | 要求 |
|----|------|
| DB / MinIO / RAG | **禁止** |
| verified / production_ready | **禁止标记** |
| testing_stable_sample | **不升级** |
| original v1 universe | **不修改** |
| calibrated universe | **不修改** |
| v1/v2 execution reports | **不修改** |
| web lookup | **禁止** |
| harvest | **禁止** |

---

## 9. Expected Dry-Run Behavior

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --known-event-replacement \
  --universe-csv outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_replacement_validation/ \
  --cases DLC003R,DLC006R
```

预期输出：

- `cninfo_calls=0`
- preflight checklist PASS
- planned cases: DLC003R, DLC006R
- planned request budget: ≤44
- output-root isolation confirmed
- gate: `NOT_APPROVED` until live approval flag

---

## 10. Expected Live Behavior（After Approval）

在用户显式提供 `--approve-d-class-known-event-replacement-validation` 后：

1. 仅 DLC003R · DLC006R 发起 CNINFO metadata/event 探针
2. 写入隔离 output-root
3. 生成 per-case execution report + summary
4. 评估 `captured_normal` vs `empty_but_valid` vs `schema_failure`
5. **不**回写 universe · **不**标记 verified

预期 gate（执行后评审，非本设计预设）：

```text
d_class_known_event_replacement_validation_execution_gate = TBD_AFTER_LIVE
```

---

## 11. Gate

```text
runner_extension_design_gate = READY_FOR_IMPLEMENTATION
d_class_known_event_replacement_validation_package_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT live_ready** · **NOT verified**

**CNINFO calls（本回合）：0**
