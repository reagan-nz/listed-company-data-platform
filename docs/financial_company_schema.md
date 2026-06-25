# 金融公司字段体系 v1

_最后更新：2026-06-25（#30 financial follow-up docs sync）_

> **实现状态（Issue #4 + #27）**：`lab/field_schema.py` 已实现 `BANK_FIELD_SPECS` / `BROKER_FIELD_SPECS` / `INSURER_FIELD_SPECS` / `OTHER_FINANCIAL_FIELD_SPECS`，以及 `detect_profile()` / `resolve_profile()` / `get_field_specs()` 分发。eval 对 `financial: true` 公司使用子 schema；非金融仍用工业 11 字段。
>
> **full_market_2024**：86 家金融 ok 已用子 schema 跑通；**不纳入**非金融 11 字段 headline（proxy / strict usable 仅统计 `financial: false` 的 5621 家；非金融 strict **9.43/11**）。
>
> **#27 金融 audit（2026-06-25，Phase 0–1B）**：
> - Phase 0：`financial_population_inventory.csv`（87 tagged / 86 ok；bank 43 / broker 37 / insurer 2 / other 4）
> - Phase 1A：`lab/strict_audit_financial_full_market.py` + `financial_audit_population.csv`（1,059 cells）+ [financial_audit_summary.md](../outputs/generalization/full_market_2024/financial_audit_summary.md)
> - Phase 1B：`lab/financial_calibration_sample.py` + `financial_audit_sample.csv`（30 公司 × 325 cells；**manual_grade 待填写**）
> - **单独报告**金融 strict（按 subtype）；**不得**与 non-fin 9.43/11 混报
> - 详见 [CURRENT_STATUS.md](../CURRENT_STATUS.md) §4.2
>
> **尚未完成（#28+）**：
> - 金融专用 plausible / extract 规则（Phase 3）；当前仍复用 generic `extract_numeric` / `table_match`，**数值字段可能含噪声**
> - auto-tag / subtype 修正（000402 金融街、600816 建元信托、600318 新力金融 等待 review）
> - 325 格 manual calibration **grading 待完成**（非全量人工验证）
> - DB `financial_subtype` 列未入库（Phase 5 未做）

## #30 results snapshot

`#30a–#30g` has now completed as a focused financial follow-up tranche:

- **audit-only**:
  - `#30a` broker `not_found_missed` tightening
  - `#30b` ratio/table calibration + `major_subsidiaries` gate
  - `#30e` financial table plausibility hardening
  - `#30f` insurer low-n semantic hardening
- **extraction helpers**:
  - `#30c` bank ratio helper
  - `#30d` broker income / margin recall helper
- **diagnosis-only**:
  - `#30g` subtype/tag review

Key outcome posture:

- financial follow-up delivered meaningful audit/extraction improvements
- financial metrics still remain **separate** from non-fin `9.43/11`
- wider financial rollout is still **deferred**
- insurer cohort remains **n=2**, so broader insurer generalization is not signed off

Subtype caveats from `#30g` (diagnosis-only; **no YAML changes yet**):

- `000402` 金融街: likely **not broker**; may be better treated as industrial / non-financial after human review
- `600816` 建元信托: clearly trust-like; **not bank**
- `600318` 新力金融: diversified financial holding; **not bank**

See [financial_audit_fix_30_summary.md](../outputs/generalization/full_market_2024/financial_audit_fix_30_summary.md) for the consolidated `#30` closeout.

## 1. 为什么需要单独 schema

当前 11 字段 schema（`lab/field_schema.py` 中的 `FIELD_SPECS`）面向工业/制造/科技/消费类公司设计，假设年报中存在：

- **主营业务分行业/分产品** 表格（营业收入、营业成本、毛利率）
- **前五名客户/供应商** 集中度披露
- **研发投入** 金额与占比
- **主要产品及服务** 独立章节

金融类上市公司（银行、券商、保险）的业务结构与披露重点完全不同：

| 工业公司典型披露 | 金融公司典型披露 |
|---|---|
| 营业收入 = 产品/服务销售收入 | 营业收入 = 利息净收入 + 手续费及佣金 + 投资收益 + … |
| 分行业/分产品收入表 | 分业务条线收入表（零售/公司金融、经纪/投行/资管、寿险/财险） |
| 前五名客户/供应商 | 最大十家借款人、客户集中度（银行）；通常不披露供应商 |
| 研发投入 | 信息科技投入（可选）；多数金融公司无 R&D 章节 |
| 毛利率 | 净息差、成本收入比、综合成本率、资本充足率 |

