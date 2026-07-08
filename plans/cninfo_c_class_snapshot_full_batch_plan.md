# CNINFO C-Class Snapshot Full Batch Plan

_生成时间：2026-07-08_

> **性质：** 863 家公司 snapshot full batch **执行规划**（Era C Phase 4）。**仅规划** · **本轮不执行 batch** · **不写 verified**。

**依据：** [architecture plan](cninfo_c_class_company_snapshot_architecture_plan.md) · [smoke 10 summary](../outputs/validation/cninfo_c_class_snapshot_smoke_10_summary.md) · [field mapping](../outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv) · [final catalog](../outputs/validation/cninfo_c_class_final_field_catalog.csv)

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

**Builder：** `lab/build_cninfo_c_class_company_snapshot.py`（离线只读 PoC，smoke 10 已验证可泛化）

---

# 1. Batch Universe

| 项 | 值 |
|----|-----|
| **company_count** | **863** |
| **来源** | [lab/eval_companies_c_class_harvest_863_non_bse.yaml](../lab/eval_companies_c_class_harvest_863_non_bse.yaml) |
| **universe_id** | `harvest_863_non_bse` |
| **parent** | 889 non-BSE 母本 |
| **排除** | [26 all6 hold](../lab/eval_companies_c_class_889_rerun_all6_hold.yaml)（`eval_companies_c_class_889_rerun_all6_hold.yaml`） |

## 板块分布（universe YAML）

| board | count |
|-------|-------|
| sse_main | 281 |
| szse_main | 226 |
| chinext | 231 |
| star | 125 |

## Universe 边界说明

- **863** 为 C-class harvest 正式 universe；26 家 all6 hold 已在 harvest 母本派生时排除，**不纳入** full batch。
- normalized 侧 `company_basic_profile/` 现有 **863** 个文件，与 universe 一致。
- `company_harvest_status.csv` 当前 **853** 行（10 家缺 status 行但 normalized 存在）；batch 以 **universe YAML + normalized 文件存在性** 为准，status CSV 仅作 quality 侧车。

## 与 smoke 10 关系

- smoke 10 样本均来自本 universe，**不修改** harvest universe。
- smoke 路径：`outputs/snapshot/cninfo_c_class/smoke/`（保留，不覆盖）。
- demo 路径：`outputs/snapshot/cninfo_c_class/company_snapshot_demo/`（保留，不覆盖）。

---

# 2. Snapshot Output Design

## 输出根目录

```
outputs/snapshot/cninfo_c_class/full/
```

## 文件命名

每家公司一个 JSON 文件：

```
{company_code}.json
```

示例：`688750.json`、`000009.json`

## 单文件顶层结构

与 architecture plan 及 builder PoC 对齐，每家公司 snapshot 包含三块：

```json
{
  "company_code": "000009",
  "company_name": "中国宝安",
  "snapshot_version": "v0.1",
  "snapshot_status": "complete_with_caveat",
  "metadata": {
    "built_at": "2026-07-08T00:00:00Z",
    "universe_id": "harvest_863_non_bse",
    "input_normalized_files": 10,
    "input_files": ["outputs/harvest/cninfo_c_class/normalized/..."]
  },
  "modules": {
    "company_identity": { "fields": {}, "status": "available", "sources": [] },
    "...": {}
  },
  "quality": {
    "module_status": {},
    "caveats": [],
    "source_quality": {}
  }
}
```

