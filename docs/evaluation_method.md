# 评估方法

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

## 指标对照表

| 指标 | eval1000（baseline） | eval1000_v2（同 cohort） | independent（新 cohort） | 含义 | 可信度 |
|---|---|---|---|---|---|
| proxy plausible | 10.5/11 | **10.33/11** | **10.30/11** | 自动规则判定 | 中（高估 3–4pp） |
| 校准 precision | 94%（60 格） | 未重跑 | 未重跑 | 人工 CORRECT/plausible | 高（但样本小） |
| strict-usable | **10.16/11** (92.4%) | **未重跑** | **未重跑** | 全量 adversarial 复核 | **最高** |
| hard-wrong rate | 1.9% | 未重跑 | 未重跑 | 全量真 false positive | 高 |

> **重要说明**：strict-usable 10.16/11 来自 eval1000 baseline（Issue #1/#2 前）。v2/independent 的更严规则使 proxy 下降至 10.33/10.30，strict 是否同步改善**尚未重新审计**，不得声称 strict 已改善。

**推荐对外报告**：如需报告单一数字，用 strict-usable **10.16/11（92.4%）**并标注「eval1000 baseline，v2 未重跑」；如需报告泛化结论，用 independent 非金融 proxy **10.30/11**。

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
