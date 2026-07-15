# CNINFO B 类 Retrieval Next-Task Search — B-R16-03 IDLE

_生成时间：2026-07-15（honest search only；无 fixture 变更；无 CNINFO）_

| 字段 | 值 |
|------|-----|
| task_id | B-R16-03 |
| track | B |
| executor | b-class-executor |
| controller_execution_allowed | false |
| result | **IDLE** |
| CNINFO live | **0** |
| allow-list | 无（未开启 live） |
| wall_time_s | **0**（无 live / 无 runner） |
| FP lineage invented | **无** |
| commit / push | **无** |
| ready_for_commit | **false**（无能力增量产物；仅 IDLE 拒绝记录） |

## 1. 搜索优先级与结论

| 优先级 | 候选 | 结论 |
|--------|------|------|
| 1 | 自既有 harvest 证据再晋升 known-document placeholder | **拒绝** — 无可区分、可对齐路由的新样本 |
| 2 | 对尚未 live 的 ready known-document 做 metadata | **拒绝** — 8/8 ready 均已 LIVE_PASS |
| 3 | retrieval path 证据质量修补 | **拒绝** — 当前 ready 集无失败；路由边角修改属扩 scope，非本轮必要 |

明确排除：新造 §7 offline FP lineage、纯 docs/policy。

## 2. 优先级 1 拒绝细节（placeholder 晋升）

当前仍为 `placeholder`：`inquiry_known_001`、`regulatory_known_001`、`regulatory_known_003`、`ir_activity_known_002`。

只读扫描 B erad/phase report CSV（quality=pass）后：

| 缺口 | 证据事实 |
|------|----------|
| 监管问询函原文 | **0** 条「收到…问询函/关注函」且无「回复」标题 |
| 警示函候选 | BD2E626 壹网壹创「关于收到浙江证监局警示函的公告」路由为 `announcement` / `cninfo_general_announcement_pdf`，**不能**填 `regulatory_inquiry` |
| 问询函回复增量 | 含「回复公告」的公司问询回复仅 BD2E470（已用于 `inquiry_known_002`） |
| CPA「问询函的回复」 | BD2E462 / BD2E794 在现行 `_inquiry_document_type` 下预测为 `regulatory_inquiry`（缺「回复公告」连续标记），晋升后 live 会 misclassified |
| 延期回复 | BD2E500 希荻微同属边角，预测 `regulatory_inquiry`，不适配 `inquiry_reply` |
| 投资者交流活动 | **0** 条；仅已占用的「投资者关系活动记录表」BD2E071 |

与 B-R16-01 §6 结论一致：缺可区分「监管问询函原文 / 投资者交流活动」样本。

## 3. 优先级 2 拒绝细节（追加 live）

| case_id | live 证据 |
|---------|-----------|
| `inquiry_known_003` | `outputs/validation/cninfo_b_class_corpus_retrieval_live_report.csv`（2026-07-05）PASS |
| `regulatory_known_002` | 同上 PASS |
| `meeting_known_001` | 同上 PASS |
| `board_resolution_known_001` | 同上 PASS |
| `inquiry_known_002` | B-R16-02 live sample PASS |
| `meeting_known_002` | B-R16-02 PASS |
| `ir_activity_known_001` | B-R16-02 PASS |
| `shareholder_meeting_known_001` | B-R16-02 PASS |

重跑 live = CNINFO 预算消耗且 **capability_gain=0**。

## 4. 优先级 3 拒绝细节

- 现行 8 ready known-document + `periodic_guard_002` 均已 classified_correctly。
- 修补「问询函的回复」reply marker 会改 shared routing，需专项测试与回归；不属于「单条最高价值下一任务」的最小闭环。
- 修正 ready case notes 中过时「Keep placeholder」措辞 = 纯文档清洁，本任务禁止 docs-only busywork。

## 5. 未触碰

- A/C/D 文件
- fixture / lab 代码
- CNINFO / PDF / verified / source status
- commit / push

## 6. 建议 Controller

1. 保持 B retrieval 线 IDLE，直至出现新的 harvest 样本（真·监管问询函原文或真·投资者交流活动）或明确批准 routing 边角专项。
2. 本文件仅作拒绝审计；**不要**当作 commit 候选。
