# CNINFO C-Class Company Registry Schema 审批清单

_生成时间：2026-07-08_

> **性质：** `company_registry` schema 正式审批清单（Era C Phase 4）。**仅文档** · **不生成 registry 数据** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `registry_design_gate = READY_FOR_SCHEMA_APPROVAL`

**依据：** [company registry design](cninfo_c_class_company_registry_design.md) · [lineage design](../outputs/validation/cninfo_c_class_company_registry_lineage_design.md) · [registry planning summary](../outputs/validation/cninfo_c_class_company_registry_planning_summary.md)

---

# 1. Schema 目的确认

## 1.1 company_registry 解决的问题

| 问题域 | registry 能力 |
|--------|---------------|
| **公司身份统一** | `company_id` + `org_id` + `company_code` 构成跨 YAML 切片、跨 era 的稳定身份键 |
| **证券代码变更** | `previous_code` · `legacy_code` 记录 83/87 → 920 等变更链 |
| **更名历史** | `rename_history` 保留简称/全称变更，避免 YAML 快照断链 |
| **org_id 冲突** | `org_id_conflict_flag` 标记同 org_id 多 code，指定 canonical 身份 |
| **BSE legacy 映射** | `legacy_code` · `active_status` · hold 政策分层 920 active / 83-87 legacy |
| **退市 / ST / hold 状态** | `delisted_flag` · `st_flag` · `hold_flag` · `suspended_flag` 统一市场状态治理 |

## 1.2 架构定位确认

| 确认项 | 结论 |
|--------|------|
| registry 是 **未来身份层（future identity layer）** | **确认** |
| registry **不是** harvest 输出 | **确认** |
| registry **不是** snapshot 输出 | **确认** |
| registry **不是** YAML universe 文件的立即替代 | **确认** |
| 当前操作输入仍为 `eval_companies_*.yaml` | **确认** |
| 未来过渡：registry → 派生 universe slice → harvest / snapshot | **确认** |

```mermaid
flowchart LR
    Registry[company_registry 身份治理层]
    YAML[eval_companies YAML 派生视图]
    Harvest[harvest]
    Snapshot[snapshot]
    Registry -.->|未来派生| YAML
    YAML --> Harvest --> Snapshot
```

---

# 2. 24 字段审批表

共 **24** 个核心字段，分 6 组。审批状态：`approved` · `approved_with_caveat` · `pending`。

