# CNINFO D 类 Known Event Targeted Probe — Command Draft

_生成时间：2026-07-09_

> **状态：NOT APPROVED** — 未来 live 命令草案 only · **Do not execute live**

---

## 1. Purpose

在用户显式批准后，对 DLC003R-T01 · DLC006R-T01 执行 **event-date targeted** metadata 探针，检验 anchor 日邻近查询能否 surfacing 公司级行。

**dry-run 已实现并通过** · **live 路径已实现（mock tests 29/29）** · **本 live 草案不执行**

---

## 2. Prerequisites

- [x] `d_class_known_event_targeted_probe_planning_gate = READY_FOR_APPROVAL`
- [x] `d_class_known_event_targeted_probe_runner_extension_gate = READY_FOR_APPROVAL`
- [x] `d_class_known_event_targeted_probe_live_implementation_gate = READY_FOR_APPROVAL`
- [x] [universe draft](../outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv) — **2 rows**
- [x] runner extension dry-run **2/2 planned_ok** · planned **24**
- [x] live-path tests **29/29 PASS**（mock only · **无真实 CNINFO**）
- [x] replacement execution gate **FAIL_REVIEW_REQUIRED**（保持）

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

**禁止写入：**

- `cninfo_d_class_known_event_replacement_validation/`
- `cninfo_d_class_tiny_live_validation/`
- `cninfo_d_class_tiny_live_validation_v2/`

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv
```

| targeted_probe_id | replacement | anchor | cap |
|-------------------|-------------|--------|-----|
| DLC003R-T01 | DLC003R | 2024-02-19 | ≤12 |
| DLC006R-T01 | DLC006R | 2024-07-16 | ≤12 |

**total cap ≤ 24**

---

## 5. Approval Flag

```text
--approve-d-class-known-event-targeted-probe
```

无此 flag → live **拒绝** · **0 CNINFO**

---

## 6. Proposed Live Command（NOT APPROVED · Do not execute）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --known-event-targeted-probe \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_targeted_probe/ \
  --approve-d-class-known-event-targeted-probe
```

---

## 7. Dry-Run Command（已验证 · 可重复执行）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --known-event-targeted-probe \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

结果：**2/2 planned_ok** · planned_request_count_total **24** · CNINFO **0**

---

## 8. Explicit Exclusions

| 项 | 值 |
|----|-----|
| old DLC003/DLC006 | **no** |
| baseline rows | **no** |
| replacement live rerun | **no** |
| full tiny-live rerun | **no** |
| PDF/OCR/extraction | **no** |
| DB/MinIO/RAG | **no** |
| verified / production_ready | **no** |

---

## 9. Gate

```text
approval_status = NOT_APPROVED
approved_for_live = false
d_class_known_event_targeted_probe_live_implementation_gate = READY_FOR_APPROVAL
d_class_known_event_targeted_probe_runner_extension_gate = READY_FOR_APPROVAL
```

**CNINFO calls（本回合）：0**
