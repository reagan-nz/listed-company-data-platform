# CNINFO C 类 Era D Harvest Resume Audit Summary

_生成时间：2026-07-10_

> **Slice：** Slice-C-EraD-02 · **dry-run only** · **CNINFO = 0** · **production harvest read-only**

---

## 执行摘要

| 项 | 值 |
|----|-----|
| Runner | `lab/run_cninfo_c_class_harvest_resume_audit.py` |
| 测试 | `lab/test_cninfo_c_class_erad_harvest_resume_audit.py` · **7/7 PASS** |
| Harvest 根 | `outputs/harvest/cninfo_c_class`（**325M**） |
| 审计输出根 | `outputs/validation/cninfo_c_class_erad_harvest_resume_audit/` |
| Universe | `lab/eval_companies_c_class_harvest_863_non_bse.yaml`（**863**） |
| CNINFO | **0** |

---

## 863_primary resume 状态计数

| resume_state | count | 占比 |
|--------------|-------|------|
| complete | **805** | 93.3% |
| needs_review | **58** | 6.7% |
| partial | **0** | — |
| missing | **0** | — |
| unknown | **0** | — |

**合计：** **863**

### 状态映射（runner 约定）

| resume_state | 判定规则 |
|--------------|----------|
| complete | `company_harvest_status=complete` 且 10 个 matrix normalized 源齐全 |
| partial | `partial`/`failed` 或源缺口但有部分文件 |
| missing | 无 status 行且无 normalized 文件 |
| needs_review | 磁盘有文件但无 status 行；或 status complete 与源计数不一致 |
| unknown | 非 863 universe 且无数据 |

---

## 扫描子树

| subtree | status_csv | complete | partial | needs_review |
|---------|------------|----------|---------|--------------|
| **863_primary** | yes | 805 | 0 | 58 |
| phase3_batch_500_001 | yes | 473 | 17 | 10 |
| phase35_batch_500_001 | yes | 408 | 81 | 11 |
| phase35_batch_500_001_resume | yes | 6 | 1 | 22 |
| phase2_smoke_200 | yes | 181 | 12 | 7 |

**说明：** batch 子树按各自 `company_harvest_status.csv` 中出现的公司审计；863_primary 以 863 universe 为准。

---

## 磁盘备注（只读 du）

| 路径 | 体量 |
|------|------|
| `outputs/harvest/cninfo_c_class` | 325M |
| `outputs/harvest/cninfo_c_class/phase3_batch_500_001` | 79M |
| `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume` | 2.8M |
| `outputs/snapshot/cninfo_c_class/full` | 45M |

生产 harvest/snapshot **未删除、未重写**。

---

## Live resume 建议

| 维度 | 结论 |
|------|------|
| 863 主轨 | **hold** — 805/863 complete；无 partial/missing |
| 58 needs_review | **offline_review_first** — 多为 status ledger 与磁盘源计数不一致，非明确 live 缺口 |
| 后续 live | **deferred** — 须另开 Slice-C-EraD-02b 规划 + 人批 |
| Snapshot rebuild | **unnecessary now** — 863 full snapshot 已存在；**NOT APPROVED** |

---

## Holdout / 红线

- **9 holdout** 保持 closed-with-caveat · **no promotion**
- **C35R016** 不 promote
- **无 snapshot rebuild**
- **无 A/B/D mutation**

---

## 产出物

| 文件 | 说明 |
|------|------|
| [reports/c_class_erad_harvest_resume_audit_report.csv](cninfo_c_class_erad_harvest_resume_audit/reports/c_class_erad_harvest_resume_audit_report.csv) | 公司级审计行 |
| [reports/c_class_erad_harvest_resume_audit_summary.md](cninfo_c_class_erad_harvest_resume_audit/reports/c_class_erad_harvest_resume_audit_summary.md) | runner 摘要 |
| [reports/c_class_erad_harvest_resume_audit_metrics.csv](cninfo_c_class_erad_harvest_resume_audit/reports/c_class_erad_harvest_resume_audit_metrics.csv) | 指标 |
| [reports/c_class_erad_harvest_resume_audit_source_ledger.csv](cninfo_c_class_erad_harvest_resume_audit/reports/c_class_erad_harvest_resume_audit_source_ledger.csv) | 源级 ledger |
| [run_meta.json](cninfo_c_class_erad_harvest_resume_audit/run_meta.json) | 运行元数据 |

---

## Gate

```
c_class_erad_harvest_resume_audit_gate = PASS_OFFLINE
```

**不是 bare PASS** · **不是 live_ready** · **不是 verified**

保留：

- `c_class_erad_cleanup_hardening_gate = PASS_OFFLINE`
- `c_class_erad_resume_stability_planning_gate = READY_FOR_APPROVAL`
- `phase35_clean_push_gate = PASS_WITH_CAVEAT`
- `phase35_holdout_closed_with_caveat_signoff_gate = PASS_WITH_CAVEAT`
- `approval_status = NOT_APPROVED` · `approved_for_live = false` · `approved_for_snapshot_rebuild = false`

---

## 下一步建议

**Slice-C-EraD-03 已完成** — 见 [snapshot rebuild readiness summary](cninfo_c_class_erad_snapshot_rebuild_readiness_summary.md) · **Option A HOLD rebuild**

**人批后：** 保持 NOT APPROVED rebuild · 可选 Slice-C-EraD-03b mock dry-run 设计