| field_name | group | purpose | source | example | approval_status | decision_note |
|------------|-------|---------|--------|---------|-----------------|---------------|
| `company_id` | identity | registry 内部稳定主键，与 code 解耦 | 派生规则 `{exchange}:{org_id}` | `SZSE:gssz0000009` | **approved** | 跨 code 变更关联键；派生规则在实现阶段固化 |
| `company_code` | identity | 当前 6 位证券代码（harvest scode） | 863 YAML `stock_code` | `000009` | **approved** | 与 snapshot 文件名、harvest runner 直接对齐 |
| `company_name` | identity | 当前简称 | YAML `short_name` / `company_name` | `中国宝安` | **approved** | 展示层主字段 |
| `company_full_name` | identity | 法定全称 | normalized basic profile `legal_name` | `中国宝安集团股份有限公司` | **approved** | 863 normalized 已有覆盖 |
| `english_name` | identity | 英文名称 | normalized basic profile `english_name` | `China Baoan Group Co., Ltd.` | **approved** | 国际化与去重辅助 |
| `exchange` | security | 交易所 | YAML `exchange` | `SZSE` | **approved** | 板块路由与 orgId 前缀推断 |
| `board` | security | 上市板块 | YAML `board` | `szse_main` | **approved** | universe 分批与统计 |
| `listing_status` | security | 上市状态 | security observe / 名称推断 | `listed` | **approved** | 与 `delisted_flag` 交叉验证 |
| `active_status` | security | 代码活跃状态 | 规则派生 | `active` · `legacy_code` · `duplicate_code` | **approved_with_caveat** | BSE 83/87→920 场景须 canonical 规则；实现前不用于 harvest scode 自动路由 |
| `org_id` | identity_mapping | CNINFO 组织 ID | YAML `orgid` | `gssz0000009` | **approved** | API 参数与跨 code 关联核心键 |
| `legacy_code` | identity_mapping | 历史证券代码（BSE 83/87 层） | BSE mapping / 人工 | `839729` | **approved_with_caveat** | 标识 legacy 层；**不**作为 harvest scode；须未来 probe 验证映射后方可升 `mapped` |
| `previous_code` | identity_mapping | 最近一次变更前代码 | 变更事件记录 | `839729` | **approved_with_caveat** | BSE 重编号场景依赖；增量事件源待实现 |
| `rename_history` | identity_mapping | 更名历史（JSON 数组） | 人工 / 公告解析（未来） | `[{"date":"2020-01","old":"深宝安A","new":"中国宝安"}]` | **approved_with_caveat** | 结构批准；**首轮派生可为空**；公告解析为后续轮次 |
| `org_id_conflict_flag` | identity_mapping | 同 org_id 多 code 标记 | 规则：同 org_id 计数>1 | `true`（839729/920729） | **approved_with_caveat** | BSE 永顺生物案例已验证；canonical 指向规则须在派生脚本中固化 |
| `st_flag` | market_status | 是否 ST/*ST | 名称规则 `*ST`/`ST` | `false` | **approved** | caveat 标注用；不自动 hold |
| `delisted_flag` | market_status | 是否退市 | 名称含「退」/ listing_status | `false` | **approved** | hold / document_archive 路由 |
| `suspended_flag` | market_status | 是否暂停上市 | 未来公告 / security | `false` | **approved_with_caveat** | 字段批准；**当前无稳定数据源**；首轮派生默认 `false` |
| `hold_flag` | market_status | 是否进入 hold 侧轨 | hold YAML / 规则 | `false`（863 主线） | **approved** | 26 all6 hold 与 BSE legacy 共用侧轨机制 |
| `harvest_support_status` | C-class support | harvest 支持状态 | 规则 + quality CSV | `completed_863` | **approved** | 枚举已定义；863 主线种子可直接标注 |
| `snapshot_support_status` | C-class support | snapshot 支持状态 | 规则 + status CSV | `completed_863` | **approved** | 与 harvest 状态解耦，支持 partial 场景 |
| `source` | quality | 记录来源（血缘） | 派生脚本标注 | `harvest_863_yaml` | **approved** | Era B/C lineage 追溯必需 |
| `last_updated` | quality | 最后更新时间 | ISO8601 UTC | `2026-07-08T00:00:00Z` | **approved** | 增量刷新与审计 |
| `confidence` | quality | 身份置信度 | 规则派生 | `high` · `medium` · `low` | **approved** | 多源冲突时优先级裁决 |
| `notes` | quality | 自由备注 | 人工 / 自动 | `889 all6 hold; HTTP 500` | **approved** | QA 与 hold 审计 |

### 审批统计

| 状态 | 数量 |
|------|------|
| `approved` | **18** |
| `approved_with_caveat` | **6** |
| `pending` | **0** |
| `rejected` | **0** |
| **合计** | **24** |

**approved_with_caveat 字段（6）：** `active_status` · `legacy_code` · `previous_code` · `rename_history` · `org_id_conflict_flag` · `suspended_flag`

### 观察层扩展字段（不计入 24 core gate）

| field_name | group | purpose | source | example | approval_status | decision_note |
|------------|-------|---------|--------|---------|-----------------|---------------|
| `security_type` | security | 证券类型 | security observe `secType`（侧车） | `001001` | **approved** | 观察层；不进主 harvest gate；待 product layer 决策后接入 |

---

# 3. 审批决议

## 3.1 总体决议

| 项 | 决议 |
|----|------|
| **24 字段 schema** | **批准**（无 rejected · 无 pending） |
| **6 组结构** | identity · security · identity_mapping · market_status · C-class support · quality — **维持** |
| **registry 定位** | 身份治理层 — **确认** |
| **YAML 替代策略** | 不立即替代 — **确认** |

## 3.2 Caveat 处理原则

| caveat 字段 | 实现阶段要求 |
|-------------|--------------|
| `legacy_code` / `previous_code` | BSE 映射须未来 targeted probe；本轮不执行 |
| `rename_history` | 首轮可为空数组；不阻塞派生 |
| `org_id_conflict_flag` | canonical code 规则写入派生脚本（920 优先于 83/87） |
| `active_status` | `duplicate_code` 行不进入 harvest scode |
| `suspended_flag` | 默认 `false`；待 security observe 或公告层接入后更新 |

---

# 4. BSE Identity Decision

> **本轮：** 政策确认 only · **无 probe** · **无 endpoint 测试**

## 4.1 分层决议

| 层级 | 代码前缀 | 决议 | harvest 策略 |
|------|----------|------|--------------|
| **BSE 920 active** | `92xxxx` | **future supported candidate** | 独立子轨；不混入 non-BSE 863 主 gate |
| **BSE 83/87 legacy** | `83xxxx` / `87xxxx` | **legacy_hold** | `hold_flag=true` · `harvest_support_status=unsupported` |

## 4.2 永顺生物案例（839729 / 920729）

| 项 | 决议 |
|----|------|
| **同 org_id** | `gfbj0839729` — **确认** |
| **canonical identity** | **`920729`** — **确认** |
| **839729（legacy）** | `active_status=duplicate_code` · `hold_flag=true` |
| **920729（current）** | `active_status=active` · harvest 唯一 scode |
| **映射验证** | 须未来 probe — **本轮 defer** |

## 4.3 BSE 与 schema 字段关系

| BSE 概念 | 对应 schema 字段 |
|----------|------------------|
| 920 active 候选 | `company_code` · `harvest_support_status=supported` |
| 83/87 legacy hold | `legacy_code` · `hold_flag` · `active_status` |
| 同 org_id 冲突 | `org_id_conflict_flag` |
| canonical 指向 | `company_code`（920 行） |

---

# 5. Registry Readiness Gate

| 项 | 值 |
|----|-----|
| **Schema 字段数** | **24** |
| **审批 gate** | **`registry_schema_approval_gate = PASS`** |
| **前置 design gate** | `registry_design_gate = READY_FOR_SCHEMA_APPROVAL` → **已满足** |

### 剩余 blocker（不阻塞 schema 批准）

| blocker | 说明 |
|---------|------|
| registry implementation not started | 派生脚本 `derive_cninfo_c_class_company_registry_draft.py` 未编写 |
| universe reconciliation not started | 6124 vs 863 合并规则未落地 |
| BSE mapping execution not started | targeted probe 未执行（政策已批准，执行 defer） |

---

# 6. 红线确认

- **无 CNINFO** · **无 live** · **无 harvest**
- **不生成** registry 数据 · **不创建** registry candidate CSV
- 不修改 raw / normalized / field_inventory / snapshot JSON
- 不写 verified · 不 testing_stable_sample · 不入库 / MinIO / RAG

**下一步（规划）：** [schema approval summary](../outputs/validation/cninfo_c_class_registry_schema_approval_summary.md) · registry 派生脚本设计
