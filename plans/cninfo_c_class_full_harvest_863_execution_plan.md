# CNINFO C-Class Full Harvest 863 执行计划（Approval Plan）

_生成时间：2026-07-07_

> **性质：** 正式 **863 家 full harvest** 的人工批准前执行计划（**planning only**）。**本轮不执行 harvest**；**不请求 CNINFO**；**不写 raw/normalized**；**不写 verified**；**不入库**。

**前置（均已完成）：**

| 阶段 | 文档 / 产物 |
|------|-------------|
| Field Inventory | [cninfo_c_class_field_inventory.md](cninfo_c_class_field_inventory.md) · [CSV](../outputs/validation/cninfo_c_class_field_inventory.csv) |
| Harvest Plan | [cninfo_c_class_harvest_plan.md](cninfo_c_class_harvest_plan.md) |
| Dry-run Validation | [harvest_dryrun_validation_summary.md](../outputs/validation/cninfo_c_class_harvest_dryrun_validation_summary.md) |
| Dividend Mapper | [cninfo_c_class_dividend_history_mapping.md](cninfo_c_class_dividend_history_mapping.md) · `lab/cninfo_c_class_mappers.py` |
| Smoke Live | [harvest_smoke_summary.md](../outputs/validation/cninfo_c_class_harvest_smoke_summary.md) |
| Post-retry Decision | [cninfo_c_class_889_post_retry_decision.md](cninfo_c_class_889_post_retry_decision.md) |

**Runner：** `lab/harvest_cninfo_c_class.py`  
**样本：** `lab/eval_companies_c_class_harvest_863_non_bse.yaml`

**红线（本计划及批准前）：** 无 CNINFO · 无 full live · 无 YAML backfill · 无 DB · 无 MinIO · 无 RAG · 无 verified · 不升级 testing_stable_sample · 不修改 B/D/Phase1

---

## 1. Harvest Scope

### 1.1 Universe

| 项 | 数量 / 说明 |
|----|-------------|
| 母本 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（**889** non-BSE） |
| **Excluded** | **26** all6 hold（`lab/eval_companies_c_class_889_rerun_all6_hold.yaml`） |
| **Harvest universe** | **863** companies |
| 样本文件 | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` |
| hold_overlap | **必须为 0**（preflight hard gate） |

```
889 non-BSE candidate
− 26 all6 hold
= 863 harvest candidate
```

**26 hold 处理：** 不删除母本记录；harvest **不请求**；quality 层 `hold_company_list.csv` 标注 `excluded_by_status_review`。

**明确不进入本轮 863 主 harvest：**

- BSE legacy（83/87 hold）— 独立 side-track
- abnormal_review（3 家）
- BSE 920 — 独立 universe

### 1.2 Source Scope

每家公司 **10** 个逻辑 source（**7** HTTP + **3** derived）；HTTP **6041** cases。

#### Direct（6 · 各 1 HTTP）

| logical_name | source_id | harvest 状态 | caveat |
|--------------|-----------|--------------|--------|
| basic | `cninfo_company_basic_profile` | proceed_testing_with_caveat | basic empty 敏感 |
| executive | `cninfo_executive_profile` | proceed_testing_with_caveat | executive caveat |
| share_capital | `cninfo_share_capital_profile` | **source_partial** | residual empty_but_valid 可能 |
| top_shareholders | `cninfo_top_shareholders_profile` | proceed_testing_with_caveat | — |
| top_float | `cninfo_top_float_shareholders_profile` | **source_partial** | — |
| dividend_history | `cninfo_dividend_financing_profile` | proceed_testing | **≠ financing** |

#### Derived（3 · 无独立 HTTP，从 basic 派生）

| logical_name | source_id |
|--------------|-----------|
| contact | `cninfo_company_contact_profile` |
| business_scope | `cninfo_company_business_scope` |
| industry | `cninfo_company_industry_profile` |

#### Observe（1 · 1 HTTP）

| logical_name | source_id | 说明 |
|--------------|-----------|------|
| security | `cninfo_company_security_profile` | observe_only · **不并入** company snapshot |

### 1.3 字段口径

依据 [field inventory](cninfo_c_class_field_inventory.md)：

| 分层 | 数量 | full harvest 行为 |
|------|------|-------------------|
| normalized_core | **64** | 写入 normalized |
| review_later | **31** | 仅 raw 保留 |
| raw_only | **25** | 仅 raw 保留 |

---

## 2. Execution Command

### 2.1 正式 full harvest 命令（批准后执行）

```bash
cd listed_company_data_collector

python lab/harvest_cninfo_c_class.py \
  --live \
  --approve-full-harvest \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml
```

可选续跑：

```bash
python lab/harvest_cninfo_c_class.py \
  --live \
  --approve-full-harvest \
  --resume \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml
```

### 2.2 当前 runner 安全限制

| 项 | 现状 |
|----|------|
| smoke 命令 | `--live --limit 10`（无需 approve · 已 **PASS**） |
| full harvest | **必须** `--approve-full-harvest`；否则 `FULL_HARVEST_APPROVAL_REQUIRED` |
| resume | `--resume` 框架已实现（跳过 `harvest_status=complete`） |
| run_status | `quality/run_status.json` |

**批准前禁止执行上述 full 命令。**

### 2.3 预估运行时

| 项 | 估算 |
|----|------|
| HTTP cases | **6041** |
| pacing | 0.5s（basic/dividend/security 间）· 0.8s（P2-A 四源间） |
| 粗算 wall time | **约 1.5–2.5 小时**（单线程顺序；不含 throttle backoff） |
| throttle backoff | 命中时额外 2s / 5s / 10s（最多 3 轮） |

### 2.4 Preflight（执行日必跑）

```bash
# dry-run 复验（无 CNINFO）
python lab/harvest_cninfo_c_class.py --dry-run \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml
```

期望：`company_count=863` · `hold_overlap=0` · `planned_http_cases=6041` · `harvest_dryrun_validation_gate=PASS`

---

## 3. Output Plan

**根目录：** `outputs/harvest/cninfo_c_class/`

### 3.1 Raw Layer — `raw/`

**用途：** 保留 CNINFO 响应证据；每条记录含请求元数据 + `raw_records`；失败响应同样落盘（若有 body）。

| 子目录 | 格式 | 示例 |
|--------|------|------|
| `basic_profile/` | `.json` | `raw/basic_profile/{company_code}.json` |
| `executive_profile/` | `.jsonl` | 单文件含 envelope（`raw_records` 为 records 列表） |
| `share_capital_profile/` | `.jsonl` | 同上 |
| `top_shareholders_profile/` | `.jsonl` | 同上 |
| `top_float_shareholders_profile/` | `.jsonl` | 同上 |
| `dividend_history/` | `.jsonl` | 同上 |
| `security_observe/` | `.json` | observe 专用 |

**Envelope 必填字段：** `company_code` · `company_name` · `source_id` · `org_id` · `request_time` · `request_url` · `retrieval_status` · `http_status` · `business_code` · `raw_records`

**禁止写入：** Cookie · Authorization · SID · 完整 request headers

**预期 raw 文件数（full）：** 863 × 7 HTTP = **6041**（derived 无独立 raw HTTP 文件）

### 3.2 Normalized Layer — `normalized/`

**用途：** 仅 **normalized_core**（64 字段口径）；mapper 输出；供下游分析与后续 schema 校验。

| 子目录 | 格式 | 说明 |
|--------|------|------|
| `company_basic_profile/` | `.json` | 每公司 1 文件 |
| `executive_profile/` | `.jsonl` | 一人一行 |
| `share_capital_profile/` | `.jsonl` | 一行一事件 |
| `top_shareholders_profile/` | `.jsonl` | 一行一股东 |
| `top_float_shareholders_profile/` | `.jsonl` | 一行一股东 |
| `dividend_history/` | `.jsonl` | 一行一分红事件 |
| `contact_profile/` | `.json` | derived |
| `business_scope/` | `.json` | derived |
| `industry_profile/` | `.json` | derived |
| `security_observe/` | `.json` | observe · 不进主 snapshot |

**预期 normalized 文件数（full）：** 863 × 10 = **8630**

### 3.3 Quality Layer — `quality/`

**用途：** 运行摘要、fill_rate、source 级统计、hold 清单、公司级 harvest 状态。

| 文件 | 用途 |
|------|------|
| `harvest_summary.md` | 本次运行 overall result · caveat 清单 |
| `field_fill_rate.csv` | company × field fill（含 derived 字段出现率） |
| `source_quality.csv` | source × retrieval_status 计数 |
| `hold_company_list.csv` | 26 hold + 排除原因 |
| `company_harvest_status.csv` | per-company `complete` / `partial` / `failed` |

**另产出（validation 层，非 harvest 数据根）：**

- `outputs/validation/cninfo_c_class_harvest_full_report.csv`（建议 full run 后生成）
- `outputs/validation/cninfo_c_class_harvest_full_summary.md`

### 3.4 Smoke 产物与 full 关系

Smoke 已在 `outputs/harvest/cninfo_c_class/` 写入 **10** 家公司产物（70 raw · 100 normalized）。  
Full harvest 执行前需选择：

1. **备份 smoke 子集** 到 `outputs/harvest/cninfo_c_class_smoke_10_backup/`（推荐），或  
2. **启用 resume**（见 §6）跳过已完成 10 家，仅补跑剩余 **853** 家

---

## 4. Runtime Safety

### 4.1 已有机制（smoke 已验证）

| 机制 | 实现位置 | 说明 |
|------|----------|------|
| 请求 pacing | `validate_cninfo_c_class_scale_smoke.py` · harvest 复用 | basic/dividend/security 后 **0.5s**；P2-A 四源间 **0.8s** |
| Throttle 业务码检测 | `_is_cninfo_throttled_business_code` | JSON `429` / `90001` 等 |
| Backoff | `THROTTLE_BACKOFF_SECONDS` | **2s → 5s → 10s**（最多 3 轮） |
| orgId fallback | `_live_fetch_data20` | scode-only 失败后尝试 `scode+orgId` |
| empty_but_valid | shareholder · dividend | 空 records 不算 http_error |
| Raw 脱敏 | `harvest_cninfo_c_class.py` | envelope 不含 Cookie/Auth/SID/headers |

### 4.2 禁止事项

| 禁止 | 原因 |
|------|------|
| 并发扩大 / 多进程批量 | 触发 CNINFO rate limit / block |
| 绕过 sleep 或 backoff | 破坏已验证 pacing |
| 保存 Cookie / Authorization / SID | 安全与合规 |
| 无批准执行 `--live` 全量 | 防误跑 |
| 本轮 YAML backfill / DB / MinIO / RAG | Phase 4 红线 |

### 4.3 执行日监控

- 每 **N** 家公司打印 progress（建议复用 smoke 统计输出）
- 出现 **blocked** 或 **429** 集群时 **暂停** 并人工评估，不自动加大并发
- 保留 `outputs/validation/` 侧 full summary 供事后审计

---

## 5. Failure Handling

### 5.1 原则

**单源失败不中断全流程** — 记录 `retrieval_status` / `source_status`，继续下一家或下一源。

### 5.2 分类处理

| 类型 | retrieval_status 示例 | 处理 |
|------|-------------------------|------|
| **HTTP error** | `http_error` · `cninfo_throttled_business_code` | 写 raw envelope（若有 body）· quality 记 fail · **继续** |
| **blocked** | `blocked` · `rate_limited` | 记 `source_status=blocked` · **继续**（集群出现时人工暂停） |
| **empty_but_valid** | `valid_empty`（dividend）· `empty_but_valid_response`（shareholder） | **不算失败** · 写空 normalized · quality 计 reachable |
| **source_partial** | share_capital · top_float residual | 保留 caveat · 不升级为 verified |
| **schema_unexpected** | 缺字段 / 结构异常 | 记 fail · raw 保留 · 继续 |
| **derived 失败** | basic 未成功 | derived 写占位 / skip · company_status=partial |

### 5.3 company_harvest_status 映射

| 条件 | status |
|------|--------|
| 全部 HTTP 源 success 或 empty_but_valid | `complete` |
| 部分成功 | `partial` |
| 全部 HTTP 失败 | `failed` |

### 5.4 与 889 post-retry 对齐

[post-retry decision](cninfo_c_class_889_post_retry_decision.md) 残留 **9** 条 `empty_but_valid_response`（executive 1 · share_capital 8）— full harvest 中**预期可出现**，**不视为 runner 缺陷**。

---

## 6. Resume Strategy

> **状态：** 本节为 **full harvest 执行要求**；runner **resume 逻辑待批准后实现**（当前 smoke 为顺序全跑，无 skip）。

### 6.1 目标

中途停止（网络、人工中断、throttle）后可续跑，避免重复 CNINFO 请求。

### 6.2 跳过规则（计划）

| 粒度 | 条件 | 行为 |
|------|------|------|
| **公司级** | `company_harvest_status.csv` 中 `harvest_status=complete` 且 raw+normalized 文件齐全 | 跳过该公司全部 source |
| **源级** | 对应 `raw/{subdir}/{code}.*` 已存在且 envelope `retrieval_status` 为 success 类 | 跳过该源 HTTP |
| **derived** | basic normalized 已存在 | 仅重跑 derived（若需） |

### 6.3 状态保留

- 追加/合并 `company_harvest_status.csv` · `source_quality.csv`
- `harvest_summary.md` 标注 `resumed_run=true` 与起止时间
- smoke 10 家若已落盘，resume 默认 **skip**（除非 `--force-refresh`）

### 6.4 建议实现（批准后开发）

```bash
# 规划接口（尚未实现）
python lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml \
  --resume
