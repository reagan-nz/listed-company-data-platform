# CNINFO D 类 Initial Planning Summary

_生成时间：2026-07-09_

> **性质：** 规划快照；不调用 CNINFO；不 live；不 harvest；不修改 C-class / B-class 输出。

---

## Architecture Conclusion

D-class 应定位为 **market structured data layer** — 回答「这家上市公司在市场层面发生了什么」，而不是 company profile。

- **C-class**：company identity + company profile（静态画像快照）
- **D-class**：company event / market behavior timeline（动态市场行为时间线）
- **B-class**：document metadata + PDF URL lineage（证据文档，通过 link 挂接 D-class 事件）

Phase 2 已验证 10 个 fixed-table JSON 源（`testing_stable_sample`）；本轮 Phase 0 将其中 **7** 个市场行为源收敛为统一架构与 discovery 计划，复用既有 registry / schema / fixture，**不重复 live 探测**。

---

## Source Categories（7）

| # | 类别 | source_id | Phase 2 状态 |
|---|------|-----------|--------------|
| 1 | 融资融券 | `margin_trading` | testing_stable_sample |
| 2 | 大宗交易 | `block_trade` | testing_stable_sample |
| 3 | 限售解禁 | `restricted_shares_unlock` | testing_stable_sample |
| 4 | 股权质押 | `equity_pledge` | testing_stable_sample |
| 5 | 股东增减持 | `shareholder_change` | testing_stable_sample |
| 6 | 高管持股变化 | `executive_shareholding` | testing_stable_sample |
| 7 | 预约披露 / 信息披露日历 | `disclosure_schedule` | testing_stable_sample |

---

## Recommended Priority

| 优先级 | 组件 | 理由 |
|--------|------|------|
| **P0** | `margin_trading` · `block_trade` · `restricted_shares_unlock` · `disclosure_schedule` · `field_semantics_freeze` | 市场交易与披露日程核心；产品时间线价值最高 |
| **P1** | `equity_pledge` · `shareholder_change` · `executive_shareholding` · `harvest_architecture` · `company_event_timeline` · `c_class_identity_linkage` | 股东/高管行为；需 harvest 架构与 C-class 键对齐 |
| **P2** | `b_class_evidence_linkage` | 证据 PDF 挂接；不阻塞 D-class 结构化行采集 |

**推荐首阶段路径：** Phase 0 架构 + discovery（本轮）→ 离线 field semantics freeze → harvest architecture dry-run → 未来 tiny live harvest approval。

---

## Blockers

| 阻塞项 | 说明 | 缓解 |
|--------|------|------|
| 无 D-class harvest runner | C-class harvest 模式不可直接复用（参数/分页/日期维度不同） | P1 专项 harvest 架构设计 |
| 大宗交易无买卖双方明细 | `block_trade` endpoint 仅公司级汇总 | 产品降级为汇总字段；或未来探测 detail API |
| 字段语义未 freeze 到产品 CSV | F00xN 单位与枚举仍 medium confidence | P0 `field_semantics_freeze` 离线任务 |
| C-class Phase 3 live 可能并行 | 带宽与注意力分散 | D-class 本轮纯 offline；未来 harvest 须显式批准 |
| B-class tiny live 待批准 | 并行但不阻塞 D-class 规划 | 职责分离；D-class 不依赖 B-class live |

---

## No Live Execution

本轮确认：

- **no CNINFO calls**
- **no live validation**
- **no harvest**
- **no PDF download**
- **no DB / MinIO / RAG**
- **no verified**
- **no testing_stable_sample upgrade**
- **no C-class output modification**
- **no B-class output modification**
- **no identity merge**

---

## Parallel Execution Note

| 线 | 状态 | 本轮影响 |
|----|------|----------|
| C-class | `SNAPSHOT_GENERATED_QA_REVIEW` | **不变**；未触碰 harvest/snapshot 输出 |
| B-class | tiny live runner `READY_FOR_APPROVAL` | **不变**；D-class 规划独立并行 |
| D-class | Phase 0 planning **启动** | 仅新增 plan / matrix / summary |

---

## Deliverables

| 交付物 | 路径 |
|--------|------|
| 架构计划 | [cninfo_d_class_market_data_architecture_plan.md](../../plans/cninfo_d_class_market_data_architecture_plan.md) |
| Source discovery 计划 | [cninfo_d_class_source_discovery_plan.md](../../plans/cninfo_d_class_source_discovery_plan.md) |
| Readiness matrix | [cninfo_d_class_readiness_matrix.csv](cninfo_d_class_readiness_matrix.csv) |
| 本摘要 | `cninfo_d_class_initial_planning_summary.md` |

---

## Recommended Next D-class Task

**离线：生成 7 源 product field semantics freeze CSV，并对照 registry YAML 做 harvest architecture dry-run 规划。**

仍不 live、不 harvest、不修改 C-class / B-class 输出。

---

## Gate

```text
d_class_initial_planning_gate = DESIGN_STARTED
```
