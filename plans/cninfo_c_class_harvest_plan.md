# CNINFO C-Class Harvest Plan（Era C Phase 4）

_生成时间：2026-07-07_

> **性质：** 基于已完成的 C-class source validation 与 [field inventory](cninfo_c_class_field_inventory.md) 的 **harvest 执行方案（planning only）**。**本轮不执行 harvest**；**不请求 CNINFO**；**不写 verified**；**不升级 testing_stable_sample**。

**前置：**

- [field inventory](cninfo_c_class_field_inventory.md) · [field inventory CSV](../outputs/validation/cninfo_c_class_field_inventory.csv)
- [source status decision](cninfo_c_class_source_status_decision.md)
- [889 post-retry decision](cninfo_c_class_889_post_retry_decision.md)
- [889 rerun retry plan](cninfo_c_class_889_rerun_retry_plan.md)

**红线（本轮及规划期）：** 不跑 live · 不创建 harvest runner · 不 YAML backfill · 不入库 · 不修改 B/D/Phase1 文件

---

## 1. Harvest 目标

### 1.1 当前阶段定位

**不是**重新验证 source。C-class 六主源 + security observe 已在 stable 200、889 rerun、partial-fail retry 等 live 中完成稳定性验证；[source status decision](cninfo_c_class_source_status_decision.md) 与 [post-retry decision](cninfo_c_class_889_post_retry_decision.md) 已给出阶段性结论。

**目标是：** 将已经确认可获取的 CNINFO C-class 数据保存为**长期数据资产**（文件级 harvest 产物），供后续分析与产品化使用。

### 1.2 本阶段关注

| 维度 | 说明 |
|------|------|
| **数据获取** | 按 universe 与 source scope 批量拉取（未来 live harvest） |
| **原始保存** | Raw Layer 完整保留 CNINFO 响应与请求元数据 |
| **字段映射** | 按 field inventory 将 raw → normalized（仅 normalized_core） |
| **质量记录** | Quality Layer 记录 fill_rate、retrieval_status、hold 与 caveat |

### 1.3 本阶段不涉及

- 数据库设计 / PostgreSQL 入库
- MinIO / 对象存储迁移
- 向量数据库
- RAG / LLM 应用
- verified / testing_stable_sample 升级
- 新 endpoint discovery

---

## 2. Harvest Universe

### 2.1 Candidate universe

| 项 | 数量 |
|----|------|
| 母本 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` |
| non-BSE universe（原始） | **889** |
| all6 hold（`eval_companies_c_class_889_rerun_all6_hold.yaml`） | **26** |
| **harvest candidate** | **863** |

**计算：**

```
889 non-BSE universe
− 26 all6 hold
= 863 harvest candidate
```

### 2.2 Hold 公司处理

| 规则 | 说明 |
|------|------|
| **保留** | 26 家仍在 hold YAML 与 quality 层 `hold_company_list.csv` 中 |
| **不删除** | 不从母本 candidate YAML 物理剔除 |
| **不 harvest** | 本轮 harvest **不请求**这 26 家 |
| **标注** | `excluded_by_status_review` · `hold_reason=sample_quality_or_status_review` |

### 2.3 明确不进入主 harvest 的 universe

| universe | 处理 |
|----------|------|
| **26 all6 hold** | 排除于 harvest candidate（见上） |
| **BSE legacy（83/87 hold）** | 不进入 non-BSE 主 harvest；独立 side-track |
| **abnormal_review（3 家）** | 不进入主 harvest |
| **BSE 920** | 不混入 non-BSE 主 harvest；若未来扩 harvest 需独立 universe |

### 2.4 未来 harvest 样本文件（规划）

| 文件（待派生） | 说明 |
|----------------|------|
| `lab/eval_companies_c_class_harvest_863_non_bse.yaml` | 889 母本 − 26 hold；**planning 阶段不创建** |

派生逻辑：从 `eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` 排除 `eval_companies_c_class_889_rerun_all6_hold.yaml` 中的 `stock_code`。

---

## 3. Source Harvest Scope

### 3.1 Direct fetch sources

以下 source **单独 HTTP 请求**；harvest 时写入 Raw Layer，再经 mapper 写入 Normalized Layer（除 observe 外）。

#### `cninfo_company_basic_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_company_basic_profile` |
| 当前状态 | **proceed_testing_with_caveat** |
| 进入 harvest | **是** |
| caveat | 困难样本 / basic empty 敏感；key fill 在可达子集极高 |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/basic_profile/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/company_basic_profile/{company_code}.json` |

