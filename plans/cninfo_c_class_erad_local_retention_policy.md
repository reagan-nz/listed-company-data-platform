# CNINFO C 类 Era D 本地保留策略（Local Retention Policy）

_生成时间：2026-07-10_

> **offline policy doc only** · **无 CNINFO** · **无 live** · **无 snapshot rebuild**  
> **Era D 未结束** · C-line **continues**

**关联：** [protected output roots](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv) · [artifact index](../outputs/validation/cninfo_c_class_erad_local_artifact_index.md) · [resume/stability plan](cninfo_c_class_erad_resume_stability_plan.md)

---

## 1. 原则

| 原则 | 说明 |
|------|------|
| **本地优先** | Era D 验收以本地 `outputs/` 可重复、可审计为准；**不入库 MinIO** |
| **git 存代码与摘要** | `lab/`、`plans/`、`outputs/validation/*summary*.md` 等可提交；大体量 harvest/snapshot **gitignore** |
| **生产根只读默认** | 规划/审计默认 read-only；写入须人批 + 备份（见 §5） |
| **测试不删生产** | `lab/cninfo_c_class_erad_cleanup_guard.py` · 仅 `_mock_*` 可清理 |
| **Option A HOLD** | 491/863 snapshot **不 rebuild** · `approved_for_snapshot_rebuild = false` |

---

## 2. 保留分类

### 2.1 KEEP_LOCAL（必须保留 · 生产研究资产）

