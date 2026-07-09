# CNINFO C-Class Phase 3 Batch 500 Harvest Command Checklist

_生成时间：2026-07-09_

> **性质：** Phase 3 batch 500 harvest 命令检查清单。**本轮不执行**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：** [harvest runner](../lab/harvest_cninfo_c_class.py) · [dry-run plan](cninfo_c_class_phase3_batch_500_001_harvest_dryrun_plan.md)

---

# 1. 脚本参数说明

当前 `harvest_cninfo_c_class.py` 已支持：

| 参数 | 说明 |
|------|------|
| `--dry-run` | 默认模式 · 不请求 CNINFO |
| `--sample-file` | universe YAML 路径 |
| `--output-root` | harvest 产物根目录（**Phase 3 须隔离**） |
| `--output-csv` | dry-run report CSV |
| `--output-md` | dry-run summary MD |
| `--output-validation-md` | dry-run validation summary MD |
| `--live` | live 模式（须额外批准） |
| `--approve-phase2-smoke-harvest` | Phase 2 smoke 批准（**不适用于** Phase 3） |
| `--approve-full-harvest` | 863 full 批准（**不适用于** Phase 3） |
| `--resume` | 跳过 complete 公司 |

**Phase 3 缺口：**

```
phase3_runner_approval_flag_required = true
```

推荐未来 flag：`--approve-phase3-batch-500-harvest`

**本轮不实现 runner extension。**

---

# 2. Dry-Run Command（候选）

## 2.1 推荐命令

```bash
cd listed_company_data_collector

python lab/harvest_cninfo_c_class.py \
  --dry-run \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001.yaml \
  --output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --output-csv outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_report.csv \
  --output-md outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_summary.md \
  --output-validation-md outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_validation_summary.md
```

## 2.2 Dry-run 预期

| 项 | 期望 |
|----|------|
| companies | **500** |
| planned_http_cases | **3500** |
| matrix_rows | **5000** |
| CNINFO 调用 | **0** |
| raw/normalized 写入 | **0** |

## 2.3 执行状态

| 项 | 状态 |
|----|------|
| dry-run 规划 | **完成** |
| dry-run 执行 | **未启动** |

---

# 3. Live Execution Command（未批准）

## 3.1 候选命令（**NOT APPROVED**）

```bash
# NOT APPROVED — 须 dry-run PASS + runner extension + 显式批准

python lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_001.yaml \
  --output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --approve-phase3-batch-500-harvest
```

**阻塞：** `--approve-phase3-batch-500-harvest` **尚未实现**；live **禁止执行**。

## 3.2 批准前阻塞项

| # | 阻塞项 |
|---|--------|
| 1 | dry-run gate **PASS** |
| 2 | output-root isolation check **PASS** |
| 3 | runner Phase 3 approval flag 实现 |
| 4 | 用户显式批准 Phase 3 batch 500 live harvest |
| 5 | 863 主轨 / Phase 2 目录未触碰确认 |

---

# 4. Post-Harvest QA Command（未来 · 未批准）

```bash
# NOT APPROVED — harvest live 完成后离线 QA

python lab/review_cninfo_c_class_phase3_batch_500_001_live_harvest_qa.py
```

（QA review script **尚未实现**）

---

# 5. Gate Summary

| 阶段 | Gate | 状态 |
|------|------|------|
| dry-run planning | `phase3_batch_500_001_harvest_dryrun_planning_gate = READY_FOR_DRYRUN` | **DONE** |
| dry-run execution | TBD | **NOT STARTED** |
| live harvest | TBD | **NOT APPROVED** |

---

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest · 未 runner extension
