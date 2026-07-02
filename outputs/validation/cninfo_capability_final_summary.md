# CNINFO 数据源能力总结（Era C 收尾）

_最后更新：2026-07-02_

> 本文件一页说清：巨潮资讯网（CNINFO）当前**能稳定拿到什么、部分能拿到什么、还没验证什么**。所有结论均为**小样本验证**结果，`recommended_status` 为 `testing` 或 `partial`，**不代表长期稳定可用，也不等于全量采集完成**。当前阶段未接任何数据库（PostgreSQL / MinIO / MongoDB）。
>
> 依据：`outputs/validation/` 下各 CSV 与 summary，尤其是 [cninfo_p0_validation_final_summary.md](cninfo_p0_validation_final_summary.md) 与 [cninfo_report_announcement_validation_summary.md](cninfo_report_announcement_validation_summary.md)；盘点主表见 [../plans/cninfo_data_source_value_inventory.md](../plans/cninfo_data_source_value_inventory.md)。

---

## 1. 能稳定拿到（类年报文档流 + 公告 PDF 元数据）

| 能力 | 结果 | 状态 | 依据 |
|---|---|---|---|
| 年报检索 | 98 success | `testing / partial` | report_announcement 验证 |
| 半年报检索 | 55 success | `testing / partial` | report_announcement 验证 |
| 季报检索（Q1/Q3） | 113 / 102 success | `testing / partial` | report_announcement 验证 |
| 报告期解析 `report_period` | 332/780（非空且非 unknown） | 可用 | 标题模式解析（annual `YYYY`、semi `YYYYH1`、季报 `YYYYQn`） |
| 公告 PDF 元数据 | 100/100 success | `testing` | P0 #83，表现最好；仅元数据/URL/hash 规则，未下载正文 |

> **类年报（年报/半年报/季报）是当前最成熟的路径**：定期披露、标题模式稳定、有 PDF，可复用同一套检索机制（`lab/validate_cninfo_report_announcements.py`）。检索总体 success 368/780；`keyword_recent` 与 `longer_time_window` 效果最好，`report_title_pattern` 单独用较弱。

---

## 2. 部分能拿到（可用但有缺口）

| 能力 | 结果 | 状态 | 缺口 |
|---|---|---|---|
| 最新公告列表 | 34/40 公司；102/108 公告记录 | `testing / partial` | BSE 部分 430 老代码 6 家失败（公司标识映射问题） |
| 个股 F10 / 公司资料 | 可达 23；Playwright 字段 22/30 | `partial / testing` | 依赖 stockCode + orgId + Playwright 渲染；部分字段语义需人工核对 |

---

## 3. 还没验证（按盘点表优先级排队）

- **P1**：预约披露、风险公告/风险提示、监管问询/处罚/诉讼、分红/回购/定增/重组、公司治理/管理层变动、股本结构、股东信息、限售解禁。
- **P2**：融资融券、大宗交易、公开信息/异常交易、互动易、网络投票。
- **暂缓**：IPO/招股书、债券、基金、全量实时行情、高频交易数据。

> 详见 [../plans/cninfo_data_source_value_inventory.md](../plans/cninfo_data_source_value_inventory.md) 第 9 节。这些栏目均保持 `candidate / 待验证`，需按第 8.1 模板逐项做小样本验证后才更新状态。

---

## 4. 边界（必须保持）

- 全部为小样本验证结果，`recommended_status` 只用 `candidate / testing / partial`，**不写 `verified`**。
- P0/类年报验证完成 ≠ 全量采集完成 ≠ 长期稳定可用。
- 未接 PostgreSQL / MinIO / MongoDB；验证结果仅作为未来设计依据。
- 未下载/解析 PDF 正文；未做 OCR；未使用 BrowserUser；未绕过登录/验证码/付费/权限。

---

## 5. 下一步

1. 类年报可扩展到同样「定期 + 标题稳定 + 有 PDF」的类型（业绩预告 / 业绩快报）。
2. 非类年报按 P1 → P2 逐项小样本验证，每项更新盘点表状态 + 留 summary。
3. 待主要栏目验证透后，再回头谈存储结构与事件表设计（当前暂缓）。

> 执行清单见 [../plans/eraC_execution_plan.md](../plans/eraC_execution_plan.md)。