| 类别 | 路径模式 | 磁盘（约） | git |
|------|----------|------------|-----|
| 863 primary harvest | `outputs/harvest/cninfo_c_class/{raw,normalized,quality}/` | **~325M** 整树 | **gitignore** |
| Phase 3 batch harvest | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` | **~79M** | **gitignore** |
| Phase 3.5 resume harvest | `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/` | **~2.8M** | **gitignore** |
| 491 expanded snapshot | `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` | **~25M** · **492** entries | **gitignore** |
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` | **~45M** · **863** JSON | **gitignore** |
| Status ledger | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` | **861** rows | **gitignore** |
| Status backups | `outputs/harvest/.../company_harvest_status.csv.bak_*` | 小 | **gitignore** |

### 2.2 GITIGNORE（大体积 · 可本地再生但成本高）

- `outputs/harvest/cninfo_c_class/raw/`、`normalized/`、`quality/`
- `outputs/harvest/cninfo_c_class/phase*/`（隔离批次）
- `outputs/snapshot/`（全部 snapshot JSON）
- 见 [gitignore retention notes](../outputs/validation/cninfo_c_class_erad_gitignore_retention_notes.md)

### 2.3 REGENERATABLE（可重跑 · 须人批 live/rebuild）

| 产物 | 再生方式 | Era D 当前策略 |
|------|----------|----------------|
| harvest normalized | live harvest + mapper | **HOLD** live resume |
| snapshot JSON | `build_cninfo_c_class_snapshot_batch.py --execute` | **HOLD** rebuild（Option A） |
| dry-run / audit CSV | offline runner | 可随时重跑 · CNINFO=0 |

### 2.4 VALIDATION_APPEND（小体积 · 建议保留并可选提交）

- `outputs/validation/cninfo_c_class_erad_*` — Era D 审计/分诊/apply 报告
- `outputs/validation/cninfo_c_class_phase35_*` — Phase 3.5 文档（append-only 纪律）
- 规划包 `plans/cninfo_c_class_erad_*`

### 2.5 EPHEMERAL（测试专用 · 可删）

- `**/_mock_*/**`、`**/_mock_live_test/**` — 仅测试 teardown 允许

---

## 3. 路径策略明细

### 3.1 Harvest（863_primary + batch 子树）

```
outputs/harvest/cninfo_c_class/
├── raw/              # HTTP 原始响应 · KEEP_LOCAL · gitignore
├── normalized/       # mapper 产物 · KEEP_LOCAL · gitignore
├── quality/          # company_harvest_status.csv 等 · KEEP_LOCAL · gitignore
├── phase3_batch_500_001/     # 生产 batch · protected
├── phase35_batch_500_001_resume/
├── phase2_smoke_200/
└── _mock_live_test/    # EPHEMERAL only
```

**写入政策（Era D）：** 默认 read-only；**已批准例外：** status-fix-8 对 `company_harvest_status.csv` append-only（8 行 + backup）。

### 3.2 Snapshot

```
outputs/snapshot/cninfo_c_class/
├── full/                                    # 863 · HOLD · ~45M
├── phase35_batch_500_001_expanded_success_491/  # 491 · HOLD · ~25M
├── phase3_batch_500_001_success/            # 历史 · protected
├── smoke/ · phase2_smoke_188/               # smoke · protected
```

**不 rebuild** 直至 `approved_for_snapshot_rebuild = true`（当前 **false**）。

### 3.3 Validation audit roots（Era D）

| 根 | 用途 | 写入 |
|----|------|------|
| `cninfo_c_class_erad_harvest_resume_audit/` | Slice-C-EraD-02 | validation only |
| `cninfo_c_class_erad_status_fix_8/` | 扫描 proposed rows | validation only |
| `cninfo_c_class_erad_status_fix_8_apply/` | apply ledger | validation only |
| `cninfo_c_class_erad_partial6_human_review/` | partial-6 packet | validation only |

---

## 4. Protected roots（复用 CSV）

完整清单：[cninfo_c_class_erad_protected_output_roots.csv](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv)（**12** rows）。

**Era D 扩展纪律（文档层 · 不修改 CSV 除非另开切片）：**

- validation 子树 `cninfo_c_class_erad_*` — append-only 文档 · 测试 runner 写入须 `assert_safe_erad_audit_write_path`
- status CSV backup 文件 — KEEP_LOCAL · 与生产 CSV 同目录 · 命名 `*.bak_erad_*_<timestamp>`

---

## 5. 备份纪律

### 5.1 生产 status CSV 写入前（强制）

1. 确认人批短语（status-fix-8 先例已执行）
2. `shutil.copy2` → `company_harvest_status.csv.bak_erad_<slice>_<timestamp>`
3. **append-only** 或 idempotent upsert — **禁止** 删除无关行
4. 写入 apply ledger 至 `outputs/validation/cninfo_c_class_erad_*_apply/`

**先例备份：**  
`outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv.bak_erad_status_fix_8_20260710T080910Z`（853 rows → 861 rows after apply）

### 5.2 Snapshot / normalized

- **默认禁止** 生产写入
- 未来 rebuild dry-run **必须** `_mock_*` 或专用 validation 子树

---

## 6. Cleanup 规则（测试）

| 规则 | 实现 |
|------|------|
| 禁止删生产 harvest/snapshot | `cninfo_c_class_erad_cleanup_guard.py` |
| mock 唯一可删 | `_mock_*` · `_mock_live_test` |
| tearDown 须调用 guard | Slice-C-EraD-01 硬化 · 35/35 PASS |

---

## 7. 磁盘与规模意识（本地 only · 无 MinIO）

| 合计（约） | 体量 |
|------------|------|
| C-class harvest 整树 | **~325M** |
| C-class snapshot（491+863 主轨） | **~70M** |
| Era D validation 报告 | **~2–3M**（含 audit CSV） |
| **典型 C-line 本地 footprint** | **~400M** |

**不默认 prune** 生产根；清理仅 mock 区或人批后的显式切片。

---

## 8. Holdout / 红线

- **9** holdout closed-with-caveat · **no promotion**
- `approved_for_live_resume = false` · `approved_for_snapshot_rebuild = false`
- No verified · no production_ready · no DB/MinIO/RAG

---

## 9. Gate

```
c_class_erad_local_retention_gate = PASS_OFFLINE
```

**NOT verified** · **NOT approved_for_live_resume** · **NOT approved_for_snapshot_rebuild**
