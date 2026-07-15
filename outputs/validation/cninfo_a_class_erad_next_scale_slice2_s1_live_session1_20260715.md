# A-class Era D Next-Scale Slice2 S1 — Live Session 1 Evidence

_日期：2026-07-15 · Run 12 Wave 1 · a-class-executor_

> **性质：** bounded live session 1（`AD2E501:AD2E550` = 50 cases）· metadata only · **无 PDF** · **不是 verified** · **不是 production_ready** · **未 commit / 未 push**

## Scope

| 项 | 值 |
|----|-----|
| HEAD（任务起点） | `8a5fe26` |
| mode | `erad_a_scale_500_slice2` live |
| case-range | **AD2E501:AD2E550**（session 1 · 50/100） |
| universe | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv` |
| output-root | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/` |
| approval flag | `--approve-a-class-erad-scale-500-slice2`（本会话授权范围内） |
| request cap | ≤ **240**（本会话实际 **100**） |

## Command

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --live \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --case-range AD2E501:AD2E550
```

## Live Result（Session 1）

| 指标 | 值 |
|------|-----|
| executed | **50** / 50 |
| found | **50** |
| acceptable | **50** / 50 |
| failed / not_found / network_error | **0** |
| needs_review | **0** |
| CNINFO requests | **100**（cap ≤ 240） |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |
| matching_logic | **v2** |
| raw_metadata JSON | **50**（AD2E501–AD2E550） |
| wall time | ~389 s |

### Gates

```text
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
```

- session1 acceptance threshold: **≥45/50** → `PASS_WITH_CAVEAT`（实际 **50 ≥ 45**）
- **不是 PASS** · **不是 verified** · **不是 production_ready**
- full 100-case combined gate **尚未**评估（session 2 `AD2E551:AD2E600` 未跑）

## Artifacts Created

| 产物 | 路径 |
|------|------|
| live report（当前顶层 = session1） | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/reports/a_class_erad_next_scale_slice2_s1_live_report.csv` |
| live quality | `.../reports/a_class_erad_next_scale_slice2_s1_live_quality_report.csv` |
| live summary | `.../reports/a_class_erad_next_scale_slice2_s1_live_summary.md` |
| session1 archive | `.../reports/session1/`（report / quality / summary / console log） |
| console log | `.../reports/live_session1_console_20260715.log` |
| raw metadata | `.../raw_metadata/AD2E501.json` … `AD2E550.json` |
| evidence（本文件） | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_live_session1_20260715.md` |

## Offline Live-Path Tests（mock only）

| 项 | 值 |
|----|-----|
| test file | `lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py`（新增） |
| stub update | `lab/test_cninfo_a_class_erad_next_scale_slice2_s1_runner_stub.py`（断言 live-path 测试文件存在） |
| result | **19 tests OK** · CNINFO calls **0** |
| mock summary | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_live_path_summary.md` |

覆盖：approval gate、wrong-flag、output isolation、cap 240、≥90/100 与 session1 ≥45/50 阈值、case-range session1、mock 无真实 CNINFO、PDF/verified 阻断。

## Isolation / Safety

| 检查 | 状态 |
|------|------|
| scale-200 / failed_retry / slice1 / Phase3 / A3M017 roots | **未写入**（本会话仅写 slice2 S1 root） |
| PDF / OCR / extraction / DB / MinIO / RAG | **未启用** |
| commit / push | **no**（controller 负责 commit） |
| verified / production_ready 声称 | **no** |

## Capability

**CAPABILITY_ADVANCED** — slice2 live path 已落地（mock 测试 + session1 bounded live 成功）。

## Next（controller）

1. 可选：session 2 live `AD2E551:AD2E600`（仍在 cap ≤240 内；本会话已用 100，剩余预算 140）
2. session2 后合并 100-case 报告并评估 ≥90/100 → `PASS_WITH_CAVEAT`
3. Controller commit（本 executor **不** commit / push）
