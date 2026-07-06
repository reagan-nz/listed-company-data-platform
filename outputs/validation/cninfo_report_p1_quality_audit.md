# CNINFO P1 Report Retrieval 人工审计清单

- 生成时间：2026-07-05T02:07:09Z
- 来源：[cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv)
- 抽样清单：[cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv)
- P1 跑次摘要：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- P1 最终总结：[cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md)

---

## 1. 为什么要人工审计

P1 A 类 report retrieval 自动跑次结果为 **750/796 = 94.22%**（effective coverage / retrieval hit rate）。

需要明确：

- **94.22% 是自动 retrieval coverage，不是人工 accuracy（准确率）**；
- 自动 **found** 仅表示脚本认为：**标题**匹配 `report_type`、**parsed_report_period** 与 `expected_period` 一致、**pdf_url** 非空（annual/semi 另经 title filter 排除说明会/预告/摘要类标题）；
- 在上述规则下，**Q1/Q3 对说明会 / 预告 / 披露提示类标题的过滤弱于 annual/semi**，found 行中仍可能存在少量**假阳性**；
- **not_found** 也可能存在假阴性（报告存在但检索策略未命中）。

因此需要在扩面或宣称 pipeline 稳定之前，对 P1 结果做**随机抽样 + 人工打开 PDF / CNINFO 核对**，估计真实 pass rate 与主要 issue 类型。

**本次文档仅生成审计清单与填写说明；Cursor 未做人工判断。**

---

## 2. 本次抽样设计

| sample_group | 目标条数 | 实际条数 | 池内可用 |
|--------------|----------|----------|----------|
| annual_report found | 20 | 20 | 193 |
| semi_annual_report found | 20 | 20 | 185 |
| quarterly_report_q1 found | 30 | 30 | 185 |
| quarterly_report_q3 found | 30 | 30 | 187 |
| not_found | 20 | 20 | 46 |

- **random seed**：`42`（可复现）
- **实际抽样总数**：**120**
- **Q1/Q3 found 中含风险词标题**（说明会/预告/摘要/投资者交流/披露提示等）：**16** 条（池内 Q1 风险 8、Q3 风险 8，已优先混入样本）

### 各 exchange 覆盖

| exchange | 条数 |
|----------|------|
| BSE | 19 |
| SSE | 50 |
| SZSE | 51 |

### 各 exchange × board 覆盖

| exchange | board | 条数 |
|----------|-------|------|
| BSE | 北交所 | 19 |
| SSE | 主板 | 21 |
| SSE | 科创板 | 29 |
| SZSE | 主板 | 19 |
| SZSE | 创业板 | 32 |

各 sample_group 均达到目标条数。

### not_found 样本 failure_reason 分布

| failure_reason | 条数 |
|----------------|------|
| empty_response | 12 |
| period_mismatch | 8 |

---

## 3. 怎么人工检查

对 [cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv) 中每一行：

1. **打开 `pdf_url`**（found 样本；not_found 通常无 URL，改在 CNINFO 公告页检索）；
2. 核对**标题**是否为**正式报告**全文（或可接受的正式披露形式）；
3. 确认**不是**说明会、预告公告、摘要、投资者交流 / 业绩说明会类公告；
4. 确认**公司**与 `company_code` / `company_name` 一致；
5. 确认 **report_type**（年报 / 半年报 / 一季报 / 三季报）与 PDF 内容一致；
6. 确认 **report_period** 与 `expected_period`（2024 / 2024H1 / 2024Q1 / 2024Q3）一致；
7. 对 **not_found** 样本：可在 CNINFO 公司公告页用报告期 + 关键词**简单人工检索**，判断是「真不存在」还是「脚本未命中」（`not_found_but_exists`）。

---

## 4. 人工字段填写说明

在 CSV 中填写以下列（生成时默认 `pending` / 空）：

