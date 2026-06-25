# 评估方法

## 术语 Glossary

| 术语 | 英文 | 含义 |
|---|---|---|
| **total** | total | 评估 universe 中的公司总数。 |
| **ok** | ok | 脚本成功找到 2024 年报、下载/解析并写出 `company_profile.json`。**不等于每个字段都正确。** |
| **no_announcement** | no_announcement | CNINFO 当前规则下未找到可用 2024 年报。不一定是代码错误。 |
| **error** | error | 网络/下载/解析等技术失败。 |
| **proxy plausible** | proxy plausible | 自动 plausibility 分数：字段结构看起来合理。**不等于人工确认正确。** 当前 proxy 已含 Issue #1/#2 收紧规则。 |
| **strict usable** | strict usable | 更严格的 adversarial 审计标签（usable only）。比 proxy 更保守。 |
| **strict lenient** | strict lenient | usable + partial 的上界：证据相关但可能不完整/有噪声。 |
| **manual PDF deep-read** | manual PDF deep-read | 读取 PDF 页文本验证 evidence；检查 `not_found` 是否应为 missed。小样本校准，非全量人工验证。 |
| **not_found_missed** | not_found_missed | 字段在 PDF 中存在但抽取返回 not_found。**工业 strict**：manual PDF deep-read 可可靠判定。**金融 audit**：自动化 anchor 召回 hint only，须 calibration worksheet 人工 grade 确认。 |
| **非金融 headline** | non-financial headline | 11 字段均值仅统计工业类（`financial: false`）公司；金融公司用独立子 schema，**不混入**（9.43/11）。 |
| **金融 strict headline** | financial strict headline | 按 bank/broker/insurer/other 子 schema 单独报告（#27）；**不得**与 non-fin 9.43/11 混报。 |

**板块名称**：bse=北交所 | star=科创板 | szse_main=深市主板 | chinext=创业板 | sse_main=沪市主板

## 核心原则

> **自动 `plausible` ≠ 人工准确率。**
>
> 解读任何 headline 数字时，必须结合人工校准（calibration_sample）与严格二次审计（对 stored value 的 adversarial 规则复核）。直接把 plausible 当准确率会高估 3–4 个百分点。

**rnd_investment proxy（2026-06-22 起）**：`status=found` 且 `labeled` 中至少含一条实质 R&D 金额（非 ratio-only、非 0.00 资本化行、非列表编号）；抽取侧优先 `研发投入金额/总额/合计` 标签，并排除利润表 `研发费用` 行。

**revenue table proxy（2026-06-22 起）**：`revenue_by_region` / `revenue_by_segment` 在 `status=found` 且 `match_hits≥1` 基础上，preview 须含至少一行真实数据行（非表头标签 + 至少一个实质金额/比例数值）；拒绝 header-only 或空 preview。

## 测试层级

### 1. 单公司测试

- **目的**：验证抽取器对特定公司/行业的表现
- **方法**：手动下载 PDF → 运行 `extract_annual_report.py` → 人工对照 PDF 检查每个字段
- **样本**：CATL（300750）、三一重工（600031）、招商银行（600036）、澜起科技（688008）
- **产出**：`outputs/extraction/<code>/company_profile.json`

### 2. 小样本泛化测试（4 公司）

- **目的**：验证抽取概念是否 overfit 到 CATL
- **方法**：冻结 pipeline，跑 4 家结构 diverse 的公司，人工逐字段评分
- **结果**：工业/科技公司 9–10/11 CORRECT；银行 4/11 + 2 ABSENT-OK
- **产出**：[outputs/generalization/generalization_report.md](../outputs/generalization/generalization_report.md)

### 3. 200 家分层评估（eval200）

- **目的**：在中等规模上验证泛化能力，发现系统性问题
- **方法**：
  - `sample_universe.py --seed 20260617` 按板块分层抽样 200 家
  - `eval_generalize.py` 批量跑抽取 + plausible 评分
  - 人工校准 40 格（calibration_sample.py）
- **样本分层**：sse_main 60 / star 25 / szse_main 50 / chinext 45 / bse 20
- **结果**：184 家 OK；proxy plausible 约 88%；校准后 precision 约 88–93%
- **发现**：hard crash（16 家）、major_products 低召回（59%）、A+H 选错报告

### 4. 1000 家受控评估（eval1000，baseline）

- **目的**：大规模验证改进后 pipeline 的稳定性与泛化
- **方法**：
  - 200 家 strict superset + 820 新增（`--scale 5`，同 seed）
  - 复用 eval200 的 184 份缓存 PDF
  - 金融公司单独标记与统计
- **结果**：
  - 1020 样本，946 OK，73 no_announcement，0 hard error
  - 非金融 proxy plausible：10.5/11（96%）；strict-usable：10.16/11（92.4%）
  - 200 子集：27 改进，0 回归
- **产出**：`outputs/generalization/eval1000/eval_summary.md`

### 5. 同 cohort 全量重跑（eval1000_v2）

