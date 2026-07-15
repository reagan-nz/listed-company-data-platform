# CNINFO B 类 Category-Sample Promotion + Live — B-FM-01

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-01 |
| track | B |
| executor | b-class-executor |
| controller_execution_allowed | false |
| standing_scope | full-market disclosure / announcement / event |
| CNINFO live | **8**（bounded；cap≤20） |
| wall_time_s | **34.21** |
| result | **LIVE_PASS**（4/4 category-sample） |
| FP lineage invented | **无**（未新造 §7 offline FP） |
| commit / push | **无** |
| ready_for_commit | **true** |
| capability_gain | `category_sample_ready_4_plus_live_metadata_path_LIVE_PASS` |

---

## 0. 五地平线搜索（≥3 候选）

| # | Horizon | 候选 | 决策 |
|---|---------|------|------|
| 1 | package closure | 重跑 8 known-document LIVE_PASS | **拒绝** — capability_gain=0；消耗 CNINFO |
| 2 | larger sample | 自 harvest 晋升 **category-sample** placeholder | **执行** — 本任务主路径 |
| 3 | generalization | 开启正向 category-sample live metadata 路径 | **执行** — 与 #2 同包 |
| 4 | scale/stability | wrong_company/wrong_period 更大 harvest 扩测 | **推迟** — §7 已齐套；本轮优先 category-sample 闭环 |
| 5 | next event class | inquiry 原文 / IR 交流活动 known-document | **拒绝** — harvest 仍无可区分样本（同 B-R16-03） |

明确排除：新造 §7 offline FP lineage；docs-only；重开 BD2E624。

---

## 1. 目的

B-R16-03 IDLE 仅扫 known-document placeholder。本任务转向 **category-sample** 推广层：
从既有 harvest CSV 晋升 ≥3 条 placeholder → dry-run → 实现并跑通正向 category-sample live metadata。

---

## 2. Fixture 晋升（4）

| case_id | prior → new | title_pattern | date window | harvest 证据 |
|---------|-------------|---------------|-------------|--------------|
| `general_sample_001` | placeholder → ready | 董事会决议公告 | 2025-06-26~29 | BD2E078 / 1224014247 |
| `general_sample_002` | placeholder → ready | 权益分派 | 2025-06-17~20 | BD2E057 / 1223933551 |
| `general_sample_003` | placeholder → ready | 回购 | 2025-06-26~29 | BD2E072 / 1224013428 |
| `meeting_sample_001` | placeholder → ready | 说明会 | 2025-06-09~12 | BD2E177 / 1223836435 |

未晋升：`inquiry_sample_*`（问询样本与 known-document 边角重叠）、`meeting_sample_002`（与 shareholder_meeting_known_001 同证据）、`periodic_guard_001`（harvest 无「延期披露」行）。

---

## 3. 代码能力增量

| 变更 | 说明 |
|------|------|
| `process_live_category_sample()` | 全市场 sse+szse metadata 抽样 + 类型/非 periodic 审计 |
| dry-run `would_query=true` | 正向 ready category-sample 不再 `live_deferred` |
| `_compute_live_result` | 按 **case pass == ready_cases** 判定 LIVE_PASS（修复多 query/case 误标 PARTIAL） |
| 单测 | `lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py`（3 OK） |

---

## 4. Dry-run

| 指标 | 值 |
|------|-----|
| command | `python lab/validate_cninfo_b_class_corpus_retrieval.py --dry-run` |
| result | **DRY_RUN_PASS** |
| ready_cases | **13**（known 8 + guard 1 + category 4） |
| invalid_ready | **0** |
| query_executed | **0** |
| report | `outputs/validation/cninfo_b_class_category_sample_promotion_dry_run_report_20260715.csv` |

Selector：`ready=13` · `invalid_ready=0` · `PASS`。

---

## 5. Bounded live

| 项 | 值 |
|----|-----|
| allow-list | 仅上表 4 条；known YAML 空 |
| CNINFO | **8** query（无 topSearch） |
| pass/fail | **4/0** |
| result | **LIVE_PASS** |

| case_id | matched_title（节选） | matched_date | type | case_result |
|---------|----------------------|--------------|------|-------------|
| `general_sample_001` | 康尼机电六届一次董事会决议公告 | 2025-06-27 | board_resolution | **pass** |
| `general_sample_002` | 中金辐照…权益分派实施公告 | 2025-06-20 | announcement | **pass** |
| `general_sample_003` | 上汽集团…注销回购股份… | 2025-06-27 | announcement | **pass** |
| `meeting_sample_001` | 关于举行2024年度网上业绩说明会的公告 | 2025-06-12 | meeting_notice | **pass** |

---

## 6. 质量边界

- 仅 live metadata；**未**下载 PDF；**未**解析；**未**写 verified。
- **未**新造 §7 FP lineage。
- **未**触碰 A/C/D；**未** commit / push。

---

## 7. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | 4 条 ready |
| `lab/validate_cninfo_b_class_corpus_retrieval.py` | category-sample live 路径 |
| `lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | 离线锁测 |
| `outputs/validation/cninfo_b_class_category_sample_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 8. Gate

```text
b_class_category_sample_promotion_live_gate = LIVE_PASS
cninfo_calls_this_package = 8
live_calls_this_package = 8
pdf_download = 0
bd2e624_touched = no
section7_fp_invented = no
commit = not_requested
push = not_requested
ready_for_commit = true
```

## 9. 下一步（Controller）

1. 审阅本包后决定 commit 边界。
2. 可选：晋升 `inquiry_sample_*` / `meeting_sample_002` / `periodic_guard_001`（需新证据）。
3. 可选：metadata→document chain prep（仍禁止默认 PDF download）。
