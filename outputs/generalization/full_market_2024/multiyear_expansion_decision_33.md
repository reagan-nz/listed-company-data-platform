# 多年份扩展决策备忘录 — Issue #33

_生成日期：2026-06-26 | 仅规划/文档 — 无抽取运行_

**术语说明：** headline = 核心指标；strict audit = 严格质量审计；validation gates = 验证门槛；human sign-off = 人工确认；Financial cohort = 金融公司分组；staged rollout = 分阶段推广。

---

## 关单决定

**#33 作为决策备忘录已关闭**。本文档记录多年份扩展推荐策略，供任何 2025 试点执行前人工确认。**Parent #23**（#24–#33）在本备忘录与文档同步提交后**可以关单**。

---

## 1. 执行摘要建议

**优先 2025，分阶段推广 — 非并行多年份，非 2023/2022 历史回填优先。**

| 决策项 | 建议 |
|---|---|
| 下一年份 | **2025 年报优先** |
| 评估全集 | **按年重建** — 来自 CNINFO，**非**冻结 2024 名单 |
| 推广路径 | **100 家分层试点 → 单板块试点 → 全市场 2025 → 回填 2023/2022** |
| CNINFO | **不**立即全市场 CNINFO；试点控制下载范围 |
| 2024 产出 | **不覆盖** — 独立 `run_name` 与输出目录 |
| 核心指标 | **2024 非金融 9.43/11 不变**，直至对该分组样本有意安排全量严格质量审计 |

**理由：** 2025 用已在 2024 验证的抽取栈向前延伸活基线；历史回填增加历史深度但运营优先级较低、模板漂移风险更高。分阶段推广在承诺约 6k+ 公司前限制磁盘、CNINFO 与回归风险。

---

## 2. 当前 2024 就绪度

| 维度 | 状态 | 说明 |
|---|---|---|
| Stage 3a 质量跟进 | **通过**（有限制说明） | 见 [stage3_quality_followup_summary.md](stage3_quality_followup_summary.md) |
| 非金融 strict 核心指标 | **9.43/11** | `run_name`=`full_market_2024_revenue_refresh`；#32 后**不变** |
| 金融公司分组 | **单独核心指标** | bank/broker/insurer 子 schema；校准表人工打分部分待完成 |
| 抽取管道 | **工业 11 字段生产就绪** | #24–#26 北交所/rnd/revenue 改善；#32c R&D 辅助 |
| 残留问题（非阻塞） | 已文档化 | #31 漏标；#32 收入试点暂缓；R&D partial |
| SQLite / CNINFO | **2024 已导入** | 62,890 行；本备忘录**无需**重跑 |
| 工具链 | **年份参数化需少量脚本工作** | `make_full_market_yaml.py`、批次合并、严格质量审计 — **不在** #33 范围 |

**就绪结论：** 2024 基线在前置条件（§5）与人工清单（§12）满足后**足以启动 2025 试点**。全市场 2025 应待验证门槛通过。

---

## 3. 方案对比

### 3.1 方案 A — 2025 优先（推荐）

| 优点 | 缺点 |
|---|---|
| 与「当前年份」数据库增长方向一致 | 2025 报告可能仍在披露（时间风险） |
| 复用 #24–#32 最新抽取修复 | 新年模板漂移需试点后才能知 |
| 自然扩展 SQLite `report_year=2025` | 需按年重建评估全集 |
| 督导叙事：向前推进 | 不立即填补历史缺口 |

### 3.2 方案 B — 2023/2022 历史回填优先

| 优点 | 缺点 |
|---|---|
| 研究用历史面板 | 旧 PDF 版式/披露规范不同 |
| 相对最新年份「新闻压力」较小 | 相对扩展活基线优先级较低 |
| 部分公司自 2022/2023 已退市 | 退市/评估全集对账更难 |
| | 推迟 2025 管道验证 |

### 3.3 方案 C — 并行多年份（2025 + 2023 + 2022）

| 优点 | 缺点 |
|---|---|
| 历史覆盖最快 | 3× CNINFO 负载、磁盘、合并复杂度 |
| | 难以跨年归因回归 |
| | 违反 full_market_2024 分阶段风险政策 |
| | 无隔离试点学习 |

**决策：** **方案 A**，全市场 2025 成功后再明确历史回填阶段。

---

## 4. 推荐路径

```
Phase 0  前置条件（#31 重打标签复核、试点 YAML 工具人工确认）
    ↓
Phase 1  full_market_2025_pilot — 100 家分层样本
    ↓  （验证门槛 §8）
Phase 2  full_market_2025_pilot_bse — 单板块试点（建议北交所：最小、strict 迭代最多）
    ↓
Phase 3  full_market_2025 — 全 A 股 2025 评估全集，5 板块批次顺序
    ↓  （严格质量审计 + 汇总；单独核心指标）
Phase 4  full_market_2023_backfill — 按年评估全集，同批次策略
    ↓
Phase 5  full_market_2022_backfill — 按年评估全集，同批次策略
```

