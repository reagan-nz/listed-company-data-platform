# A-class Era D Next-Scale Slice2 S1 — Live Session 2 Evidence

_日期：2026-07-15 · Run 12 Wave 2 · a-class-executor_

> **性质：** bounded live session 2（`AD2E551:AD2E600` = 50 cases）· metadata only · **无 PDF** · **不是 verified** · **不是 production_ready** · **未 commit / 未 push**

## Scope

| 项 | 值 |
|----|-----|
| HEAD（任务起点） | `594866a` |
| mode | `erad_a_scale_500_slice2` live |
| case-range | **AD2E551:AD2E600**（session 2 · 50/100） |
| universe | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv` |
| output-root | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/` |
| approval flag | `--approve-a-class-erad-scale-500-slice2`（本会话授权范围内） |
| request cap | ≤ **240**（本会话实际 **103**；session1 已用 100，累计 **203**） |

## Command

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --live \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --case-range AD2E551:AD2E600
```

## Live Result（Session 2）

| 指标 | 值 |
|------|-----|
| executed | **50** / 50 |
| found | **47** |
| acceptable | **47** / 50 |
| failed / not_found | **3**（AD2E578 / AD2E590 / AD2E598） |
| network_error | **0** |
| needs_review | **3** |
| CNINFO requests | **103**（cap ≤ 240） |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |
| matching_logic | **v2** |
| raw_metadata JSON | **50**（AD2E551–AD2E600；目录合计 100） |
| wall time | ~399 s |

### Not-found cases（session2）

| case_id | company_code | doc_type | period_end | status |
|---------|--------------|----------|------------|--------|
| AD2E578 | 688605 | semi_annual_report | 2024-06-30 | not_found / needs_review |
| AD2E590 | 688688 | quarterly_report_q3 | 2024-09-30 | not_found / needs_review |
| AD2E598 | 688758 | semi_annual_report | 2024-06-30 | not_found / needs_review |

### Gates

```text
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
```

- session2 acceptance threshold: **≥45/50** → `PASS_WITH_CAVEAT`（实际 **47 ≥ 45**）
- **不是 PASS** · **不是 verified** · **不是 production_ready**

## Artifacts Created

| 产物 | 路径 |
|------|------|
| live report（当前顶层 = session2） | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/reports/a_class_erad_next_scale_slice2_s1_live_report.csv` |
| live quality | `.../reports/a_class_erad_next_scale_slice2_s1_live_quality_report.csv` |
| live summary | `.../reports/a_class_erad_next_scale_slice2_s1_live_summary.md` |
| session2 archive | `.../reports/session2/`（report / quality / summary / console log） |
| console log | `.../reports/live_session2_console_20260715.log` |
| raw metadata | `.../raw_metadata/AD2E551.json` … `AD2E600.json` |
| evidence（本文件） | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_live_session2_20260715.md` |

## Isolation / Safety

| 检查 | 状态 |
|------|------|
| scale-200 / failed_retry / slice1 / Phase3 / A3M017 roots | **未写入**（本会话仅写 slice2 S1 root） |
| PDF / OCR / extraction / DB / MinIO / RAG | **未启用** |
| commit / push | **no**（controller 负责 commit） |
| verified / production_ready 声称 | **no** |

## Capability

**CAPABILITY_ADVANCED** — slice2 S1 session2 bounded live 完成（47/50 ≥45）；与 session1 合计见 rollup note（未 verified）。

## Next（controller）

1. 合并 100-case 评估：session1+2 = **97/100** ≥90 → `PASS_WITH_CAVEAT`（见 optional rollup；**未 verified**）
2. 可选：复核 3 个 not_found（AD2E578 / AD2E590 / AD2E598）
3. Controller commit（本 executor **不** commit / push）
