# CNINFO C-Class Snapshot Full Execution Approval Checklist

_生成时间：2026-07-08_

> **性质：** 863 家 snapshot full batch **执行前审核清单**（Era C Phase 4）。**仅审核** · **本轮不执行 batch** · **不写 verified**。

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

**依据：** [full batch plan](cninfo_c_class_snapshot_full_batch_plan.md) · [dry-run summary](../outputs/validation/cninfo_c_class_snapshot_batch_dryrun_summary.md) · [batch runner](../lab/build_cninfo_c_class_snapshot_batch.py)

**前置 gate：** `snapshot_batch_dryrun_gate = PASS_WITH_CAVEAT`

---

# 1. Universe Check

| 项 | 预期 | 实测（2026-07-08） |
|----|------|-------------------|
| company_count | **863** | **863**（dry-run report 864 行含 header） |
| hold_overlap | **0** | **0** |
| 来源 | `lab/eval_companies_c_class_harvest_863_non_bse.yaml` | 已对齐 |
| 排除 | 26 all6 hold | 已排除 |
| universe_ok | True | **True** |

**状态：PASS**

---

# 2. Runner Safety Check

| 项 | 要求 | 实测 |
|----|------|------|
| 默认模式 | `--dry-run`（无参数不执行 build） | `argparse` 默认 `dry_run=True` |
| execute 双开关 | `--execute` + `--approve-full-snapshot-batch` | 已实现 |
| 无批准拒绝 | 仅 `--execute` 时 exit 2 | `FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED` · exit **2** |
| 无 CNINFO | dry-run 不调用 `build_snapshot` | 已确认 |
| 测试 | runner test 5/5 PASS | **5/5 PASS** |

**状态：PASS**

---

# 3. Output Path Check

| 路径 | 用途 | 状态 |
|------|------|------|
| `outputs/snapshot/cninfo_c_class/full/` | snapshot JSON 输出根 | **存在**（仅 `quality/` 子目录） |
| `outputs/snapshot/cninfo_c_class/full/quality/` | status / error CSV | **存在** |
| `outputs/snapshot/cninfo_c_class/smoke/` | smoke 10（隔离） | **不写入** |
| `outputs/snapshot/cninfo_c_class/company_snapshot_demo/` | demo（隔离） | **不写入** |

| 风险项 | 检查 |
|--------|------|
| 旧 full snapshot 覆盖 | `full/*.json` 当前 **0** 个；首次执行无覆盖风险 |
| normalized 写入 | runner 只读 normalized · **不修改** |
| raw 写入 | **不修改** |

**状态：PASS**

---

# 4. Resume Check

**文件：** `outputs/snapshot/cninfo_c_class/full/quality/company_snapshot_status.csv`

| 字段 | 存在 |
|------|------|
| company_code, company_name, status | 是 |
| started_at, finished_at | 是 |
| module_available_count, module_partial_count, module_missing_count | 是 |
| error_count, last_error, retry_status | 是 |

**status 枚举支持：**

| status | 支持 | 当前 863 家分布 |
|--------|------|----------------|
| pending | 是 | **863** |
| running | 是 | 0 |
| complete | 是 | 0 |
| complete_with_caveat | 是 | 0 |
| failed | 是 | 0 |

**Resume 行为：**

- `--resume`：跳过 `complete` / `complete_with_caveat` / `failed` 终态行
- `--force`：忽略 resume 跳过，全量重建
- 中断后可从 status CSV 续跑

**状态：PASS**

---

# 5. Error Isolation Check

| 项 | 要求 | 实测 |
|----|------|------|
| 单公司失败不停止 batch | `run_single_company_safe` + per-company `try/except` | 已实现 |
| error CSV | `company_snapshot_error.csv` | **存在**（header only） |
| error 字段 | company_code, module, error_type, error_message, retry_possible | 已对齐 |
| 测试 | case_4 error isolation mock | **PASS** |

**状态：PASS**

---

# 6. Quality Expectation

## 允许（执行后预期常态）

| 项 | 说明 |
|----|------|
| `complete_with_caveat` | smoke 10/10；863 预期主流 |
| partial module | shareholder / capital_action / risk / market / investor 等 |
| not_available module | `technology_profile` 全量 not_available |

## 不允许（执行 gate 失败条件）

| 项 | 阈值建议 |
|----|----------|
| 大量 `failed` | failed_count > **10** 或 > **1%** |
| schema corruption | 系统性 module 缺失 / JSON 不可解析 |
| output missing | 成功 status 但无对应 `{code}.json` |

## 政策对齐

- `empty_but_valid` **不**判 failed（与 harvest QA 一致）
- `security_observe` 不进入主 snapshot gate

---

# 7. Module Risk Review

## High risk（预期 partial / not_available，不阻塞执行）

| module | 风险 | smoke 10 观测 |
|--------|------|---------------|
| technology_profile | 无独立源 | not_available **10/10** |
| market_behavior | security observe_only | partial **10/10** |
| investor_relation | 与 organization 重叠 | partial **10/10** |

## Medium risk

| module | 风险 | 863 预期 |
|--------|------|----------|
| risk_profile | observe_only 侧轨 | partial 为主 |
| capital_action_profile | share_capital source_partial | partial；~10 empty_but_valid |
| shareholder_profile | top_sh / top_float source_partial | partial；~15–18 empty_but_valid |

## Low risk

| module | 风险 |
|--------|------|
| company_identity | basic 全覆盖 |
| business_profile | derived business_scope |
| financial_snapshot | share_capital empty ~10 家 → partial |
| document_evidence | per-source hash 稳定 |

---

# 8. Disk / Runtime Estimate

| 项 | 值 |
|----|-----|
| company_count | **863** |
| expected JSON count | **863** |
| estimated storage | **500–900 MB** |
| estimated runtime | **15–45 min**（离线单进程粗估） |
| resume strategy | `--resume` 跳过终态；`--force` 全量重建 |
| quality sidecar | status CSV + error CSV + 执行后 `snapshot_quality_summary.md` |

---

# 9. Final Approval Gate

## Checklist 汇总

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | Universe Check | **PASS** |
| 2 | Runner Safety Check | **PASS** |
| 3 | Output Path Check | **PASS** |
| 4 | Resume Check | **PASS** |
| 5 | Error Isolation Check | **PASS** |
| 6 | Quality Expectation | 已记录（允许 caveat） |
| 7 | Module Risk Review | 已记录（无阻塞） |
| 8 | Disk / Runtime Estimate | 已记录 |

## 前置 gate

- `snapshot_batch_dryrun_gate = PASS_WITH_CAVEAT`

## 最终判定

```
snapshot_full_execution_gate = READY_FOR_APPROVAL
```

**说明：** 全部安全/框架检查 PASS；质量层面预期 `complete_with_caveat` 为主，属产品政策而非执行阻塞。执行仍需人工显式 `--approve-full-snapshot-batch`。

---

## 红线确认（本轮）

- **未执行** `--execute` · **未生成** full snapshot JSON
- 未请求 CNINFO · 未改 raw / normalized / field_inventory
- 未入库 / MinIO / RAG · 未 registry backfill · 未 verified