- **目的**：在 Issue #1/#2/#4（规则收紧 + 金融 schema）后，验证同一公司列表上无回归
- **方法**：
  - 同 YAML（`lab/eval_companies_1000.yaml`，1020 家）
  - 从 eval1000 预拷贝 947 份 PDF（无重新下载）
  - 运行最新代码，对比 baseline 与修复后数字
- **结果**：
  - 947 OK / 73 no_announcement / 0 error
  - 非金融 proxy：**10.33/11**（baseline 10.54，下降系更严规则所致，非故障）
  - SQLite 导入 10428 行（`run_name=eval1000_v2`）
- **产出**：`outputs/generalization/eval1000_v2/eval1000_v2_comparison.md`

> **与 baseline 的区别**：同 cohort 重跑验证的是「修复后同一批公司上无回归」，不是新公司的泛化能力。

### 6. 独立 cohort 泛化验证（independent eval1000）

- **目的**：验证管道在从未见过的公司上的泛化能力（真正的 out-of-sample 测试）
- **方法**：
  - 新 cohort：`lab/eval_companies_1000_independent_20260623.yaml`（seed 20260623，1000 家）
  - 与 eval1000 重叠 159 家（15.9%），841 家全新
  - 不预拷贝 PDF（新鲜下载，完整验证抓取链路）
  - 18 家 ChunkedEncodingError（VPN 干扰）经 VPN-off 重试全部恢复
- **结果**：
  - 918 OK / 82 no_announcement / 0 error（retry 后）
  - 非金融 proxy：**10.30/11**（vs eval1000_v2 10.33，Δ −0.04，在 ±0.15 容差内）
  - SQLite 导入 10112 行（`run_name=eval1000_independent_20260623`）
  - **泛化结论：PASS**
- **产出**：`outputs/generalization/eval1000_independent_20260623/independent_comparison.md`

> **与 eval1000_v2 的区别**：独立泛化验证使用不同 seed 抽取的公司，且不共享缓存 PDF，是对管道泛化能力更严格的测试。

### 7. 人工校准（calibration_sample）

- **目的**：测量 proxy plausible 与人工判断的一致率
- **工具**：`lab/calibration_sample.py`
- **方法**：
  1. `--eval-dir` + `--n 60` + `--seed` 生成分层样本 CSV
  2. 人工打开 PDF 对照，填写 `manual_grade` 列
  3. `--score` 计算 precision、FP rate、FN rate、field-level patterns
- **分级**：CORRECT / PARTIAL / WRONG / MISSED / ABSENT-OK
- **eval1000 结果**（60 格）：
  - precision（CORRECT only）：94%
  - false-positive rate：3%
  - calibrated population correctness：约 91%

### 8. 严格二次审计

- **目的**：不依赖小样本，对**全部 plausible 单元格**做 adversarial 规则复核
- **方法**：读取每个 plausible 字段的 stored `value`，按类型应用严格规则：
  - **numeric**：要求 TOTAL 标签 + 实质金额（≥10 万元），拒绝 list-marker 和 ratio-only
  - **table**：要求 preview 中至少一行含数字的数据行（非 header-only）
  - **concentration**：要求 evidence 含 top-5 关键词 + 合理聚合比
  - **section_snippet**：拒绝 pointer-only（详见/请见）、法律法规列表、金融工具风险
- **范围**：eval1000 全部 9937 个 plausible 单元格
- **结果**：
  - PASS：96.4%
  - hard-wrong：1.9%
  - strict-usable：10.16/11（92.4%）
  - 最弱字段：rnd_investment 67.7%，revenue_by_region 90.7%

### 9. full_market_2024 混合 strict 审计（2026-06-24）

- **目的**：在全 A 股规模上估计 strict-usable，并用小样本 PDF deep-read 校准
- **方法**（`lab/strict_audit_full_market.py`）：
  1. **自动化 adversarial recheck**：全部 5621 非金融 ok 公司 × 11 工业字段 = 61,831 cells；规则比 proxy 更严（如 rnd 要求总额标签 + ≥10万元、section 要求 in_region + len≥80、拒绝 pointer-only）
  2. **分层样本 CSV**：55 公司 × 7 targeted 字段 = 476 rows
  3. **manual PDF deep-read**：15 公司 × 7 字段 = 105 rows；PyMuPDF 读 cited page + anchor 搜索判定 `not_found_missed`
- **结果**：
  - proxy plausible：**10.35/11**
  - strict usable（usable only）：**9.01/11**（81.9%）
  - strict lenient（usable + partial）：**10.47/11**（95.2%）
  - gap proxy − strict usable：**1.34**
  - 手动 vs 自动化一致率：52/105（50%）
- **产出**：`outputs/generalization/full_market_2024/strict_audit_summary.md`、`strict_audit_sample.csv`

