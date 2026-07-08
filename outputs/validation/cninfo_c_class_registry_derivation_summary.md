# CNINFO C-Class Registry Candidate Derivation Summary

_生成时间：2026-07-08_

> **性质：** Registry candidate 派生设计收口摘要。**仅设计** · **不生成 registry 数据**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**前置 gate：** `registry_schema_approval_gate = PASS`

---

## Current State

| 项 | 状态 |
|----|------|
| Registry schema | **已批准**（24 core 字段） |
| Schema approval gate | `registry_schema_approval_gate = PASS` |
| BSE identity policy | **已决策**（920 supported candidate · 83/87 legacy_hold） |
| Universe lineage design | **已完成** |
| Derivation design | **本轮完成** |

---

## Derivation Status

| 项 | 状态 |
|----|------|
| 派生设计文档 | **完成** |
| 24 字段映射 CSV | **完成** |
| 实现（`derive_cninfo_c_class_company_registry_candidate.py`） | **未启动** |
| registry candidate 数据行 | **未生成**（本轮红线） |

---

## Field Mapping

| 项 | 值 |
|----|-----|
| **映射字段数** | **24** |
| 映射表路径 | [cninfo_c_class_registry_derivation_mapping.csv](cninfo_c_class_registry_derivation_mapping.csv) |
| 设计文档路径 | [cninfo_c_class_registry_derivation_design.md](../../plans/cninfo_c_class_registry_derivation_design.md) |

### 映射类型分布

| mapping_type | 字段数 |
|--------------|--------|
| direct | 6 |
| enrichment | 2 |
| rule_derived | 11 |
| lookup | 2 |
| default | 2 |
| merge | 1 |

---

## Input Artifacts

| 产物 | 路径 | 角色 |
|------|------|------|
| 863 harvest YAML | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` | Primary 种子 |
| 26 hold YAML | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` | Hold 侧轨 |
| BSE 920 YAML | `lab/eval_companies_c_class_smoke_195_bse_920_active.yaml` | BSE active |
| BSE legacy YAML | `lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml` | BSE legacy |
| 6124 baseline | `lab/eval_companies_full_market_2024.yaml` | Era B 填充 |
| 863 snapshot | `outputs/snapshot/cninfo_c_class/full/*.json` | Enrichment |
| Snapshot status | `outputs/snapshot/cninfo_c_class/full/quality/company_snapshot_status.csv` | snapshot_support_status |

---

## Known Caveats

| caveat | 说明 | 派生策略 |
|--------|------|----------|
| **BSE legacy mapping** | 83/87 与 920 同 org_id；无 probe | legacy 行 `unsupported`；canonical=920 |
| **rename_history** | 无公告解析源 | 首轮 `[]` |
| **org_id conflict** | 839729/920729 等同 org_id 多 code | `org_id_conflict_flag=true`；920 为 canonical |
| **delisted/ST status** | 仅名称规则推断 | `st_flag` / `delisted_flag`；不自动 hold |
| **suspended_flag** | 无稳定数据源 | 默认 `false` |
| **6124 填充** | 5221+ 行仅 baseline 质量 | `confidence=low` · `unsupported` |

---

## Remaining Blockers

| blocker | 说明 |
|---------|------|
| registry candidate generator 未实现 | 派生脚本待编写 |
| universe reconciliation 未执行 | 6124 与 863 合并未落地 |
| BSE mapping probe 未执行 | legacy→920 映射政策已设计，执行 defer |
| product layer 决策 | security_type 观察层未接入 |

以上 blocker **不阻塞**派生设计；阻塞的是 candidate 数据生成。

---

## Next Step

**registry candidate generator 实现**（`lab/derive_cninfo_c_class_company_registry_candidate.py`）

实现轮次仍须遵守：

- 离线-only · 不 CNINFO · 不 live · 不 harvest
- 输出至 `config/` 或 `outputs/validation/`（非 production registry）
- 不改 raw / normalized / snapshot

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 registry build
- 无 registry candidate 数据行
- 无 raw / normalized / snapshot / field_inventory 修改
- 无 DB · MinIO · RAG · verified · testing_stable_sample

---

## eraC 章节

- 本节对应 **§7cg Registry Candidate Derivation Design**
- 上一节 §7cf Company Registry Schema Approval 已完成