#### `cninfo_executive_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_executive_profile` |
| 当前状态 | **proceed_testing_with_caveat** |
| 进入 harvest | **是** |
| caveat | **executive caveat** — 困难样本敏感；empty_but_valid 可能 residual |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/executive_profile/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/executive_profile/{company_code}.jsonl`（一人一行） |

#### `cninfo_share_capital_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_share_capital_profile` |
| 当前状态 | **source_partial** |
| 进入 harvest | **是** |
| caveat | **source_partial** — 不可假设全市场非空；empty_but_valid 合法 |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/share_capital_profile/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/share_capital_profile/{company_code}.jsonl` |

#### `cninfo_top_shareholders_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_top_shareholders_profile` |
| 当前状态 | **proceed_testing_with_caveat** |
| 进入 harvest | **是** |
| caveat | reachable ≠ non_empty；empty_but_valid **不算失败** |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/top_shareholders_profile/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/top_shareholders_profile/{company_code}.jsonl` |

#### `cninfo_top_float_shareholders_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_top_float_shareholders_profile` |
| 当前状态 | **source_partial** |
| 进入 harvest | **是** |
| caveat | **top_float source_partial** — non_empty 低于 reach；单独统计 |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/top_float_shareholders_profile/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/top_float_shareholders_profile/{company_code}.jsonl` |

#### `cninfo_dividend_financing_profile` → **dividend_history**