**并行工作（不阻塞 Phase 1）：** 收入 Tier4 试点（#32b）、R&D 剩余 partial — **勿**阻塞 2025 试点（若单独小范围推进）。

**禁止：** 跳过 Phase 1–2；覆盖 `outputs/generalization/full_market_2024/`；一次性全量 CNINFO 跑所有年份。

---

## 5. 扩展前置条件

| # | 前置条件 | 负责人 | 阻塞项 |
|---|---|---|---|
| P1 | **本备忘录人工确认**（§12 清单） | 督导 | 任何 CNINFO 下载 |
| P2 | **#31 金融漏标复核** — 至少文档化 `000402` / `600816` / `600318` 重打标签决策及 8 个金融控股类 revenue wrong | 人工 + 开发 | 金融 2025 strict 核心指标可信度 |
| P3 | **年份参数化运行脚本** — `make_full_market_yaml.py --year 2025`、批次 runner、合并、审计入口（实现 issue，#33 之后） | 开发 | Phase 1+ |
| P4 | **试点评估全集 YAML** — 100 家分层样本（板块 × 规模 × 金融标签）；seed 沿用 `sample_universe.py` 模式 | 开发 | Phase 1 |
| P5 | **磁盘 / CNINFO 预算** — 估算约 6k PDF × N 年；确认 `outputs/generalization/` 下存储路径 | 运维 | Phase 2+ |
| P6 | **评估方法文档** — 确认 2025 指标使用同一 strict audit 脚本版本；汇总中记录 `run_name` | 开发 | Phase 3 核心指标 |
| P7 | **2025 报告可用性** — 确认 CNINFO 上多数 A 股 2025 年报已发布 | 人工 | Phase 3 时间 |

**软前置（可暂缓）：** 收入 Tier4 生产试点；全量 R&D partial 修复；金融校准表 325 字段单元格打分完成。

---

## 6. 试点设计

### 6.1 Phase 1 — 100 家分层试点

| 参数 | 值 |
|---|---|
| `run_name` | `full_market_2025_pilot` |
| 规模 | **100** 家公司 |
| 分层 | 约 5 板块按比例；含 ≥5 家金融标记；含 ≥10 家北交所；seed 固定可复现 |
| 字段 | 完整 11 字段工业 + 已标记处金融子 schema |
| 成功标准 | ok 率 ≥90%；error=0；proxy 在 eval1000_v2 参考 ±0.15 内；强制对照无阻塞回归（002415、000333、600011 类） |
| 输出 | `outputs/generalization/full_market_2025_pilot/` |

### 6.2 Phase 2 — 单板块试点

| 参数 | 值 |
|---|---|
| `run_name` | `full_market_2025_pilot_bse`（推荐） |
| 规模 | 完整**北交所** 2025 评估全集（约 580–650 家，按年名单） |
| 理由 | 最小板块；北交所 strict 迭代最多（#24）；反馈快 |
| 成功标准 | ok 率与 2024 北交所可比；strict audit 可运行；合并 + 汇总已生成 |
| 输出 | `outputs/generalization/full_market_2025_pilot_bse/` |

### 6.3 Phase 3 — 全市场 2025

| 参数 | 值 |
|---|---|
| `run_name` | `full_market_2025` |
| 批次顺序 | **bse → star → szse_main → chinext → sse_main**（同 2024） |
| 评估全集 | **按年** CNINFO A 股 2025 披露季名单 |
| 运行后 | 混合 strict audit + `full_market_2025_summary.md`；SQLite 导入 `run_name=full_market_2025` |
| 小范围定向刷新 | 沿用 2024 模式：先抽取；仅当残留 warrant 时 rnd/revenue 刷新 |

---

## 7. run_name / 输出目录规划

| 阶段 | `run_name` | 输出目录 | SQLite `run_name` | 覆盖 2024？ |
|---|---|---|---|---|
| 100 家试点 | `full_market_2025_pilot` | `outputs/generalization/full_market_2025_pilot/` | `full_market_2025_pilot` | **否** |
| 板块试点 | `full_market_2025_pilot_bse` | `outputs/generalization/full_market_2025_pilot_bse/` | `full_market_2025_pilot_bse` | **否** |
| 全量 2025 | `full_market_2025` | `outputs/generalization/full_market_2025/` | `full_market_2025` | **否** |
| 2023 回填 | `full_market_2023_backfill` | `outputs/generalization/full_market_2023_backfill/` | `full_market_2023_backfill` | **否** |
| 2022 回填 | `full_market_2022_backfill` | `outputs/generalization/full_market_2022_backfill/` | `full_market_2022_backfill` | **否** |