若用工业 schema 评估金融公司，会出现：

1. **字段语义错配**：`revenue_by_segment` 锚点指向「主营业务分行业/分产品」，金融年报中不存在该表；`top_suppliers` 几乎永远 `not_found`。
2. **plausible 率虚低**：4 公司泛化测试中，招商银行仅 4/11 CORRECT + 2 ABSENT-OK；eval1000 中 12 家金融公司若计入 headline，会拉低整体指标。
3. **关键信息缺失**：净息差、不良贷款率、资本充足率、偿付能力充足率等金融核心指标完全不在当前 schema 中。

`lab/field_schema.py` 中已有实验性 `FINANCIAL_FIELD_SPECS`（单一 generic profile，11 个 key 与工业 schema 相同），通过 `--profile financial` 或 `detect_profile()` 选用。代码注释已明确：**生产版本需要拆分为 bank / insurer / broker 子 schema**。Issue #3 将这一 future work 文档化，**暂不修改抽取代码**。

## 2. 金融公司分类

按 A 股年报披露惯例与 eval1000 样本，划分为四类：

| 子类型 | 代码前缀 | eval1000 样本 | 典型披露特征 |
|---|---|---|---|
| **银行** (`bank`) | 601xxx / 600xxx 大型国有行 | 中国银行、工商银行、建设银行、交通银行 | 利息净收入、存贷款结构、不良率、资本充足率 |
| **券商/经纪** (`broker`) | 601xxx / 600xxx / 002xxx 证券 | 东方证券、方正证券、天风证券、国信证券、山西证券、宏源证券 | 经纪/投行/资管/自营收入、融资融券、净资本指标 |
| **保险** (`insurer`) | 601xxx / 600xxx 保险 | 新华保险 | 已赚保费、寿险/财险分部、偿付能力、内含价值 |
| **其他金融** (`other_financial`) | 期货、信托、多元金融等 | 永安期货 | 暂复用 generic financial profile；期货专用 schema 后续再议 |

**分类依据**（实现阶段）：优先使用 eval 列表中的 `financial: true` 标记 + 证监会行业分类；可选 `detect_profile()` 扩展为返回 `bank` / `broker` / `insurer` / `other_financial` / `industrial`。

## 3. 子 schema 字段提案（v1）

以下字段均沿用 `FieldSpec` 结构。**v1 已写入 `field_schema.py`（Issue #4）。**

### 3.1 银行子 schema（`bank_v1`）

#### 共享字段（与工业 schema 相同或微调锚点）

| key | label_cn | extraction | 说明 |
|---|---|---|---|
| `mda` | 管理层讨论与分析 | section_snippet | 锚点不变 |
| `industry_discussion` | 所处行业/经营环境 | section_snippet | 增加「监管政策」「宏观环境」等锚点 |
| `risk_factors` | 风险因素 | section_snippet | 增加「信用风险」「市场风险」「流动性风险」「操作风险」 |
| `major_subsidiaries` | 主要控股参股公司 | section_snippet | 锚点不变 |
| `main_business_segments` | 主营业务/业务分部 | section_snippet | 锚点改为：主要业务分部、零售金融、公司金融、金融市场 |

#### 银行专用字段

| key | label_cn | extraction | anchors（草案） | expected_location |
|---|---|---|---|---|
| `net_interest_income` | 利息净收入 | numeric | 利息净收入、净利息收入、利息收入合计 | MD&A 或利润表摘要 |
| `non_interest_income` | 非利息收入 | numeric | 非利息收入、手续费及佣金净收入、中间业务收入 | MD&A 收入构成 |
| `loan_structure` | 贷款结构 | table | 贷款总额、公司贷款、个人贷款、票据贴现 | MD&A 或附注「发放贷款及垫款」 |
| `deposit_structure` | 存款结构 | table | 吸收存款、对公存款、个人存款、公司存款 | MD&A 或附注「吸收存款」 |
| `npl_ratio` | 不良贷款率 | numeric | 不良贷款率、不良率、不良贷款比例 | MD&A 资产质量 / 风险管理 |
| `capital_adequacy_ratio` | 资本充足率 | numeric | 资本充足率、核心一级资本充足率、一级资本充足率 | MD&A 资本管理 |
| `provision_coverage_ratio` | 拨备覆盖率 | numeric | 拨备覆盖率、贷款损失准备覆盖率 | MD&A 资产质量 |
| `regional_distribution` | 地区分布 | table | 地区分部、分地区、长三角、环渤海 | 大型银行 MD&A 地区分部表（可选） |