| 字段 | 说明 | 建议取值 |
|------|------|----------|
| `manual_pdf_opens` | PDF 是否可打开 | `yes` / `no` / `pending` |
| `manual_is_official_report` | 是否为正式报告（非说明会/预告/摘要/交流类） | `yes` / `no` / `uncertain` / `pending` |
| `manual_company_correct` | 公司主体是否正确 | `yes` / `no` / `pending` |
| `manual_report_type_correct` | report_type 是否正确 | `yes` / `no` / `pending` |
| `manual_period_correct` | 报告期是否正确 | `yes` / `no` / `pending` |
| `manual_title_problem` | 若标题有问题，简述（如「业绩说明会预告」） | 自由文本 |
| `manual_issue_type` | 问题分类 | 见下表 |
| `manual_audit_result` | 本条审计结论 | `pass` / `fail` / `uncertain` / `pending` |
| `manual_auditor_notes` | 补充说明 | 自由文本 |

### `manual_issue_type` 可选值

- `ok` — 无问题
- `pdf_unavailable` — PDF 打不开或链接失效
- `wrong_company` — 公司不对
- `wrong_report_type` — 报告类型不对（如命中半年报却标年报）
- `wrong_period` — 报告期不对
- `title_false_positive` — 标题匹配但非正式报告
- `summary_or_abstract_only` — 仅摘要/节选，非全文
- `investor_meeting_notice` — 说明会/投资者交流类
- `announcement_preview` — 预告/提示性公告
- `not_found_but_exists` — 脚本 not_found 但人工查到存在
- `other` — 其他

### `manual_audit_result` 可选值

- `pass` — 脚本结论与人工一致且内容正确（found 且正式报告正确；或 not_found 且确认不存在）
- `fail` — 脚本结论错误或内容明显不对
- `uncertain` — 无法判断（如 PDF 乱码、需进一步查阅）
- `pending` — 尚未审计

---

## 5. 审计完成后怎么统计

人工填完 CSV 后，可离线统计（示例口径，**不写 verified**）：

| 指标 | 计算方式 |
|------|----------|
| **pass rate** | `manual_audit_result=pass` / 已完成审计条数 |
| **false positive count** | found 样本中 `manual_audit_result=fail` 且 issue 为 title_false_positive / summary_or_abstract_only / investor_meeting_notice / announcement_preview 等 |
| **false negative count** | not_found 样本中 `manual_issue_type=not_found_but_exists` |
| **by report_type pass rate** | 按 `report_type` 分组统计 pass rate |
| **by exchange / board pass rate** | 按 `exchange`、`board` 分组统计 pass rate |
| **main issue types** | `manual_issue_type` 计数（排除 `ok`） |

建议将统计结果写入 `cninfo_report_p1_quality_audit_results.md`（人工审计完成后另建，本次不生成）。

---

## 6. 边界

- 本次**仅生成审计清单**（CSV + 本 Markdown）；
- **未联网**；**未打开 PDF**；**未下载 PDF**；**未解析 PDF**；
- **未做人工判断**；所有 `manual_*` 字段为占位；
- **不写 verified**；审计结果仅代表 P1 抽样样本，不代表全市场准确率。

---

## 附录：audit_id 索引