**小范围定向刷新运行**（若后续需要）：追加后缀 — 如 `full_market_2025_rnd_refresh`、`full_market_2025_revenue_refresh` — 沿用 2024 惯例。

**YAML 命名：** `lab/eval_companies_full_market_2025.yaml`、`lab/eval_companies_full_market_2025_pilot.yaml` 等。

**Gitignore：** 同 2024 — PDF、每公司子目录、`eval_results.json` 忽略；summary markdown 可提交。

---

## 8. 验证门槛

| 门槛 | 之后 | 进入下一阶段前必须满足 |
|---|---|---|
| **G1 试点抽取** | Phase 1 | ok ≥90%，error=0，人工抽查 10 家公司 |
| **G2 试点 proxy** | Phase 1 | 非金融 proxy 在相对 eval1000_v2 的约定区间内 |
| **G3 板块试点** | Phase 2 | 全板块合并 OK；strict audit 脚本无崩溃运行 |
| **G4 板块 strict** | Phase 2 | 北交所 strict ≥8.5/11 或文档化模板差距计划 |
| **G5 全量抽取** | Phase 3 | ok 率 ≥2024 参考（93%±2%）；error=0 |
| **G6 全量 strict audit** | Phase 3 | 混合 strict 完成；2025 目录下**单独** `strict_audit_summary.md` |
| **G7 SQLite 导入** | Phase 3 | 行数 sanity vs ok × 字段；FK 干净 |
| **G8 核心指标发布** | Phase 3 | **仅 G6 之后** — 发布 2025 非金融 strict 为**新核心指标**；**勿** retro 编辑 2024 |
| **G9 回填** | Phase 4–5 | 每年独立通过 G5–G7 |

**跨年比较规则：** 2025 strict usable **不得**与 2024 **9.43/11** 直接比「改善」，除非同一 audit 方法版本在两队 cohort 上运行且规则对等已文档化。

---

## 9. 风险登记

| 风险 | 可能性 | 影响 | 缓解 |
|---|---|---|---|
| 2025 报告未完全发布 | 中 | Phase 3 延迟 | 尽早启动 Phase 1–2；监控 CNINFO |
| 2025 PDF 模板/版式漂移 | 中 | 字段回归 | 100 家试点 + 板块试点后再全量 |
| 按年评估全集 ≠ 2024 名单 | 高 | ok/no_announcement 差异 | 预期内；汇总中文档化 |
| 磁盘耗尽（多年 PDF） | 中 | 运行失败 | 板块批次顺序；gitignore PDF；回填顺序执行 |
| CNINFO 限速 / VPN 问题 | 中 | ChunkedEncodingError | 沿用 eval1000 独立运行重试策略 |
| 金融误标传播 | 中 | 错误子 schema 评估 | 金融 2025 核心指标前完成 #31 |
| 2024/2025 指标混报 | 中 | 误导叙事 | 分开 `run_name`、分开 summary 文件 |
| 跳过试点直接全量 CNINFO | 低 | 高成本失败 | 人工门槛 P1；不得声称 §11 |

---

## 10. 暂缓项（仍在 #33 / 初始 2025 范围外）

| 事项 | Issue | 说明 |
|---|---|---|
| 收入 Tier4 + 错表生产试点 | #32b 跟进 | 仅试跑框架信号；暂缓至试点后或并行小范围批次 |
| R&D 剩余 partial（72/104 P0 + 全人口） | #32 暂缓 | 不阻塞 2025 向前抽取 |
| 收入 partial 全量方法论（约 753） | #32 暂缓 | 枚举暂缓 |
| 金融更大范围抽取推广 | #30 暂缓 | 审计框架已完成；打分待完成 |
| #32c 后 2024 全量 strict audit 重跑 | 政策暂缓 | 9.43/11 不变 |
| BrowserUser 数据源 | ROADMAP Phase 4 | 多年基线稳定后 |
| `strict_audit_result` SQLite loader | 可选 | 低优先级 |
| 并行 2023+2022+2025 CNINFO | **已拒绝** | 见 §3.3 |

---

## 11. 不得声称

| 声称 | 是否允许 |
|---|---|
| #33 决策备忘录已完成 | **是** |
| 多年份扩展已执行 | **否** — 仅规划 |
| #33 中执行了 CNINFO 重跑 | **否** |
| 未来年份全量人工验证 | **否** |
| 2025 指标可与 2024 9.43/11 直接比 delta | **否** — 需同一 audit 方法 |
| 金融与非金融指标合并 | **否** — 单独核心指标 |
| #33 更新了 2024 核心指标 | **否** — 仍为 9.43/11 |
| Parent #23 可以关单 | **是** — memo 提交 + 人工确认后 |
| #31 / 收入试点永久阻塞 | **否** — 并行后续待办 |

