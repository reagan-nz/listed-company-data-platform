# CNINFO C-Class Company Registry Planning Summary

_生成时间：2026-07-08_

> **性质：** Company Registry Draft Design 规划收口摘要。**仅规划** · **不生成 registry 数据**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Gate：** `registry_design_gate = READY_FOR_SCHEMA_APPROVAL`

---

## 1. 本轮交付

| # | 产出 | 路径 |
|---|------|------|
| 1 | Registry 设计（schema 24 字段 + BSE identity §4） | [plans/cninfo_c_class_company_registry_design.md](../../plans/cninfo_c_class_company_registry_design.md) |
| 2 | Universe lineage 设计 | [cninfo_c_class_company_registry_lineage_design.md](cninfo_c_class_company_registry_lineage_design.md) |
| 3 | Registry readiness matrix | [cninfo_c_class_registry_readiness_matrix.csv](cninfo_c_class_registry_readiness_matrix.csv) |
| 4 | 本摘要 | 本文件 |

---

## 2. 核心结论

### 2.1 Registry 定位

- **身份治理层**，非数据采集层
- **不立即替代** `eval_companies_*.yaml`；YAML 逐步降级为 registry 派生视图
- 目标 pipeline：`company_registry → harvest / snapshot`

### 2.2 Schema

- **24** 核心字段，6 组：identity · security · identity mapping · market status · C-class support · quality
- BSE 扩展字段记入 identity mapping：`legacy_code` · `current_code` · `legacy_status` · `mapping_confidence`

### 2.3 Lineage

| 来源 | 规模 | registry 角色 |
|------|------|---------------|
| Era B 全市场 | 6124 | 最大候选池 |
| Era C 863 主线 | 863 | `completed_863` 种子 |
| Hold 侧轨 | 26 | `hold_flag=true` |
| BSE 920 / legacy | smoke | 分层种子 |

### 2.4 BSE 政策（registry 内固化）

- **920 active：** 可 supported；独立子轨
- **83/87 legacy：** legacy_hold · unsupported
- **839729/920729：** 同 org_id · canonical=920729

---

## 3. Readiness Matrix 摘要

| 维度 | 状态 | 优先级 |
|------|------|--------|
| schema_24_fields | ready | high |
| era_c_863_lineage | ready | high |
| era_b_6124_baseline | ready | high |
| identity_mapping | ready（待 canonical 政策） | high |
| bse_83_87_to_920 | ready（待 probe） | medium |
| harvest/snapshot 集成 | not_ready | low |
| product_layer_decision | blocked | medium |

---

## 4. 红线确认

- 无 CNINFO · 无 live · 无 harvest 重跑
- 不改 raw / normalized / field_inventory / snapshot JSON
- 不写 verified · 不 testing_stable_sample · 不入库
- **本轮不生成** registry 数据行

---

## 5. 推荐下一步

1. **registry schema 审批**（24 字段 + BSE 扩展）
2. **lineage mapping 规则**落地到派生脚本设计
3. **BSE identity 政策**固化（probe 仍 defer）
4. **`derive_cninfo_c_class_company_registry_draft.py`** 设计（未来轮次执行）
5. **product layer / security observe** 决策（与 registry 并行）

---

## 6. eraC 章节

- 本节对应 **§7ce Company Registry Draft Design**
- 上一节 §7cd Full Market Expansion Planning 已完成