| audit_id | sample_group | company_code | company_name | report_type | found |
|----------|--------------|--------------|--------------|-------------|-------|
| P1-AUD-001 | annual_report_found | 871753 | 天纺标 | annual_report | yes |
| P1-AUD-002 | annual_report_found | 600738 | 丽尚国潮 | annual_report | yes |
| P1-AUD-003 | annual_report_found | 688178 | 万德斯 | annual_report | yes |
| P1-AUD-004 | annual_report_found | 002132 | 恒星科技 | annual_report | yes |
| P1-AUD-005 | annual_report_found | 301302 | 华如科技 | annual_report | yes |
| P1-AUD-006 | annual_report_found | 002011 | 盾安环境 | annual_report | yes |
| P1-AUD-007 | annual_report_found | 301133 | 金钟股份 | annual_report | yes |
| P1-AUD-008 | annual_report_found | 600790 | 轻纺城 | annual_report | yes |
| P1-AUD-009 | annual_report_found | 688213 | 思特威 | annual_report | yes |
| P1-AUD-010 | annual_report_found | 831689 | 克莱特 | annual_report | yes |
| P1-AUD-011 | annual_report_found | 688251 | 井松智能 | annual_report | yes |
| P1-AUD-012 | annual_report_found | 688141 | 杰华特 | annual_report | yes |
| P1-AUD-013 | annual_report_found | 300278 | 华昌达 | annual_report | yes |
| P1-AUD-014 | annual_report_found | 688709 | 成都华微 | annual_report | yes |
| P1-AUD-015 | annual_report_found | 603194 | 中力股份 | annual_report | yes |
| P1-AUD-016 | annual_report_found | 603657 | 春光科技 | annual_report | yes |
| P1-AUD-017 | annual_report_found | 688016 | 心脉医疗 | annual_report | yes |
| P1-AUD-018 | annual_report_found | 688651 | 盛邦安全 | annual_report | yes |
| P1-AUD-019 | annual_report_found | 002091 | 江苏国泰 | annual_report | yes |
| P1-AUD-020 | annual_report_found | 873690 | 捷众科技 | annual_report | yes |
| P1-AUD-021 | semi_annual_report_found | 832171 | 志晟信息 | semi_annual_report | yes |
| P1-AUD-022 | semi_annual_report_found | 601992 | 金隅集团 | semi_annual_report | yes |
| P1-AUD-023 | semi_annual_report_found | 688733 | 壹石通 | semi_annual_report | yes |
| P1-AUD-024 | semi_annual_report_found | 003006 | 百亚股份 | semi_annual_report | yes |
| P1-AUD-025 | semi_annual_report_found | 301500 | 飞南资源 | semi_annual_report | yes |
| P1-AUD-026 | semi_annual_report_found | 002171 | 楚江新材 | semi_annual_report | yes |
| P1-AUD-027 | semi_annual_report_found | 603303 | 得邦照明 | semi_annual_report | yes |
| P1-AUD-028 | semi_annual_report_found | 688588 | 凌志软件 | semi_annual_report | yes |
| P1-AUD-029 | semi_annual_report_found | 002541 | 鸿路钢构 | semi_annual_report | yes |
| P1-AUD-030 | semi_annual_report_found | 002668 | TCL智家 | semi_annual_report | yes |
| P1-AUD-031 | semi_annual_report_found | 603353 | 和顺石油 | semi_annual_report | yes |
| P1-AUD-032 | semi_annual_report_found | 002712 | 思美传媒 | semi_annual_report | yes |
| P1-AUD-033 | semi_annual_report_found | 600688 | 上海石化 | semi_annual_report | yes |
| P1-AUD-034 | semi_annual_report_found | 688001 | 华兴源创 | semi_annual_report | yes |
| P1-AUD-035 | semi_annual_report_found | 688510 | 航亚科技 | semi_annual_report | yes |
| P1-AUD-036 | semi_annual_report_found | 688528 | 秦川物联 | semi_annual_report | yes |
| P1-AUD-037 | semi_annual_report_found | 831087 | 秋乐种业 | semi_annual_report | yes |
| P1-AUD-038 | semi_annual_report_found | 688196 | 卓越新能 | semi_annual_report | yes |
| P1-AUD-039 | semi_annual_report_found | 300320 | 海达股份 | semi_annual_report | yes |
| P1-AUD-040 | semi_annual_report_found | 002132 | 恒星科技 | semi_annual_report | yes |
| P1-AUD-041 | quarterly_report_q1_found | 300080 | 易成新能 | quarterly_report_q1 | yes |
| P1-AUD-042 | quarterly_report_q1_found | 300661 | 圣邦股份 | quarterly_report_q1 | yes |
| P1-AUD-043 | quarterly_report_q1_found | 301058 | 中粮科工 | quarterly_report_q1 | yes |
| P1-AUD-044 | quarterly_report_q1_found | 920106 | 林泰新材 | quarterly_report_q1 | yes |
| P1-AUD-045 | quarterly_report_q1_found | 300695 | 兆丰股份 | quarterly_report_q1 | yes |
| P1-AUD-046 | quarterly_report_q1_found | 300625 | 三雄极光 | quarterly_report_q1 | yes |
| P1-AUD-047 | quarterly_report_q1_found | 300732 | 设研院 | quarterly_report_q1 | yes |
| P1-AUD-048 | quarterly_report_q1_found | 300320 | 海达股份 | quarterly_report_q1 | yes |
| P1-AUD-049 | quarterly_report_q1_found | 920475 | 三友科技 | quarterly_report_q1 | yes |
| P1-AUD-050 | quarterly_report_q1_found | 600117 | 西宁特钢 | quarterly_report_q1 | yes |
| P1-AUD-051 | quarterly_report_q1_found | 688320 | 禾川科技 | quarterly_report_q1 | yes |
| P1-AUD-052 | quarterly_report_q1_found | 002712 | 思美传媒 | quarterly_report_q1 | yes |
| P1-AUD-053 | quarterly_report_q1_found | 300200 | 高盟新材 | quarterly_report_q1 | yes |
| P1-AUD-054 | quarterly_report_q1_found | 301020 | 密封科技 | quarterly_report_q1 | yes |
| P1-AUD-055 | quarterly_report_q1_found | 920580 | 科创新材 | quarterly_report_q1 | yes |
| P1-AUD-056 | quarterly_report_q1_found | 920418 | 苏轴股份 | quarterly_report_q1 | yes |
| P1-AUD-057 | quarterly_report_q1_found | 920779 | 武汉蓝电 | quarterly_report_q1 | yes |
| P1-AUD-058 | quarterly_report_q1_found | 603578 | 三星新材 | quarterly_report_q1 | yes |
| P1-AUD-059 | quarterly_report_q1_found | 301263 | 泰恩康 | quarterly_report_q1 | yes |
| P1-AUD-060 | quarterly_report_q1_found | 002413 | 雷科防务 | quarterly_report_q1 | yes |
| P1-AUD-061 | quarterly_report_q1_found | 300041 | 回天新材 | quarterly_report_q1 | yes |
| P1-AUD-062 | quarterly_report_q1_found | 600885 | 宏发股份 | quarterly_report_q1 | yes |
| P1-AUD-063 | quarterly_report_q1_found | 688570 | 天玛智控 | quarterly_report_q1 | yes |
| P1-AUD-064 | quarterly_report_q1_found | 000686 | 东北证券 | quarterly_report_q1 | yes |
| P1-AUD-065 | quarterly_report_q1_found | 688336 | 三生国健 | quarterly_report_q1 | yes |
| P1-AUD-066 | quarterly_report_q1_found | 300481 | 濮阳惠成 | quarterly_report_q1 | yes |
| P1-AUD-067 | quarterly_report_q1_found | 002213 | 大为股份 | quarterly_report_q1 | yes |
| P1-AUD-068 | quarterly_report_q1_found | 839167 | 同享科技 | quarterly_report_q1 | yes |
| P1-AUD-069 | quarterly_report_q1_found | 688161 | 威高骨科 | quarterly_report_q1 | yes |
| P1-AUD-070 | quarterly_report_q1_found | 688588 | 凌志软件 | quarterly_report_q1 | yes |
| P1-AUD-071 | quarterly_report_q3_found | 300320 | 海达股份 | quarterly_report_q3 | yes |
| P1-AUD-072 | quarterly_report_q3_found | 300554 | 三超新材 | quarterly_report_q3 | yes |
| P1-AUD-073 | quarterly_report_q3_found | 300732 | 设研院 | quarterly_report_q3 | yes |
| P1-AUD-074 | quarterly_report_q3_found | 301058 | 中粮科工 | quarterly_report_q3 | yes |
| P1-AUD-075 | quarterly_report_q3_found | 300661 | 圣邦股份 | quarterly_report_q3 | yes |
| P1-AUD-076 | quarterly_report_q3_found | 300695 | 兆丰股份 | quarterly_report_q3 | yes |
| P1-AUD-077 | quarterly_report_q3_found | 300625 | 三雄极光 | quarterly_report_q3 | yes |
| P1-AUD-078 | quarterly_report_q3_found | 300278 | 华昌达 | quarterly_report_q3 | yes |
| P1-AUD-079 | quarterly_report_q3_found | 920026 | 卓兆点胶 | quarterly_report_q3 | yes |
| P1-AUD-080 | quarterly_report_q3_found | 600633 | 浙数文化 | quarterly_report_q3 | yes |
| P1-AUD-081 | quarterly_report_q3_found | 688733 | 壹石通 | quarterly_report_q3 | yes |
| P1-AUD-082 | quarterly_report_q3_found | 000560 | 我爱我家 | quarterly_report_q3 | yes |
| P1-AUD-083 | quarterly_report_q3_found | 301302 | 华如科技 | quarterly_report_q3 | yes |
| P1-AUD-084 | quarterly_report_q3_found | 600738 | 丽尚国潮 | quarterly_report_q3 | yes |
| P1-AUD-085 | quarterly_report_q3_found | 300001 | 特锐德 | quarterly_report_q3 | yes |
| P1-AUD-086 | quarterly_report_q3_found | 836414 | 欧普泰 | quarterly_report_q3 | yes |
| P1-AUD-087 | quarterly_report_q3_found | 688016 | 心脉医疗 | quarterly_report_q3 | yes |
| P1-AUD-088 | quarterly_report_q3_found | 688073 | 毕得医药 | quarterly_report_q3 | yes |
| P1-AUD-089 | quarterly_report_q3_found | 601619 | 嘉泽新能 | quarterly_report_q3 | yes |
| P1-AUD-090 | quarterly_report_q3_found | 002495 | 佳隆股份 | quarterly_report_q3 | yes |
| P1-AUD-091 | quarterly_report_q3_found | 600969 | 郴电国际 | quarterly_report_q3 | yes |
| P1-AUD-092 | quarterly_report_q3_found | 430017 | 星昊医药 | quarterly_report_q3 | yes |
| P1-AUD-093 | quarterly_report_q3_found | 300877 | 金春股份 | quarterly_report_q3 | yes |
| P1-AUD-094 | quarterly_report_q3_found | 600530 | 交大昂立 | quarterly_report_q3 | yes |
| P1-AUD-095 | quarterly_report_q3_found | 688510 | 航亚科技 | quarterly_report_q3 | yes |
| P1-AUD-096 | quarterly_report_q3_found | 603657 | 春光科技 | quarterly_report_q3 | yes |
| P1-AUD-097 | quarterly_report_q3_found | 832786 | 骑士乳业 | quarterly_report_q3 | yes |
| P1-AUD-098 | quarterly_report_q3_found | 688108 | 赛诺医疗 | quarterly_report_q3 | yes |
| P1-AUD-099 | quarterly_report_q3_found | 002413 | 雷科防务 | quarterly_report_q3 | yes |
| P1-AUD-100 | quarterly_report_q3_found | 300590 | 移为通信 | quarterly_report_q3 | yes |
| P1-AUD-101 | not_found | 600840 | 新湖创业 | annual_report | no |
| P1-AUD-102 | not_found | 688449 | 联芸科技 | semi_annual_report | no |
| P1-AUD-103 | not_found | 301556 | 托普云农 | semi_annual_report | no |
| P1-AUD-104 | not_found | 000522 | 白云山A | annual_report | no |
| P1-AUD-105 | not_found | 600840 | 新湖创业 | semi_annual_report | no |
| P1-AUD-106 | not_found | 688605 | 先锋精科 | semi_annual_report | no |
| P1-AUD-107 | not_found | 603194 | 中力股份 | semi_annual_report | no |
| P1-AUD-108 | not_found | 688411 | 海博思创 | semi_annual_report | no |
| P1-AUD-109 | not_found | 920080 | 奥美森 | semi_annual_report | no |
| P1-AUD-110 | not_found | 600840 | 新湖创业 | quarterly_report_q3 | no |
| P1-AUD-111 | not_found | 688605 | 先锋精科 | quarterly_report_q1 | no |
| P1-AUD-112 | not_found | 001365 | 天海电子 | quarterly_report_q1 | no |
| P1-AUD-113 | not_found | 301606 | 绿联科技 | quarterly_report_q1 | no |
| P1-AUD-114 | not_found | 000522 | 白云山A | quarterly_report_q3 | no |
| P1-AUD-115 | not_found | 920128 | 胜业电气 | quarterly_report_q1 | no |
| P1-AUD-116 | not_found | 688449 | 联芸科技 | quarterly_report_q3 | no |
| P1-AUD-117 | not_found | 301556 | 托普云农 | quarterly_report_q1 | no |
| P1-AUD-118 | not_found | 920128 | 胜业电气 | semi_annual_report | no |
| P1-AUD-119 | not_found | 920106 | 林泰新材 | semi_annual_report | no |
| P1-AUD-120 | not_found | 688605 | 先锋精科 | quarterly_report_q3 | no |