| 项 | 值 |
|----|-----|
| source_id（registry） | `cninfo_dividend_financing_profile` |
| harvest 逻辑名 | **`dividend_history`** |
| 当前状态 | **proceed_testing** |
| 进入 harvest | **是** |
| caveat | **≠ financing** — 仅历史分红；YAML 命名窄化 **GO（决策 only）**，**本轮不执行** backfill |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/dividend_history/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/dividend_history/{company_code}.jsonl` |
| mapper 缺口 | ~~需补 map_dividend_history draft~~ → **规格+代码已完成**（[dividend_history mapping](cninfo_c_class_dividend_history_mapping.md) · §7bc） |

### 3.2 Derived sources

以下字段**来自 basic profile**，harvest 时**不单独请求 CNINFO**；在 Normalized Layer 由 basic raw/normalized 派生写出。

| source_id | derived_from | 进入 harvest | Normalized 输出 |
|-----------|--------------|--------------|-----------------|
| `cninfo_company_contact_profile` | basic `basicInformation[0]` | **是**（派生） | `normalized/contact_profile/{company_code}.json` |
| `cninfo_company_business_scope` | basic F015V/F016V/F017V | **是**（派生） | `normalized/business_scope/{company_code}.json` |
| `cninfo_company_industry_profile` | basic F032V/F044V/MARKET | **是**（派生） | `normalized/industry_profile/{company_code}.json` |

**caveat：** 完全依赖 basic 可达性；basic fail 则 derived 无数据。

### 3.3 Observe-only

#### `cninfo_company_security_profile`

| 项 | 值 |
|----|-----|
| source_id | `cninfo_company_security_profile` |
| 当前状态 | **observe_only** |
| 进入 harvest | **是**（观察采集） |
| 进入 normalized company profile | **否** |
| caveat | `secType=szshe` 硬编码；不绑定主 gate |
| Raw 输出 | `outputs/harvest/cninfo_c_class/raw/security_observe/{company_code}.json` |
| Normalized 输出 | `outputs/harvest/cninfo_c_class/normalized/security_observe/{company_code}.json`（**独立分区**，不并入 company 主 snapshot） |

### 3.4 Source scope 汇总

| 类别 | source 数 | HTTP 请求数/公司（规划） |
|------|-----------|-------------------------|
| direct fetch | **6** | **6**（basic · executive · share_capital · top_sh · top_float · dividend） |
| derived | **3** | **0**（随 basic） |
| observe-only | **1** | **1**（security，独立写出） |
| **合计请求/公司** | | **7** |

**863 家公司 planned requests（live 时）：** 863 × 7 = **6041** cases

---

## 4. 数据输出设计

三层文件结构；**均为本地 `outputs/harvest/` 下文件**，不入库。

### 4.1 Raw Layer

**目的：** 保存原始 CNINFO 返回，作为证据链与 replay 基础。

**根目录：** `outputs/harvest/cninfo_c_class/raw/`

**子目录（按 source）：** `basic_profile/` · `executive_profile/` · `share_capital_profile/` · `top_shareholders_profile/` · `top_float_shareholders_profile/` · `dividend_history/` · `security_observe/`

**单条记录最小字段（JSON 包装）：**

| 字段 | 说明 |
|------|------|
| `company_code` | 证券代码 |
| `company_name` | 公司名称 |
| `org_id` | CNINFO orgId |
| `source_id` | 源标识 |
| `request_time` | ISO 8601 UTC |
| `request_url` | 完整请求 URL |
| `retrieval_status` | endpoint_found / empty_but_valid_response / http_error / … |
| `http_status` | HTTP 状态码 |
| `response_metadata` | json_code · result_code · retry_count · used_orgid_variant 等 |
| `raw_records` | CNINFO 响应体（或 `data.records` 切片）；**不修改** |

**要求：** 保留原始证据；不做字段清洗；失败响应同样落盘（若 HTTP 层有 body）。

### 4.2 Normalized Layer

**根目录：** `outputs/harvest/cninfo_c_class/normalized/`

**原则：** 仅包含 [field inventory](cninfo_c_class_field_inventory.md) 中 **`include_in_normalized_snapshot=yes`** 的 **normalized_core** 字段（**64** 字段口径，含 lineage `raw_record_json` / `raw_record_hash`）。

**逻辑分区：**

| 分区 | 内容 |
|------|------|
| `company_basic_profile/` | 公司基本信息 |
| `contact_profile/` | 联系方式（derived） |
| `business_scope/` | 业务信息（derived） |
| `industry_profile/` | 行业信息（derived） |
| `executive_profile/` | 高管（jsonl，一人一行） |
| `share_capital_profile/` | 股本（jsonl） |
| `top_shareholders_profile/` | 十大股东（jsonl） |
| `top_float_shareholders_profile/` | 十大流通股东（jsonl） |
| `dividend_history/` | 历史分红（jsonl） |
| `security_observe/` | 观察指标（**不并入**主 company snapshot） |

**可选聚合（未来）：** `normalized/company_snapshot/{company_code}.json` — 按公司合并各分区引用或嵌入；planning 阶段不实现。

### 4.3 Quality Layer

**根目录：** `outputs/harvest/cninfo_c_class/quality/`

| 文件 | 内容 |
|------|------|
| `harvest_summary.md` | 本次 harvest 运行摘要 · overall result · caveat 清单 |
| `field_fill_rate.csv` | 字段级 fill_rate（company × field） |
| `source_quality.csv` | source 级 reachability · non_empty · blocked · empty_but_valid 计数 |
| `hold_company_list.csv` | 26 家 hold + `excluded_by_status_review` 标注 |
| `company_harvest_status.csv` | company_level harvest_status（见 §6） |

**harvest_summary.md 必含 caveat：**

- 26 家 all6 hold 已排除
- share_capital **source_partial**
- executive **caveat**
- top_float **source_partial**
- security **observe-only**
- dividend_history **≠ financing**
- **no verified** · **no testing_stable_sample**

---

## 5. Field Mapping Strategy

依据 [cninfo_c_class_field_inventory.csv](../outputs/validation/cninfo_c_class_field_inventory.csv)：

### 5.1 normalized_core（64 fields · `include=yes`）

- **进入** Normalized Layer
- **mapper 来源：** `lab/cninfo_c_class_mappers.py`（dividend 待补）
- **schema 校验：** `schemas/c_class/`（离线，harvest 后可选跑现有 validate 脚本）
- **示例：** basic `legal_name` · executive `person_name` · shareholder `holding_ratio` · dividend `dividend_plan_text`

### 5.2 review_later（31 fields · `include=review`）

**暂不进入 normalized snapshot。**

| 原因类型 | 示例 |
|----------|------|
| 语义不稳定 | F007V 股东变动、F005N/F012N 高管持股/薪酬 |
| 覆盖不足 | executive `term_start/end`（mapper 未映射） |
| 待确认 | industry `index_or_plate_labels`（F044V） |
| schema 槽位未用 | security `is_st_candidate` |

**处理：** 保留在 Raw Layer `raw_records`；Quality Layer 可统计出现率，供下轮晋升决策。

### 5.3 raw_only（25 fields · `include=no`）

**仅保留原始数据，暂不标准化。**

| 原因 | 示例 |
|------|------|
| 与 derived 重叠存 raw | basic F012V–F014V |
| observe 不进主 snapshot | security 全字段 observe 分区策略 |
| 行级 ID 仅 lineage | executive SEQID · F001V |

---

## 6. Quality Rules

### 6.1 Company level

| 字段 | 说明 |
|------|------|
| `company_code` | 主键 |
| `harvest_status` | `complete` / `partial` / `failed` / `excluded_hold` |
| `last_updated` | 本次 harvest request_time |
| `sources_attempted` | 7 |
| `sources_with_data` | 至少一条 endpoint_found 或 empty_but_valid 的 source 数 |
| `excluded_reason` | hold 公司填 `sample_quality_or_status_review` |

**`harvest_status=partial`：** 部分 direct source 失败或 empty，但非全源失败。

### 6.2 Source level

| 字段 | 说明 |
|------|------|
| `source_id` | 源标识 |
| `retrieval_status` | 与 validate runner 口径一致 |
| `fill_rate` | 期望字段非空比例（records 非空时） |
| `source_status` | proceed_testing / source_partial / observe_only 等（来自 decision） |
| `record_count` | raw records 行数 |
| `empty_but_valid` | yes/no |

### 6.3 Field level

| 字段 | 说明 |
|------|------|
| `field_name` | normalized 或 raw 字段名 |
| `value` | 采样值或 hash（大字段可截断） |
| `source` | source_id |
| `evidence` | request_url 或 raw 路径 |
| `status` | `filled` / `empty` / `missing` / `review` |

### 6.4 特殊规则

| 规则 | 说明 |
|------|------|
| **empty_but_valid** | HTTP 200 + 空 `data.records` → **不算失败**；`retrieval_status=empty_but_valid_response`；计入 reachability |
| **source_partial** | share_capital · top_float — Quality 与 summary **必须**保留 caveat；不作全市场 non_empty gate |
| **security** | 采集但不进入主 company normalized gate |
| **derived** | 无独立 retrieval_status；继承 basic 状态 |
| **hold 26** | 不请求；写入 `hold_company_list.csv` only |

---

## 7. Future Harvest Runner Design（仅设计，不实现）

### 7.1 脚本

**未来路径：** `lab/harvest_cninfo_c_class.py`

**CLI（规划）：**

```bash
# dry-run：装载样本、构造 URL、统计 planned 输出，无 CNINFO
python lab/harvest_cninfo_c_class.py --dry-run \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml \
  --output-dir outputs/harvest/cninfo_c_class

