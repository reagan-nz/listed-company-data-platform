# 上市公司基础数据库

## 一句话介绍

从 A 股公开年报 PDF 中批量抽取结构化字段，保留页码与证据句，建立可审计的公司数据底座。

---

## 老师阅读版

如果只看结论：

本项目已完成 **2024 年 A 股年报结构化数据底座的第一阶段质量闭环**。系统可以批量抽取字段、保留来源证据、运行严格质量审计，并对问题字段做小范围修复。

但它**还不是**完整的智能问答产品，**也不是**全量人工验证后的最终数据库。金融公司与非金融公司的质量指标**分开报告**，不得混为一谈。

---

## 现在已经完成什么

| 事项 | 结果 |
|---|---|
| 2024 全市场抽取 | 6124 家公司全集，5707 家成功，417 家未找到公告，0 技术错误 |
| 数据入库 | SQLite 共 62,890 条字段级记录 |
| 质量审计与修复 | 第 3a 阶段通过；非金融核心指标 **9.43/11** |
| 残留问题处理 | #30 金融跟进、#32 收入与研发残留、#33 多年份决策均已文档化 |

详细数字见 **[CURRENT_STATUS.md](CURRENT_STATUS.md)**。

---

## 当前能达到什么标准

- 已完成 2024 年 A 股年报**结构化数据底座**的第一阶段质量闭环。
- 可批量抽取、记录证据、运行严格质量审计，并做小范围定向刷新或小范围写回。
- 数据可支撑内部分析、字段查询、公司档案，以及检索增强问答原型的底层数据层。

---

## 当前不能宣称什么

- **不是**全量人工验证（62,890 行未逐条人工核对）。
- **不是**完整的 RAG 产品或大模型知识页产品。
- **不是**所有字段都已完全修复。
- **不能**将金融公司指标与非金融核心指标 9.43/11 混报。
- **不能**声称 #32c 小范围写回已更新全局 9.43/11。

---

## 老师 / 评审应该怎么阅读

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 主进度页（建议从这里开始）
2. **[stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md)** — 第 3a 阶段质量汇总
3. **[ROADMAP.md](ROADMAP.md)** — 分阶段路线图
4. **[CHANGELOG.md](CHANGELOG.md)** — 变更记录
5. **[docs/](docs/)** — 评估方法、数据库、抽取流程等技术细节

---

## 核心指标入口

最新指标不在此重复（避免文档过期）。请查看 [CURRENT_STATUS.md](CURRENT_STATUS.md) 的「当前关键数字」一节。

当前非金融核心指标：**9.43/11**（运行名称 `full_market_2024_revenue_refresh`）。

---

## 文档目录

| 文档 | 说明 |
|---|---|
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | 主进度页 |
| [ROADMAP.md](ROADMAP.md) | 路线图 |
| [CHANGELOG.md](CHANGELOG.md) | 变更记录 |
| [docs/evaluation_method.md](docs/evaluation_method.md) | 评估方法 |
| [stage3_quality_followup_summary.md](outputs/generalization/full_market_2024/stage3_quality_followup_summary.md) | 第 3a 阶段汇总 |
| [multiyear_expansion_decision_33.md](outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md) | 多年份扩展决策 |
| [plans/](plans/) | 历史方案归档 |

---

## 技术术语简表

| 术语 | 含义 |
|---|---|
| `full_market_2024` | 2024 年全 A 股年报抽取运行 |
| `run_name` | 一次运行的名称，用于输出目录与数据库批次 |
| 严格质量审计 | 对已存字段做更严规则复核，标签含 `usable` / `partial` / `wrong` |
| 自动合理性分数 | 抽取时的结构合理性估计，通常高于严格审计结果 |
| 小范围定向刷新 | 用已缓存 PDF 仅重抽部分字段，不重新全量下载 |
| 小范围写回 | 经验证通过的修复，写回少量公司档案 |
| 只读诊断 | 不写回档案，仅评估修复效果 |
| 核心指标 | 对外报告的主质量数字；非金融与金融分开 |
| 分组样本 | 按规则选出的公司集合，如 eval1000 |
| 试点 | 小规模试跑，验证管道后再扩全市场 |
| 历史年份回填 | 在 2025 基线稳定后补跑 2023/2022 等历史年报 |
| `not_found_missed` | PDF 中应有披露但抽取结果为未找到 |
| CNINFO | 巨潮资讯网，法定信息披露来源 |
| SQLite | 项目使用的轻量数据库原型 |
| RAG | 检索增强生成；本项目提供底层数据，非完整产品 |
| LLM Wiki | 大模型知识页原型；本项目尚未交付 |

完整指标解释见 [CURRENT_STATUS.md](CURRENT_STATUS.md) 与 [docs/evaluation_method.md](docs/evaluation_method.md)。

---

## 快速开始

```bash
cd listed_company_data_collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```bash
# 单公司抽取（需本地 PDF + 官方 URL）
python lab/extract_annual_report.py \
  --pdf path/to/report.pdf --stock-code 600031 \
  --source-url https://static.cninfo.com.cn/...

# 批量评估（需网络，可断点续跑）
python lab/eval_generalize.py \
  --companies lab/eval_companies_1000.yaml \
  --out outputs/generalization/eval1000 --throttle 1.0
```

---

## 项目结构

```
listed_company_data_collector/
  lab/           # 年报抽取与评估
  config/        # 公司与数据源配置
  outputs/       # 运行产物（PDF 不提交 Git）
  docs/          # 技术文档
  plans/         # 方案归档
```
