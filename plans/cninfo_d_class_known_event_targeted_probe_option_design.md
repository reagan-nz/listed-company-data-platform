# CNINFO D 类 Known Event — Targeted Probe Option Design

_生成时间：2026-07-09_

> **性质：** 设计 only · **无实现** · **无 live** · **无 CNINFO** · **NOT APPROVED**

**关联：** [live failure review](cninfo_d_class_known_event_replacement_live_failure_review.md) · [evidence reconciliation matrix](../outputs/validation/cninfo_d_class_known_event_replacement_evidence_reconciliation_matrix.csv)

---

## 1. Context

Replacement live（bounded probe）结果：**2/2 failed** · `empty_but_valid_after_budget` · CNINFO **40** · gate **`FAIL_REVIEW_REQUIRED`**

人工披露证据存在，但 metadata 端点未返回公司级行。本设计评估 **event-date targeted probe** 是否为合理下一步。

---

## 2. Option A — Event-Date Targeted Probe Extension（推荐规划优先）

### DLC003R `restricted_shares_unlock`

| 项 | 建议值 |
|----|--------|
| company_code | 688671 |
| anchor date | **2024-02-19** |
| endpoint | 既有 `liftBan/detail` |
| purpose | 测试 date-targeted `tdate` 查询能否 surfacing unlock 记录 |
| request cap | **≤ 12** |
| probe window | anchor ±7d / ±30d / 月末邻近日（去重后） |

### DLC006R `shareholder_change`

| 项 | 建议值 |
|----|--------|
| company_code | 301259 |
| anchor date | **2024-07-16** |
| endpoint | 既有 `shareholeder/detail` |
| purpose | 测试 date-targeted `type`+`tdate` 查询能否 surfacing 股东变动记录 |
| request cap | **≤ 12** |
| probe window | anchor ±7d / ±30d / inc+desc 模式邻近日 |

### 合计预算

| 项 | 建议值 |
|----|--------|
| total request cap | **≤ 24** |
| early stop | 任一 case 公司级命中 ≥1 行即停 |

### 隔离输出根

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

**禁止写入：** replacement live 报告 · v1/v2 输出根 · original/calibrated universe

### 建议 approval flag

```text
--approve-d-class-known-event-targeted-probe
```

### 建议 CLI 模式（未来 · NOT APPROVED）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --known-event-targeted-probe \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_targeted_probe/ \
  --approve-d-class-known-event-targeted-probe \
  --cases DLC003R,DLC006R
```

**本设计不实现上述 flag。**

### Option A 成功/失败 gate（未来）

| 结果 | 建议 gate |
|------|-----------|
| 双 case 可接受命中 | `PASS_WITH_CAVEAT`（**不是 PASS**） |
| 部分/全部仍空 | `FAIL_REVIEW_REQUIRED` |

---

## 3. Option B — Accept Outstanding Gap with Human Signoff

接受 `restricted_shares_unlock` · `shareholder_change` 组件级 live `captured_normal` **仍 outstanding**，以人工披露证据作为 **parallel disclosure track**，不升级为 live captured 证据。

| 优点 | 风险 |
|------|------|
| 不增加 CNINFO | mapper 回归 live 证据仍缺 |
| 边界清晰 | 可能过度依赖人工记录 |

需显式人工 signoff · **不是 verified**

---

## 4. Option C — Hold Until Endpoint Behavior Understood

暂停 known-event replacement 轨道，优先研究：

- metadata 端点与公司级过滤逻辑
- 披露事件日 vs API `tdate` 参数对齐
- 端点是否索引 finalpage 类披露

| 优点 | 风险 |
|------|------|
| 避免无效 probe 花费 | 组件缺口长期 open |

---

## 5. Recommendation

```text
Recommended: Option A planning package first
Not: live execution
Not: implementation in this round
Not: PASS / verified / production_ready upgrade
```

**下一步：** 完成 targeted probe planning checklist 评审 → runner extension 设计 → dry-run → 人工 approval 后 isolated live

---

## 6. Gate

```text
d_class_known_event_targeted_probe_planning_gate = NOT_STARTED
d_class_known_event_replacement_live_failure_review_gate = READY_FOR_HUMAN_DECISION
```

**NOT APPROVED** · **approved_for_live = false**
