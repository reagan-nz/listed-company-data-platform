# CNINFO C 类 Era D — Local Artifact Index

_生成时间：2026-07-10 · read-only inventory_

> 体量为本地 `du` 快照（2026-07-10）· **CNINFO = 0** · 仅索引 · 不修改磁盘

---

## Harvest

| 路径 | 用途 | 规模（约） | git 政策 | protection |
|------|------|------------|----------|------------|
| `outputs/harvest/cninfo_c_class/` | **863_primary** raw/normalized/quality | **325M** | gitignore | C-ROOT-003 production |
| `outputs/harvest/cninfo_c_class/raw/` | CNINFO HTTP 原始 | （含于上） | gitignore | production |
| `outputs/harvest/cninfo_c_class/normalized/` | mapper 产物 · 10 源矩阵 | （含于上） | gitignore | production |
| `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` | 公司 harvest 状态 ledger | **861** rows | gitignore | append-only（人批后） |
| `.../company_harvest_status.csv.bak_erad_status_fix_8_20260710T080910Z` | status-fix-8 备份 | **853** rows | gitignore | KEEP backup |
| `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` | Phase 3.5 原批 500 harvest | **79M** | gitignore | C-ROOT-001 |
| `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/` | Phase 3.5 isolated resume（28） | **2.8M** | gitignore | C-ROOT-002 |
| `outputs/harvest/cninfo_c_class/phase35_batch_500_001/` | Phase 3.5 别名目录 | （若存在） | gitignore | C-ROOT-001B |
| `outputs/harvest/cninfo_c_class/phase2_smoke_200/` | Phase 2 smoke | 小 | gitignore | C-ROOT-009 |
| `outputs/harvest/cninfo_c_class/_mock_live_test/` | 测试 ephemeral | 可变 | gitignore | mock only |

---

## Snapshot

| 路径 | 用途 | 规模（约） | git 政策 | protection |
|------|------|------------|----------|------------|
| `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` | **491** expanded success JSON | **25M** · **492** files | gitignore | C-ROOT-004 · **HOLD** |
| `outputs/snapshot/cninfo_c_class/full/` | **863** full company snapshot | **45M** · **863** JSON | gitignore | C-ROOT-005 · **HOLD** |
| `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` | Phase 3 历史子集 | 小 | gitignore | C-ROOT-006 |
| `outputs/snapshot/cninfo_c_class/smoke/` | 10-company smoke | 小 | gitignore | C-ROOT-007 |
| `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` | Phase 2 smoke 188 | 小 | gitignore | C-ROOT-008 |

---

## Era D Validation / Audit Roots

| 路径 | 用途 | 规模 | git 政策 |
|------|------|------|----------|
| `outputs/validation/cninfo_c_class_erad_harvest_resume_audit/` | Slice-C-EraD-02 audit CSV | **~2.2M** | 可提交 summary；大 CSV 可选 |
| `outputs/validation/cninfo_c_class_erad_status_fix_8/` | status-fix-8 scan | **~16K** | 可提交 |
| `outputs/validation/cninfo_c_class_erad_status_fix_8_apply/` | status-fix-8 apply ledger | **~12K** | 可提交 |
| `outputs/validation/cninfo_c_class_erad_partial6_human_review/` | partial-6 packet | **~24K** | 可提交 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | 保护根 CSV | **4K** | **应提交** |
| `outputs/validation/cninfo_c_class_erad_option_a_hold_ledger.csv` | HOLD cohort 决策 | **4K** | 可提交 |
| `outputs/validation/cninfo_c_class_erad_needs_review_58_triage_ledger.csv` | 58 分诊 | **12K** | 可提交 |

---

## Era D Planning / Policy（本包）

| 路径 | 用途 |
|------|------|
| [plans/cninfo_c_class_erad_local_retention_policy.md](../../plans/cninfo_c_class_erad_local_retention_policy.md) | 保留策略 |
| [cninfo_c_class_erad_local_artifact_index.md](cninfo_c_class_erad_local_artifact_index.md) | 本索引 |
| [cninfo_c_class_erad_gitignore_retention_notes.md](cninfo_c_class_erad_gitignore_retention_notes.md) | gitignore 说明 |
| [cninfo_c_class_erad_local_retention_summary.md](cninfo_c_class_erad_local_retention_summary.md) | 摘要 |

---

## Lab（硬化 / 审计 runner）

| 路径 | 用途 |
|------|------|
| `lab/cninfo_c_class_erad_cleanup_guard.py` | 生产根清理保护 |
| `lab/run_cninfo_c_class_harvest_resume_audit.py` | 863 resume audit dry-run |
| `lab/run_cninfo_c_class_erad_status_fix_8_scan.py` | status-fix-8 扫描 |
| `lab/run_cninfo_c_class_erad_status_fix_8_apply.py` | status-fix-8 apply（须人批） |
| `lab/run_cninfo_c_class_erad_partial6_human_review_scan.py` | partial-6 扫描 |

---

## 索引维护

- 新 Era D 切片产出应 **append** 本表或 `cninfo_c_class_erad_local_artifact_index.md` 同级 summary
- 大体量路径变更须同步 [protected_output_roots.csv](cninfo_c_class_erad_protected_output_roots.csv)
