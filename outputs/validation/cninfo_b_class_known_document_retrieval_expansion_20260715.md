# CNINFO B 类 Known-Document Retrieval Expansion — B-R16-01

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-R16-01 |
| track | B |
| executor | b-class-executor |
| controller_execution_allowed | false |
| CNINFO live | **未执行**（dry-run 后停止；live 非必需且未获 controller 授权） |
| 新造 offline §7 FP lineage | **无** |
| commit / push | **无** |

## 1. 目的

将 `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` 中
≥3 条 `placeholder` 晋升为 `ready`，证据仅来自既有 B live/harvest report CSV
（真实 `company_code` / 标题 / 披露日），随后跑 corpus retrieval dry-run。

## 2. 晋升结果

| case_id | prior → new | company | title_pattern | date window | evidence row |
|---------|-------------|---------|---------------|-------------|--------------|
| `inquiry_known_002` | placeholder → ready | 601901 方正证券 | 信息披露监管问询函的回复公告 | 2025-06-12 ~ 2025-06-15 | BD2E470 |
| `meeting_known_002` | placeholder → ready | 688041 海光信息 | 关于召开重大资产重组事项投资者说明会的公告 | 2025-06-09 ~ 2025-06-12 | BD2E177 |
| `ir_activity_known_001` | placeholder → ready | 000559 万向钱潮 | 投资者关系活动记录表 | 2025-06-24 ~ 2025-06-27 | BD2E071 |
| `shareholder_meeting_known_001` | placeholder → ready | 300446 航天智造 | 股东大会通知 | 2025-06-23 ~ 2025-06-26 | BD2E574 |

**promoted_count = 4**（目标 ≥3）

## 3. 证据来源（只读既有 CSV）

| case_id | announcement_id | evidence_date | source CSV |
|---------|-----------------|---------------|------------|
| inquiry_known_002 | 1223879047 | 2025-06-13 | `outputs/validation/cninfo_b_class_erad_next_scale_slice1/reports/b_class_erad_next_scale_slice1_combined_report.csv` |
| meeting_known_002 | 1223836435 | 2025-06-10 | `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv` |
| ir_activity_known_001 | 1223981179 | 2025-06-25 | `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv` |
| shareholder_meeting_known_001 | 1223974102 | 2025-06-24 | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv` |

离线路由核对（`route_title`）：四条均与 `expected_document_type` / `expected_route_to` 一致。

## 4. Dry-run

| 指标 | 数值 |
|------|------|
| command | `python lab/validate_cninfo_b_class_corpus_retrieval.py --dry-run` |
| result | **DRY_RUN_PASS** |
| total_cases | 21 |
| ready_cases | **9**（known 8 + periodic_guard_002） |
| invalid_ready | **0** |
| query_executed | **0** |
| wall_time | **0.285 s** |
| report | `outputs/validation/cninfo_b_class_known_document_retrieval_expansion_dry_run_report_20260715.csv` |
| summary | `outputs/validation/cninfo_b_class_known_document_retrieval_expansion_dry_run_summary_20260715.md` |

Selector 复核：`invalid_ready=0`，`ready=9`，`result=PASS`。

## 5. Live 决策

- dry-run 通过后：**不**调用 CNINFO。
- 理由：`controller_execution_allowed=false`；四条已有 harvest metadata 证据；既有 live 报告已覆盖旧 ready 集；增量 live 对本任务 capability_gain 有限。
- CNINFO 调用数：**0**
- allow-list / live 范围：未开启（无 live）

## 6. 质量边界

- 不下载 PDF；不解析；不写 verified；不升级 source status。
- 不发明新的 offline §7 FP lineage。
- 未晋升的 placeholder（如 `inquiry_known_001`、`regulatory_known_001/003`、`ir_activity_known_002`）因 harvest 中缺少可区分的「监管问询函原文 / 投资者交流活动」样本而保留。

## 7. 下一步

1. Controller 若需验证新 ready 集，可单独批准 tiny live metadata（仅新晋 4 条或全 ready 集）。
2. commit 边界由 controller 决定；本任务 `ready_for_commit=true`（fixture + evidence 自洽，无 live 依赖）。