---

## 12. 决策清单（人工确认）

- [ ] **A1** 批准 **2025 优先**（非 2023/2022 先回填）
- [ ] **A2** 批准 **按年评估全集**（非冻结 2024 名单用于 2025 生产）
- [ ] **A3** 批准 **分阶段推广**：100 家 → 板块 → 全量 → 回填
- [ ] **A4** 批准 **run_name / 目录** 方案（§7）
- [ ] **A5** 确认 **2024 产出只读** — 不覆盖
- [ ] **A6** 确认 **#31 重打标签复核** 时间（Phase 1 前或并行）
- [ ] **A7** 确认 **CNINFO 预算** 与试点 + 全量 2025 磁盘
- [ ] **A8** 确认 **2025 披露季** 就绪度与 Phase 3 目标日期
- [ ] **A9** 批准开启 **年份参数化脚本实现 issue**（#33 之后）
- [ ] **A10** memo 提交后关闭 **#33** 与 **#23**

---

## 13. 可提交 / 勿提交列表

### 可提交

- `outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md`（本文件）
- 文档同步：`CURRENT_STATUS.md`、`CHANGELOG.md`、`ROADMAP.md`、`stage3_quality_followup_summary.md`

### 勿提交（#33 未产出）

- 任何 `outputs/generalization/full_market_2025*/` 目录
- PDFs、`eval_results.json`、`company_profile.json`
- SQLite DB 变更
- 新 YAML 评估全集文件（至实现阶段）

---

## 14. GitHub #33 关单评论（中文）

```
#33 多年份扩展决策 — 已完成（决策备忘录）

结论：优先 2025，分阶段推广，2024 产出只读不覆盖。

推荐路径：
1. 100 家分层试点（full_market_2025_pilot）
2. 单板块试点（建议北交所，full_market_2025_pilot_bse）
3. 全市场 2025（full_market_2025）
4. 再回填 2023 / 2022（full_market_2023_backfill、full_market_2022_backfill）

关键决策：
- 下一年份：2025 优先（非 2023/2022 先回填）
- 评估全集：按年重建 CNINFO 列表（非冻结 2024 名单）
- 不立即全量 CNINFO；不并行多年份
- run_name / 输出目录与 2024 分离
- 2024 非金融 strict 9.43/11 核心指标不变

前置条件：本备忘录人工确认、#31 金融漏标复核、年份参数化脚本（后续 implementation issue）、磁盘/CNINFO 预算。

暂缓：revenue Tier4 试点、R&D partial、2024 全量 strict audit 重跑、BrowserUser。

未做：抽取、CNINFO、refresh、strict audit、SQLite、YAML、代码修改。

产物：multiyear_expansion_decision_33.md
```

---

## 决策问题速查

| # | 问题 | 答案 |
|---|---|---|
| 1 | 2025 优先还是回填 2023/2022？ | **2025 优先** |
| 2 | 2024 评估全集还是按年？ | **按年评估全集** |
| 3 | 试点、板块还是直接全市场？ | **分阶段：100 家 → 板块 → 全量** |
| 4 | 前置条件？ | §5 — 人工确认、#31、工具链、磁盘、披露季 |
| 5 | run_name 命名？ | §7 — `full_market_2025_pilot`、`_pilot_bse`、`full_market_2025`、`_2023_backfill`、`_2022_backfill` |
| 6 | 验证门槛？ | §8 — G1–G9 |
| 7 | 暂缓项？ | §10 |
| 8 | 金融 vs 非金融？ | **分开核心指标**；金融子 schema 评估；永不混入 9.43/11 |
| 9 | 不得声称？ | §11 |

---

## Parent #23 关单评论草稿（中文）

```
#23 Stage 3 质量跟进与多年份规划 — 可以关单

子 issue 全部完成：
- #24 北交所 strict audit-rule
- #25 rnd 小范围定向刷新
- #26 revenue 小范围定向刷新
- #27 金融 strict audit 框架
- #28 Stage 3a 汇总
- #30 金融跟进（#30a–#30g）
- #31 金融漏标候选已识别（重打标签执行暂缓至 2025 前置）
- #32 revenue/R&D 残留当前范围关闭
- #33 多年份扩展决策备忘录

2024 基线状态：
- Stage 3a 通过（有保留项）
- 非金融 strict usable 9.43/11（不变）
- 金融公司分组单独核心指标
- 2024 产出只读；后续 2025 分阶段扩展

后续工作（新 issue，非 #23 范围）：
- 2025 试点实施（人工确认 §12 后）
- #31 重打标签复核
- revenue Tier4 / R&D partial 后续待办
- BrowserUser（ROADMAP Phase 4）

产物索引：stage3_quality_followup_summary.md、revenue_rnd_fix_32_final_summary.md、multiyear_expansion_decision_33.md
```
