# CNINFO C-Class Phase 3 Batch 500 Output Design

_生成时间：2026-07-09_

> Phase 3 batch 500 产物路径设计。**本轮不生成 YAML** · **不执行**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# 1. Design Principles

- 每 batch 独立 output root；不复用 Phase 2 或 863 主轨
- 命名约定：`phase3_batch_500_{seq}` — 首个 batch seq = **001**
- validation 产物与 harvest/snapshot 产物路径一一对应
- snapshot 仅对 harvest QA 后的 **success subset** 构建

---

# 2. Universe & Selection Artifacts

| 产物 | 路径 | 阶段 | 状态 |
|------|------|------|------|
| universe YAML | `lab/eval_companies_c_class_phase3_batch_500_001.yaml` | selection | **未生成** |
| selection matrix | `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_matrix.csv` | selection | **未生成** |
| selection summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_summary.md` | selection | **未生成** |

**YAML 预期字段：**

- `company_count: 500`
- `batch_id: phase3_batch_500_001`
- `seed`（stratified）
- `exclusion_policy_version: phase3_v1`
- companies 列表（code / name / exchange / board / listing_status）

---

# 3. Harvest Artifacts

| 产物 | 路径 | 阶段 | 状态 |
|------|------|------|------|
| harvest root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` | harvest | **未创建** |
| raw | `.../raw/{source}/{company_code}.json` | harvest | — |
| normalized | `.../normalized/{module}/{company_code}.jsonl` | harvest | — |
| run_status | `.../run_status.json` | harvest | — |
| dry-run report | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_report.csv` | dry-run | **未生成** |
| dry-run summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_summary.md` | dry-run | **未生成** |
| live harvest report | `outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_report.csv` | live QA | **未生成** |
| live harvest QA | `outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_qa_summary.md` | live QA | **未生成** |
| company failure summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_company_failure_summary.csv` | live QA | **未生成** |
| output isolation check | `outputs/validation/cninfo_c_class_phase3_batch_500_001_output_isolation_check.md` | live QA | **未生成** |

**Expected scale（500 companies）：**

- HTTP cases: **3500**
- raw files: **3500**
- normalized direct max: **3000**
- normalized derived: **~1500**
- normalized total estimate: **~5000**

---

# 4. Snapshot Artifacts

| 产物 | 路径 | 阶段 | 状态 |
|------|------|------|------|
| success subset YAML | `lab/eval_companies_c_class_phase3_batch_500_001_success_subset.yaml` | post-QA | **未生成** |
| snapshot root | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success_subset/` | snapshot | **未创建** |
| snapshot JSON | `.../{company_code}.json` | snapshot | — |
| quality status | `.../quality/company_snapshot_status.csv` | snapshot QA | — |
| build report | `outputs/validation/cninfo_c_class_phase3_batch_500_001_snapshot_build_report.csv` | snapshot | **未生成** |
| snapshot QA summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_snapshot_qa_summary.md` | snapshot QA | **未生成** |

**Subset 命名：** `success_subset` — 仅含 harvest QA 后 all-direct-failure 排除后的干净子集（Phase 2 模式：500 → ~475+ 预期）。

---

# 5. CLI Extension（未来）

复用 Phase 2 extension 模式：

```bash
# harvest（未来 · 需批准）
python lab/harvest_cninfo_c_class.py \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001.yaml \
  --output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --approve-phase3-batch-500-harvest

# snapshot build（未来 · 需批准）
python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001_success_subset.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --output-dir outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success_subset \
  --approve-phase3-batch-500-snapshot
```

**注：** approval flag 名称待 runner extension 实现时 finalize。

---

# 6. Isolation Map

```
outputs/
├── harvest/cninfo_c_class/
│   ├── (main 863 track)          ← DO NOT WRITE
│   ├── phase2_smoke_200/         ← DO NOT WRITE
│   └── phase3_batch_500_001/     ← Phase 3 batch harvest
└── snapshot/cninfo_c_class/
    ├── full/                     ← DO NOT WRITE (863)
    ├── phase2_smoke_188/         ← DO NOT WRITE
    └── phase3_batch_500_001_success_subset/  ← Phase 3 batch snapshot
```

---

# 7. References

- [expansion plan](cninfo_c_class_phase3_batch_500_expansion_plan.md)
- [execution checklist](cninfo_c_class_phase3_batch_500_execution_checklist.md)
- Phase 2 reference: `outputs/harvest/cninfo_c_class/phase2_smoke_200/`

## 红线确认

- 本轮未生成 YAML · 未创建目录 · 未执行 harvest/snapshot
