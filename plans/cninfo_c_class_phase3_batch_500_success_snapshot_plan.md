# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Plan

_生成时间：2026-07-09_

> Phase 3 batch 500 success-subset snapshot 离线规划。**无 CNINFO** · **无 harvest 重跑** · **无 snapshot build**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

**planning gate：** `phase3_batch_500_success_snapshot_planning_gate = DESIGN_COMPLETE`

---

# 1. Input Universe

```
500 harvest universe (phase3_batch_500_001)
        ↓
  identity caveat triage
        ↓
491 snapshot eligible (identity-clean)
        ↓
  9 excluded caveat (temporary)
```

| 阶段 | 数量 | 来源 |
|------|------|------|
| harvest universe | **500** | [company_harvest_status.csv](../outputs/harvest/cninfo_c_class/phase3_batch_500_001/quality/company_harvest_status.csv) |
| identity caveat excluded | **9** | [failure_identity_caveat_ledger.csv](../outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv) |
| snapshot eligible | **491** | [success_snapshot_subset_design.csv](../outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv) |

**Harvest YAML：** [eval_companies_c_class_phase3_batch_500_001.yaml](../lab/eval_companies_c_class_phase3_batch_500_001.yaml)

---

# 2. Snapshot Purpose

Build company snapshot **only** for identity-clean successful companies.

- 目标：为 Phase 3 batch 500 中 **491** 家 identity-clean 公司生成隔离 snapshot JSON
- 范围：company snapshot（18 模块映射）；security 仍 observe-only
- 非目标：verified · DB · MinIO · RAG · registry merge

---

# 3. Output Isolation

| 项 | 路径 |
|----|------|
| **snapshot root** | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` |
| harvest root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |
| subset design | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv` |

**隔离规则：**

| 禁止覆盖 | 路径 |
|----------|------|
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` |
| Phase 2 smoke 188 | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` |
| Phase 2 harvest | `outputs/harvest/cninfo_c_class/phase2_smoke_200/` |
| 863 harvest 主轨 | `outputs/harvest/cninfo_c_class/raw/` · `normalized/` |

**未来 CLI 扩展（规划 only）：**

```bash
# 未批准 · 勿执行
python lab/build_cninfo_c_class_snapshot_batch.py \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001_success_subset.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --output-root outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success
```

---

# 4. Exclusion Policy

Do **not** snapshot:

| identity_status | count | snapshot_policy |
|-----------------|-------|-----------------|
| `delisted_or_reorganized` | **7** | `exclude` |
| `manual_identity_review` | **2** | `exclude_pending_review` |

**Temporary exclusion：** 9 家 identity caveat 公司不进入 snapshot universe，直至 registry / identity 复核完成。

**不在本轮排除（仍纳入 491）：** partial / failed harvest 但 identity-clean 的公司（如 `300055` 等）— snapshot build QA 阶段再判定。

---

# 5. Expected Scale

| 项 | 值 |
|----|-----|
| snapshot JSON count | **491** |
| modules per company | **18**（mapper 覆盖） |
| security module | observe-only（不绑定主 gate） |

---

# 6. Preflight Dependencies

| 依赖 | gate | 状态 |
|------|------|------|
| Phase 3 live harvest | `harvest_full_gate` | **FAIL**（487 complete；可接受 caveat） |
| Identity triage | `phase3_batch_500_failure_identity_triage_gate` | **READY_FOR_REVIEW** |
| Snapshot planning | `phase3_batch_500_success_snapshot_planning_gate` | **DESIGN_COMPLETE** |
| Snapshot dry-run | — | **未执行** |
| Snapshot build | — | **未批准** |

---

# 7. Next Step

**Phase 3 batch 500 success-subset snapshot dry-run planning**（491 家 · 隔离 output root · **无 build**）

---

# 8. Red Lines

- **no CNINFO**
- **no live**
- **no harvest rerun**
- **no snapshot JSON build**（本轮）
- **no raw / normalized modification**
- **no registry implementation**
- **no verified**