**银行不适用 / 需替换的工业字段：**

- `top_customers` → 替换为 **最大十家借款人** / 客户贷款集中度（anchors: 最大十家客户、最大单一客户、前十大客户）
- `top_suppliers` → **N/A**（标记 `not_applicable`）
- `revenue_by_segment` → 由 **业务分部收入表** 替代（anchors: 分部业绩、业务分部、利息净收入、手续费及佣金）
- `revenue_by_region` → 由 `regional_distribution` 替代（大型银行才有）
- `rnd_investment` → 可选 **信息科技投入**（anchors: 科技投入、信息科技投入、金融科技投入）；多数银行无此披露
- `major_products` → **N/A**（金融产品分散在业务分部叙述中）

---

### 3.2 券商/经纪子 schema（`broker_v1`）

#### 共享字段

同银行：`mda`, `industry_discussion`, `risk_factors`, `major_subsidiaries`, `main_business_segments`（锚点：经纪业务、投资银行业务、资产管理业务、自营业务）

#### 券商专用字段

| key | label_cn | extraction | anchors（草案） | expected_location |
|---|---|---|---|---|
| `brokerage_income` | 经纪业务收入 | numeric | 经纪业务、经纪业务收入、证券经纪 | MD&A 分业务经营情况 |
| `investment_banking_income` | 投资银行业务收入 | numeric | 投资银行业务、投行业务、承销保荐 | MD&A 分业务经营情况 |
| `asset_management_income` | 资产管理业务收入 | numeric | 资产管理业务、资管业务、受托客户资产管理 | MD&A 分业务经营情况 |
| `proprietary_trading_income` | 自营/投资收入 | numeric | 自营业务、投资收益、公允价值变动损益 | MD&A 或利润表摘要 |
| `margin_lending_balance` | 融资融券余额 | numeric | 融资融券、融出资金、融券 | MD&A 信用业务 |
| `risk_control_indicators` | 风险控制指标 | numeric / table | 净资本、净资本与净资产比率、风险覆盖率、流动性覆盖率 | MD&A 风险控制指标表 |
| `revenue_by_segment` | 营业收入构成-分业务 | table | 分部信息、分业务、手续费及佣金 | MD&A 分业务经营情况表 |

**券商不适用字段：**

- `top_customers` → 意义有限；若披露则为 **客户集中度**（弱优先级）
- `top_suppliers` → **N/A**
- `revenue_by_region` → 极少披露 → **N/A** 或 optional
- `rnd_investment` → 可选 科技投入
- `major_products` → **N/A**

---

### 3.3 保险子 schema（`insurer_v1`）

#### 共享字段

同银行：`mda`, `industry_discussion`, `risk_factors`, `major_subsidiaries`, `main_business_segments`（锚点：寿险、产险、健康险、财产保险、人身保险）

#### 保险专用字段

| key | label_cn | extraction | anchors（草案） | expected_location |
|---|---|---|---|---|
| `premium_income` | 保费/已赚保费 | numeric | 已赚保费、保险业务收入、原保险保费收入 | MD&A 或利润表摘要 |
| `investment_income` | 投资收益 | numeric | 投资收益、净投资收益、投资资产 | MD&A 投资业务 |
| `claims_expense` | 赔付/给付支出 | numeric | 赔付支出、给付支出、退保金 | MD&A 或利润表 |
| `solvency_ratio` | 偿付能力充足率 | numeric | 偿付能力充足率、综合偿付能力、核心偿付能力 | MD&A 偿付能力 |
| `combined_ratio` | 综合成本率 | numeric | 综合成本率、赔付率、费用率 | 财险公司 MD&A（optional） |
| `embedded_value` | 内含价值 | numeric | 内含价值、有效业务价值、一年新业务价值 | 寿险公司 MD&A（optional） |
| `revenue_by_segment` | 营业收入构成-分险种 | table | 分险种、寿险、产险、保险业务收入 | MD&A 分险种经营情况 |

