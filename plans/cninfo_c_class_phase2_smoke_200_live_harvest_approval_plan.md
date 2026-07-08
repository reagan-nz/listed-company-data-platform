# CNINFO C-Class Phase 2 Smoke 200 Live Harvest Approval Plan

_生成时间：2026-07-08_

> **性质：** Phase 2 smoke 200 live harvest 批准规划。**仅规划** · **不执行 live** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [smoke YAML](../lab/eval_companies_c_class_phase2_smoke_200.yaml)
- [dry-run QA](../outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_qa_summary.md)
- [dry-run report](../outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv)
- [command checklist](cninfo_c_class_phase2_smoke_200_harvest_command_checklist.md)

---

# 1. Purpose

本计划判定 Phase 2 smoke **200** 是否具备进入 **live harvest** 的批准条件。

| 项 | 本轮 | 未来 live |
|----|------|-----------|
| 决策 | 批准规划 · gate **READY_FOR_APPROVAL** | 须 **显式用户批准** |
| CNINFO | **不调用** | 批准后执行 |
| harvest | **不执行** | 须 runner 隔离扩展 |

**本计划不执行 live harvest。**

---

# 2. Dry-Run Evidence

| 证据 | 值 |
|------|-----|
| companies | **200** |
| planned HTTP cases | **1400** |
| matrix_rows | **2000** |
| dry-run gate | **`phase2_smoke_harvest_dryrun_execution_gate = PASS`** |
| validation checks | **10/10 PASS** |
| CNINFO called | **false** |
| real harvest executed | **false** |
| raw/normalized | **unchanged**（6041 / 8630 文件） |
| security | **observe-only**（200 行 `observe_fetch`） |

### Source breakdown（dry-run matrix）

| 类型 | matrix rows |
|------|-------------|
| direct | **1200** |
| derived | **600** |
| observe | **200** |

---

# 3. Live Execution Scope

若未来获批准：

## 3.1 Universe

| 项 | 值 |
|----|-----|
| YAML | `lab/eval_companies_c_class_phase2_smoke_200.yaml` |
| universe_id | `phase2_smoke_200_non_bse` |
| companies | **200** |

## 3.2 Planned calls

| 类别 | 计算 | 数量 |
|------|------|------|
| **Live HTTP total** | 200 × 7 | **1400** |
| Direct normal live | 200 × 6 | **1200** |
| Security observe-only | 200 × 1 | **200** |
| Derived normalized rows | 200 × 3 | **600**（无独立 HTTP） |

## 3.3 Eligibility（选股已保证）

- matched_active only
- no 863 overlap（0 already_in_c_class）
- no hold · no BSE · no manual_review · no identity_conflict

---

# 4. Output Isolation

## 4.1 要求

未来 live 产物根目录 **必须隔离**：

```
outputs/harvest/cninfo_c_class/phase2_smoke_200/
├── raw/
├── normalized/
└── quality/
```

**禁止写入** 现有 863 harvest 目录：

```
outputs/harvest/cninfo_c_class/raw/
outputs/harvest/cninfo_c_class/normalized/
outputs/harvest/cninfo_c_class/quality/
```

## 4.2 当前 runner 状态

| 项 | 状态 |
|----|------|
| `HARVEST_OUTPUT_ROOT` | 硬编码 `outputs/harvest/cninfo_c_class` |
| `--output-root` | **不存在** |
| **runner_extension_required** | **true** |

### 最小扩展需求

| 扩展 | 说明 |
|------|------|
| `--output-root` | 指向 `outputs/harvest/cninfo_c_class/phase2_smoke_200` |
| `--approve-phase2-smoke-harvest` | 显式 live 批准 flag（与 863 `--approve-full-harvest` 分离） |
| 隔离 `company_harvest_status.csv` | 写入 phase2 quality 子目录 · 不读 863 resume 状态 |

> **code 级无重叠**（200 家均非 863），但 **resume marker 与 output root 仍须隔离** 方可安全 live。

---

# 5. Risk Controls

| 控制 | 政策 |
|------|------|
| 规模上限 | **max 200** companies |
| 重试 | 不超出既有 runner 退避/重试政策 |
| security | **observe-only** · 不进主 snapshot gate |
| delisted | **7** 家 `listing_status=delisted` · 保留 · 单独跟踪 caveat |
| merge | **禁止** · merge_executed=false |
| registry | **不更新** · implementation deferred |
| snapshot | harvest 阶段 **不 build** snapshot |
| resume | marker **须与 863 隔离** |
| rate limit | 沿用 harvest runner 退避 |

### Delisted caveat（7 家）

选股摘要：listed **193** · delisted **7**。

**政策：** live 执行时 **保留** 7 家 delisted · 不剔除 · 在 QA 中单独标注 `expansion_smoke_caveat`。

---

# 6. Approval Gate

| Gate | 值 |
|------|-----|
| **phase2_smoke_200_live_harvest_approval_gate** | **`READY_FOR_APPROVAL`** |

| 项 | 状态 |
|----|------|
| dry-run | **PASS** |
| approval planning | **complete** |
| runner extension | **required** |
| **live execution** | **NOT APPROVED** |

**Live execution still requires explicit approval.**

---

# 7. 红线

本轮 **不做：**

- CNINFO / live / harvest 执行
- snapshot build
- raw / normalized / field_inventory 修改
- registry / DB
- identity merge
- verified / testing_stable_sample
