# CNINFO B 类 Era D Fuller Next-Slice — Command Draft

_生成时间：2026-07-10 · live-path mock wired_

> **DO NOT RUN LIVE** · **CNINFO = 0** · **NOT APPROVED** · live-path **mock only**

---

## 1. Flags（Runner Extension + Live Path）

| Flag | 说明 |
|------|------|
| `--erad-b-fuller-slice2` | 启用 fuller next-slice2 模式（BD2E501–800 · 300 cases） |
| `--approve-b-class-erad-fuller-slice2` | live 模式人批 gate（dry-run 不需要） |
| `--universe-csv` | 指向 fuller slice2 draft universe CSV |
| `--output-root` | 隔离输出根（见下） |
| `--case-range` | 可选 session split（如 `BD2E501:BD2E650`） |
| `--live` | live 模式（**须单独批准** · **mock tests only until approved**） |

---

## 2. Output Root（Write-Block Enforced）

```
outputs/validation/cninfo_b_class_erad_fuller_next_slice2/
```

**Write-blocks（runner 拒绝）：**

- `outputs/validation/cninfo_b_class_erad_scale_200/`
- `outputs/validation/cninfo_b_class_erad_next_scale_slice1/`
- `outputs/validation/cninfo_b_class_phase3_100_expansion/`
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/`
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/`
- A/C/D validation / harvest / snapshot production roots

Mock-only live outputs: `_mock_live_test/` under slice2 root.

---

## 3. Dry-Run Shape（CNINFO = 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2/ \
  --dry-run
```

**Result（2026-07-10 reconfirm）：** 300/300 `planned_ok` · planned requests **600** · cap **≤720** · CNINFO **0**

See [runner extension summary](../outputs/validation/cninfo_b_class_erad_fuller_next_slice2_runner_extension_summary.md).

---

## 4. Live Shape（DO NOT RUN · Separate Approval · Wired · Mock-Tested Only）

Live path implemented: `process_erad_fuller_slice2_live` · acceptance **≥270/300** → `PASS_WITH_CAVEAT`.

**Session 1（须先执行）：**

```bash
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --approve-b-class-erad-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2/ \
  --live \
  --case-range BD2E501:BD2E650
```

**Session 2（Session 1 完成后 · ≥4h gap）：**

```bash
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --approve-b-class-erad-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2/ \
  --live \
  --case-range BD2E651:BD2E800
```

See [live-path summary](../outputs/validation/cninfo_b_class_erad_fuller_next_slice2_live_path_summary.md).

---

## 5. Red Lines

| 约束 | 政策 |
|------|------|
| CNINFO | 本任务 **0**（mock only） |
| Rerun BD2E001–500 | **禁止**（lineage-reference only） |
| BD2E090/092 in primary slice | **禁止**（side-track only） |
| PDF / DB / MinIO / RAG | **禁止** |
| verified / production_ready | **禁止宣称** |

---

## 6. Gate

```text
b_class_erad_fuller_next_slice_planning_gate = READY_FOR_APPROVAL
b_class_erad_fuller_next_slice_runner_extension_gate = READY_FOR_APPROVAL
b_class_erad_fuller_next_slice_live_path_gate = READY_FOR_APPROVAL
```

Approval phrase for live:

```
I approve B-class Era D fuller slice2 live metadata validation.
```