**保险不适用字段：**

- `top_customers` → **N/A**（保单分散，一般不披露客户集中度）
- `top_suppliers` → **N/A**
- `revenue_by_region` → 极少 → **N/A**
- `rnd_investment` → **N/A**
- `major_products` → **N/A**（险种即产品，已在 segment 中体现）

---

### 3.4 其他金融（`other_financial_v1`）

期货（如永安期货）、信托、多元金融等：

- **v1 策略**：继续复用现有 `FINANCIAL_FIELD_SPECS`（generic 11 字段）
- **后续**：若样本增多，可单独设计 `futures_v1` 等子 schema
- eval 报告中标注为「其他金融，schema 待细化」

## 4. 跨类型字段适用性总表

| 字段 | 工业 | 银行 | 券商 | 保险 | 说明 |
|---|---|---|---|---|---|
| `mda` | ✓ | ✓ | ✓ | ✓ | 通用 |
| `industry_discussion` | ✓ | ✓ | ✓ | ✓ | 通用；金融侧重监管/宏观 |
| `risk_factors` | ✓ | ✓ | ✓ | ✓ | 通用；金融侧重信用/市场/流动性风险 |
| `major_subsidiaries` | ✓ | ✓ | ✓ | ✓ | 通用 |
| `main_business_segments` | ✓ | ✓（重锚） | ✓（重锚） | ✓（重锚） | 语义相同，锚点不同 |
| `revenue_by_segment` | ✓ 分行业/产品 | 重映射 分部业绩 | 重映射 分业务 | 重映射 分险种 | 表格结构不同 |
| `revenue_by_region` | ✓ | 部分（大银行） | 罕见 | 罕见 | 银行用 `regional_distribution` |
| `top_customers` | ✓ 前五名客户 | 替换 最大十家借款人 | 弱/可选 | N/A | |
| `top_suppliers` | ✓ | N/A | N/A | N/A | 金融公司无供应商概念 |
| `rnd_investment` | ✓ | 可选 科技投入 | 可选 | N/A | |
| `major_products` | ✓ | N/A | N/A | N/A | 由 segment 替代 |

**图：schema 与 profile 关系（目标架构）**

```
FieldSpec (base)
├── industrial (当前 11 字段，默认)
├── bank_v1      ← 已实现 (13 字段)
├── broker_v1    ← 已实现 (12 字段)
├── insurer_v1   ← 已实现 (12 字段)
└── other_financial_v1 ← 已实现 (8 字段; legacy alias: financial)
```

## 5. 评估报告建议

### 5.1 当前做法（eval1000 已部分实现）

- eval 公司列表中 `financial: true` 标记（**16 家**：银行含沪农商行、券商若干、保险、资本类）
- summary 中**非金融 headline** 仅统计 `financial: false` 的公司（eval1000_v2：936 家；independent：907 家）
- 金融公司单独一行：「金融公司（单独统计）」

### 5.2 推荐报告结构（实现子 schema 后）

| 指标 | 范围 | 说明 |
|---|---|---|
| **非金融 strict-usable** | `financial: false` | 主 headline，11 字段 industrial schema |
| **银行 coverage** | `profile=bank` | bank_v1 字段集 plausible / strict 均值 |
| **券商 coverage** | `profile=broker` | broker_v1 字段集 |
| **保险 coverage** | `profile=insurer` | insurer_v1 字段集 |
| **全样本 status=ok 率** | 全部 1020 | 下载/解析成功率，与 schema 无关 |

**原则：**

1. **保留在 eval run 中**：金融公司仍跑抽取与评估，便于回归与样本积累。
2. **tag 为 financial**：列表 + 运行时 `profile` 字段双重标记。
3. **排除出非金融 headline**：工业 11 字段均值不包含金融公司。
4. **单独报告金融 coverage**：子 schema 实现后，按 bank/broker/insurer 分别报字段级 plausible 与 strict-usable。

### 5.3 数据库 implications（后续）

- `company_basic` 或 `report_source` 增加 `financial_subtype`（bank / broker / insurer / other / null）
- `extracted_field.field_name` 将包含金融专用 key（如 `npl_ratio`）；需与 industrial 字段并存
- `evaluation_result` 可按 `run_name` + `profile` 分维度汇总

