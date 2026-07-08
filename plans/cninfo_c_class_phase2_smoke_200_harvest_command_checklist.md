# CNINFO C-Class Phase 2 Smoke 200 Harvest Command Checklist

_生成时间：2026-07-08_

> **性质：** Phase 2 smoke harvest 命令检查清单。**本轮不执行**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：** [harvest runner](../lab/harvest_cninfo_c_class.py) · [dry-run plan](cninfo_c_class_phase2_smoke_200_harvest_dryrun_plan.md)

---

# 1. 脚本参数说明

当前 `harvest_cninfo_c_class.py` 使用：

| 参数 | 说明 |
|------|------|
| `--dry-run` | 默认模式 · 不请求 CNINFO |
| `--sample-file` | universe YAML 路径（**非** `--universe`） |
| `--output-csv` | dry-run report CSV |
| `--output-md` | dry-run summary MD |
| `--output-validation-md` | dry-run validation summary MD |
| `--live` | live 模式（须额外批准） |
| `--limit N` | smoke live 限制 N 家 |
| `--approve-full-harvest` | 863 full 批准（**不适用于** phase2 smoke） |
| `--resume` | 跳过 complete 公司 |

**注意：** 当前 runner **无** `--output-root`；live 隔离须未来扩展。**本轮不修改 runner。**

---

# 2. Dry-Run Command（候选）

## 2.1 推荐命令

```bash
cd listed_company_data_collector

python lab/harvest_cninfo_c_class.py \
  --dry-run \
  --sample-file lab/eval_companies_c_class_phase2_smoke_200.yaml \
  --output-csv outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv \
  --output-md outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_summary.md \
  --output-validation-md outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_validation_summary.md
```

## 2.2 Dry-run 预期

| 项 | 期望 |
|----|------|
| companies | **200** |
| HTTP cases | **1400** |
| CNINFO 调用 | **0** |
| raw/normalized 写入 | **0** |

## 2.3 执行状态

| 项 | 状态 |
|----|------|
| dry-run 规划 | **完成** |
| dry-run 执行 | **未启动** |

---

# 3. Live Execution Command（未批准）

## 3.1 候选命令（**NOT APPROVED YET**）

```bash
# NOT APPROVED YET — 须 dry-run 审查 + 显式批准 + output-root 隔离确认

python lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_phase2_smoke_200.yaml \
  --limit 200
```

## 3.2 批准前阻塞项

| # | 阻塞 |
|---|------|
| 1 | dry-run 报告审查 PASS |
| 2 | output-root 隔离机制就绪 |
| 3 | `company_harvest_status.csv` 不与 863 冲突 |
| 4 | 显式 `--approve-phase2-smoke-harvest`（规划 flag · 尚未实现） |
| 5 | rate limit / 退避策略确认 |

**Live harvest: NOT APPROVED YET**

---

# 4. Post-Dry-Run Review

dry-run 执行后审查：

1. [dry-run review checklist](../outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_review_checklist.md)
2. [expected case matrix](../outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_expected_case_matrix.csv)

---

# 5. 红线

- 本轮 **不执行** 上述命令
- **无 CNINFO**（dry-run 模式）
- **无 live harvest 批准**
