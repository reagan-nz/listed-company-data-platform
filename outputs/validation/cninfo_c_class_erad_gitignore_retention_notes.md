# CNINFO C 类 Era D — Gitignore Retention Notes

_生成时间：2026-07-10_

> **本文件为说明文档 only** · **默认不修改 `.gitignore`** · CNINFO = 0

---

## 当前 `.gitignore` 相关条目（摘录）

来源：仓库根 `listed_company_data_collector/.gitignore`

```
outputs/harvest/cninfo_c_class/raw/
outputs/harvest/cninfo_c_class/normalized/
outputs/harvest/cninfo_c_class/quality/
outputs/harvest/cninfo_c_class/phase*/
outputs/harvest/**/run_status.json
outputs/harvest/**/company_harvest_status.csv
outputs/snapshot/
```

以及 Phase 3.5 部分 validation 大 CSV 模式（`cninfo_c_class_phase*_harvest_*report.csv` 等）。

---

## 应保持 gitignore（大体积 · 本地 KEEP）

| 模式 / 路径 | 原因 |
|-------------|------|
| `outputs/harvest/cninfo_c_class/raw/` | HTTP 原始 · ~数百 MB 级 |
| `outputs/harvest/cninfo_c_class/normalized/` | mapper 产物 |
| `outputs/harvest/cninfo_c_class/quality/` | status CSV · field fill 等 |
| `outputs/harvest/cninfo_c_class/phase*/` | 隔离 batch harvest |
| `outputs/snapshot/` | 全部 snapshot JSON（491+863 **~70M**） |
| `company_harvest_status.csv.bak_*` | 隐式：父目录 quality/ 已 ignore |

**纪律：** 即使 status-fix-8 已写入生产 CSV，**仍不提交** harvest quality 文件入 git。

---

## 可提交（小体积 · 规划/审计摘要）

| 类别 | 示例 |
|------|------|
| `plans/cninfo_c_class_erad_*.md` | 策略 · signoff · retention |
| `lab/cninfo_c_class_erad_*.py` | guard · offline runner |
| `outputs/validation/cninfo_c_class_erad_*summary.md` | 门控摘要 |
| `outputs/validation/cninfo_c_class_erad_*checklist.md` | 批准清单 |
| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | 保护根 |
| `outputs/validation/cninfo_c_class_erad_*_ledger.csv` | 小 CSV（<100KB 级） |

---

## 可选提交（中等 CSV · 团队约定）

| 路径 | 说明 |
|------|------|
| `cninfo_c_class_erad_harvest_resume_audit/reports/*.csv` | **~2M** · 可 gitignore 或 LFS；summary 必保留 |
| `cninfo_c_class_erad_needs_review_58_triage_ledger.csv` | **12K** · 通常可提交 |

**建议：** 大 audit CSV 本地保留；git 仅提交 `*_summary.md` + `run_meta.json`。

---

## 不应提交

- 任何 `outputs/snapshot/**/*.json`（491/863 生产 JSON）
- 生产 harvest raw/normalized  bulk
- `.bak_erad_*` 备份（留在本地 · 已在 ignore 树下）
- secrets · `.env` · credentials

---

## 若未来需改 `.gitignore`（非本任务）

仅当新增 Era D validation 根产生 **>1MB** 重复 CSV 时，考虑追加：

```
# outputs/validation/cninfo_c_class_erad_harvest_resume_audit/reports/*.csv
```

**须单独切片 + 人批** · 本包 **不修改** `.gitignore`。

---

## 与 Option A HOLD 对齐

- snapshot JSON **继续 gitignore**
- 远端 `origin/main` 已 land Phase 3.5 **文档/代码**（`a12d5fb`+`522c89b`）· **不含** 491 本地 JSON
- 本地 retention = 研究 MVP 资产 · 与 git 发布解耦
