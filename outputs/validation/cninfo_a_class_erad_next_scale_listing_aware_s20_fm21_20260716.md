# A-FM-21 — S20 six not_found isolated retry（AD2E1540–1545 / 605*）

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-21_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **12** · dry-run → bounded 6-case live retry · **未 mutate S1–S20 live 主根** · **无 commit/push**  
> **Prior：** A-FM-20 S20 AD2E1501–1550 live 44/50 `FAIL_REVIEW_REQUIRED`（CNINFO=87；6×not_found 均为 605*）

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-21** |
| track | A |
| executor | a-class-executor |
| controller_execution_allowed | false |
| 目标 | 仅为 AD2E1540–1545 建孤立 retry 根；核查 orgid/listing/date；诚实 live 重试；合并证据评估是否达 PASS_WITH_CAVEAT（≥45/50） |
| 保护 | **禁止** mutate S1–S20 live 主根（含 A-FM-20 S20 `reports/*live*`） |

## 2. Precheck（orgid / listing / date）

| case_id | code | listing_date | expected_period | org_id_offline | listing_before_period | prior last_err |
|---------|------|--------------|-----------------|----------------|-----------------------|----------------|
| AD2E1540 | 605133 | 2021-02-24 | 2024-09-30 | 9900039741 | yes | SSLEof / protocol violation |
| AD2E1541 | 605151 | 2020-12-15 | 2024-12-31 | 9900032989 | yes | SSLEof / protocol violation |
| AD2E1542 | 605222 | 2020-07-31 | 2024-12-31 | 9900039833 | yes | SSLEof / protocol violation |
| AD2E1543 | 605296 | 2021-05-28 | 2024-12-31 | 9900033227 | yes | SSLEof / protocol violation |
| AD2E1544 | 605305 | 2021-05-06 | 2024-12-31 | gfbj0831344 | yes | SSLEof / protocol violation |
| AD2E1545 | 605333 | 2020-08-18 | 2024-12-31 | 9900038389 | yes | SSLEof / protocol violation |

```text
prior_class   = ssl_transport_eof_with_orgid_already_resolved
not_cause     = listing_date_after_period | orgid_missing | empty_matching_window
likely_cause  = transient_ssl_transport (cninfo_request_count=0 on S20 main live)
retry_strategy = isolated_subdir_live_retry_same_matching_v2
```

证据：S20 主 live raw_metadata 已带正确 org_id，但 `cninfo_request_count=0`；同片 605* 邻居（AD2E1537–1539 / 1546–1550）均已 found —— 非前缀/板块结构性空窗。

## 3. Isolated retry root

| 项 | 路径 |
|----|------|
| universe（文档） | `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_retry_universe_20260716.csv` |
| precheck ledger | `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_precheck_20260716.csv` |
| output root | `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/retry_not_found_1540_1545/` |
| runner 输入 universe | 复用 S20 plus50 CSV + `--case-range AD2E1540:AD2E1545`（S6 timeout-retry 同构） |

Live 命令：

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_plus50_universe_20260716.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/retry_not_found_1540_1545 \
  --case-range AD2E1540:AD2E1545 \
  --live
```

## 4. Verified metrics

| 指标 | 值 |
|------|-----|
| dry-run | **6/6** planned_ok · planned_requests=12 · CNINFO=0 |
| retry live | **6/6** found · quality=pass · CNINFO=**12** · orgid_fallback hits=0 |
| found recovery count | **6** |
| S20 first-pass（A-FM-20 主根，未改） | 44/50 |
| **combined S20+retry** | **50/50** acceptable |
| execution gate（combined evidence） | `PASS_WITH_CAVEAT`（阈值 ≥45/50） |
| S1–S20 live 主根 mutated | **no**（mtime 全量校验通过；S20 主 live 仍 2026-07-16 00:55:01） |

## 5. Tests / wall times

| 步骤 | 结果 | wall |
|------|------|------|
| precheck offline（orgid/listing） | 6/6 orgid hit · listing≪period | ~3s |
| `test_cninfo_a_class_erad_listing_aware_s20_runner.py` | 5/5 OK | ~0.01s |
| dry-run 6-case retry | 6/6 planned_ok | **~0.30s** |
| **live 6-case retry** | 6/6 PASS_WITH_CAVEAT · CNINFO=12 | **~46.8s** |
| offline combined merge | 50/50 | ~0.5s |

## 6. Files

### Created
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_retry_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_precheck_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/retry_not_found_1540_1545/`（独立 retry 子根 · dry-run + live + raw_metadata×6）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_recovery_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_combined_live_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_combined_live_quality_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_20260716.md`（本报告）

### Modified
- `lab/test_cninfo_a_class_erad_listing_aware_s20_runner.py`（断言 retry 子根 `retry_not_found_1540_1545` 可通过 S20 output-root 校验）
- 无 runner / builder 生产逻辑修改（复用既有 listing-aware S20 + case-range 路径）

### Not touched（保护）
- 封闭 S1 **live** 主报告
- listing-aware S2–S19 **live** 主报告
- A-FM-20 S20 **live 主根** `reports/*live*`（mtime 未变；仍保留 6×not_found 原状）
- B/C/D · commit/push

## 7. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D）：

1. `lab/test_cninfo_a_class_erad_listing_aware_s20_runner.py`
2. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_retry_universe_20260716.csv`
3. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_not_found_precheck_20260716.csv`
4. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20/retry_not_found_1540_1545/`（整子根；`raw_metadata/` 按 `.gitignore` 排除；`reports/live_fm21_retry_console_20260716.log` 不入 allow-list）
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_recovery_ledger_20260716.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_combined_live_report_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_combined_live_quality_report_20260716.csv`
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s20_fm21_20260716.md`

**Exclude：** S20 主根 `reports/dryrun_fm20_console_*` / `live_fm20_console_*`；retry `live_fm21_retry_console_*`；任意 `raw_metadata/`；B/C/D；未请求的 A-FM-20 wiring commit 决策外文件。

## 8. Gate

```text
a_class_fm21_s20_not_found_retry_gate = PASS_WITH_CAVEAT
a_class_fm20_listing_aware_s20_first_pass_gate = FAIL_REVIEW_REQUIRED  # 主根未改写，仍 44/50
a_class_fm21_combined_s20_plus_retry_gate = PASS_WITH_CAVEAT           # 50/50 combined evidence
cninfo_calls = 12
found_recovery_count = 6
s1_s20_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 9. Next

```text
Controller：审阅 combined 50/50 证据 → 可选 track-A-only commit（A-FM-20 wiring ∪ A-FM-21 retry/combined）；
勿把 retry 结果静默写回 S20 主 live CSV（除非明确批准 merge）；
可继续 S21 listing-aware 扩片；勿 mutate S1–S20 live 主根；无 B/C/D；无 push。
```
