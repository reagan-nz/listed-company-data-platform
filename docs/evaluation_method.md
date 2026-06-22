# 评估方法

## 核心原则

> **自动 `plausible` ≠ 人工准确率。**
>
> 解读任何 headline 数字时，必须结合人工校准（calibration_sample）与严格二次审计（对 stored value 的 adversarial 规则复核）。直接把 plausible 当准确率会高估 3–4 个百分点。

**rnd_investment proxy（2026-06-22 起）**：`status=found` 且 `labeled` 中至少含一条实质 R&D 金额（非 ratio-only、非 0.00 资本化行、非列表编号）；抽取侧优先 `研发投入金额/总额/合计` 标签，并排除利润表 `研发费用` 行。

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

### 4. 1000 家受控评估（eval1000）

- **目的**：大规模验证改进后 pipeline 的稳定性与泛化
- **方法**：
  - 200 家 strict superset + 820 新增（`--scale 5`，同 seed）
  - 复用 eval200 的 184 份缓存 PDF
  - 金融公司单独标记与统计
- **结果**：
  - 1020 样本，946 OK，73 no_announcement，0 hard error
  - 非金融 proxy plausible：10.5/11（96%）
  - 200 子集：27 改进，0 回归
- **产出**：`outputs/generalization/eval1000/eval_summary.md`

### 5. 人工校准（calibration_sample）

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

### 6. 严格二次审计

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

| 指标 | eval1000 非金融 | 含义 | 可信度 |
|---|---|---|---|
| proxy plausible | 10.5/11 (96%) | 自动规则判定 | 中（高估 3–4pp） |
| 校准 precision | 94% (60 格) | 人工 CORRECT / plausible | 高（但样本小） |
| strict-usable | 10.16/11 (92.4%) | 全量 adversarial 复核 | **最高** |
| hard-wrong rate | 1.9% | 全量真 false positive | 高 |

**推荐对外报告数字**：strict-usable **10.16/11（92.4%）**，而非 proxy 的 10.5/11。

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