| 区块 | 说明 |
|------|------|
| **modules/** | 18 个一级模块；每模块含 `fields` · `status` · `sources` |
| **quality/** | `module_status` rollup · `caveats` · per-source `source_quality` |
| **metadata/** | 构建时间 · universe · 输入文件清单 · batch run id（执行时写入） |

## 目录隔离

| 路径 | 用途 | full batch 是否写入 |
|------|------|---------------------|
| `smoke/` | smoke 10 验证 | **否** |
| `company_snapshot_demo/` | builder demo | **否** |
| `full/` | 863 full batch | **是**（待执行） |

## 预计磁盘

- 单文件约 **400–1100** 字段量级（smoke 10 观测）；863 家合计约 **500–900 MB** JSON（粗估，取决于数组模块行数）。
- **不入库** · **不 MinIO** · 产物本地 `outputs/snapshot/`。

---

# 3. Module Coverage Expectation

基于 smoke 10（10/10 `complete_with_caveat`）+ 863 harvest `source_quality.csv` 推断。**不强制补齐**缺失模块。

| module | expected available | expected partial | expected not_available | 依据 |
|--------|-------------------|------------------|------------------------|------|
| company_identity | ~863 | ~0 | 0 | basic 全覆盖 |
| securities_profile | ~863 | ~0 | 0 | basic board/exchange |
| business_profile | ~863 | ~0 | 0 | derived business_scope |
| industry_profile | ~863 | ~0 | 0 | derived industry |
| financial_snapshot | ~853 | ~10 | 0 | share_capital empty_but_valid **10** 家 |
| **technology_profile** | **0** | **0** | **863** | 无 R&D 源；smoke 10/10 not_available |
| organization_profile | ~863 | ~0 | 0 | contact derived |
| shareholder_profile | **0** | **~863** | **0** | source_partial 语义；smoke 10/10 partial |
| executive_profile | ~854 | **~9** | 0 | executive empty_but_valid **9** 家 |
| governance_profile | ~863 | ~0 | 0 | basic + contact |
| dividend_profile | ~815 | **~48** | 0 | dividend valid_empty **38** + parse partial |
| capital_action_profile | **0** | **~863** | 0 | share_capital source_partial；smoke 10/10 partial |
| risk_profile | **0** | **~863** | 0 | security observe_only；smoke 10/10 partial |
| event_timeline | ~815 | **~48** | 0 | 依赖 dividend + share_capital |
| **market_behavior** | **0** | **~863** | **0** | security observe_only；smoke 10/10 partial |
| **investor_relation** | **0** | **~863** | **0** | contact 与 organization 重叠；smoke 10/10 partial |
| document_evidence | ~863 | ~0 | 0 | per-source hash |
| data_quality | ~863 | ~0 | 0 | harvest quality 侧车 |

### 政策

- `technology_profile` · `market_behavior` · `investor_relation` **保持** partial / not_available，**不**为 batch 新增源或 patch mapper。
- `empty_but_valid` **不**自动判 `failed`；模块 `partial` + snapshot `complete_with_caveat` 为预期常态。
- `security_observe` **不**进入主 snapshot gate（与 harvest QA 一致）。

---

# 4. Batch Size Planning

| 项 | 值 |
|----|-----|
| 公司数 | **863** |
| 预计 snapshot JSON | **863**（每公司 1 文件） |
| 并行度（建议） | 单进程顺序或 `--workers 4`（执行阶段再定） |
| 预计耗时（离线） | **15–45 分钟**（单进程粗估；仅读 normalized） |
| 本轮 | **不执行** |

## 执行前置（规划，本轮不做）

1. 人工批准 full batch 执行（独立于 harvest live 批准流）。
2. 实现 batch runner（参考 `lab/run_cninfo_c_class_snapshot_smoke_10.py` 泛化）。
3. 确认 `outputs/snapshot/cninfo_c_class/full/` 磁盘空间。
4. 确认红线：无 CNINFO · normalized 只读。

---

# 5. Resume Design

## 状态文件

路径：

```
outputs/snapshot/cninfo_c_class/full/company_snapshot_status.csv
```

## 字段

| 字段 | 说明 |
|------|------|
| company_code | 6 位代码 |
| snapshot_status | 见下表 |
| started_at | ISO8601 UTC |
| finished_at | ISO8601 UTC |
| module_success_count | status=available 模块数 |
| module_partial_count | status=partial 模块数 |
| error_count | 构建异常次数 |
| last_error | 最近错误摘要 |
| retry_status | `none` / `pending` / `done` |

## snapshot_status 枚举

| 状态 | 含义 |
|------|------|
| `pending` | 未开始 |
| `running` | 构建中 |
| `complete` | 全部模块 available（863 上预期极少） |
| `complete_with_caveat` | 构建成功，含 partial/not_available（**预期主流**） |
| `failed` | 无法生成 snapshot（如 basic profile 缺失、JSON 解析失败） |

## Resume 规则

1. 启动时读取 `company_snapshot_status.csv`；`complete` / `complete_with_caveat` **跳过**（除非 `--force`）。
2. `failed` / `pending` 可 `--resume` 重试。
3. 每完成一家公司 **append/upsert** 一行（防止 batch 中断丢进度）。
4. batch run 元数据写入 `outputs/snapshot/cninfo_c_class/full/batch_run_manifest.json`（run_id · started_at · universe · company_count）。

---

# 6. Failure Handling

## 隔离原则

**单家公司失败不得影响其他公司。**

- batch runner 对每家公司 `try/except` 包裹 `build_snapshot()`。
- 失败公司写入 `failed` status，继续下一家。
- 不因单模块 partial 中止整批。

## 错误日志

路径：

```
outputs/snapshot/cninfo_c_class/full/company_snapshot_error.csv
```

| 字段 | 说明 |
|------|------|
| company_code | 公司代码 |
| module | 失败模块（`__build__` 表示顶层） |
| error_type | 异常类名 |
| error_message | 错误信息 |
| retry_possible | `yes` / `no` |

## 错误分类（规划）

| error_type | retry_possible | 处理 |
|------------|----------------|------|
| `FileNotFoundError`（basic 缺失） | no | 记录 failed；核对 universe |
| `json.JSONDecodeError` | no | 记录 failed；归 QA，**不改 normalized** |
| `KeyError` / builder bug | yes | 记录 failed；修 builder 后 resume |
| 模块 partial（非错误） | n/a | **不写入** error.csv |

## 预期 failed 规模

- smoke 10：**0 failed**。
- 863 预期：**0–5**（若 normalized 文件损坏）；**不**因 empty_but_valid 计为 failed。

---

# 7. Quality Summary Design

batch 完成后（执行阶段）生成：

```
outputs/snapshot/cninfo_c_class/full/snapshot_quality_summary.md
```

## 内容结构

### 7.1 公司级汇总

| 指标 | 说明 |
|------|------|
| company_count | 863 |
| complete_count | snapshot_status=complete |
| complete_with_caveat_count | snapshot_status=complete_with_caveat |
| failed_count | snapshot_status=failed |

### 7.2 模块级汇总

| 指标 | 说明 |
|------|------|
| module_fill_rate | 每模块 available_count / 863 |
| module_partial_rate | 每模块 partial_count / 863 |
| missing_module_distribution | 每模块 not_available_count / 863 |

### 7.3 附表

- 与 smoke 10 module coverage 对照表
- Top N `quality_caveat_count` 公司
- schema drift 抽样（可选，参考 smoke cross_company 检测）

### 7.4 Gate

```
snapshot_full_batch_gate = PASS / PASS_WITH_CAVEAT / FAIL
```

- **PASS_WITH_CAVEAT**：预期默认（与 smoke 一致）
- **FAIL**：failed_count 超阈值（建议 >10 或 >1%）或系统性 builder 异常

---

## 红线确认（规划）

- **无 CNINFO** · **无 live** · **无 harvest**
- raw / normalized / field_inventory **不修改**
- **不入库** · **不 MinIO** · **不 RAG** · **不 registry backfill**
- **不写 verified** · **不升级 testing_stable_sample**
- C-class 保持 **`HARVEST_COMPLETED_QA_ONGOING`**

## 相关产物（本轮规划产出）

| 产物 | 路径 |
|------|------|
| 本计划 | `plans/cninfo_c_class_snapshot_full_batch_plan.md` |
| 规划摘要 | `outputs/validation/cninfo_c_class_snapshot_full_batch_planning_summary.md` |
