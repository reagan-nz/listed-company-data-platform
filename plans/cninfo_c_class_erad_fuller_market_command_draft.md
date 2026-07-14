# CNINFO C 类 Era D — Fuller-Market Command Draft

_生成时间：2026-07-10_

> **NOT APPROVED for live.** 下列命令为 **未来执行形状** · 本任务 **不执行** live / CNINFO。

---

## 0. 本规划轮（已执行 · offline）

```bash
cd listed_company_data_collector

# Part 1: 50 closure ledger（read-only 派生 · CNINFO=0）
# 产出: outputs/validation/cninfo_c_class_erad_needs_review_50_closure_ledger.csv

# Part 2: slice1 universe draft（read-only 派生 · CNINFO=0）
# 产出: outputs/validation/cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv
```

**CNINFO 预期：0**

---

## 1. 预备 — 从 slice1 CSV 生成 eval YAML（offline · **已完成**）

```bash
cd listed_company_data_collector

python3 lab/build_cninfo_c_class_fuller_market_slice_yaml.py
# 产出: lab/eval_companies_c_class_fuller_market_slice1_200.yaml
#       outputs/validation/cninfo_c_class_erad_fuller_market_slice1_overlap_recheck.md
```

**CNINFO 预期：0** · builder tests **5/5 PASS**

---

## 2. Slice 1 Harvest Dry-run（**已完成 · offline**）

```bash
cd listed_company_data_collector

python3 lab/harvest_cninfo_c_class.py --dry-run \
  --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --output-root outputs/harvest/cninfo_c_class/_mock_fuller_market_slice1_dryrun/ \
  --output-csv outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_dryrun_report.csv \
  --output-md outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_dryrun_summary.md \
  --output-validation-md outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_dryrun_validation_summary.md
```

**CNINFO 预期：0** · gate **`c_class_erad_fuller_market_slice1_dryrun_gate = PASS_OFFLINE`**

**结果：** companies **200** · planned_http_cases **1400** · matrix_rows **2000**

---

## 3. Slice 1 Harvest Live（NOT APPROVED · 禁止本任务执行 · 路径已接线）

```bash
# 须人批短语 + gates:
#   c_class_erad_fuller_market_planning_gate = APPROVED
#   c_class_erad_fuller_market_slice1_live_path_gate = APPROVED
#   c_class_erad_fuller_market_slice1_dryrun_gate = PASS_OFFLINE
#   approved_for_live = true

# Session 1（建议 limit=100）:
# python3 lab/harvest_cninfo_c_class.py --live \
#   --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --output-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --approve-fuller-market-slice1-harvest \
#   --limit 100 --resume

# Session 2（续跑）:
# python3 lab/harvest_cninfo_c_class.py --live \
#   --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --output-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --approve-fuller-market-slice1-harvest \
#   --limit 100 --resume
```

**CNINFO 预期（全批 200）：** ~1400 HTTP · ~2000 点估计 · ≤2800 cap

**本任务：** live path **wired** · **NOT executed**

---

## 4. Post-harvest Audit（offline · 可复用）

```bash
cd listed_company_data_collector

python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \
  --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
  --protected-roots-csv outputs/validation/cninfo_c_class_erad_protected_output_roots.csv \
  --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --output-root outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_audit/
```

**CNINFO 预期：0**

---

## 5. Snapshot Build（NOT APPROVED · separate gate）

```bash
# 须另批 approved_for_snapshot_rebuild 或 slice-specific snapshot approval
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/fuller_market_slice1_200/
```

**863 full rebuild：禁止（Option A HOLD）**

---

## 6. 863 Resume Audit（已完成 · 参照）

```bash
python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \
  --output-root outputs/validation/cninfo_c_class_erad_harvest_resume_audit_post_fix8/
```

**CNINFO 预期：0** · 813+50

---

## Red Lines

Refuse `--live` without explicit human approval · No 863 mutation · No commit/push
