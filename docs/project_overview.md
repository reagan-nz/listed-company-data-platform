# 项目概览

## 项目目标

搭建中国 **A 股上市公司基础数据库**，从公开披露信息中提取结构化基础标签，为后续公司分析、行业研究、产业链挖掘提供数据基础。

**短期**（当前）：基于巨潮资讯网公开年报 PDF，抽取 11 项基础字段。

**中期**：覆盖全部 A 股上市公司，形成可查询、可更新的基础数据库。

**长期**：用 BrowserUser 爬虫智能体补充 PDF 无法覆盖的数据（投资者互动、官网 IR、招投标等），并用跨年度对比提供变化追踪能力。

## 设计原则

1. **证据链优先**：每个字段保留 `source_url`、`page`、`evidence_sentence`，可回溯到原文。
2. **不编造数据**：字段不存在时返回 `not_found`，不填充默认值。
3. **确定性抽取**：当前不使用 LLM 做字段抽取；规则 + 锚点 + 表格解析。
4. **公司无关**：代码中不 hard-code 任何公司；公司信息来自 CLI 或 YAML 配置。
5. **合规边界**：只访问公开数据；不绕过登录、验证码、付费墙。

## 系统架构

```
公司列表 (YAML)
    │
    ▼
CNINFO probe ──→ 查询年报公告 ──→ 下载 PDF
    │
    ▼
PDF 解析 (PyMuPDF + pdfplumber)
    │
    ▼
字段定位 (锚点 + region + avoid)
    │
    ▼
字段抽取 (section_snippet / table / numeric / concentration)
    │
    ▼
company_profile.json + company_brief.md
    │
    ▼
评估 / 校准 / 审计
```

## 目录结构

```
listed_company_data_collector/
├── lab/                    # 核心：年报抽取与评估
│   ├── extract_annual_report.py   # 确定性抽取器
│   ├── field_schema.py            # 11 字段定义
│   ├── probe_cninfo.py            # CNINFO 年报获取
│   ├── eval_generalize.py         # 批量评估 harness
│   ├── calibration_sample.py      # 人工校准工具
│   └── sample_universe.py         # 分层抽样
├── config/
│   ├── companies.yaml             # 公司列表（运行时配置）
│   └── sources.yaml               # 多数据源定义（早期框架）
├── collectors/             # 15 类数据源采集器（早期框架）
├── parsers/                # HTML / PDF / 表格解析
├── utils/                  # 通用工具
├── main.py                 # 早期多数据源验证入口
├── outputs/                # 运行产物（PDF 不提交 Git）
├── docs/                   # 中文技术文档
└── plans/                  # 历史方案归档
```

## 核心模块

| 模块 | 文件 | 职责 |
|---|---|---|
| 年报获取 | `lab/probe_cninfo.py` | CNINFO API 查询、orgId 解析、PDF 下载、全文筛选 |
| 字段 schema | `lab/field_schema.py` | 11 字段定义：锚点、区域、抽取方式、avoid 规则 |
| 抽取器 | `lab/extract_annual_report.py` | PDF 解析 → 定位 → 抽取 → 输出 profile |
| 评估 | `lab/eval_generalize.py` | 批量跑抽取 + plausible 代理评分 |
| 校准 | `lab/calibration_sample.py` | 分层抽样 + 人工评分 + 指标计算 |

## 相关文档

- [数据来源](data_sources.md)
- [年报抽取流程](annual_report_extraction.md)
- [字段 schema](database_schema.md)
- [评估方法](evaluation_method.md)
- [爬虫策略](crawler_strategy.md)
- [GitHub 协作流程](github_workflow.md)
