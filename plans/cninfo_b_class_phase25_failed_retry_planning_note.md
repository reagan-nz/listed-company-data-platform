# CNINFO B 类 Phase 2.5 Failed Case — Isolated Retry Planning Note

_生成时间：2026-07-09_

> **性质：** 未来 isolated retry 规划 only · **NOT APPROVED** · **无 CNINFO** · **无 live** · **无 rerun**

---

## Status

```text
NOT APPROVED for execution
```

本文件仅为规划备忘；**本回合不实现 runner 变更、不执行 retry**。

---

## Retry Universe

| 项 | 值 |
|----|-----|
| retry cases | **5** only |
| case IDs | B25E003 · B25E008 · B25E032 · B25E039 · B25E040 |
| successful cases | **45** — **must NOT be rerun** |
| overlap Phase 1/2 | **0**（与主 batch 一致） |

---

## Scope

| 允许 | 禁止 |
|------|------|
| metadata retrieval | PDF download |
| announcement lineage | PDF parse |
| pdf URL lineage | OCR · section extraction |
| EP001/EP002/EP004/EP005 | DB write · MinIO write · RAG |
| | verified · production_ready |

**metadata only** — 与 Phase 2.5 主 batch 边界一致

---

## Output Root

```text
outputs/validation/cninfo_b_class_phase25_failed_retry/
```

**隔离要求：**

- 不得写入 `cninfo_b_class_phase25_expansion/` 主 batch 产物
- 不得覆盖 Phase 1 tiny live · TLC002 retry · Phase 2 expansion · C-class harvest

---

## Approval Flag Placeholder

```bash
# NOT APPROVED — future use only
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase25_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase25_failed_retry/ \
  --approve-b-class-phase25-failed-retry
```

**Approval flag（占位）：** `--approve-b-class-phase25-failed-retry`

> Runner 当前 **不支持** 此 flag；未来回合需扩展 runner + tests + approval package 后方可执行。

---

## Failure Summary

| case_id | failure_type | retry_priority |
|---------|--------------|----------------|
| B25E003 | network_timeout | high |
| B25E008 | proxy_503 | high |
| B25E032 | network_timeout | high |
| B25E039 | ep002_orgid_resolution_failed | medium |
| B25E040 | ep002_orgid_resolution_failed | medium |

**schema_impact：** none（全 5 例）  
**quality_impact：** retry_needed（全 5 例）

---

## Preconditions（未来批准前）

1. 人工审阅 [failed-case triage](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv)
2. 创建 `cninfo_b_class_phase25_failed_retry_universe.csv`（5 case only）
3. 扩展 runner 支持 `--approve-b-class-phase25-failed-retry` + output root isolation
4. dry-run + tests PASS
5. 显式人工批准

---

## Red Lines

- No retry in this round
- No rerun of 45 successful cases
- No 100-company expansion
- No verified · No production_ready · No testing_stable_sample upgrade
