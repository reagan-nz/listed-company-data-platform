# 阶段成果记录：每个阶段完成了什么

_本文件只记录**已完成**的工作。未来规划见 [ROADMAP.md](ROADMAP.md)，当前进展见 [CURRENT_STATUS.md](CURRENT_STATUS.md)，控制面见 [PROJECT_CONTROL.md](PROJECT_CONTROL.md)。_

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。所有指标保持不变。

---

## 最新：Controller 工作流与文档控制面（2026-07-14）

- **Controller policy foundation**（`0f63a90`）：落地 orchestration / autonomy / worktree / integration / push / recovery 等策略文档（`plans/controller_*.md`）。
- **Runtime artifact isolation**（`d385bb6`）：扩展 ignore 边界，将 harvest bulk / validation noise / run_meta / guards 等 runtime 产物与仓库历史分离。
- **Agent infrastructure**（`4a62f78`）：新增 `.cursor/agents/*`（A/B/C/D executors + evidence / git-boundary / regression reviewers）。
- **PROJECT_CONTROL reconciliation**（`710b3c3`）：控制面寄存器与 post-integration Git 现实同步（A/B HOLD · queue · autonomy split）。
- **A/B local integration（先前已完成，本条仅登记）**：B fuller slice2 `f0bff3a` · A next-scale slice1 `4118974` · merge `71a83c1` · **无 push** · **无 verified** · **无 production_ready**。

---

## 最新：存储结构设计启动（2026-06-30）

- 开始设计动态平台的存储结构：`MinIO`（原始文件层）+ `MongoDB`（采集 / 解析 / 事件候选层）+ `PostgreSQL`（正式核心库）三层分工。
- `PostgreSQL` 定位为当前最优先验证的核心数据库方向，**非立即全量迁移**；`MongoDB` 纳入设计但不一定第一阶段部署。
- 仅文档：新增 [plans/storage_schema_design_plan.md](plans/storage_schema_design_plan.md)；**不改代码、不动数据、不部署任何数据库**。

---

## 动态平台架构讨论启动（2026-06-29）

- 开始从「静态年报数据库」转向「动态上市公司数据平台」的规划。
- 当前仅更新文档与路线，**不改代码、不跑数据、不动数据库**。
- 新增计划文件：[plans/dynamic_data_platform_plan.md](plans/dynamic_data_platform_plan.md)、[plans/README.md](plans/README.md)。
- 重新组织文档分工：`README.md`（入口）/ `ROADMAP.md`（大方向）/ `CURRENT_STATUS.md`（当前小方向）/ `CHANGELOG.md`（已完成）/ `plans/`（详细计划）。

---

## Stage 1：2024 年报结构化数据底座（已完成）

- **2024 全量提取**：`full_market_2024` 共 6124 家公司全集，5707 家成功，417 家未找到公告，0 错误；5 个板块批次顺序执行。
- **入库**：合并结果并导入 `SQLite`，约 62,890 条字段级记录。
- **字段证据**：每个字段尽量保留来源 PDF、页码、证据句、来源 URL。
- **更早的验证基础**：
  - 4 公司泛化测试 + 5 项通用鲁棒性修复（2026-06-16）。
  - 200 家分层评估 eval200（2026-06-17）。
  - 1000 家受控评估 eval1000，严格二次审计 `usable` 10.16/11（2026-06-18）。
  - eval1000_v2 同批重跑：947 成功，自动合理性分数 10.33/11。
  - 独立 1000 家泛化验证：918 成功，自动合理性分数 10.30/11，通过。
- **数据库与 schema 设计**（Issue #3–#8）：四表结构 + 金融子字段体系。

---

## Stage 2：质量审计与字段修复（已完成）

- **北交所审计规则修正**（#24）：北交所指标 7.14→7.71。
- **研发字段小范围刷新**（#25）：`rnd_investment` 找到率 67.9%→94.2%（+1460 未找到→找到）；核心指标 9.06→9.38。
- **收入字段小范围刷新**（#26）：分页表头恢复为主；`revenue_by_region` 错误 258→38、`revenue_by_segment` 109→19；297 个错误→可用；核心指标 9.38→**9.43/11**。
- **第 3a 阶段汇总**（#28）：第 3a 阶段质量跟进**通过**；非金融核心指标稳定在 `usable` **9.43/11**、自动合理性分数 **10.67/11**。

---

## Stage 3：金融 / 收入 / 研发 follow-up（已完成）

- **金融审计框架**（#27）：1059 个字段单元；银行 9.00/13、券商 7.66/12；325 格人工校准表待填写；金融指标与非金融 9.43/11 **分开报告**。
- **金融跟进汇总**（#30，含 #30a–#30g）：审计加固 + 定向抽取辅助；
  - #30a 券商 `not_found_missed` 收紧：人工校准一致率 62%→69.5%。
  - #30b 比率 / 表格审计校准：一致率 69.5%→71.7%。
  - #30d 券商收入召回：4/4 确认漏抽恢复，23/23 对照组保持非可用。
  - 全量金融推广暂缓；**无** CNINFO / YAML / SQLite 改动。
- **收入与研发残留关单**（#32）：盘点 513 行 + 研发 P0 小范围写回（104 家目标 / 32 家更新 / 0 错误 / 14 未找到→找到，写回后验证通过）+ 收入只读诊断（57 个错误字段单元分类，暂不生产写回）；**无**核心指标更新。
- **多年份扩展决策**（#33）：结论为 2025 优先、分阶段试点、按年重建公司全集；仅文档，**无**抽取 / CNINFO / SQLite。

---

## Stage 4：文档整理（已完成）

- **项目文档中文润色**（2026-06-26）：重写 README / CURRENT_STATUS / ROADMAP / CHANGELOG 与阶段汇总；集中术语表；保留文件名与指标不变。
- **协作结构整理**：GitHub 协作结构与中文文档目录。
- **早期框架**（2026-06-15 及更早）：多数据源验证框架、CNINFO 年报探测、确定性年报抽取器 v1、11 字段 schema 定义。
