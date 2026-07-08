# CNINFO C-Class establishment_date Mapper Patch Plan

_生成时间：2026-07-08_

> **性质：** mapper patch **规划 only**。**PLANNED_NOT_IMPLEMENTED** · **无 CNINFO** · **无 live** · **无 raw 修改** · **本轮不实施 patch**

---

## 1. Current Issue

`establishment_date`（成立日期）在 review_later 复判与 promotion planning 中被评为 **promote candidate**，但当前状态为：

```
recommended_target = normalized_core_candidate_after_mapper_patch
```

**问题：** `map_company_basic_profile()` 未将 raw 字段导出至 basic normalized 记录；863 harvest 中成立日期仅存在于 `raw/basic_profile/*.json` 的 `basicInformation[0].F010D`，`normalized/company_basic_profile/` 无 `establishment_date` 键。

**fill 证据：** 863/863（100%）— 离线核对 `raw/basic_profile`。

**阻塞：** promotion candidate approval 已排除本字段；待 patch 规划完成后进入 implementation 轮次。

---

## 2. Raw Source

| 项 | 值 |
|----|-----|
| source_id | `cninfo_company_basic_profile` |
| endpoint | `getCompanyIntroduction` |
| raw 路径 | `raw_records.basicInformation[0]` |
| **raw field** | **`F010D`**（成立日期） |
| 示例 | `2004-03-09` |
| retrieval | `endpoint_found`（863 家） |

**确认方式：** 现有 `outputs/harvest/cninfo_c_class/raw/basic_profile/*.json`；**未请求 CNINFO**。

**注意：** `listing_date` 使用 **`F006D`**（上市日期），与 `F010D`（成立日期）不同字段，不可混用。

---

## 3. Expected Normalized Field

| normalized field | 类型 | 说明 |
|------------------|------|------|
| **`establishment_date`** | date (ISO-8601) | 公司成立日期 |

**目标产物：** `normalized/company_basic_profile/{company_code}.json` 增加 `establishment_date` 键（当 raw 非空时）。

---

## 4. Mapper Patch Design

### 修改位置

| 文件 | 函数 |
|------|------|
| `lab/cninfo_c_class_mappers.py` | `map_company_basic_profile()` |

### 设计要点

1. 在 `optional_fields` 中增加：
   ```python
   "establishment_date": normalize_date(basic.get("F010D")),
   ```
   与现有 `listing_date: normalize_date(basic.get("F006D"))` 并列。

2. **不新增 CNINFO 请求** — 仅读取已有 raw `basicInformation[0].F010D`。

3. **不修改 raw** — patch 仅影响 mapper 与后续 offline re-map。

4. **离线 re-map 路径（规划）**
   - 新脚本或复用 pattern：`lab/remap_cninfo_c_class_basic_profile_offline.py`（待 implementation 轮次创建）
   - 输入：`raw/basic_profile/`
   - 输出：`normalized/company_basic_profile/` only
   - **本轮不执行**

5. **schema 对齐：** `schemas/c_class/c_company_basic_profile.schema.json` 若尚无 `establishment_date`，implementation 前需确认 draft schema 槽位（本轮不改 schema 文件，仅在规划中标注）。

6. **harvest derived 影响：** contact / business_scope / industry derived 源**不**派生 establishment_date；仅 basic profile 落槽。

---

## 5. Test Fixture Requirements

在 `fixtures/c_class/basic_profile/` 增加或扩展 case（implementation 轮次）：

| case_id | F010D raw | 期望 establishment_date | 说明 |
|---------|-----------|-------------------------|------|
| `estab_case_normal` | `2004-03-09` | `2004-03-09` | 正常 ISO 日期 |
| `estab_case_empty` | `""` 或缺失键 | 字段不出现或 `null` | 空日期 |
| `estab_case_nonstandard` | `2004/03/09` 或 `2004年3月9日` | 依 `normalize_date()` 行为 | 非标准格式；以现有 normalize_date 为准 |
| `estab_case_null` | `null` | 字段不出现 | 源端 null |

**验收：** `lab/seed_cninfo_c_class_basic_profile_fixtures.py` + schema validation **PASS**（implementation 轮次）。

---

## 6. Acceptance Criteria

| # | 条件 |
|---|------|
| 1 | mapper unit / fixture test **PASS** |
| 2 | **不请求 CNINFO** |
| 3 | **不修改 raw** |
| 4 | 可 **offline re-map** `normalized/company_basic_profile/` only |
| 5 | field_fill_rate ≥ 99%（与 raw F010D 对齐） |
| 6 | QA **不新增** P0 严重 flag |
| 7 | **不写 verified** |
| 8 | **不升级** testing_stable_sample / registry stable |

**升格链：** patch + re-map + fixture PASS → `establishment_date` 可进入 **promotion candidate approval**（第二轮）→ inventory 升格批准（单独轮次）。

---

## 7. Current Status

```
establishment_date_patch_status = IMPLEMENTED
```

| 项 | 状态 |
|----|------|
| patch plan | **完成**（本文档） |
| mapper 代码 | **未改** |
| offline re-map | **未执行** |
| promotion approval | **pending** patch |

---

## 红线确认

- 未请求 CNINFO · 未重跑 harvest · raw/normalized 未改（本轮）
- 未改 field inventory · 未写 verified
