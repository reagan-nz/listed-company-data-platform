# CNINFO D 类 Known Event Replacement Validation — Command Draft

_生成时间：2026-07-09_

> **状态：NOT APPROVED** — 未来命令草案 only · **本回合不执行**

---

## 1. Purpose

在用户显式批准且 **人工填码完成** 后，对 DLC003R · DLC006R replacement cases 执行 isolated metadata/event validation，补全组件级 `captured_normal` 覆盖。

---

## 2. Prerequisites

- [ ] `d_class_known_event_replacement_case_planning_gate = READY_FOR_HUMAN_CANDIDATES` 已完成填码
- [ ] [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv) 中 `human_provided=true`
- [ ] [replacement universe draft](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv) placeholders **已替换**为人工公司
- [ ] [approval checklist](../outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md) 全部勾选
- [ ] runner 实现（**未实现**）
- [ ] calibrated / original universe **未修改**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_known_event_replacement_validation/
```

**禁止写入：**

- `outputs/validation/cninfo_d_class_tiny_live_validation/`（v1）
- `outputs/validation/cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv
```

| 规则 | 说明 |
|------|------|
| DLC003R · DLC006R | 仅 `human_provided=true` 且非 placeholder 行可执行 |
| `*_CANDIDATE_REQUIRED` | **skip** · 0 CNINFO |
| DLC001/002/004/005/007 | baseline reference · **0 CNINFO** |
| invented company codes | **禁止** |

---

## 5. Approval Flag（占位）

```text
--approve-d-class-known-event-replacement-validation
```

无此 flag → runner **拒绝 live**。

---

## 6. Proposed Command（NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --known-event-replacement \
  --universe outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_replacement_validation/ \
  --approve-d-class-known-event-replacement-validation \
  --cases DLC003R,DLC006R
```

> **注：** `--known-event-replacement` 为 **未来 runner 参数**；当前 runner **尚未实现**。

---

## 7. Dry-run Command（未来 · NOT APPROVED）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --known-event-replacement \
  --universe outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_replacement_validation/ \
  --cases DLC003R,DLC006R
```

预期：`cninfo_calls=0` until human candidates filled and approved.

---

## 8. Explicit Exclusions

| 项 | 值 |
|----|-----|
| invented company codes | **no** |
| web lookup | **no** |
| only human-filled cases run | **yes** |
| DB write | **no** |
| MinIO write | **no** |
| RAG run | **no** |
| verified | **no** |
| production_ready | **no** |
| testing_stable_sample upgrade | **no** |
| harvest | **no** |
| v1/v2 execution report mutation | **no** |

---

## 9. Gate

```text
d_class_known_event_replacement_validation_gate = NOT_APPROVED
```

（未来执行 gate — **本草案不设定为 PASS**）

**CNINFO calls（本回合）：0**