```

---

## 7. Completion Criteria

863 full harvest **完成后**检查以下项（人工 + 脚本）：

### 7.1 Universe & overlap

| 检查项 | 期望 |
|--------|------|
| `company_count` | **863** |
| `hold_overlap` | **0** |
| hold 未误 harvest | `hold_company_list.csv` 含 26 家 |

### 7.2 HTTP & success rate

| 检查项 | 期望 |
|--------|------|
| `planned_http_cases` | **6041** |
| `blocked` | **≈ 0**（集群则调查） |
| `http_error` rate | **< 5%**（对齐历史 scale smoke） |
| per-source reachability | basic/dividend/shareholder **≥ 95%** reachable（含 empty_but_valid） |
| share_capital / executive | 允许 residual empty_but_valid · 标注 source_partial |

### 7.3 文件计数

| 层 | 期望（full · 不含 smoke 重叠时需按 resume 调整） |
|----|--------------------------------------------------|
| raw files | **6041** |
| normalized files | **8630** |
| quality summary | `harvest_summary.md` 存在且含 caveat |

### 7.4 质量分析

| 检查项 | 期望 |
|--------|------|
| `field_fill_rate.csv` | 生成 · normalized_core 主字段可统计 |
| `source_quality.csv` | 各 source retrieval_status 分布 |
| dividend_history parse | `dividend_parse_status` 分布（parsed / empty_but_valid / needs_review） |
| error distribution | blocked · http_error · schema_unexpected 分列 |

### 7.5 Smoke 回归对照

| Smoke（10 家） | Full 期望 |
|----------------|-----------|
| harvest_smoke_gate **PASS** | 同等机制 · 无 blocked/http_error 集群 |
| dividend 10/10 parsed | 全量 parse 率单独统计 |
| empty_but_valid=2 | 允许按比例出现 |

### 7.6 非目标（本轮仍不做）

- verified / testing_stable_sample 升级
- PostgreSQL / MinIO / RAG
- YAML registry backfill 执行
- `company_snapshot` 聚合（planning 可选未来项）

---

## 8. Approval Gate

### 8.1 当前 Gate 状态

| Gate | 状态 |
|------|------|
| field_inventory | **DONE** |
| harvest_plan | **DONE** |
| dryrun_validation | **PASS** |
| dividend_mapper | **DONE** |
| harvest_smoke_gate | **PASS** |
| **full_harvest_gate** | **PENDING_APPROVAL** |

### 8.2 Smoke 证据摘要

来源：[harvest_smoke_summary.md](../outputs/validation/cninfo_c_class_harvest_smoke_summary.md)

| 指标 | 值 |
|------|-----|
| companies | 10 |
| HTTP requests | 70 |
| success | 100 |
| empty_but_valid | 2 |
| blocked | 0 |
| http_error | 0 |
| raw files | 70 |
| normalized files | 100 |
| dividend_history | **10/10** parsed |

### 8.3 批准条件（建议）

人工批准 full harvest 前确认：

1. 已阅读本执行计划与 [harvest plan](cninfo_c_class_harvest_plan.md)
2. smoke gate **PASS** · dry-run validation **PASS**
3. 接受 share_capital / executive **source_partial** caveat
4. 接受 26 hold 排除与 dividend **≠ financing** 语义
5. 已安排执行窗口（~2h+）与 resume/备份策略
6. 同意解除 runner `--limit` 限制或增加 `--approve-full-harvest`
7. **仍不写 verified** · **不入库**

### 8.4 批准后下一步

1. 实现 `--approve-full-harvest`（或解除 `--limit` 强制）+ `--resume`（建议）
2. 备份 smoke 10 家产物（可选）
3. 执行 §2.1 命令
4. 按 §7 完成验收
5. 更新 `CURRENT_STATUS.md` · `eraC_execution_plan.md` · 产出 full summary

---

## 附录 A — 相关文件索引

| 类型 | 路径 |
|------|------|
| Runner | `lab/harvest_cninfo_c_class.py` |
| Mappers | `lab/cninfo_c_class_mappers.py` |
| Sample | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` |
| Hold | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` |
| Dividend mapper YAML | `config/cninfo_dividend_history_mapper.yaml` |

## 附录 B — 红线确认（本计划轮次）

| 项 | 本轮 |
|----|------|
| CNINFO 请求 | **无** |
| full live harvest | **无** |
| 新 raw / normalized | **无** |
| YAML backfill | **无** |
| DB / MinIO / RAG | **无** |
| verified | **无** |
