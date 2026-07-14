# CNINFO C 类 — Fuller-Market Slice1 Caveat10 统一索引

_生成时间：2026-07-14 · offline index only · CNINFO=0_

> **offline only** · **no live** · **no snapshot** · **no harvest mutation** · **no commit/push** · **approved_for_snapshot_rebuild=false（保持不变）**

---

## 任务范围

将 slice1 universe 200 中 **10 家 caveat** 公司统一编入单一离线索引，合并既有 **partial7** 与 **empty-dividend-3** 证据包引用。**不重复**逐案证据评估；仅建立 case_id 级交叉索引供 Controller / Evidence Auditor 检索。

**任务 ID：** C-GEN-20260714-04

---

## 来源（只读）

| 文件 | 用途 |
|------|------|
| `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` | partial7 离线矩阵（7 行） |
| `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv` | empty-dividend 离线矩阵（3 行） |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` | closure 权威 case_id 列表 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` | `exact_caveat_case_ids` 指标 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` | 10 行 caveat 明细 |

---

## 汇总

| 指标 | 值 |
|------|-----|
| **caveat 总数** | **10 / 10** |
| partial 家族 | 7（`caveat_family=partial`） |
| empty_dividend 家族 | 3（`caveat_family=empty_dividend`） |
| requires_snapshot | **全部 false** |
| requires_live | **全部 false** |
| QA gate（closure） | `PASS_WITH_CAVEAT` |
| snapshot | **blocked**（`approved_for_snapshot_rebuild=false`） |
| CNINFO 调用 | **0** |

**确认 10/10 case_id：** CE1E002, CE1E003, CE1E034, CE1E061, CE1E067, CE1E070, CE1E071, CE1E176, CE1E188, CE1E193

与 `cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` 中 `exact_caveat_case_ids` **完全一致**。

---

## 统一索引表

| case_id | company_code | company_name | caveat_family | package_ref | requires_snapshot | requires_live |
|---------|--------------|--------------|---------------|-------------|-------------------|---------------|
| CE1E002 | 600001 | 邯郸钢铁 | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E003 | 600005 | 武钢股份 | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E034 | 600068 | 葛洲坝 | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E061 | 000003 | PT金田A | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E067 | 000015 | PT中浩A | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E070 | 000022 | 深赤湾A | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E071 | 000024 | 招商地产 | partial | `cninfo_c_class_partial7_evidence_completeness_20260714.md` | false | false |
| CE1E176 | 688031 | 星环科技 | empty_dividend | `cninfo_c_class_empty_dividend_evidence_20260714.md` | false | false |
| CE1E188 | 688062 | 迈威生物 | empty_dividend | `cninfo_c_class_empty_dividend_evidence_20260714.md` | false | false |
| CE1E193 | 688071 | 华依科技 | empty_dividend | `cninfo_c_class_empty_dividend_evidence_20260714.md` | false | false |

机器可读副本：[cninfo_c_class_caveat10_registry_20260714.csv](cninfo_c_class_caveat10_registry_20260714.csv)

---

## 家族说明

### A. partial（7）

- **caveat_class：** `delisted_or_merged_partial_normalized`
- **ledger：** `partial` · 4/10 normalized
- **disposition：** `accept_with_caveat` · 不建议 re-live
- **证据包：** `cninfo_c_class_partial7_evidence_completeness_20260714.md` + `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv`

### B. empty_dividend（3）

- **caveat_class：** `empty_but_valid_dividend_normalized_zero_byte`
- **ledger：** `complete`（10/10）· resume-audit `needs_review`
- **disposition：** `accept_with_caveat` · 不升级 live retry
- **证据包：** `cninfo_c_class_empty_dividend_evidence_20260714.md` + `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv`

---

## 影响说明

本索引 **不改变** closure gate、harvest 产物或 snapshot 审批状态。10 家 caveat 仍计入 slice1 `PASS_WITH_CAVEAT`：7 家退市/合并/PT partial 与 3 家 STAR empty-but-valid dividend 在质量层均保持 `accept_with_caveat`。`approved_for_snapshot_rebuild` **保持 false**；snapshot rebuild 与 live retry **均未授权**。本产物仅供下游（Evidence Auditor、Controller、snapshot planning）按 `case_id` 快速定位对应家族证据包，避免在 partial7 与 empty-dividend 包之间重复检索。

---

## 产出物

| 文件 | 说明 |
|------|------|
| `cninfo_c_class_caveat10_registry_20260714.md` | 本索引报告 |
| `cninfo_c_class_caveat10_registry_20260714.csv` | 10 行机器可读索引 |

**未重做：** partial7 证据包 · empty-dividend 证据包 · QA closure 包

---

## Gates

```
c_class_erad_fuller_market_slice1_qa_closure_gate = PASS_WITH_CAVEAT（未变）
approved_for_snapshot_rebuild = false（未变）
caveat10_registry_gate = INDEX_COMPLETE
```

**NOT verified** · **NOT production_ready** · snapshot **blocked**

---

## 安全确认

| 项 | 状态 |
|----|------|
| CNINFO 调用 | **0** |
| live 执行 | **未执行** |
| harvest root 变更 | **无** |
| 既有 QA 产物变更 | **无**（仅新增索引） |
| snapshot | **未创建** |
| 其他 track | **未触碰** |

---

## 下一步建议

Evidence Auditor 核验本索引与 closure `exact_caveat_case_ids`、partial7/empty-dividend 矩阵行数一致后，Controller 可将 caveat10 索引登记入 PROJECT_CONTROL。
