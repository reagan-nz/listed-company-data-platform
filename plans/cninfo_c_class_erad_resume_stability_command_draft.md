# CNINFO C 类 Era D Resume / Stability 命令草稿

_生成时间：2026-07-10_

> **NOT APPROVED for live or snapshot rebuild.**  
> 下列命令仅供 **Slice-C-EraD-01 硬化实现后** 的 offline 验证草稿。本任务 **不执行** live / rebuild。

---

## 0. 规划轮（本任务 · 已执行范围）

```bash
# 无 CNINFO · 无 live · 仅文档与 ledger 生成
# 见 outputs/validation/cninfo_c_class_erad_* 与 plans/cninfo_c_class_erad_resume_stability_plan.md
```

---

## 1. Slice-C-EraD-01 — Cleanup 硬化回归（已完成 · offline）

```bash
cd listed_company_data_collector

python3 lab/test_cninfo_c_class_erad_cleanup_hardening.py          # 7/7 PASS
python3 lab/test_cninfo_c_class_phase35_expanded_snapshot_builder.py  # 17/17 PASS
python3 lab/test_cninfo_c_class_phase3_success_snapshot_approval.py   # 11/11 PASS
```

**CNINFO 预期：** **0** · **合计 35/35 PASS**

---

## 2. Slice-C-EraD-01 — 保护根只读审计（offline · 可选）

```bash
cd listed_company_data_collector

# 列出生产 harvest 根体量（只读）
du -sh outputs/harvest/cninfo_c_class/phase3_batch_500_001 2>/dev/null || true
du -sh outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume 2>/dev/null || true
du -sh outputs/harvest/cninfo_c_class 2>/dev/null || true

# 列出生产 snapshot 根体量（只读）
du -sh outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491 2>/dev/null || true
du -sh outputs/snapshot/cninfo_c_class/full 2>/dev/null || true
```

**禁止：** `rm -rf` on any path in [protected_output_roots.csv](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv) except `_mock_*`.

---

## 3. Slice-C-EraD-02 — 863 Harvest Resume Audit Dry-run（已完成 · offline）

```bash
cd listed_company_data_collector

python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \
  --harvest-root outputs/harvest/cninfo_c_class \
  --protected-roots-csv outputs/validation/cninfo_c_class_erad_protected_output_roots.csv \
  --output-root outputs/validation/cninfo_c_class_erad_harvest_resume_audit/

python3 lab/test_cninfo_c_class_erad_harvest_resume_audit.py   # 7/7 PASS
```

**CNINFO 预期：** **0** · **gate `c_class_erad_harvest_resume_audit_gate = PASS_OFFLINE`**

**863_primary：** complete **805** · needs_review **58** · partial **0** · missing **0**

---

## 4. 延后切片 — 491 Snapshot Rebuild Dry-run（NOT APPROVED）

```bash
# 须另批 approved_for_snapshot_rebuild=true
# python lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
#   --resume-harvest-root outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume \
#   --universe-yaml lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_dryrun/
```

**注意：** dry-run 输出根 **必须** 使用 `_mock_*` 隔离目录，不得指向生产 `phase35_batch_500_001_expanded_success_491/`.

---

## 红线

No CNINFO（规划轮）· No live harvest · No production snapshot rebuild · No holdout promotion · No A/B/D root writes