## 6. 实现路径

| Phase | 状态 |
|---|---|
| Phase 1–2：子 schema + profile 检测/分发 | **Done**（Issue #4） |
| Phase 3：金融专用 numeric/table plausible 规则 | 未做（#28+；复用 generic extract_numeric/table） |
| Phase 4：eval summary 分 subtype 报告 | **部分**（`schema_profile` + eval_summary 金融段） |
| **#27 Phase 0–1B：金融 audit 框架** | **Done**（inventory + automated strict + calibration worksheet；grading 待完成） |
| Phase 5：DB `financial_subtype` + 新 field_name 入库 | 未做 |

### #27 金融 automated strict（Phase 1A，86 ok × ~1,059 cells）

**不得与 non-fin 9.43/11 混报。** 非全量人工验证。

| subtype | strict usable | strict lenient | proxy |
|---|---:|---:|---:|
| bank (43) | **9.00 / 13** | 11.28 / 13 | 8.98 / 13 |
| broker (37) | **7.66 / 12** | 9.00 / 12 | 8.57 / 12 |
| insurer (2) | **9.25 / 12** | 10.50 / 12 | 10.50 / 12 |
| other_financial (4) | **5.75 / 8** | 7.00 / 8 | 5.50 / 8 |

标签分布（population）：usable 557 / partial 310 / wrong 81 / not_found_missed 75 / not_found_unverified 36。

**Audit 解读 caveat（#27 严格 review）：**

- `not_found_missed`（75 cells）为 PDF anchor **recall hint**，**非确认 truth**；**broker 占比高**（~58/75），`投资收益` 等锚点易触发 — 须 Phase 1B worksheet 人工 grade（`MISSED` vs `ABSENT-OK`）确认。
- `major_subsidiaries` **0/86 usable** 主因 industrial-style `in_region` / 附注 vs MD&A 门控，**结构性 partial**；**不得**过度解读为金融 subtype 抽取失败。
- **insurer n=2**：§ 上表 insurer 均值 **非统计显著**，仅作方向参考。
- **financial under-tagging scan**（YAML `financial: true` 完整性）**未做**，deferred **#28 或更晚**。

**Subtype caveats（stored schema；audit 仍按 stored 跑）：**

| code | 说明 |
|---|---|
| 000402 金融街 | stored `broker`；疑为地产/REIT，非券商 |
| 600816 建元信托 | stored `bank`；疑为 trust / `other_financial` |
| 600318 新力金融 | stored `bank`；多元金融控股，subtype 不清 |

**产物：**

- [financial_audit_summary.md](../outputs/generalization/full_market_2024/financial_audit_summary.md)
- `financial_audit_population.csv`（1,059 rows）
- `financial_population_inventory.csv`（87 YAML financial）
- `financial_audit_sample.csv`（30 公司 × 325 cells；**manual_grade blank**）

**验证样本（cached PDF）：**

- 银行：601988 中国银行、601398 工商银行
- 券商：600958 东方证券、601162 天风证券
- 保险：601336 新华保险

## 7. 开放问题

1. **子类型自动检测**：仅靠年报前 80 页关键词（现有 `FINANCIAL_TERMS`）能否稳定区分 bank/broker/insurer？是否需引入证监会行业代码？
2. **字段数量**：bank_v1 约 13 字段、broker_v1 约 12、insurer_v1 约 11；是否与 industrial 11 字段对齐为「约 11 字段」以简化 headline，还是允许子 schema 字段数不同？
3. **N/A vs not_found**：对 `top_suppliers` 等明确不适用字段，应用 `not_applicable` 状态还是继续 `not_found`？
4. **A+H 金融公司**：部分银行/保险同时披露 H 股报告；是否与工业公司一样优先 A 股全文 PDF？
5. **期货/信托**：eval 样本少；是否 v1 仅文档化 generic fallback，待样本 ≥5 再设计专用 schema？

## 8. 相关文档

- [项目概览](project_overview.md)
- [年报抽取流程](annual_report_extraction.md)
- [评估方法](evaluation_method.md)
- [数据库存储方案](database_schema.md)
- [当前状态](../CURRENT_STATUS.md)
- 代码参考：`lab/field_schema.py`（`FIELD_SPECS`, `FINANCIAL_FIELD_SPECS`, `detect_profile`）
