# CNINFO C-Class Phase 3 Batch 500 Execution Checklist

_生成时间：2026-07-09_

> Phase 3 batch 500 执行检查清单。**规划产物** · **本轮不执行**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置：** `phase3_batch_500_planning_gate = DESIGN_COMPLETE`

---

# 1. Pre-selection Checks

- [ ] Refreshed candidate CSV 最新：`cninfo_c_class_company_registry_candidate_refreshed.csv`
- [ ] Candidate matrix 已审阅：`cninfo_c_class_phase3_batch_500_candidate_matrix.csv`
- [ ] Eligible pool ≥ **500**（当前 ~**4145**）
- [ ] Phase 2 excluded ledger 12 码已加载
- [ ] Phase 2 smoke 200 codes 已加载排除
- [ ] `listing_status=delisted` 预筛规则已编码
- [ ] 名称 caveat 规则（退 / 退市 / *ST）已编码
- [ ] BSE / hold / identity_conflict / manual_review 排除已确认
- [ ] 选股 seed 与 stratified bucket 定义已文档化

---

# 2. Universe Generation Checks

- [ ] Selection script 已实现/扩展（基于 Phase 2 `select_cninfo_c_class_phase2_smoke_universe.py`）
- [ ] `lab/eval_companies_c_class_phase3_batch_500_001.yaml` 已生成
- [ ] YAML `company_count` = **500**
- [ ] Selection matrix 已生成：`cninfo_c_class_phase3_batch_500_001_selection_matrix.csv`
- [ ] Selection summary 已生成
- [ ] Overlap check：vs 863 = **0**
- [ ] Overlap check：vs Phase 2 200 = **0**
- [ ] Overlap check：vs excluded ledger 12 = **0**
- [ ] Delisted count in YAML = **0**
- [ ] BSE count = **0**
- [ ] Manual review count = **0**
- [ ] Unit test PASS（选股脚本）

---

# 3. Harvest Dry-run Checks

- [ ] Dry-run plan 文档已创建
- [ ] Expected case matrix：**500 × 7 = 3500** HTTP
- [ ] `--output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001` 已配置
- [ ] Dry-run 执行：**0** HTTP · **0** raw · **0** normalized 写入
- [ ] Output isolation dry-run PASS
- [ ] `phase3_batch_500_harvest_dryrun_gate` 记录
- [ ] Command checklist 与 Phase 2 对齐

---

# 4. Live Approval Checks

- [ ] 用户显式批准 Phase 3 batch 500 live harvest
- [ ] Approval flag 已实现（如 `--approve-phase3-batch-500-harvest`）
- [ ] Pre-flight：YAML 存在 · count=500 · exclusions PASS
- [ ] 863 主轨 / Phase 2 目录 isolation 再确认
- [ ] Resume marker 路径在 isolated root 内
- [ ] 无 `--approve-full-harvest` 误用

---

# 5. Live Harvest QA Checks

- [ ] Live harvest 完成；terminal status 记录
- [ ] raw files = **3500**（或 documented delta）
- [ ] normalized files 统计
- [ ] Company failure summary 生成
- [ ] All-direct-failure 公司识别
- [ ] 9240002 集中度分析
- [ ] Delisted/inactive 漏网检查（应为 0 若预筛正确）
- [ ] Output isolation check PASS
- [ ] `phase3_batch_500_live_harvest_qa_gate` 记录（预期 PASS_WITH_CAVEAT）
- [ ] Success subset 定义（排除 all-direct-failure）

---

# 6. Snapshot Subset Policy

- [ ] Success subset YAML 从 harvest QA 导出
- [ ] 排除 all-direct-failure 公司
- [ ] 排除 excluded ledger 模式匹配公司
- [ ] Subset count 文档化（预期 ≥475 if 95% usable rate）
- [ ] Snapshot dry-run plan 完成
- [ ] Builder `--harvest-root` / `--output-dir` 指向 phase3 isolated paths

---

# 7. Snapshot Build Approval Checks

- [ ] 用户显式批准 Phase 3 batch 500 snapshot build
- [ ] Pre-flight：success subset YAML · harvest root · output dir
- [ ] `--approve-phase3-batch-500-snapshot`（或等价 flag）
- [ ] Dry-run snapshot batch PASS
- [ ] Execute：JSON count = success subset count
- [ ] `full/` 未触碰
- [ ] `phase3_batch_500_snapshot_build_gate` 记录

---

# 8. Snapshot QA Checks

- [ ] QA review script 执行（复用 Phase 2 188 模式）
- [ ] Completeness / module coverage / quality flags 生成
- [ ] `company_snapshot_status.csv` 从 JSON 校正
- [ ] Excluded codes absent
- [ ] `phase3_batch_500_snapshot_qa_gate` 记录

---

# 9. Rollback / Resume Policy

## 9.1 Harvest

| 场景 | 策略 |
|------|------|
| 单公司 HTTP 失败 | 记录 error CSV；继续下一家；不 abort batch |
| Batch 中断 | resume marker 在 `phase3_batch_500_001/` 内；`--resume` 跳过已完成 |
| 误写主轨 | **禁止**；若发生则 stop + isolation audit |
| Rollback | 删除 isolated root 内容；**不**删除 863/Phase2 产物 |

## 9.2 Snapshot

| 场景 | 策略 |
|------|------|
| 单公司 build 失败 | error CSV 记录；继续 |
| status CSV 遗留 pending | QA review 强制校正 |
| 误写 `full/` | **禁止**；isolation gate 阻断 |
| Rebuild | 需显式 `--force` + approval；仅 isolated output dir |

## 9.3 Planning rollback

- 本轮仅规划；无 live 产物需 rollback
- 若选股错误：重新生成 YAML + matrix；不触发 harvest

---

# 10. Gate Summary

| 阶段 | Gate | 本轮状态 |
|------|------|----------|
| planning | `phase3_batch_500_planning_gate = DESIGN_COMPLETE` | **DONE** |
| selection | TBD | **NOT STARTED** |
| harvest dry-run | TBD | **NOT STARTED** |
| live harvest | TBD | **NOT APPROVED** |
| snapshot build | TBD | **NOT STARTED** |

---

# References

- [expansion plan](cninfo_c_class_phase3_batch_500_expansion_plan.md)
- [output design](cninfo_c_class_phase3_batch_500_output_design.md)
- Phase 2 reference: [phase2 smoke execution checklist](cninfo_c_class_phase2_expansion_smoke_execution_checklist.md)

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest · 未 snapshot · 未生成 YAML
