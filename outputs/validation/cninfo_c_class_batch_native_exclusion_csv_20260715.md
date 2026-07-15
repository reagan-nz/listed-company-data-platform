# CNINFO C-class — Batch Builder Native `--exclusion-csv` (Run 14)

_生成时间：2026-07-15_  
_性质：离线能力接线 · **CNINFO = 0** · **无 production EXECUTE** · **NOT verified**_

---

## 1. Gap closed

Run 12 剩余：`build_cninfo_c_class_snapshot_batch.py` **仍未原生接受** `--exclusion-csv`（仅 mock-root adapter 有语义）。

本包：将 `--exclusion-csv` 接到 batch builder 标准 dry-run 路径。

---

## 2. Command（demo）

```bash
python3 lab/build_cninfo_c_class_snapshot_batch.py \
  --dry-run \
  --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
  --output-root outputs/validation/_batch_exclusion_csv_native_dryrun/ \
  --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv
```

| Metric | Value |
|--------|-------|
| sample_mode | `exclusion_csv_filter` |
| company_count_before_filter | 200 |
| excluded_unique_count | 10 |
| company_count | **190** |
| exclusion_csv_native_dryrun_gate | **PASS_OFFLINE** |
| snapshot_batch_dryrun_gate | PASS_WITH_CAVEAT |
| CNINFO | **0** |
| snapshot_json_written | 0 |
| execute_production_snapshot_rebuild | false |

---

## 3. Safety

- `--exclusion-csv` + `--execute` → `EXCLUSION_CSV_EXECUTE_FORBIDDEN`（exit 2）
- 输出根必须在 `outputs/validation/`；拒绝 full/phase2/phase3/phase35 生产 snapshot 根
- Phase 3.5 路径不支持 `--exclusion-csv`（显式 unsupported）

---

## 4. Tests

```text
python3 lab/test_cninfo_c_class_snapshot_batch_exclusion_csv.py
→ 8 tests OK
```

摘要：`outputs/validation/cninfo_c_class_batch_native_exclusion_csv_test_summary_20260715.md`

---

## 5. Capability gain

```text
capability_gain = CAPABILITY_ADVANCED
capability_gain_expected = true
```

Batch builder 现可原生消费 Wave1 exclusion reconcile，无需仅依赖 mock-root adapter。

**仍禁止：** production snapshot EXECUTE（人控）。

---

## 6. Async note（Run 14）

本 C-wave 为长任务轨：`15:18:18` 开始接线，期间 A 于 `15:21:41` 完成并 commit（`d202962`），证明 **C EXECUTING 未阻塞 A**。