# live：人工批准后
python lab/harvest_cninfo_c_class.py --live \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml \
  --output-dir outputs/harvest/cninfo_c_class
```

### 7.2 复用 validate runner 能力

从 `lab/validate_cninfo_c_class_scale_smoke.py` 复用（不修改 B/D/Phase1）：

| 能力 | 用途 |
|------|------|
| backoff / retry | 90001 / 429 退避 |
| orgId fallback | data20 endpoint |
| empty_but_valid policy | 股东 / executive / share_capital |
| SOURCE_SPECS | URL 与 expected_fields |
| load_sample_companies | YAML 装载 |
| mappers | raw → normalized |

### 7.3 执行流程（规划）

```
load sample (863)
→ preflight（company_count · hold 零重叠 · planned cases）
→ for each company:
    → direct fetch × 6 + security observe × 1
    → write raw
    → map normalized_core
    → derive contact / business / industry from basic
→ aggregate quality layer
→ write harvest_summary.md
```

### 7.4 本轮明确不做

- **不创建** `harvest_cninfo_c_class.py`
- **不创建** `outputs/harvest/` 目录下真实数据文件
- **不跑** dry-run / live

---

## 8. Harvest Gate

未来开始 **harvest live** 前，须满足：

| 门槛 | 状态 |
|------|------|
| field inventory 完成 | **是**（[§7ay](eraC_execution_plan.md)） |
| universe 明确（863 − 26 hold） | **是**（本文档 §2） |
| source status 明确 | **是**（[source status decision](cninfo_c_class_source_status_decision.md)） |
| output structure 明确（raw / normalized / quality） | **是**（本文档 §4） |
| quality rules 明确 | **是**（本文档 §6） |
| harvest plan 文档 | **是**（本文档） |
| harvest runner dry-run PASS | **否** — 下一步 |
| 人工批准 harvest live | **否** — 待 dry-run 后 |
| dividend mapper draft | **否** — runner 实现前补 |
| 863 样本 YAML 派生 | **否** — runner 实现前派生 |

**Gate 结论：** **planning gate = PASS** · **live gate = PENDING_RUNNER_DRYRUN**

---

## 9. 下一步

**下一步不是直接 harvest live。**

| 顺序 | 动作 | 说明 |
|------|------|------|
| 1 | **实现 harvest runner dry-run** | `lab/harvest_cninfo_c_class.py --dry-run` |
| 2 | **派生 863 样本 YAML** | 889 − 26 hold |
| 3 | **补 dividend_history mapper draft** | 对齐 field inventory |
| 4 | **检查输出结构** | raw / normalized / quality 路径与字段 |
| 5 | **人工批准** | 批准后 `--live` harvest（863 × 7 = 6041） |

---

## 10. 红线确认

| 项 | 本轮 |
|----|------|
| CNINFO 请求 | **无** |
| live harvest | **无** |
| harvest runner 实现 | **无** |
| YAML backfill 执行 | **无** |
| DB / MinIO | **无** |
| RAG / LLM | **无** |
| verified | **不写** |
| testing_stable_sample | **不升级** |
| B/D/Phase1 文件 | **未修改** |

---

## 附录：参考路径

| 类型 | 路径 |
|------|------|
| 母本 universe | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` |
| hold 子集 | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` |
| field inventory | `plans/cninfo_c_class_field_inventory.md` |
| mappers | `lab/cninfo_c_class_mappers.py` |
| validate runner | `lab/validate_cninfo_c_class_scale_smoke.py` |
| source candidates | `config/cninfo_c_class_source_candidates.yaml` |