> **为何 proxy 10.35 与 strict 9.01 差距小于旧 gap（10.54→10.16）？** 当前 proxy 已含 Issue #1/#2 收紧规则，本身更接近 strict。**不得将 9.01 与旧 10.16 比较并声称「改善」或「下降」**——baseline、proxy 规则、universe 规模均不同。

> **不得声称全量人工验证**：9.01/11 是自动化 adversarial 全 population 估计 + 15 家 PDF 小样本校准，不是 62,890 SQLite 行的人工逐条核对。

### 10. full_market_2024 金融 strict audit（#27，2026-06-25）

- **目的**：对 86 家 `financial: true` ok 公司按子 schema 做 **单独** automated strict audit；与 non-fin 9.43/11 **完全分开**
- **方法**：
  1. Phase 0：`financial_population_inventory.csv`（87 tagged / 86 ok；subtype breakdown）
  2. Phase 1A：`lab/strict_audit_financial_full_market.py` — 1,059 field-cells；financial-specific numeric/table/section rules（非 industrial `revenue_table_plausible` 盲目复用）
  3. Phase 1B：`lab/financial_calibration_sample.py` — 30 公司 × 325 cells worksheet；`manual_grade` **待填写**
- **结果（automated strict usable，非全量人工验证）**：

| subtype | strict usable | strict lenient | proxy |
|---|---:|---:|---:|
| bank (43) | **9.00 / 13** | 11.28 / 13 | 8.98 / 13 |
| broker (37) | **7.66 / 12** | 9.00 / 12 | 8.57 / 12 |
| insurer (2) | **9.25 / 12** | 10.50 / 12 | 10.50 / 12 |
| other_financial (4) | **5.75 / 8** | 7.00 / 8 | 5.50 / 8 |

- **产出**：`financial_audit_summary.md`、`financial_audit_population.csv`、`financial_audit_sample.csv`
- **不得声称**：金融 audit 已 fully validated；`not_found_missed`（75 cells，broker-heavy）为 **recall hint 非确认 truth**；`major_subsidiaries` 低 usable 为 **结构性 partial**（industrial in_region 门控）；**insurer n=2** 勿过度解读 subtype 均值；**financial under-tagging scan** deferred #28+；extraction fixes deferred #28

```bash
# 金融 automated strict audit
python lab/strict_audit_financial_full_market.py \
  --out-dir outputs/generalization/full_market_2024

# 生成校准 worksheet
python lab/financial_calibration_sample.py --generate \
  --out-dir outputs/generalization/full_market_2024

# 填写 manual_grade 后：
python lab/financial_calibration_sample.py \
  --score outputs/generalization/full_market_2024/financial_audit_sample.csv
```

## 指标对照表

| 指标 | eval1000 | eval1000_v2 | independent | full_market_2024 | 含义 |
|---|---:|---:|---:|---:|---|
| proxy plausible | 10.5/11 | 10.33/11 | 10.30/11 | **10.35/11** | 自动规则 |
| strict usable | **10.16/11** | 未重跑 | 未重跑 | **9.01/11** | adversarial 复核 |
| strict lenient | — | — | — | **10.47/11** | usable+partial |
| 样本 | 1020 | 1020 | 1000 | **6124** | universe |

> **重要说明**：eval1000 strict 10.16/11 基于 proxy 10.5/11（Issue #1/#2 前）。full_market strict 9.01/11 基于 proxy 10.35/11（Issue #1/#2 后）。**不可直接比较为改善或退步。**

**推荐对外报告**：
- 全市场规模：**strict usable 9.01/11**（自动化 adversarial + 小样本 PDF 校准）
- 受控泛化：**proxy 10.30–10.35/11**（independent / full_market）
- 历史 baseline：**strict 10.16/11**（eval1000 only，标注 baseline 与 proxy 版本）

## 如何运行评估

```bash
# 生成公司列表
python lab/sample_universe.py --scale 5 --seed 20260617 \
  --out lab/eval_companies_1000_raw.yaml

# 批量评估
python lab/eval_generalize.py \
  --companies lab/eval_companies_1000.yaml \
  --out outputs/generalization/eval1000 --throttle 1.0

# 人工校准
python lab/calibration_sample.py \
  --eval-dir outputs/generalization/eval1000 --n 60 --seed 1000
# 填写 manual_grade 后：
python lab/calibration_sample.py \
  --score outputs/generalization/eval1000/calibration_sample_graded.csv
```

## 评估产物与 Git 提交建议

| 文件 | 大小 | 建议 |
|---|---|---|
| `eval_summary.md` | ~48KB | **提交** |
| `calibration_sample*.csv` | ~KB | **提交** |
| `calibration_sample.md` | ~KB | **提交** |
| `eval_results.json` | ~1.9MB | **不提交**（过大，本地保留） |
| `*.pdf` | MB 级 | **不提交** |
| `.cache/` | MB 级 | **不提交** |
| `run.log` | 可选 | 按需 |

## 相关文档

- [当前状态](../CURRENT_STATUS.md)
- [字段 schema](database_schema.md)
- [年报抽取流程](annual_report_extraction.md)
