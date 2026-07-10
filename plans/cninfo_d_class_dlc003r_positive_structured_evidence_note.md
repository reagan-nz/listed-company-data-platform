# CNINFO D 类 DLC003R — Positive Structured Evidence Note

_生成时间：2026-07-10_

> **性质：** 离线证据注记 only · **非** verified · **非** production_ready

---

## 1. Case Identity

| 项 | 值 |
|----|-----|
| targeted_probe_id | **DLC003R-T01** |
| replacement_case_id | DLC003R |
| company_code | **688671** |
| company_name | 碧兴物联 |
| component | `restricted_shares_unlock` |
| anchor_date | **2024-02-19** |

---

## 2. Targeted Probe Live Result

| 项 | 值 |
|----|-----|
| CNINFO requests | **1** |
| retrieval_status | **found** |
| record_count | **1** |
| acceptable | **yes** |
| structured_record_evidence | **yes** |
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| probe mode | anchor-date window `tdate` · early stop on company-level hit |
| quality_status | pass |
| lineage_status | discovered |

来源：[live report](../outputs/validation/cninfo_d_class_known_event_targeted_probe/reports/d_class_known_event_targeted_probe_live_report.csv)

---

## 3. Why This Is Positive Structured Evidence

- metadata API 返回 **≥1** 条公司级 JSON 行（SECCODE 匹配 688671）
- 证据经 live 探针路径获得 · **非** PDF 下载 · **非** OCR · **非** 披露文本解析
- `structured_record_evidence = yes` 由 runner 基于 `found` + `record_count >= 1` 判定
- 记入 effective result ledger：`final_effective_status = captured_normal_structured_evidence`

---

## 4. Why This Resolves Prior Empty Result for DLC003R

| 阶段 | requests | records | status |
|------|----------|---------|--------|
| replacement live | 21 | 0 | empty_but_valid_after_budget |
| targeted probe live | 1 | **1** | **found** |

**结论：** replacement bounded replay（v2-style 月/季 baseline）未命中；**anchor-date targeted** 策略在第 1 次请求即命中。组件路径对 DLC003R **已有正向结构化证据**。

---

## 5. What Remains Caveated

- 仅覆盖 **688671** · **restricted_shares_unlock** · anchor **2024-02-19** 邻近窗口
- 不等同于 D-class 全组件生产验证
- overall targeted probe execution gate 仍为 **FAIL_REVIEW_REQUIRED**（因 DLC006R-T01 失败）
- **不** 标记 verified · **不** 标记 production_ready · **不** 升级 testing_stable_sample

---

## 6. Why This Does Not Automatically Resolve DLC006R

- DLC006R-T01（301259 · shareholder_change · anchor 2024-07-16）targeted probe 仍 **12/12 empty**
- 组件与 endpoint 族不同（`shareholeder/detail` vs `liftBan/detail`）
- 人工披露证据对 DLC006R **独立保留** · **不得** 因 DLC003R 成功而推断 DLC006R captured_normal

---

## 7. Gate Impact

| gate | 值 |
|------|-----|
| DLC003R effective | `captured_normal_structured_evidence` |
| overall execution gate | **FAIL_REVIEW_REQUIRED**（保持） |
| closure gate | **READY_FOR_HUMAN_DECISION** |
