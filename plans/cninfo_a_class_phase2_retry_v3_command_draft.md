# CNINFO A 类 Phase 2 Retry v3 命令草稿

_最后更新：2026-07-10_

> **状态：NOT APPROVED**  
> **approved_for_live：false**  
> **请勿执行 live 命令**

---

## 输出根

```text
outputs/validation/cninfo_a_class_phase2_metadata_retry_v3/
```

## 批准 Flag

```text
--approve-a-class-phase2-retry-v3
```

## Universe CSV

```text
outputs/validation/cninfo_a_class_phase2_retry_v3_universe.csv
```

---

## Runner 状态

`lab/run_cninfo_a_class_phase2_metadata_expansion.py` **已支持**：

- `--retry-v3` dry-run + **live path implemented**
- `--approve-a-class-phase2-retry-v3` approval guard
- live report writers（report · summary · quality）
- execution gate logic（≥6/8 acceptable → `PASS_WITH_CAVEAT`）
- dry-run **8/8 planned_ok** · runner test **23/23 PASS**
- live-path test **25/25 PASS**（mock CNINFO · **无真实 live**）

**Gates:**

```text
a_class_phase2_retry_v3_runner_extension_gate = READY_FOR_APPROVAL
a_class_phase2_retry_v3_live_implementation_gate = READY_FOR_APPROVAL
```

---

## Dry-run 命令（已完成）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-v3 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_phase2_retry_v3_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry_v3/
```

**结果：** 8/8 planned_ok · CNINFO **0**

---

## 未来 Live Retry v3 命令（NOT APPROVED · Do not execute）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-v3 \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_phase2_retry_v3_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry_v3/ \
  --approve-a-class-phase2-retry-v3
```

**Live 报告路径（future）：**

- `reports/a_class_phase2_retry_v3_report.csv`
- `reports/a_class_phase2_retry_v3_summary.md`
- `reports/a_class_phase2_retry_v3_quality_report.csv`

---

## 执行前条件

| 项 | 状态 |
|----|------|
| precheck gate | `PASS_WITH_CAVEAT`（已完成） |
| runner extension | **已实现** |
| live path implementation | **已实现**（mock tests **25/25 PASS**） |
| dry-run | **8/8 planned_ok** · CNINFO **0** |
| tests | runner **23/23** · live-path **25/25 PASS** |
| 人工批准 | **待完成** |
| universe | **8** case · successful 12 excluded |

---

## 红线

- **不要** 在未批准时执行 live 命令
- **不要** 重跑 successful 12
- **不要** 修改 original / v1 / v2 / precheck 报告
- **不要** PDF / OCR / DB / MinIO / RAG

**NOT APPROVED · Do not execute live.**
