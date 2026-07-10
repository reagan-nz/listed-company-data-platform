# CNINFO A 类 Phase 2 CNINFO Reachability Precheck 命令草稿

_生成时间：2026-07-09 · 更新：runner + dry-run 完成_

> **状态：NOT APPROVED**  
> **approved_for_live：false**  
> **请勿执行 live 命令**

---

## 输出根

```text
outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/
```

## 批准 Flag

```text
--approve-a-class-phase2-cninfo-reachability-precheck
```

## 候选 CSV

```text
outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv
```

---

## Dry-run 命令（已完成 · CNINFO **0**）

```bash
python lab/run_cninfo_a_class_phase2_cninfo_reachability_precheck.py \
  --dry-run \
  --candidates-csv outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/
```

**结果：** 3/3 planned_ok · planned_requests=3 · test **23/23 PASS**

---

## 未来 Live Precheck 命令（草稿 only · NOT APPROVED）

```bash
python lab/run_cninfo_a_class_phase2_cninfo_reachability_precheck.py \
  --live \
  --candidates-csv outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/ \
  --approve-a-class-phase2-cninfo-reachability-precheck
```

---

## 执行前条件

| 项 | 状态 |
|----|------|
| runner | **已实现** |
| dry-run | **3/3 planned_ok** · CNINFO **0** |
| tests | **23/23 PASS** |
| 人工批准 | **待完成** |
| request cap | **≤ 6** |

---

## 红线

- **不要** 在本回合执行 live 命令
- **不要** 用于 retry_v3
- **不要** 包含 successful 12
- **不要** PDF / OCR / DB / MinIO / RAG

**NOT APPROVED · Do not execute live.**
