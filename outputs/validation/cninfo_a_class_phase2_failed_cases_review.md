# CNINFO A 类 Phase 2 Failed Cases Review

_生成时间：2026-07-09_

> **性质：** Phase 2 live 失败后 isolated retry 评审；**无 CNINFO** · **无 live** · **不是 verified**

---

## 1. Phase 2 Execution Recap

| 项 | 值 |
|----|-----|
| execution gate | `a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED` |
| total cases | **20** |
| success (found) | **12** |
| failed | **8** |
| wrong report-type | **0** |
| title mismatch | **2**（均为 not_found · 无实际标题匹配） |
| period mismatch | **0** |
| CNINFO requests | **28** |
| PDF download / parse | **0 / 0** |
| matching_logic | **v2** |

输入：[a_class_phase2_metadata_report.csv](cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_report.csv)

---

## 2. Failed Case List

| case_id | company | report_type | retrieval_status | failure category |
|---------|---------|-------------|------------------|------------------|
| A2M005 | 601012 隆基绿能 | annual_report | network_error | orgId resolution failed |
| A2M010 | 300750 宁德时代 | semi_annual_report | not_found | CNINFO proxy 503 |
| A2M011 | 600887 伊利股份 | semi_annual_report | network_error | orgId resolution failed |
| A2M012 | 601166 兴业银行 | semi_annual_report | network_error | orgId resolution failed |
| A2M013 | 688599 天合光能 | quarterly_report_q1 | network_error | orgId resolution failed |
| A2M018 | 688111 金山办公 | quarterly_report_q3 | not_found | CNINFO proxy 503 |
| A2M019 | 600309 万华化学 | quarterly_report_q3 | network_error | orgId resolution failed |
| A2M020 | 002594 比亚迪 | quarterly_report_q3 | network_error | orgId resolution failed |

---

## 3. Failure Category Breakdown

| 类别 | count | case_ids |
|------|-------|----------|
| network_error（orgId） | **6** | A2M005, A2M011, A2M012, A2M013, A2M019, A2M020 |
| not_found（proxy 503） | **2** | A2M010, A2M018 |

**wrong_report_type = 0** — 无 case 匹配到错误 report-type 标题。

---

## 4. Why This Is Not Report-type Matching Failure

- 12/12 成功 case 全部 `title_match_status=pass` · `period_match_status=pass`
- 失败 case 均未进入有效标题匹配阶段：
  - **6** 个在 orgId 解析阶段失败（`cninfo_request_count=0`）
  - **2** 个在 announcement query 阶段因 proxy 503 返回空记录
- `wrong_report_type_count = 0` — v2 matching 在可检索 case 上工作正常
- 失败 notes 均为 `network_error` 或 `ProxyError 503`，非 `title_mismatch` / `reject_pattern`

---

## 5. Why This Is Not Schema Failure

- phase1_freeze_v1 schema **未变更**
- registry draft **未变更**
- 成功 12 case 均产出完整 metadata 字段（announcement_id · title · time · pdf_url lineage）
- 失败 case 无 schema validation error · 无 field catalog lint failure
- 问题层：**CNINFO 瞬时网络 / proxy**，非对象模型或字段定义

---

## 6. Why Retry Should Be Isolated

1. **成功 12 case 已验证** — 重跑浪费 CNINFO quota 且可能覆盖 baseline
2. **失败原因可隔离** — network/proxy 瞬态错误，适合单 case retry（参照 B-class TLC002 pattern）
3. **输出隔离** — retry 写入专用根 `cninfo_a_class_phase2_metadata_retry/`，不覆盖 Phase 2 expansion 报告
4. **universe 不变** — 同一 8 case · 同一 report_type · 同一 expected_period
5. **matching v2 不变** — 无需修改标题过滤逻辑

---

## 7. Why Successful 12 Should Not Be Rerun

| 成功 case | 状态 |
|-----------|------|
| A2M001–A2M004, A2M006–A2M009, A2M014–A2M017 | found · title pass · period pass |

- 已产出可审计 metadata snapshot
- 重跑无增量验证价值
- 可能引入新的瞬态失败噪声
- Phase 2 closure 应合并 12 success + retry results，而非全量 rerun

---

## 8. Decision Matrix

| 项 | 决定 |
|----|------|
| Schema change | **No** |
| Matching logic change | **No** |
| Universe change | **No** |
| Retry needed | **Yes — isolated 8-case retry only** |

---

## 9. Next Step（未执行）

人工审阅 [failed retry approval package](cninfo_a_class_phase2_failed_retry_approval_summary.md) → 批准后 `--approve-a-class-phase2-failed-retry` isolated live retry。

**不是 verified** · **不是 production_ready** · **无 PDF**
